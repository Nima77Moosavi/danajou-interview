import logging
from uuid import UUID, uuid4

import httpx
from fastapi import HTTPException, status

from app.domain.enums import ReservationStatus
from app.domain.interfaces import IReservationRepository
from app.domain.schemas import CurrentUser, ReservationCreateRequest
from app.infrastructure.database import settings
from app.infrastructure.messaging import RabbitMQEventBus


logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(
        self,
        repository: IReservationRepository,
        event_bus: RabbitMQEventBus | None = None,
    ):
        self.repository = repository
        self.event_bus = event_bus or RabbitMQEventBus()

    async def create_reservation(
        self,
        current_user: CurrentUser,
        data: ReservationCreateRequest,
    ):
        if current_user.role != "passenger":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only passengers can create reservations",
            )

        reservation_id = uuid4()
        await self._update_transport_hold(
            method="post",
            path="/transport/internal/seat-holds",
            json={
                "reservation_id": str(reservation_id),
                "passenger_gender": current_user.gender,
                "trip_id": str(data.trip_id),
                "seat_id": str(data.seat_id),
            },
            expected_status=status.HTTP_201_CREATED,
        )

        reservation = await self.repository.create_reservation(
            reservation_id=reservation_id,
            passenger_id=current_user.user_id,
            passenger_gender=current_user.gender,
            trip_id=data.trip_id,
            seat_id=data.seat_id,
        )

        await self.event_bus.publish(
            "reservation.created",
            {
                "reservation_id": str(reservation.id),
                "passenger_id": str(reservation.passenger_id),
                "trip_id": str(reservation.trip_id),
                "seat_id": str(reservation.seat_id),
                "status": reservation.status.value,
            },
        )

        logger.info("reservation created", extra={"reservation_id": reservation.id})

        return reservation

    async def confirm_reservation(
        self,
        reservation_id: UUID,
        current_user: CurrentUser,
    ):
        reservation = await self._get_owned_reservation(
            reservation_id,
            current_user,
        )

        if reservation.status != ReservationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending reservations can be confirmed",
            )

        reservation = await self.repository.update_status(
            reservation,
            ReservationStatus.CONFIRMED,
        )
        await self._set_transport_hold_status(
            reservation.id,
            "confirmed",
        )

        await self.event_bus.publish(
            "reservation.confirmed",
            {"reservation_id": str(reservation.id)},
        )

        logger.info("reservation confirmed", extra={"reservation_id": reservation.id})

        return reservation

    async def cancel_reservation(
        self,
        reservation_id: UUID,
        current_user: CurrentUser,
    ):
        reservation = await self._get_owned_reservation(
            reservation_id,
            current_user,
        )

        if reservation.status in {
            ReservationStatus.CANCELLED,
            ReservationStatus.EXPIRED,
        }:
            return reservation

        reservation = await self.repository.update_status(
            reservation,
            ReservationStatus.CANCELLED,
        )
        await self._set_transport_hold_status(
            reservation.id,
            "released",
        )

        await self.event_bus.publish(
            "reservation.cancelled",
            {"reservation_id": str(reservation.id)},
        )

        logger.info("reservation cancelled", extra={"reservation_id": reservation.id})

        return reservation

    async def expire_reservation(
        self,
        reservation_id: UUID,
    ):
        reservation = await self.repository.get_by_id(reservation_id)

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )

        if reservation.status != ReservationStatus.PENDING:
            return reservation

        reservation = await self.repository.update_status(
            reservation,
            ReservationStatus.EXPIRED,
        )
        await self._set_transport_hold_status(
            reservation.id,
            "released",
        )

        await self.event_bus.publish(
            "reservation.expired",
            {"reservation_id": str(reservation.id)},
        )

        logger.info("reservation expired", extra={"reservation_id": reservation.id})

        return reservation

    async def get_reservation(
        self,
        reservation_id: UUID,
        current_user: CurrentUser,
    ):
        return await self._get_owned_reservation(reservation_id, current_user)

    async def _get_owned_reservation(
        self,
        reservation_id: UUID,
        current_user: CurrentUser,
    ):
        reservation = await self.repository.get_by_id(reservation_id)

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )

        if (
            current_user.role != "admin"
            and reservation.passenger_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this reservation",
            )

        return reservation

    async def _set_transport_hold_status(
        self,
        reservation_id: UUID,
        hold_status: str,
    ) -> None:
        await self._update_transport_hold(
            method="patch",
            path=f"/transport/internal/seat-holds/{reservation_id}",
            json={"status": hold_status},
            expected_status=status.HTTP_200_OK,
        )

    async def _update_transport_hold(
        self,
        method: str,
        path: str,
        json: dict,
        expected_status: int,
    ) -> None:
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.request(
                    method,
                    f"{settings.TRANSPORT_SERVICE_URL}{path}",
                    auth=(
                        settings.TRANSPORT_SERVICE_USERNAME,
                        settings.TRANSPORT_SERVICE_PASSWORD,
                    ),
                    json=json,
                )
            except httpx.HTTPError as exc:
                logger.exception("transport service request failed")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Transport service is unavailable",
                ) from exc

        if response.status_code != expected_status:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except ValueError:
                pass

            raise HTTPException(
                status_code=response.status_code,
                detail=detail,
            )
