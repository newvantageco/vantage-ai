"""
Performance tests using Locust
Tests API endpoints under load
"""

from locust import HttpUser, task, between
import random
import json

class VantageAIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Simulate user login or setup
        self.client.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'VantageAI-PerformanceTest/1.0'
        })
    
    @task(3)
    def health_check(self):
        """Test health endpoint - most frequent"""
        self.client.get("/api/v1/health")
    
    @task(2)
    def get_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        self.client.get("/api/v1/dashboard/stats")
    
    @task(1)
    def get_analytics(self):
        """Test analytics endpoint"""
        self.client.get("/api/v1/analytics/overview")
    
    @task(1)
    def get_content_library(self):
        """Test content library endpoint"""
        self.client.get("/api/v1/cms/content")
    
    @task(1)
    def get_integrations(self):
        """Test integrations endpoint"""
        self.client.get("/api/v1/integrations")
    
    @task(1)
    def create_content(self):
        """Test content creation endpoint"""
        content_data = {
            "title": f"Test Content {random.randint(1, 1000)}",
            "content": "This is a test content for performance testing",
            "content_type": "text",
            "status": "draft",
            "tags": ["test", "performance"],
            "metadata": {}
        }
        self.client.post("/api/v1/cms/content", json=content_data)
    
    @task(1)
    def get_publishing_history(self):
        """Test publishing history endpoint"""
        self.client.get("/api/v1/publishing/publishes")
    
    @task(1)
    def get_whatsapp_templates(self):
        """Test WhatsApp templates endpoint"""
        self.client.get("/api/v1/whatsapp/templates")
    
    @task(1)
    def get_billing_info(self):
        """Test billing information endpoint"""
        self.client.get("/api/v1/billing/overview")
    
    @task(1)
    def get_collaboration_data(self):
        """Test collaboration endpoint"""
        self.client.get("/api/v1/collaboration/teams")
    
    @task(1)
    def get_scheduled_content(self):
        """Test scheduled content endpoint"""
        self.client.get("/api/v1/schedule/upcoming")
    
    @task(1)
    def get_reports(self):
        """Test reports endpoint"""
        self.client.get("/api/v1/reports/summary")
    
    @task(1)
    def get_webhooks(self):
        """Test webhooks endpoint"""
        self.client.get("/api/v1/webhooks")
    
    @task(1)
    def get_api_keys(self):
        """Test API keys endpoint"""
        self.client.get("/api/v1/api-keys")
    
    @task(1)
    def get_limits(self):
        """Test limits endpoint"""
        self.client.get("/api/v1/limits/usage")
    
    @task(1)
    def get_ai_usage(self):
        """Test AI usage endpoint"""
        self.client.get("/api/v1/ai/usage")
    
    @task(1)
    def get_conversions(self):
        """Test conversions endpoint"""
        self.client.get("/api/v1/conversions/tracking")
    
    @task(1)
    def get_translations(self):
        """Test translations endpoint"""
        self.client.get("/api/v1/translations/languages")
    
    @task(1)
    def get_rate_limiting(self):
        """Test rate limiting endpoint"""
        self.client.get("/api/v1/rate-limiting/status")
    
    @task(1)
    def get_ads_management(self):
        """Test ads management endpoint"""
        self.client.get("/api/v1/ads/overview")
    
    @task(1)
    def get_ugc(self):
        """Test UGC endpoint"""
        self.client.get("/api/v1/ugc/content")
    
    @task(1)
    def get_exports(self):
        """Test exports endpoint"""
        self.client.get("/api/v1/exports/history")
    
    @task(1)
    def get_analytics_explorer(self):
        """Test analytics explorer endpoint"""
        self.client.get("/api/v1/analytics/explorer")
    
    @task(1)
    def get_orgs(self):
        """Test organizations endpoint"""
        self.client.get("/api/v1/orgs")
    
    @task(1)
    def get_channels(self):
        """Test channels endpoint"""
        self.client.get("/api/v1/channels")
    
    @task(1)
    def get_plans(self):
        """Test plans endpoint"""
        self.client.get("/api/v1/plan")
    
    @task(1)
    def get_content_plans(self):
        """Test content plans endpoint"""
        self.client.get("/api/v1/content-plan")
    
    @task(1)
    def get_schedule(self):
        """Test schedule endpoint"""
        self.client.get("/api/v1/schedule")
    
    @task(1)
    def get_reports_detailed(self):
        """Test detailed reports endpoint"""
        self.client.get("/api/v1/reports")
    
    @task(1)
    def get_billing_detailed(self):
        """Test detailed billing endpoint"""
        self.client.get("/api/v1/billing")
    
    @task(1)
    def get_oauth_meta(self):
        """Test OAuth Meta endpoint"""
        self.client.get("/api/v1/oauth/meta")
    
    @task(1)
    def get_oauth_google(self):
        """Test OAuth Google endpoint"""
        self.client.get("/api/v1/oauth/google")
    
    @task(1)
    def get_ai_endpoint(self):
        """Test AI endpoint"""
        self.client.get("/api/v1/ai")
    
    @task(1)
    def get_templates(self):
        """Test templates endpoint"""
        self.client.get("/api/v1/templates")
    
    @task(1)
    def get_inbox(self):
        """Test inbox endpoint"""
        self.client.get("/api/v1/inbox")
    
    @task(1)
    def get_insights(self):
        """Test insights endpoint"""
        self.client.get("/api/v1/insights")
    
    @task(1)
    def get_privacy(self):
        """Test privacy endpoint"""
        self.client.get("/api/v1/privacy")
    
    @task(1)
    def get_rules(self):
        """Test rules endpoint"""
        self.client.get("/api/v1/rules")
    
    @task(1)
    def get_billing_enhanced(self):
        """Test enhanced billing endpoint"""
        self.client.get("/api/v1/billing/enhanced")
    
    @task(1)
    def get_stripe_webhooks(self):
        """Test Stripe webhooks endpoint"""
        self.client.get("/api/v1/stripe/webhooks")
    
    @task(1)
    def get_ai_usage_detailed(self):
        """Test detailed AI usage endpoint"""
        self.client.get("/api/v1/ai/usage/detailed")
    
    @task(1)
    def get_billing_enhanced_detailed(self):
        """Test detailed enhanced billing endpoint"""
        self.client.get("/api/v1/billing/enhanced/detailed")
    
    @task(1)
    def get_limits_detailed(self):
        """Test detailed limits endpoint"""
        self.client.get("/api/v1/limits/detailed")
    
    @task(1)
    def get_api_keys_detailed(self):
        """Test detailed API keys endpoint"""
        self.client.get("/api/v1/api-keys/detailed")
    
    @task(1)
    def get_ugc_detailed(self):
        """Test detailed UGC endpoint"""
        self.client.get("/api/v1/ugc/detailed")
    
    @task(1)
    def get_exports_detailed(self):
        """Test detailed exports endpoint"""
        self.client.get("/api/v1/exports/detailed")
    
    @task(1)
    def get_analytics_explorer_detailed(self):
        """Test detailed analytics explorer endpoint"""
        self.client.get("/api/v1/analytics/explorer/detailed")
    
    @task(1)
    def get_conversions_detailed(self):
        """Test detailed conversions endpoint"""
        self.client.get("/api/v1/conversions/detailed")
    
    @task(1)
    def get_webhooks_detailed(self):
        """Test detailed webhooks endpoint"""
        self.client.get("/api/v1/webhooks/detailed")
    
    @task(1)
    def get_collaboration_detailed(self):
        """Test detailed collaboration endpoint"""
        self.client.get("/api/v1/collaboration/detailed")
    
    @task(1)
    def get_translations_detailed(self):
        """Test detailed translations endpoint"""
        self.client.get("/api/v1/translations/detailed")
    
    @task(1)
    def get_rate_limiting_detailed(self):
        """Test detailed rate limiting endpoint"""
        self.client.get("/api/v1/rate-limiting/detailed")
    
    @task(1)
    def get_ads_management_detailed(self):
        """Test detailed ads management endpoint"""
        self.client.get("/api/v1/ads/detailed")
    
    @task(1)
    def get_dashboard_detailed(self):
        """Test detailed dashboard endpoint"""
        self.client.get("/api/v1/dashboard/detailed")
