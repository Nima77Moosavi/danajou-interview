# ADR 0001: Service Boundaries

## Status

Accepted

## Context

The assignment requires independent services, independent databases, REST communication, and asynchronous events for a bus ticket reservation system.

## Decision

Split the system into five FastAPI services:

- Auth owns users, OTP initiation, and JWT issuing.
- Transport owns bus inventory and seat availability holds.
- Search owns public search and search query logs.
- Reservation owns reservation state transitions.
- Notification owns OTP generation, expiry, and verification.

Each service has its own PostgreSQL database and Alembic migrations.

## Consequences

This keeps database ownership clear and avoids cross-service table access. The tradeoff is that Reservation must coordinate with Transport through an internal REST seat-hold endpoint to prevent double booking.
