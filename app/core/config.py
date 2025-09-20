from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os


class Settings(BaseSettings):
	model_config = {
		"protected_namespaces": ("settings_",),
		"env_file": ".env",
		"env_file_encoding": "utf-8",
		"extra": "ignore"  # Ignore extra environment variables
	}
	
	app_name: str = "Vantage AI Marketing SaaS"
	environment: str = "production"
	api_base: str = "/api/v1"

	# Database - Required for production
	database_url: str = Field(
		default="postgresql+psycopg://postgres:postgres@localhost:5432/vantage_ai",
		description="PostgreSQL database URL"
	)

	# Clerk
	clerk_secret_key: Optional[str] = None
	clerk_publishable_key: Optional[str] = None
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
	secret_key: str = "KYL8vtS4cI-8GPD-j5uSWd-r-Q79Vb87qEnG0o2w4dI="

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
	feature_fake_insights: bool = False  # Set to False to use real platform APIs
	insights_poll_interval_hours: int = 6  # How often to poll for new metrics
	e2e_mocks: bool = False  # Enable E2E mock mode for testing
	meta_insights_fields_fb: str = "impressions,post_impressions_unique,likes,comments,shares,clicks"
	ig_insights_metrics: str = "impressions,reach,likes,comments,saves,video_views"
	linkedin_stats_fields: str = "impressionCount,likeCount,commentCount,shareCount"

	# Automation & Rules
	automations_enabled: bool = True  # Feature flag for rules automation
	rules_worker_interval_minutes: int = 5  # How often to check for rule triggers
	rules_cooldown_minutes: int = 60  # Minimum time between rule executions
	max_budget_pct_change: int = 15  # Maximum budget change percentage per rule run

	# AI Cost Optimization
	redis_url: str = "redis://redis:6379"
	redis_host: str = "redis"
	redis_port: int = 6379
	redis_db: int = 0
	redis_password: Optional[str] = None
	ai_cache_ttl_secs: int = 86400  # 24 hours
	dev_tools_enabled: bool = False  # Feature flag for dev tools panel
	ai_budget_soft_limit_multiplier: float = 2.0  # Block when 2x over limit
	
	# AI Provider Configuration
	ai_primary_provider: str = "openai"
	ai_fallback_provider: str = "anthropic"
	anthropic_api_key: Optional[str] = None
	cohere_api_key: Optional[str] = None
	ollama_base_url: str = "http://localhost:11434"
	
	# AI Budget Limits (per organization)
	ai_org_daily_token_limit: int = 100000
	ai_org_daily_cost_limit_usd: float = 50.0
	ai_org_monthly_token_limit: int = 2000000
	ai_org_monthly_cost_limit_usd: float = 1000.0
	
	# AI Budget Limits (per user)
	ai_user_daily_token_limit: int = 10000
	ai_user_daily_cost_limit_usd: float = 5.0
	ai_user_monthly_token_limit: int = 200000
	ai_user_monthly_cost_limit_usd: float = 100.0
	
	# Media Upload
	media_upload_dir: str = Field(
		default="uploads/media",
		description="Directory for media file uploads"
	)
	max_file_size_mb: int = Field(
		default=100,
		description="Maximum file size in MB"
	)
	allowed_file_types: str = Field(
		default="image/jpeg,image/png,image/gif,image/webp,video/mp4,video/mov,audio/mp3,audio/wav",
		description="Comma-separated list of allowed MIME types"
	)

	# Stripe Billing
	stripe_secret_key: Optional[str] = None
	stripe_publishable_key: Optional[str] = None
	stripe_webhook_secret: Optional[str] = None
	stripe_price_id_starter: Optional[str] = None
	stripe_price_id_growth: Optional[str] = None
	stripe_price_id_pro: Optional[str] = None
	stripe_price_starter: Optional[str] = None
	stripe_price_growth: Optional[str] = None
	stripe_price_pro: Optional[str] = None
	stripe_dry_run: bool = False

	# PWA & Push Notifications
	vapid_public_key: Optional[str] = None
	vapid_private_key: Optional[str] = None
	vapid_email: Optional[str] = None

	# Rate Limiting
	rate_limit_enabled: bool = True
	rate_limit_requests_per_minute: int = 60
	rate_limit_burst: int = 100
	rate_limit_window_seconds: int = 60  # Time window for rate limiting
	rate_limit_storage_url: Optional[str] = None  # Redis URL for distributed rate limiting

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

	# Web Configuration
	next_public_api_base: Optional[str] = None

	# Configuration moved to model_config above

	@validator('environment')
	def validate_environment(cls, v):
		"""Validate environment is one of the allowed values."""
		allowed_envs = ['local', 'development', 'staging', 'production']
		if v not in allowed_envs:
			raise ValueError(f'Environment must be one of: {", ".join(allowed_envs)}')
		return v

	@validator('database_url')
	def validate_database_url(cls, v):
		"""Validate database URL format."""
		if not v.startswith(('postgresql://', 'postgresql+psycopg://')):
			raise ValueError('Database URL must be a valid PostgreSQL connection string')
		return v

	def validate_production_settings(self) -> None:
		"""Validate that all required settings are present for production."""
		if self.environment == 'production':
			required_settings = [
				('database_url', 'DATABASE_URL'),
				('secret_key', 'SECRET_KEY'),
			]
			
			missing_settings = []
			for setting_name, env_var in required_settings:
				value = getattr(self, setting_name)
				if not value or value in ['', 'placeholder', 'your_secret_key_here']:
					missing_settings.append(env_var)
			
			if missing_settings:
				raise ValueError(
					f"Missing required environment variables for production: {', '.join(missing_settings)}"
				)

	def is_development(self) -> bool:
		"""Check if running in development mode."""
		return self.environment in ['local', 'development']

	def is_production(self) -> bool:
		"""Check if running in production mode."""
		return self.environment == 'production'


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	settings = Settings()  # type: ignore[call-arg]
	
	# Validate production settings if in production
	if settings.is_production():
		settings.validate_production_settings()
	
	return settings


