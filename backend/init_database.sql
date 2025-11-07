-- ============================================
-- 新闻推荐系统数据库初始化脚本
-- Database: recommandation
-- ============================================

-- 创建数据库（如果不存在，需要先连接到 postgres 数据库执行）
-- CREATE DATABASE recommandation;

-- 连接到 recommandation 数据库
-- \c recommandation;

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. 用户表 (users)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    
    -- 用户状态
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    
    -- 用户信息
    avatar_url VARCHAR(500),
    bio TEXT,
    
    -- 人口统计信息
    age INTEGER,
    gender VARCHAR(10),  -- 'male', 'female', 'other'
    location VARCHAR(255),
    language VARCHAR(10) DEFAULT 'zh',
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- 统计信息
    login_count INTEGER DEFAULT 0,
    reading_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================
-- 2. 新闻分类表 (news_categories)
-- ============================================
CREATE TABLE IF NOT EXISTS news_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    name_zh VARCHAR(100),
    description TEXT,
    parent_id INTEGER,
    icon VARCHAR(255),
    color VARCHAR(7),  -- Hex color code
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES news_categories(id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_news_categories_name ON news_categories(name);
CREATE INDEX IF NOT EXISTS idx_news_categories_parent_id ON news_categories(parent_id);

-- ============================================
-- 3. 新闻表 (news)
-- ============================================
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    
    -- 基本信息
    title VARCHAR(500) NOT NULL,
    title_zh VARCHAR(500),
    content TEXT NOT NULL,
    summary TEXT,
    summary_zh TEXT,
    
    -- 来源信息
    source VARCHAR(255) NOT NULL,
    source_url VARCHAR(1000) NOT NULL UNIQUE,
    author VARCHAR(255),
    
    -- 媒体
    image_url VARCHAR(1000),
    video_url VARCHAR(1000),
    
    -- 分类
    category_id INTEGER NOT NULL,
    tags VARCHAR[],
    
    -- 元数据
    language VARCHAR(10) DEFAULT 'zh',
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    
    -- 质量指标
    quality_score DOUBLE PRECISION DEFAULT 0.0,
    sentiment_score DOUBLE PRECISION DEFAULT 0.0,
    
    -- 参与度指标
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    click_through_rate DOUBLE PRECISION DEFAULT 0.0,
    
    -- 流行度和趋势
    popularity_score DOUBLE PRECISION DEFAULT 0.0,
    trending_score DOUBLE PRECISION DEFAULT 0.0,
    
    -- 内容向量（用于相似度计算）
    embedding_vector JSONB,
    
    -- 状态
    is_published BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_breaking BOOLEAN DEFAULT FALSE,
    
    -- 时间戳
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_crawled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- SEO
    slug VARCHAR(500) UNIQUE,
    meta_description TEXT,
    meta_keywords TEXT,
    
    -- 额外元数据
    metadata JSONB,
    
    FOREIGN KEY (category_id) REFERENCES news_categories(id) ON DELETE RESTRICT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_news_title ON news(title);
CREATE INDEX IF NOT EXISTS idx_news_source ON news(source);
CREATE INDEX IF NOT EXISTS idx_news_category_id ON news(category_id);
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at);
CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at);
CREATE INDEX IF NOT EXISTS idx_news_slug ON news(slug);
CREATE INDEX IF NOT EXISTS idx_news_source_url ON news(source_url);

-- ============================================
-- 4. 用户资料表 (user_profiles)
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    
    -- 内容偏好
    preferred_categories JSONB,
    preferred_tags JSONB,
    preferred_sources JSONB,
    blocked_sources VARCHAR[],
    blocked_keywords VARCHAR[],
    
    -- 阅读偏好
    preferred_language VARCHAR(10) DEFAULT 'zh',
    preferred_article_length VARCHAR(20) DEFAULT 'medium',  -- 'short', 'medium', 'long'
    reading_frequency VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high'
    
    -- 兴趣画像（ML生成）
    interest_vector JSONB,
    interest_keywords JSONB,
    interest_categories JSONB,
    
    -- 行为模式
    typical_reading_times JSONB,
    typical_session_duration DOUBLE PRECISION DEFAULT 5.0,
    bounce_rate DOUBLE PRECISION DEFAULT 0.0,
    
    -- 内容质量偏好
    quality_threshold DOUBLE PRECISION DEFAULT 0.5,
    diversity_preference DOUBLE PRECISION DEFAULT 0.5,
    novelty_preference DOUBLE PRECISION DEFAULT 0.5,
    
    -- 通知偏好
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    notification_frequency VARCHAR(20) DEFAULT 'daily',  -- 'immediate', 'daily', 'weekly'
    notification_categories VARCHAR[],
    
    -- 隐私设置
    data_collection_allowed BOOLEAN DEFAULT TRUE,
    personalization_allowed BOOLEAN DEFAULT TRUE,
    analytics_sharing_allowed BOOLEAN DEFAULT FALSE,
    
    -- 人口统计信息（增强）
    education_level VARCHAR(50),
    occupation VARCHAR(100),
    interests VARCHAR[],
    
    -- ML模型数据
    model_version VARCHAR(20),
    last_profile_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    profile_confidence DOUBLE PRECISION DEFAULT 0.0,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- ============================================
