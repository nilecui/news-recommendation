// Common types used across the application

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  bio?: string
  is_active: boolean
  is_verified: boolean
  age?: number
  gender?: 'male' | 'female' | 'other'
  location?: string
  language: string
  created_at: string
  last_login_at?: string
  reading_count: number
  like_count: number
  share_count: number
}

export interface NewsCategory {
  id: number
  name: string
  name_zh?: string
  description?: string
  parent_id?: number
  icon?: string
  color?: string
  sort_order: number
  is_active: boolean
}

export interface News {
  id: number
  title: string
  title_zh?: string
  summary?: string
  summary_zh?: string
  content?: string
  source: string
  source_url: string
  author?: string
  image_url?: string
  video_url?: string
  category?: string
  category_id: number
  tags?: string[]
  language: string
  word_count: number
  reading_time: number
  quality_score: number
  sentiment_score: number
  view_count: number
  like_count: number
  share_count: number
  comment_count: number
  popularity_score: number
  trending_score: number
  is_published: boolean
  is_featured: boolean
  is_breaking: boolean
  published_at: string
  created_at: string
  slug?: string
  meta_description?: string
}

export interface UserBehavior {
  id: number
  user_id: number
  news_id: number
  behavior_type: 'impression' | 'click' | 'read' | 'like' | 'share' | 'comment' | 'bookmark'
  position?: number
  page?: number
  context?: Record<string, any>
  duration?: number
  scroll_percentage?: number
  read_percentage?: number
  sentiment?: 'positive' | 'negative' | 'neutral'
  feedback_score?: number
  device_type?: 'mobile' | 'desktop' | 'tablet'
  platform?: 'web' | 'ios' | 'android'
  session_id?: string
  timestamp: string
  time_of_day?: number
  day_of_week?: number
  is_valid: boolean
  engagement_weight: number
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

export interface RecommendationResponse extends PaginatedResponse<News> {
  algorithm_version?: string
  refreshed_at?: string
  cache_hit?: boolean
}

export interface SearchFilters {
  category?: string
  source?: string
  date_range?: {
    start: string
    end: string
  }
  tags?: string[]
  sort_by?: 'relevance' | 'date' | 'popularity'
  language?: string
}

export interface UserProfile {
  preferred_categories?: Record<string, number>
  preferred_tags?: Record<string, number>
  preferred_sources?: Record<string, number>
  blocked_sources?: string[]
  blocked_keywords?: string[]
  preferred_language: string
  preferred_article_length: 'short' | 'medium' | 'long'
  reading_frequency: 'low' | 'medium' | 'high'
  quality_threshold: number
  diversity_preference: number
  novelty_preference: number
  email_notifications: boolean
  push_notifications: boolean
  notification_frequency: 'immediate' | 'daily' | 'weekly'
  notification_categories?: string[]
  data_collection_allowed: boolean
  personalization_allowed: boolean
  analytics_sharing_allowed: boolean
  education_level?: string
  occupation?: string
  interests?: string[]
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: number
}

export interface ApiError {
  code: number
  message: string
  detail?: string
}

// Tracking event types
export interface TrackingEvent {
  type: UserBehavior['behavior_type']
  newsId: number
  position?: number
  context?: Record<string, any>
  duration?: number
  scrollPercentage?: number
}

// Notification types
export interface Notification {
  id: number
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  is_read: boolean
  created_at: string
  data?: Record<string, any>
}