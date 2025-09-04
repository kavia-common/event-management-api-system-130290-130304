from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.database import Base, engine
from .routers import events as events_router
from .routers import attendees as attendees_router


settings = get_settings()

openapi_tags = [
    {"name": "Health", "description": "Health check endpoint"},
    {"name": "Events", "description": "CRUD operations for events"},
    {"name": "Attendees", "description": "Manage event attendees"},
]

# Ensure public API description reflects no authentication requirement
public_description = (
    "Public API system for managing events and attendees. "
    "All endpoints are open; no authentication required."
)

app = FastAPI(
    title=settings.APP_NAME,
    description=public_description or settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=openapi_tags,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Create tables if not exists
Base.metadata.create_all(bind=engine)


# Root and health
@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


# API router with prefix
api_router = APIRouter(prefix=settings.API_PREFIX)
api_router.include_router(events_router.router)
api_router.include_router(attendees_router.router)
app.include_router(api_router)


# WebSocket usage help (no actual WS endpoints in this service)
@app.get(
    "/ws-docs",
    tags=["Health"],
    summary="WebSocket usage",
    description="This service currently does not provide WebSocket endpoints.",
)
def websocket_docs():
    """Static note: no websocket endpoints in this service."""
    return JSONResponse({"websocket": "No WebSocket endpoints available in this API."})
