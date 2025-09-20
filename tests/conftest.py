"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from app.main import create_app
from app.db.base_class import Base
from app.db.session import get_db
from app.models.cms import UserAccount, Organization

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def db_session():
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return UserAccount(
        id=1,
        organization_id=1,
        clerk_user_id="test_user_123",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role="admin",
        is_active=True
    )


@pytest.fixture
def mock_organization():
    """Create a mock organization for testing"""
    return Organization(
        id=1,
        name="Test Organization",
        slug="test-org",
        subscription_status="active",
        plan="growth"
    )


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer mock_jwt_token"}


@pytest.fixture
def mock_jwt_decode():
    """Mock JWT decode function"""
    with patch("app.api.deps.jwt.decode") as mock_decode:
        mock_decode.return_value = {
            "sub": "test_user_123",
            "email": "test@example.com"
        }
        yield mock_decode


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    with patch("app.middleware.rate_limiting.redis.from_url") as mock_redis:
        mock_client = Mock()
        mock_client.pipeline.return_value.__enter__.return_value.execute.return_value = [0, 0]  # Mock pipeline results
        mock_redis.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_celery_task():
    """Mock Celery task execution"""
    with patch("app.workers.tasks.ai_content_tasks.generate_ai_content_task.delay") as mock_task:
        mock_task.return_value.id = "test_task_123"
        yield mock_task
