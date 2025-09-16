from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

from app.api.v1.health import router as health_router
from app.api.v1.orgs import router as orgs_router
from app.api.v1.channels import router as channels_router
from app.api.v1.oauth_meta import router as oauth_meta_router
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
from app.api.v1.stripe_webhooks import router as stripe_webhooks_router
from app.api.v1.limits import router as limits_router
from app.api.v1.api_keys import router as api_keys_router
from app.api.v1.ugc import router as ugc_router
from app.api.v1.exports import router as exports_router
from app.api.v1.analytics_explorer import router as analytics_explorer_router
from app.api.v1.conversions import router as conversions_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.collaboration import router as collaboration_router
from app.api.v1.translations import router as translations_router
from app.api.v1.rate_limiting import router as rate_limiting_router
from app.api.v1.ads_management import router as ads_management_router


def create_app() -> FastAPI:
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

	app.include_router(health_router, prefix="/api/v1")
	app.include_router(orgs_router, prefix="/api/v1")
	app.include_router(channels_router, prefix="/api/v1")
	app.include_router(oauth_meta_router, prefix="/api/v1")
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
	app.include_router(limits_router, prefix="/api/v1")
	app.include_router(api_keys_router, prefix="/api/v1")
	app.include_router(ugc_router, prefix="/api/v1")
	app.include_router(exports_router, prefix="/api/v1")
	app.include_router(analytics_explorer_router, prefix="/api/v1")
	app.include_router(conversions_router, prefix="/api/v1")
	app.include_router(webhooks_router, prefix="/api/v1")
	app.include_router(collaboration_router, prefix="/api/v1")
	app.include_router(translations_router, prefix="/api/v1")
	app.include_router(rate_limiting_router, prefix="/api/v1")
	app.include_router(ads_management_router, prefix="/api/v1")
	
	# Webhook routes (no prefix)
	app.include_router(meta_webhook_router)
	app.include_router(linkedin_webhook_router)
	app.include_router(whatsapp_webhook_router)
	app.include_router(stripe_webhooks_router)

	# Auto-create tables in dev
	Base.metadata.create_all(bind=engine)
	return app


app = create_app()


