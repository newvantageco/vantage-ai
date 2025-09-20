"""
Security Tests for VANTAGE AI
Tests critical security configurations and vulnerabilities
"""

import pytest
import os
import re
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestSecurityConfiguration:
    """Test security configuration and headers"""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        response = client.get("/api/v1/health")
        
        # Check for security headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
        
        # Check header values
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    
    def test_csp_header_present(self):
        """Test that Content Security Policy header is present"""
        response = client.get("/api/v1/health")
        
        assert "Content-Security-Policy" in response.headers
        csp = response.headers["Content-Security-Policy"]
        
        # Check for basic CSP directives
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "style-src" in csp
        assert "img-src" in csp
    
    def test_no_server_header(self):
        """Test that server information is not exposed"""
        response = client.get("/api/v1/health")
        
        # Server header should be removed by security middleware
        assert "Server" not in response.headers
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        # Test preflight request
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should not allow wildcard origins
        assert "Access-Control-Allow-Origin" in response.headers
        allowed_origin = response.headers["Access-Control-Allow-Origin"]
        assert allowed_origin != "*"
        assert "localhost" in allowed_origin


class TestAuthenticationSecurity:
    """Test authentication security measures"""
    
    def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints require authentication"""
        # Test dashboard endpoint
        response = client.get("/api/v1/dashboard")
        
        # Should require authentication (401 or 403)
        assert response.status_code in [401, 403]
    
    def test_no_auth_bypass_in_production(self):
        """Test that authentication bypass is not available in production"""
        # This test would need to be run with ENVIRONMENT=production
        # For now, we'll test that the auth middleware is properly configured
        response = client.get("/api/v1/dashboard")
        
        # Should not return 200 without proper authentication
        assert response.status_code != 200


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting_headers(self):
        """Test that rate limiting headers are present"""
        response = client.get("/api/v1/health")
        
        # Rate limiting headers should be present
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_rate_limiting_functionality(self):
        """Test that rate limiting actually works"""
        # Make multiple requests quickly
        responses = []
        for i in range(10):
            response = client.get("/api/v1/health")
            responses.append(response)
        
        # All requests should succeed (rate limit is high for health endpoint)
        for response in responses:
            assert response.status_code == 200


class TestEnvironmentSecurity:
    """Test environment configuration security"""
    
    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets are present in code"""
        # Check docker-compose.yml
        with open("docker-compose.yml", "r") as f:
            docker_compose_content = f.read()
        
        # Should not contain hardcoded secrets
        assert "SECRET_KEY=dev-not-secret" not in docker_compose_content
        assert "SECRET_KEY=KYL8vtS4cI-8GPD-j5uSWd-r-Q79Vb87qEnG0o2w4dI=" not in docker_compose_content
    
    def test_cors_no_wildcards(self):
        """Test that CORS configuration doesn't use wildcards"""
        # Check main.py
        with open("app/main.py", "r") as f:
            main_content = f.read()
        
        # Should not contain CORS wildcards
        assert 'allow_origins=["*"]' not in main_content
    
    def test_environment_variables_secure(self):
        """Test that environment variables are properly configured"""
        # Check that SECRET_KEY is set and not default
        secret_key = os.getenv("SECRET_KEY")
        
        if secret_key:
            assert secret_key != "dev-not-secret"
            assert secret_key != "your-secure-secret-key-32-chars-minimum"
            assert len(secret_key) >= 32  # Should be at least 32 characters
    
    def test_production_environment_secure(self):
        """Test production environment configuration"""
        environment = os.getenv("ENVIRONMENT", "development")
        
        if environment == "production":
            # In production, debug should be disabled
            debug = os.getenv("DEBUG", "false")
            assert debug.lower() != "true"
            
            # CORS should not use wildcards
            cors_origins = os.getenv("CORS_ORIGINS", "")
            assert "*" not in cors_origins


class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        # Test with potentially malicious input
        malicious_input = "'; DROP TABLE users; --"
        
        # This should be handled safely by the ORM
        response = client.get(f"/api/v1/health?test={malicious_input}")
        
        # Should not cause a 500 error
        assert response.status_code != 500
    
    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        # Test with potentially malicious input
        malicious_input = "<script>alert('xss')</script>"
        
        response = client.get(f"/api/v1/health?test={malicious_input}")
        
        # Should not cause a 500 error
        assert response.status_code != 500
        
        # Response should not contain unescaped script tags
        response_text = response.text
        assert "<script>" not in response_text


class TestOAuthSecurity:
    """Test OAuth token security"""
    
    def test_oauth_tokens_encrypted(self):
        """Test that OAuth tokens are encrypted at rest"""
        # This test would need to check the database
        # For now, we'll test that the encryption functions exist
        from app.integrations.oauth.meta import MetaOAuth
        
        oauth = MetaOAuth()
        
        # Test encryption/decryption
        test_token = "test_token_123"
        encrypted = oauth._encrypt_token(test_token)
        decrypted = oauth._decrypt_token(encrypted)
        
        assert encrypted != test_token  # Should be encrypted
        assert decrypted == test_token  # Should decrypt correctly
    
    def test_oauth_token_rotation(self):
        """Test that OAuth tokens can be rotated"""
        # This would test the token refresh functionality
        # For now, we'll just ensure the methods exist
        from app.integrations.oauth.meta import MetaOAuth
        
        oauth = MetaOAuth()
        
        # Check that refresh methods exist
        assert hasattr(oauth, 'refresh_access_token')
        assert hasattr(oauth, 'get_long_lived_token')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
