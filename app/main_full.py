from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.observability.telemetry import init_telemetry

# Initialize telemetry early
init_telemetry()

from app.api.v1.health import router as health_router
from app.api.v1.orgs import router as orgs_router
from app.api.v1.channels import router as channels_router
from app.api.v1.oauth_meta import router as oauth_meta_router
from app.api.v1.oauth_linkedin import router as oauth_linkedin_router
from app.api.v1.oauth_test import router as oauth_test_router
from app.api.v1.ai import router as ai_router
from app.api.v1.plan import router as plan_router
from app.db.base import Base
from app.db.session import engine
from app.api.v1.content import router as content_router
from app.api.v1.content_plan import router as content_plan_router
from app.api.v1.schedule import router as schedule_router
from app.api.v1.reports import router as reports_router
from app.api.v1.billing import router as billing_router
from app.api.v1.oauth_google import router as oauth_google_router
from app.routes.templates import router as templates_router
from app.routes.inbox import router as inbox_router
from app.routes.insights import router as insights_router
from app.routes.privacy import router as privacy_router
from app.routes.webhooks.meta import router as meta_webhook_router
from app.routes.webhooks.linkedin import router as linkedin_webhook_router
from app.routes.webhooks.whatsapp import router as whatsapp_webhook_router
from app.routes.rules import router as rules_router
from app.api.v1.ai_usage import router as ai_usage_router
from app.api.v1.billing_enhanced import router as billing_enhanced_router
from app.api.v1.billing_dashboard import router as billing_dashboard_router
from app.api.v1.billing_demo import router as billing_demo_router
from app.api.v1.stripe_webhooks import router as stripe_webhooks_router
from app.api.v1.limits import router as limits_router
from app.api.v1.api_keys import router as api_keys_router
from app.api.v1.ugc import router as ugc_router
from app.api.v1.exports import router as exports_router
from app.api.v1.analytics_explorer import router as analytics_explorer_router
from app.api.v1.content_creation import router as content_creation_router
from app.api.v1.dashboard_real import router as dashboard_real_router
from app.api.v1.conversions import router as conversions_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.collaboration import router as collaboration_router
from app.api.v1.translations import router as translations_router
from app.api.v1.rate_limiting import router as rate_limiting_router
from app.api.v1.ads_management import router as ads_management_router
from app.api.v1.test_ai import router as test_ai_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.cms import router as cms_router
from app.api.v1.publishing import router as publishing_router
from app.api.v1.whatsapp import router as whatsapp_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.platform_webhooks import router as platform_webhooks_router
from app.api.v1.ai_content import router as ai_content_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.analytics_enhanced import router as analytics_enhanced_router
from app.api.v1.privacy_enhanced import router as privacy_enhanced_router
from app.api.v1.auth import router as auth_router
# from app.api.v1.auth_dev import router as auth_dev_router  # Removed for production
from app.api.v1.auth_simple import router as auth_simple_router
from app.api.v1.media import router as media_router
from app.api.v1.bulk_operations import router as bulk_operations_router
from app.api.v1.content_library import router as content_library_router
from app.api.v1.custom_reports import router as custom_reports_router
from app.api.v1.competitive_analysis import router as competitive_analysis_router
from app.api.v1.performance_tracking import router as performance_tracking_router
from app.api.v1.ai_features import router as ai_features_router
from app.api.v1.automation import router as automation_router


