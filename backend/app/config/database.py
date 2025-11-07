"""
Database configuration and connection setup
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import redis.asyncio as aioredis
from elasticsearch import AsyncElasticsearch

from app.config.settings import settings

# SQLAlchemy database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis connection
async def get_redis() -> aioredis.Redis:
    """Get Redis connection"""
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis


# Elasticsearch connection
async def get_elasticsearch() -> AsyncElasticsearch:
    """Get Elasticsearch client"""
    es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
    return es


# Database connection test
async def test_database_connection():
    """Test database connectivity"""
    try:
        # Test PostgreSQL
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful")

        # Test Redis
        redis = await get_redis()
        await redis.ping()
        await redis.close()
        print("✅ Redis connection successful")

        # Test Elasticsearch
        es = await get_elasticsearch()
        await es.ping()
        await es.close()
        print("✅ Elasticsearch connection successful")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise