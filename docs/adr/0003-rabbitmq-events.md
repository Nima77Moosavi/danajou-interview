# ADR 0003: RabbitMQ Eventing

## Status

Accepted

## Context

The assignment requires durable asynchronous events and retry handling.

## Decision

Use RabbitMQ with a durable topic exchange named `bus_reservation.events`. Published messages use persistent delivery. Notification consumes `otp.requested` from a durable queue and retries failed messages by republishing with an `x-retry-count` header up to three attempts.

## Consequences

The implementation demonstrates durable eventing and retry behavior without introducing a separate worker framework. More consumers can bind to the same topic exchange later.
