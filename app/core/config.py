from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	model_config = {
		"protected_namespaces": ("settings_",),
		"env_file": ".env",
		"env_file_encoding": "utf-8"
	}
	
	app_name: str = "Vantage AI Marketing SaaS"
	environment: str = "local"
	api_base: str = "/api/v1"

	# Database
	database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/vantage_ai"

	# Clerk
	clerk_jwks_url: Optional[str] = None
	clerk_issuer: Optional[str] = None

	# Meta OAuth & Platform
	meta_app_id: Optional[str] = None
	meta_app_secret: Optional[str] = None
	meta_redirect_uri: Optional[str] = None
	meta_graph_version: str = "20.0"
	meta_page_id: Optional[str] = None
	meta_ig_business_id: Optional[str] = None

	# LinkedIn OAuth & Platform
	linkedin_client_id: Optional[str] = None
	linkedin_client_secret: Optional[str] = None
	linkedin_redirect_url: Optional[str] = None
	linkedin_page_urn: Optional[str] = None

	# Google OAuth & Platform
	google_client_id: Optional[str] = None
	google_client_secret: Optional[str] = None
	google_redirect_url: Optional[str] = None
	google_business_location_id: Optional[str] = None
	gbp_enabled: bool = False

	# WhatsApp Cloud API
	whatsapp_verify_token: Optional[str] = None
	whatsapp_phone_id: Optional[str] = None
	whatsapp_access_token: Optional[str] = None

	# General
	dry_run: bool = False
	secret_key: str = "your-secret-key-change-in-production"

	model_router_primary: Optional[str] = None
	model_router_fallback: Optional[str] = None
	
	# OpenAI API
	openai_api_key: Optional[str] = None
	
	# Model configuration
	model_mode: Optional[str] = None
	hosted_model_name: Optional[str] = None
	
	# Debug mode
	debug: bool = False

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
	stripe_secret_key: Optional[str] = None
	stripe_publishable_key: Optional[str] = None
	stripe_webhook_secret: Optional[str] = None
	stripe_price_id_starter: Optional[str] = None
	stripe_price_id_growth: Optional[str] = None
	stripe_price_id_pro: Optional[str] = None

	# PWA & Push Notifications
	vapid_public_key: Optional[str] = None
	vapid_private_key: Optional[str] = None
	vapid_email: Optional[str] = None

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
	tiktok_access_token: Optional[str] = None
	tiktok_advertiser_id: Optional[str] = None

	# Google Ads
	google_ads_access_token: Optional[str] = None
	google_ads_customer_id: Optional[str] = None
	google_ads_developer_token: Optional[str] = None

	# Configuration moved to model_config above


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()  # type: ignore[call-arg]


