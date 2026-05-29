import json
import logging
import secrets
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, IncomingMessage, Message

from app.infrastructure.database import AsyncSessionLocal, settings
from app.infrastructure.repositories import OTPRepository


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


async def start_otp_consumer():
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        RabbitMQEventBus.exchange_name,
        ExchangeType.TOPIC,
        durable=True,
    )
    queue = await channel.declare_queue(
        "notification.otp.requests",
        durable=True,
    )
    await queue.bind(exchange, routing_key="otp.requested")

    async def handle(message: IncomingMessage) -> None:
        try:
            payload = json.loads(message.body.decode("utf-8"))
            phone_number = payload["phone_number"]
            code = f"{secrets.randbelow(1_000_000):06d}"

            async with AsyncSessionLocal() as session:
                repository = OTPRepository(session)
                await repository.create_code(phone_number, code)

            logger.info(
                "otp generated",
                extra={"phone_number": phone_number, "otp_code": code},
            )

            await message.ack()
        except Exception:
            retry_count = int((message.headers or {}).get("x-retry-count", 0))

            if retry_count < 3:
                await exchange.publish(
                    Message(
                        message.body,
                        headers={"x-retry-count": retry_count + 1},
                        delivery_mode=DeliveryMode.PERSISTENT,
                        content_type=message.content_type,
                    ),
                    routing_key="otp.requested",
                )
                await message.ack()
            else:
                logger.exception("otp requested event failed permanently")
                await message.reject(requeue=False)

    await queue.consume(handle)

    return connection
