import logging

from fastapi import FastAPI

from app.api.routers import router


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Search Service")
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
