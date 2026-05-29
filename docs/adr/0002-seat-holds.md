# ADR 0002: Seat Holds in Transport

## Status

Accepted

## Context

Reservation owns business reservation records, but Transport is the source of truth for seats, restrictions, and capacity. The system needs a way to prevent double booking while keeping service databases separate.

## Decision

Transport owns `seat_holds`, keyed by Reservation's reservation ID. Reservation asks Transport to hold a seat before it persists a pending reservation. Confirmed and pending holds reduce remaining capacity; cancelled and expired reservations release the hold.

## Consequences

Transport can calculate remaining capacity without reading Reservation's database. This introduces a small distributed workflow; failures after a hold but before reservation persistence would need a cleanup job in a production system.
