# Bus Reservation Microservices

Interview project for a Dockerized bus ticket reservation platform using FastAPI, PostgreSQL, RabbitMQ, Alembic, JWT, and service-to-service Basic Authentication.

## Services

| Service | Port | Responsibility |
| --- | ---: | --- |
| Auth | 8000 | Admin/transport-owner password auth, passenger OTP auth, JWT issuing, service Basic credential validation endpoint |
| Transport | 8001 | Companies, buses, seats, trip inventory, seat restrictions, internal seat holds |
| Search | 8002 | Public trip search with remaining capacity |
| Reservation | 8003 | Reservation lifecycle: pending, confirmed, cancelled, expired |
| Notification | 8004 | OTP generation, expiry, verification, OTP event consumer |

Each service has its own PostgreSQL database container. RabbitMQ is used for durable events such as `otp.requested`, `otp.verified`, `reservation.created`, `reservation.confirmed`, and `reservation.expired`.

## Run Locally

```bash
docker compose up --build
```

Docs are available at:

- Auth: http://localhost:8000/docs
- Transport: http://localhost:8001/docs
- Search: http://localhost:8002/docs
- Reservation: http://localhost:8003/docs
- Notification: http://localhost:8004/docs
- RabbitMQ management: http://localhost:15672

Migrations run automatically when each service container starts.

## Basic Flow

1. Register a transport owner with `POST /auth/register`.
2. Login with `POST /auth/login` and use the JWT to create a company, bus, seats, and trips in Transport.
3. Search trips publicly through `GET /search/trips`.
4. Request passenger OTP with `POST /auth/otp/request`.
5. For local testing, read the generated OTP from `GET /notifications/dev/otp/{phone_number}`.
6. Verify OTP with `POST /auth/otp/verify` to receive a passenger JWT.
7. Create a reservation with `POST /reservations`, then confirm or cancel it.

## Tests

```bash
python -m pytest -q
python -m coverage run -m unittest discover -s tests
python -m coverage report
```

Current focused coverage is around JWT claims, service credential validation, transport role policy, seat restriction support, and reservation lifecycle behavior.

## Documentation

- Technical design: [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)
- ADRs: [docs/adr](docs/adr)
