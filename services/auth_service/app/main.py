from fastapi import FastAPI
from app.api.routers import router

app = FastAPI(title="Auth Service")

app.include_router(router)