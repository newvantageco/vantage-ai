from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.observability.telemetry import init_telemetry
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiting import rate_limit_middleware

# Initialize telemetry early
init_telemetry()

# Import core routers
from app.api.v1.health import router as health_router
from app.api.v1.auth_simple import router as auth_simple_router
from app.api.v1.ai_standalone import router as ai_standalone_router
from app.api.v1.publishing_simple import router as publishing_simple_router
from app.api.v1.scheduling_simple import router as scheduling_simple_router
from app.api.v1.analytics_simple import router as analytics_simple_router
from app.api.v1.billing_simple import router as billing_simple_router
from app.api.v1.media_simple import router as media_simple_router
from app.api.v1.content_library_simple import router as content_library_simple_router
from app.api.v1.oauth_simple import router as oauth_simple_router
from app.api.v1.production_simple import router as production_simple_router

# Import real OAuth routers
from app.api.v1.oauth_meta import router as oauth_meta_router
from app.api.v1.oauth_linkedin import router as oauth_linkedin_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.publishing import router as publishing_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.events import router as events_router
from app.api.v1.brave_search import router as brave_search_router

# Database setup
from app.db.base import Base
from app.db.session import engine

def create_app() -> FastAPI:
	# Set up logging first
	setup_logging()
	
	app = FastAPI(title="Vantage AI Marketing SaaS", version="0.1.0")
	settings = get_settings()

	# Security Headers Middleware (must be first)
	app.add_middleware(SecurityHeadersMiddleware, environment=settings.environment)
	
	# Rate Limiting Middleware
	app.middleware("http")(rate_limit_middleware)
	
	# CORS configuration
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.cors_origins.split(",") if settings.cors_origins else ["http://localhost:3000"],
		allow_credentials=True,
		allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
		allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
	)

	# Include core routers
	app.include_router(health_router, prefix="/api/v1", tags=["health"])
	app.include_router(auth_simple_router, prefix="/api/v1", tags=["auth"])
	app.include_router(ai_standalone_router, prefix="/api/v1", tags=["ai"])
	app.include_router(publishing_simple_router, prefix="/api/v1", tags=["publishing"])
	app.include_router(scheduling_simple_router, prefix="/api/v1", tags=["scheduling"])
	app.include_router(analytics_simple_router, prefix="/api/v1", tags=["analytics"])
	app.include_router(billing_simple_router, prefix="/api/v1", tags=["billing"])
	app.include_router(media_simple_router, prefix="/api/v1", tags=["media"])
	app.include_router(content_library_simple_router, prefix="/api/v1", tags=["content"])
	app.include_router(oauth_simple_router, prefix="/api/v1", tags=["oauth"])
	app.include_router(production_simple_router, prefix="/api/v1", tags=["production"])
	
	# Include real OAuth and integration routers
	app.include_router(oauth_meta_router, prefix="/api/v1", tags=["oauth-meta"])
	app.include_router(oauth_linkedin_router, prefix="/api/v1", tags=["oauth-linkedin"])
	app.include_router(integrations_router, prefix="/api/v1", tags=["integrations"])
	app.include_router(publishing_router, prefix="/api/v1", tags=["publishing-real"])
	app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
	app.include_router(events_router, prefix="/api/v1", tags=["events"])
	app.include_router(brave_search_router, prefix="/api/v1", tags=["brave-search"])

	return app

# Create the FastAPI application
app = create_app()

# Auto-create tables in dev (with error handling for existing objects)
try:
	Base.metadata.create_all(bind=engine)
	print("Database tables created successfully")
except Exception as e:
	# Log the error but don't fail the app startup
	print(f"Warning: Error creating database tables: {e}")

@app.get("/")
def read_root():
	return {
		"message": "🚀 VANTAGE AI API is running!",
		"status": "healthy",
		"version": "0.1.0",
		"docs": "/docs"
	}

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)