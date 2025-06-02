from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.users.routes import router as users_router

api_router = APIRouter()

# Include auth and users routers under v1
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"]) 