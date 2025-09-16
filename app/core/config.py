from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	app_name: str = "Vantage AI Marketing SaaS"
	environment: str = "local"
	api_base: str = "/api/v1"

	# Database
	database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/vantage_ai"

	# Clerk
	clerk_jwks_url: str | None = None
	clerk_issuer: str | None = None

	# Meta OAuth & Platform
	meta_app_id: str | None = None
	meta_app_secret: str | None = None
	meta_redirect_uri: str | None = None
	meta_graph_version: str = "20.0"
	meta_page_id: str | None = None
	meta_ig_business_id: str | None = None

	# LinkedIn OAuth & Platform
	linkedin_client_id: str | None = None
	linkedin_client_secret: str | None = None
	linkedin_redirect_url: str | None = None
	linkedin_page_urn: str | None = None

	# Google OAuth & Platform
	google_client_id: str | None = None
	google_client_secret: str | None = None
	google_redirect_url: str | None = None
	google_business_location_id: str | None = None
	gbp_enabled: bool = False

	# WhatsApp Cloud API
	whatsapp_verify_token: str | None = None
	whatsapp_phone_id: str | None = None
	whatsapp_access_token: str | None = None

	# General
	dry_run: bool = False
	secret_key: str = "your-secret-key-change-in-production"

	model_router_primary: str | None = None
	model_router_fallback: str | None = None

	# Insights & Metrics
	feature_fake_insights: bool = True  # Set to False to use real platform APIs
	insights_poll_interval_hours: int = 6  # How often to poll for new metrics
	e2e_mocks: bool = False  # Enable E2E mock mode for testing
	meta_insights_fields_fb: str = "impressions,post_impressions_unique,likes,comments,shares,clicks"
	ig_insights_metrics: str = "impressions,reach,likes,comments,saves,video_views"
	linkedin_stats_fields: str = "impressionCount,likeCount,commentCount,shareCount"

	# Automation & Rules
	automations_enabled: bool = False  # Feature flag for rules automation
	rules_worker_interval_minutes: int = 5  # How often to check for rule triggers
	rules_cooldown_minutes: int = 60  # Minimum time between rule executions
	max_budget_pct_change: int = 15  # Maximum budget change percentage per rule run

	# AI Cost Optimization
	redis_url: str = "redis://localhost:6379"
	ai_cache_ttl_secs: int = 86400  # 24 hours
	dev_tools_enabled: bool = False  # Feature flag for dev tools panel
	ai_budget_soft_limit_multiplier: float = 2.0  # Block when 2x over limit

	# Stripe Billing
	stripe_secret_key: str | None = None
	stripe_publishable_key: str | None = None
	stripe_webhook_secret: str | None = None
	stripe_price_id_starter: str | None = None
	stripe_price_id_growth: str | None = None
	stripe_price_id_pro: str | None = None

	# PWA & Push Notifications
	vapid_public_key: str | None = None
	vapid_private_key: str | None = None
	vapid_email: str | None = None

	# Rate Limiting
	rate_limit_enabled: bool = True
	rate_limit_requests_per_minute: int = 60
	rate_limit_burst: int = 100

	# Security
	secret_key_version: int = 1
	
	# CORS Configuration
	cors_origins: str = "http://localhost:3000,http://localhost:3001"  # Comma-separated list of allowed origins
	cors_methods: str = "GET,POST,PUT,DELETE,PATCH,OPTIONS"  # Comma-separated list of allowed methods
	cors_headers: str = "Content-Type,Authorization,X-Requested-With,Accept,Origin"  # Comma-separated list of allowed headers

	# TikTok Business Ads
	tiktok_access_token: str | None = None
	tiktok_advertiser_id: str | None = None

	# Google Ads
	google_ads_access_token: str | None = None
	google_ads_customer_id: str | None = None
	google_ads_developer_token: str | None = None

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()  # type: ignore[call-arg]


