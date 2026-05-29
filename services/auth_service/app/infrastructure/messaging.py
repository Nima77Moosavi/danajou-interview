import json
import logging
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message

from app.infrastructure.database import settings


logger = logging.getLogger(__name__)


class RabbitMQEventBus:
    exchange_name = "bus_reservation.events"

    async def publish(
        self,
        routing_key: str,
        payload: dict[str, Any],
    ) -> None:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

        try:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,
            )

            await exchange.publish(
                Message(
                    json.dumps(payload, default=str).encode("utf-8"),
                    delivery_mode=DeliveryMode.PERSISTENT,
                    content_type="application/json",
                ),
                routing_key=routing_key,
            )
        finally:
            await connection.close()