-- 5. 用户偏好表 (user_preferences)
-- ============================================
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL,
    
    -- 偏好类型和值
    preference_type VARCHAR(50) NOT NULL,  -- 'category', 'source', 'topic', 'author'
    preference_key VARCHAR(255) NOT NULL,
    preference_value DOUBLE PRECISION NOT NULL DEFAULT 0.0,  -- -1 to 1
    
    -- 元数据
    source VARCHAR(50),  -- 'explicit', 'implicit', 'ml'
    confidence DOUBLE PRECISION DEFAULT 0.0,  -- 0-1
    weight DOUBLE PRECISION DEFAULT 1.0,
    
    -- 时间数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_preferences_profile_id ON user_preferences(profile_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_type ON user_preferences(preference_type);
CREATE INDEX IF NOT EXISTS idx_user_preferences_key ON user_preferences(preference_key);

-- ============================================
-- 6. 用户行为表 (user_behaviors)
-- ============================================
CREATE TABLE IF NOT EXISTS user_behaviors (
    id SERIAL PRIMARY KEY,
    
    -- 外键
    user_id INTEGER NOT NULL,
    news_id INTEGER NOT NULL,
    
    -- 行为类型
    behavior_type VARCHAR(50) NOT NULL,  -- 'impression', 'click', 'read', 'like', 'share', 'comment', 'bookmark'
    
    -- 行为上下文
    position INTEGER,
    page INTEGER DEFAULT 1,
    context JSONB,
    
    -- 持续时间和完成度（用于阅读行为）
    duration DOUBLE PRECISION,
    scroll_percentage DOUBLE PRECISION,
    read_percentage DOUBLE PRECISION,
    
    -- 情感和反馈
    sentiment VARCHAR(20),  -- 'positive', 'negative', 'neutral'
    feedback_score DOUBLE PRECISION,
    feedback_text VARCHAR(1000),
    
    -- 推荐上下文
    recommendation_id VARCHAR(100),
    algorithm_version VARCHAR(20),
    ab_test_group VARCHAR(20),
    
    -- 设备和会话信息
    device_type VARCHAR(50),  -- 'mobile', 'desktop', 'tablet'
    platform VARCHAR(50),  -- 'web', 'ios', 'android'
    session_id VARCHAR(100),
    ip_address VARCHAR(45),  -- IPv6 compatible
    user_agent VARCHAR(500),
    
    -- 地理信息
    country VARCHAR(2),  -- ISO 3166-1 alpha-2
    city VARCHAR(100),
    timezone VARCHAR(50),
    
    -- 时间
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    time_of_day INTEGER,  -- 0-23
    day_of_week INTEGER,  -- 0-6
    
    -- 质量指标
    is_valid BOOLEAN DEFAULT TRUE,
    is_bot BOOLEAN DEFAULT FALSE,
    confidence DOUBLE PRECISION DEFAULT 1.0,
    
    -- 处理标志
    is_processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_behaviors_user_id ON user_behaviors(user_id);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_news_id ON user_behaviors(news_id);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_type ON user_behaviors(behavior_type);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_timestamp ON user_behaviors(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_session_id ON user_behaviors(session_id);

-- ============================================
-- 创建更新时间触发器函数
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_news_categories_updated_at BEFORE UPDATE ON news_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_news_updated_at BEFORE UPDATE ON news
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 初始化数据（可选）
-- ============================================

-- 插入一些默认的新闻分类
INSERT INTO news_categories (name, name_zh, description, sort_order) VALUES
    ('technology', '科技', '科技类新闻', 1),
    ('politics', '政治', '政治类新闻', 2),
    ('economy', '经济', '经济类新闻', 3),
    ('sports', '体育', '体育类新闻', 4),
    ('entertainment', '娱乐', '娱乐类新闻', 5),
    ('health', '健康', '健康类新闻', 6),
    ('education', '教育', '教育类新闻', 7),
    ('society', '社会', '社会类新闻', 8)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 完成
-- ============================================
-- 显示创建的表
SELECT 'Database initialization completed!' AS status;
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

