
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from contextlib import asynccontextmanager
from app.core.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app:FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()

app = FastAPI(
        title = settings.PROJECT_NAME,
        version = settings.VERSION,
        openapi_url = f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health",summary="Health Check")
async def health_check():
    return{
        "status":"healthy",
        "project":settings.PROJECT_NAME,
        "version":settings.VERSION
    }