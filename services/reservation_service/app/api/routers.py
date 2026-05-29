from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_reservation_service
from app.domain.schemas import (
    CurrentUser,
    ReservationCreateRequest,
    ReservationResponse,
)
from app.domain.services import ReservationService


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
)


@router.post("", response_model=ReservationResponse, status_code=201)
async def create_reservation(
    data: ReservationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.create_reservation(current_user, data)


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.get_reservation(reservation_id, current_user)


@router.post("/{reservation_id}/confirm", response_model=ReservationResponse)
async def confirm_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.confirm_reservation(reservation_id, current_user)


@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
async def cancel_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.cancel_reservation(reservation_id, current_user)


@router.post("/{reservation_id}/expire", response_model=ReservationResponse)
async def expire_reservation(
    reservation_id: UUID,
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.expire_reservation(reservation_id)
