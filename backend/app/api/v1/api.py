from fastapi import APIRouter
from app.api.v1.endpoints import analytics, applications, auth

api_router = APIRouter()

# 1. Authentication endpoints under /auth
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

# 2. Applications endpoints under /applications
api_router.include_router(
    applications.router,
    prefix="/applications",
    tags=["applications"],
)

# 3. Analytics endpoints under /analytics
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
)




