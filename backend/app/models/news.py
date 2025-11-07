"""
News model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON

from app.config.database import Base


class NewsCategory(Base):
    """
    News category model
    """
    __tablename__ = "news_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_zh = Column(String(100), nullable=True)  # Chinese name
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("news_categories.id"), nullable=True)
    icon = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Self-referential relationship for subcategories
    parent = relationship("NewsCategory", remote_side=[id], back_populates="children")
    children = relationship("NewsCategory", back_populates="parent", overlaps="parent")

    def __repr__(self):
        return f"<NewsCategory(id={self.id}, name={self.name})>"


class News(Base):
    """
    News model for storing news articles
    """
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    title = Column(String(500), nullable=False, index=True)
    title_zh = Column(String(500), nullable=True)  # Chinese title
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    summary_zh = Column(Text, nullable=True)  # Chinese summary

    # Source information
    source = Column(String(255), nullable=False, index=True)
    source_url = Column(String(1000), nullable=False, unique=True)
    author = Column(String(255), nullable=True)

    # Media
    image_url = Column(String(1000), nullable=True)
    video_url = Column(String(1000), nullable=True)

    # Categorization
    category_id = Column(Integer, ForeignKey("news_categories.id"), nullable=False, index=True)
    category = relationship("NewsCategory", backref="news")
    tags = Column(ARRAY(String), nullable=True)  # PostgreSQL array for tags

    # Metadata
    language = Column(String(10), default="zh")  # Language code
    word_count = Column(Integer, default=0)
    reading_time = Column(Integer, default=0)  # Estimated reading time in minutes

    # Quality metrics
    quality_score = Column(Float, default=0.0)  # Content quality score (0-1)
    sentiment_score = Column(Float, default=0.0)  # Sentiment analysis score (-1 to 1)

    # Engagement metrics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    click_through_rate = Column(Float, default=0.0)  # CTR

    # Popularity and trending
    popularity_score = Column(Float, default=0.0)  # Calculated popularity score
    trending_score = Column(Float, default=0.0)  # Trending score

    # Content vector for similarity (can be stored as array or JSON)
    embedding_vector = Column(JSON, nullable=True)  # Content embedding for ML

    # Status
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_breaking = Column(Boolean, default=False)

    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_crawled_at = Column(DateTime(timezone=True), server_default=func.now())

    # SEO
    slug = Column(String(500), nullable=True, unique=True, index=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(Text, nullable=True)

    # Additional metadata as JSON
    extra_metadata = Column(JSON, nullable=True, name="metadata")  # Additional structured data

    # Relationships
    behaviors = relationship("UserBehavior", back_populates="news", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<News(id={self.id}, title={self.title[:50]}..., source={self.source})>"

    @property
    def is_trending(self):
        """Check if news is currently trending"""
        return self.trending_score > 0.7

    @property
    def engagement_rate(self):
        """Calculate engagement rate"""
        if self.view_count == 0:
            return 0.0
        total_engagement = self.like_count + self.share_count + self.comment_count
        return total_engagement / self.view_count

    def to_dict(self, include_content=False):
        """Convert news object to dictionary"""
        data = {
            "id": self.id,
            "title": self.title,
            "title_zh": self.title_zh,
            "summary": self.summary,
            "summary_zh": self.summary_zh,
            "source": self.source,
            "source_url": self.source_url,
            "author": self.author,
            "image_url": self.image_url,
            "video_url": self.video_url,
            "category": self.category.name if self.category else None,
            "category_id": self.category_id,
            "tags": self.tags,
            "language": self.language,
            "word_count": self.word_count,
            "reading_time": self.reading_time,
            "quality_score": self.quality_score,
            "sentiment_score": self.sentiment_score,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "comment_count": self.comment_count,
            "popularity_score": self.popularity_score,
            "trending_score": self.trending_score,
            "is_published": self.is_published,
            "is_featured": self.is_featured,
            "is_breaking": self.is_breaking,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "slug": self.slug,
            "meta_description": self.meta_description,
        }

        if include_content:
            data["content"] = self.content

        return data