def create_app() -> FastAPI:
	# Set up logging first
	setup_logging()
	
	app = FastAPI(title="Vantage AI Marketing SaaS", version="0.1.0")
	settings = get_settings()

	# Parse CORS configuration from environment
	cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
	cors_methods = [method.strip() for method in settings.cors_methods.split(",") if method.strip()]
	cors_headers = [header.strip() for header in settings.cors_headers.split(",") if header.strip()]

	app.add_middleware(
		CORSMiddleware,
		allow_origins=cors_origins,
		allow_credentials=True,
		allow_methods=cors_methods,
		allow_headers=cors_headers,
	)
	
	# Add rate limiting middleware
	from app.middleware.rate_limiting import rate_limit_middleware
	app.middleware("http")(rate_limit_middleware)

	app.include_router(health_router, prefix="/api/v1")
	app.include_router(orgs_router, prefix="/api/v1")
	app.include_router(channels_router, prefix="/api/v1")
	app.include_router(oauth_meta_router, prefix="/api/v1")
	app.include_router(oauth_linkedin_router, prefix="/api/v1")
	app.include_router(oauth_test_router, prefix="/api/v1")
	app.include_router(ai_router, prefix="/api/v1")
	app.include_router(plan_router, prefix="/api/v1")
	app.include_router(content_router, prefix="/api/v1")
	app.include_router(content_plan_router, prefix="/api/v1")
	app.include_router(schedule_router, prefix="/api/v1")
	app.include_router(reports_router, prefix="/api/v1")
	app.include_router(billing_router, prefix="/api/v1")
	app.include_router(oauth_google_router, prefix="/api/v1")
	app.include_router(templates_router, prefix="/api/v1")
	app.include_router(inbox_router, prefix="/api/v1")
	app.include_router(insights_router, prefix="/api/v1")
	app.include_router(privacy_router, prefix="/api/v1")
	app.include_router(rules_router, prefix="/api/v1")
	app.include_router(ai_usage_router, prefix="/api/v1/ai")
	app.include_router(billing_enhanced_router, prefix="/api/v1")
	app.include_router(billing_dashboard_router, prefix="/api/v1")
	app.include_router(billing_demo_router, prefix="/api/v1")
	app.include_router(limits_router, prefix="/api/v1")
	app.include_router(api_keys_router, prefix="/api/v1")
	app.include_router(ugc_router, prefix="/api/v1")
	app.include_router(exports_router, prefix="/api/v1")
	app.include_router(analytics_explorer_router, prefix="/api/v1")
	app.include_router(content_creation_router, prefix="/api/v1/content", tags=["content-creation"])
	app.include_router(dashboard_real_router, prefix="/api/v1/dashboard", tags=["dashboard"])
	app.include_router(conversions_router, prefix="/api/v1")
	app.include_router(webhooks_router, prefix="/api/v1")
	app.include_router(collaboration_router, prefix="/api/v1")
	app.include_router(translations_router, prefix="/api/v1")
	app.include_router(rate_limiting_router, prefix="/api/v1")
	app.include_router(ads_management_router, prefix="/api/v1")
	app.include_router(test_ai_router, prefix="/api/v1", tags=["test-ai"])
	app.include_router(dashboard_router, prefix="/api/v1")
	app.include_router(cms_router, prefix="/api/v1")
	app.include_router(publishing_router, prefix="/api/v1")
	app.include_router(whatsapp_router, prefix="/api/v1")
	app.include_router(integrations_router, prefix="/api/v1")
	app.include_router(platform_webhooks_router, prefix="/api/v1")
	app.include_router(ai_content_router, prefix="/api/v1")
	app.include_router(analytics_router, prefix="/api/v1")
	app.include_router(analytics_enhanced_router, prefix="/api/v1")
	app.include_router(privacy_enhanced_router, prefix="/api/v1")
	app.include_router(auth_router, prefix="/api/v1")
	# app.include_router(auth_dev_router, prefix="/api/v1")  # Removed for production
	app.include_router(auth_simple_router, prefix="/api/v1")
	app.include_router(media_router, prefix="/api/v1/media", tags=["media"])
	app.include_router(bulk_operations_router, prefix="/api/v1/bulk", tags=["bulk-operations"])
	app.include_router(content_library_router, prefix="/api/v1/content-library", tags=["content-library"])
	app.include_router(custom_reports_router, prefix="/api/v1", tags=["custom-reports"])
	app.include_router(competitive_analysis_router, prefix="/api/v1", tags=["competitive-analysis"])
	app.include_router(performance_tracking_router, prefix="/api/v1", tags=["performance-tracking"])
	app.include_router(ai_features_router, prefix="/api/v1/ai", tags=["ai-features"])
	app.include_router(automation_router, prefix="/api/v1/automation", tags=["automation"])
	
	# Webhook routes (no prefix)
	app.include_router(meta_webhook_router)
	app.include_router(linkedin_webhook_router)
	app.include_router(whatsapp_webhook_router)
	app.include_router(stripe_webhooks_router)

	# Optionally expose Prometheus metrics
	if os.getenv("ENABLE_PROMETHEUS_METRICS") == "1":
		try:
			from prometheus_client import make_asgi_app
			metrics_app = make_asgi_app()
			app.mount("/metrics", metrics_app)
			print("Prometheus metrics endpoint mounted at /metrics")
		except ImportError:
			print("Warning: prometheus_client not available, metrics endpoint not mounted")

	# Auto-create tables in dev (with error handling for existing objects)
	try:
		Base.metadata.create_all(bind=engine)
		print("Database tables created successfully")
	except Exception as e:
		# Log the error but don't fail the app startup
		print(f"Warning: Some database objects already exist: {e}")
		# Try to continue anyway - the app should still work
		pass
	return app


app = create_app()


