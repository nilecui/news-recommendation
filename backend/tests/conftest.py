"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config.database import Base, get_db
from app.models import User, NewsCategory, News, UserProfile, UserBehavior, UserPreference
from tests.test_utils import JSONList


# Test database URL (SQLite in-memory for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# SQLite doesn't support some PostgreSQL features, so we need to handle them
# For JSON columns, SQLite uses TEXT with JSON serialization
# For ARRAY columns, we'll use JSON serialization as well


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys in SQLite"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function", autouse=True)
def patch_array_types():
    """Patch ARRAY types for SQLite compatibility before each test"""
    # Replace ARRAY columns with JSONList for SQLite
    import app.models.news as news_module
    import app.models.profile as profile_module
    
    # Store original column definitions
    original_columns = {}
    
    # Patch News.tags
    if hasattr(news_module.News, 'tags'):
        col = news_module.News.__table__.columns['tags']
        original_columns['news_tags'] = col.type
        col.type = JSONList()
    
    # Patch UserProfile ARRAY columns
    for col_name in ['blocked_sources', 'blocked_keywords', 'notification_categories', 'interests']:
        if hasattr(profile_module.UserProfile, col_name):
            col = profile_module.UserProfile.__table__.columns[col_name]
            original_columns[f'profile_{col_name}'] = col.type
            col.type = JSONList()
    
    yield
    
    # Restore original types
    if 'news_tags' in original_columns:
        news_module.News.__table__.columns['tags'].type = original_columns['news_tags']
    for col_name in ['blocked_sources', 'blocked_keywords', 'notification_categories', 'interests']:
        key = f'profile_{col_name}'
        if key in original_columns:
            profile_module.UserProfile.__table__.columns[col_name].type = original_columns[key]


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    import bcrypt
    import hashlib
    
    password = "Test123456"
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        full_name="Test User",
        is_active=True,
        is_verified=True,
        language="zh"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(client, test_user):
    """Get access token for test user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "Test123456"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def authenticated_client(client, test_user_token):
    """Create an authenticated test client"""
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client


@pytest.fixture
def test_category(db_session):
    """Create a test news category"""
    category = NewsCategory(
        name="technology",
        name_zh="科技",
        description="科技类新闻",
        sort_order=1,
        is_active=True
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_news(db_session, test_category):
    """Create test news"""
    from datetime import datetime, timezone
    
    news = News(
        title="Test News Title",
        title_zh="测试新闻标题",
        content="This is test news content.",
        summary="Test summary",
        source="Test Source",
        source_url="https://example.com/news/1",
        category_id=test_category.id,
        published_at=datetime.now(timezone.utc),
        is_published=True
    )
    db_session.add(news)
    db_session.commit()
    db_session.refresh(news)
    return news

