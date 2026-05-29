import importlib
import sys
import unittest
from pathlib import Path
from uuid import UUID, uuid4


ROOT = Path(__file__).resolve().parents[1]


def import_from_service(service_name: str, module_name: str):
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]

    service_path = str(ROOT / "services" / service_name)
    sys.path.insert(0, service_path)

    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(service_path)


class AuthTokenTests(unittest.TestCase):
    def test_access_token_contains_role_gender_and_phone(self):
        security = import_from_service(
            "auth_service",
            "app.infrastructure.security",
        )

        token = security.create_access_token(
            user_id=str(uuid4()),
            role="transport_owner",
            gender="male",
            phone_number="+989120000000",
        )
        payload = security.decode_access_token(token)

        self.assertEqual(payload["role"], "transport_owner")
        self.assertEqual(payload["gender"], "male")
        self.assertEqual(payload["phone_number"], "+989120000000")


class TransportPolicyTests(unittest.TestCase):
    def test_transport_owner_policy_rejects_passenger(self):
        schemas = import_from_service("transport_service", "app.domain.schemas")
        services = import_from_service("transport_service", "app.domain.services")

        user = schemas.CurrentUser(
            user_id=uuid4(),
            role="passenger",
            gender="male",
        )

        with self.assertRaises(Exception):
            services.TransportService._require_transport_owner(user)

    def test_public_seat_gender_type_exists(self):
        enums = import_from_service("transport_service", "app.domain.enums")

        self.assertEqual(enums.SeatGenderType.NONE.value, "none")


class FakeReservationRepository:
    def __init__(self, reservation_status):
        self.reservations = {}
        self.reservation_status = reservation_status

    async def create_reservation(
        self,
        reservation_id,
        passenger_id,
        passenger_gender,
        trip_id,
        seat_id,
    ):
        reservation = type(
            "Reservation",
            (),
            {
                "id": reservation_id,
                "passenger_id": passenger_id,
                "passenger_gender": passenger_gender,
                "trip_id": trip_id,
                "seat_id": seat_id,
                "status": self.reservation_status.PENDING,
            },
        )()
        self.reservations[reservation_id] = reservation
        return reservation

    async def get_by_id(self, reservation_id):
        return self.reservations.get(reservation_id)

    async def update_status(self, reservation, status):
        reservation.status = status
        return reservation


class FakeEventBus:
    def __init__(self):
        self.events = []

    async def publish(self, routing_key, payload):
        self.events.append((routing_key, payload))


class ReservationLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_and_confirm_reservation(self):
        schemas = import_from_service("reservation_service", "app.domain.schemas")
        services = import_from_service("reservation_service", "app.domain.services")

        repository = FakeReservationRepository(services.ReservationStatus)
        event_bus = FakeEventBus()
        service = services.ReservationService(repository, event_bus)
        hold_calls = []

        async def fake_update_transport_hold(**kwargs):
            hold_calls.append(kwargs)

        service._update_transport_hold = fake_update_transport_hold

        current_user = schemas.CurrentUser(
            user_id=uuid4(),
            role="passenger",
            gender="female",
        )
        reservation = await service.create_reservation(
            current_user,
            schemas.ReservationCreateRequest(
                trip_id=uuid4(),
                seat_id=uuid4(),
            ),
        )
        confirmed = await service.confirm_reservation(
            reservation.id,
            current_user,
        )

        self.assertEqual(confirmed.status, services.ReservationStatus.CONFIRMED)
        self.assertEqual(hold_calls[0]["method"], "post")
        self.assertEqual(hold_calls[1]["method"], "patch")
        self.assertEqual(event_bus.events[0][0], "reservation.created")
        self.assertEqual(event_bus.events[1][0], "reservation.confirmed")


class NotificationSecurityTests(unittest.TestCase):
    def test_service_credentials_validate_auth_service(self):
        security = import_from_service(
            "notification_service",
            "app.infrastructure.security",
        )

        self.assertTrue(
            security.validate_service_credentials("auth_service", "auth-secret")
        )
        self.assertFalse(
            security.validate_service_credentials("auth_service", "bad-secret")
        )


if __name__ == "__main__":
    unittest.main()
