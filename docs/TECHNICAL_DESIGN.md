# Technical Design Document

## Architecture

```mermaid
flowchart LR
    Client["Client / API consumer"]
    Auth["Auth Service"]
    Transport["Transport Service"]
    Search["Search Service"]
    Reservation["Reservation Service"]
    Notification["Notification Service"]
    Rabbit["RabbitMQ durable topic exchange"]

    AuthDb[("auth_db")]
    TransportDb[("transport_db")]
    SearchDb[("search_db")]
    ReservationDb[("reservation_db")]
    NotificationDb[("notification_db")]

    Client --> Auth
    Client --> Search
    Client --> Reservation
    Client --> Transport

    Search -- "REST + Basic Auth" --> Transport
    Reservation -- "REST + Basic Auth" --> Transport
    Auth -- "REST + Basic Auth" --> Notification

    Auth --> AuthDb
    Transport --> TransportDb
    Search --> SearchDb
    Reservation --> ReservationDb
    Notification --> NotificationDb

    Auth --> Rabbit
    Transport --> Rabbit
    Reservation --> Rabbit
    Notification --> Rabbit
    Rabbit --> Notification
```

## Service Responsibilities

Auth Service:
- Registers users with roles `admin`, `transport_owner`, and `passenger`.
- Authenticates admin and transport-owner users with password credentials.
- Issues JWTs containing `sub`, `role`, `gender`, and `phone_number`.
- Publishes `otp.requested` events for passenger authentication.
- Calls Notification over Basic Auth to verify OTP.

Transport Service:
- Owns transport companies, buses, seats, trips, and seat holds.
- Enforces transport-owner ownership for resource management.
- Supports reservable/non-reservable seats and gender restrictions: `none`, `male`, `female`.
- Exposes internal Basic-auth endpoints for Search and Reservation.

Search Service:
- Publicly exposes trip search by origin, destination, and departure date.
- Calls Transport over REST + Basic Auth.
- Logs search queries to its own PostgreSQL database.

Reservation Service:
- Owns reservation records and lifecycle status.
- Creates `pending` reservations after Transport successfully holds a seat.
- Confirms, cancels, and expires reservations.
- Publishes reservation lifecycle events to RabbitMQ.

Notification Service:
- Consumes durable `otp.requested` events.
- Generates OTP codes with expiry.
- Verifies OTP through an internal Basic-auth endpoint.
- Publishes `otp.verified` and `otp.rejected` events.

## Data Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth
    participant N as Notification
    participant R as RabbitMQ

    C->>A: POST /auth/otp/request
    A->>R: publish otp.requested
    R->>N: deliver otp.requested
    N->>N: store OTP with expiry
    C->>A: POST /auth/otp/verify
    A->>N: POST /internal/otp/verify (Basic Auth)
    N->>R: publish otp.verified
    A->>C: passenger JWT
```

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Search
    participant T as Transport

    C->>S: GET /search/trips
    S->>T: GET /transport/internal/trips (Basic Auth)
    T->>T: calculate remaining capacity from seats and active holds
    T->>S: trips with remaining capacity
    S->>S: log search query
    S->>C: search results
```

```mermaid
sequenceDiagram
    participant C as Client
    participant Res as Reservation
    participant T as Transport
    participant R as RabbitMQ

    C->>Res: POST /reservations with passenger JWT
    Res->>T: POST /transport/internal/seat-holds (Basic Auth)
    T->>T: validate seat, trip, gender restriction, availability
    T->>Res: seat hold created
    Res->>Res: create pending reservation
    Res->>R: publish reservation.created
    C->>Res: POST /reservations/{id}/confirm
    Res->>T: PATCH hold status confirmed
    Res->>R: publish reservation.confirmed
```

## Event Flow

All services publish to a durable RabbitMQ topic exchange named `bus_reservation.events`.

Important events:
- `otp.requested`
- `otp.verified`
- `otp.rejected`
- `trip.created`
- `seat.updated`
- `seat.held`
- `reservation.created`
- `reservation.confirmed`
- `reservation.cancelled`
- `reservation.expired`

Notification consumes `otp.requested` from a durable queue. Failed handling is retried by republishing the same event with an `x-retry-count` header up to three attempts, then rejected without requeue.

## Security

User authentication:
- JWT bearer tokens are used for user-facing protected endpoints.
- JWTs include role and gender claims so Transport and Reservation can enforce RBAC and seat restrictions without sharing the Auth database.

Service-to-service authentication:
- Internal REST endpoints use HTTP Basic credentials.
- Credentials are passed through environment variables and are distinct per caller/target pair.
- Auth also exposes `/auth/internal/basic/validate` as a central validation endpoint.

## Databases and Migrations

Each service owns a separate PostgreSQL database:
- `auth_db`
- `transport_db`
- `search_db`
- `reservation_db`
- `notification_db`

Each service has its own Alembic migration directory and Docker startup runs `alembic upgrade head` before starting FastAPI.
