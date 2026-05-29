import logging

from fastapi import FastAPI

from app.api.routers import router
from app.infrastructure.messaging import start_otp_consumer


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Notification Service")
app.include_router(router)


@app.on_event("startup")
async def startup() -> None:
    app.state.rabbitmq_connection = await start_otp_consumer()


@app.on_event("shutdown")
async def shutdown() -> None:
    connection = getattr(app.state, "rabbitmq_connection", None)

    if connection:
        await connection.close()


@app.get("/health")
async def health():
    return {"status": "ok"}
