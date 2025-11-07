/**
 * User service for user profile and preferences management
 */

import { get, put, del } from './apiClient';
import type { User, UserProfile, PaginatedResponse } from '../types';

export interface UserUpdateParams {
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  location?: string;
  language?: string;
}

export interface UserProfileUpdateParams {
  preferred_categories?: Record<string, number>;
  preferred_tags?: Record<string, number>;
  preferred_sources?: Record<string, number>;
  blocked_sources?: string[];
  blocked_keywords?: string[];
  preferred_language?: string;
  preferred_article_length?: 'short' | 'medium' | 'long';
  reading_frequency?: 'low' | 'medium' | 'high';
  quality_threshold?: number;
  diversity_preference?: number;
  novelty_preference?: number;
  email_notifications?: boolean;
  push_notifications?: boolean;
  notification_frequency?: 'immediate' | 'daily' | 'weekly';
  notification_categories?: string[];
  data_collection_allowed?: boolean;
  personalization_allowed?: boolean;
  analytics_sharing_allowed?: boolean;
  education_level?: string;
  occupation?: string;
  interests?: string[];
}

export interface UserHistoryParams {
  behavior_type?: 'read' | 'like' | 'share' | 'bookmark';
  start_date?: string;
  end_date?: string;
  category_id?: number;
  page?: number;
  page_size?: number;
}

export interface UserHistoryItem {
  id: number;
  news_id: number;
  news_title: string;
  news_summary?: string;
  news_image_url?: string;
  news_category?: string;
  behavior_type: string;
  duration?: number;
  timestamp: string;
}

export interface UserStatsResponse {
  total_reading_count: number;
  total_like_count: number;
  total_share_count: number;
  total_bookmark_count: number;
  total_reading_time: number;
  average_session_duration: number;
  most_read_categories: Array<{ category: string; count: number }>;
  most_read_tags: Array<{ tag: string; count: number }>;
  reading_streak_days: number;
  last_active_at?: string;
  member_since: string;
}

export interface OnboardingPreferences {
  categories: number[];
  tags?: string[];
  preferred_sources?: string[];
  article_length?: 'short' | 'medium' | 'long';
  diversity_preference?: number;
  novelty_preference?: number;
}

class UserService {
  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    return get<User>('/users/me');
  }

  /**
   * Update current user info
   */
  async updateCurrentUser(data: UserUpdateParams): Promise<User> {
    return put<User>('/users/me', data);
  }

  /**
   * Get user profile (extended info with preferences)
   */
  async getUserProfile(): Promise<UserProfile> {
    return get<UserProfile>('/users/me/profile');
  }

  /**
   * Update user profile
   */
  async updateUserProfile(data: UserProfileUpdateParams): Promise<UserProfile> {
    return put<UserProfile>('/users/me/profile', data);
  }

  /**
   * Get user reading history
   */
  async getReadingHistory(params: UserHistoryParams = {}): Promise<PaginatedResponse<UserHistoryItem>> {
    const { page = 1, page_size = 20, ...filters } = params;

    return get<PaginatedResponse<UserHistoryItem>>('/users/me/history', {
      page,
      page_size,
      ...filters,
    });
  }

  /**
   * Get user collections (bookmarks)
   */
  async getUserCollections(page: number = 1, page_size: number = 20): Promise<PaginatedResponse<UserHistoryItem>> {
    return get<PaginatedResponse<UserHistoryItem>>('/users/me/collections', {
      page,
      page_size,
    });
  }

  /**
   * Get user statistics
   */
  async getUserStats(): Promise<UserStatsResponse> {
    return get<UserStatsResponse>('/users/me/stats');
  }

  /**
   * Setup initial preferences (onboarding)
   */
  async setupPreferences(preferences: OnboardingPreferences): Promise<UserProfile> {
    return put<UserProfile>('/users/me/preferences/setup', preferences);
  }

  /**
   * Delete user account
   */
  async deleteAccount(): Promise<{ success: boolean; message: string }> {
    return del<{ success: boolean; message: string }>('/users/me');
  }

  /**
   * Check if user has completed onboarding
   */
  async hasCompletedOnboarding(): Promise<boolean> {
    try {
      const profile = await this.getUserProfile();
      return profile.profile_completeness > 0.3; // 30% threshold
    } catch {
      return false;
    }
  }

  /**
   * Get recommended categories for onboarding
   */
  getRecommendedCategories(): Array<{ id: number; name: string; name_zh: string; icon: string }> {
    // This could be fetched from API, but for now return static list
    return [
      { id: 1, name: 'Technology', name_zh: '科技', icon: '💻' },
      { id: 2, name: 'Business', name_zh: '商业', icon: '💼' },
      { id: 3, name: 'Entertainment', name_zh: '娱乐', icon: '🎬' },
      { id: 4, name: 'Sports', name_zh: '体育', icon: '⚽' },
      { id: 5, name: 'Health', name_zh: '健康', icon: '🏥' },
      { id: 6, name: 'Science', name_zh: '科学', icon: '🔬' },
      { id: 7, name: 'Politics', name_zh: '政治', icon: '🏛️' },
      { id: 8, name: 'Education', name_zh: '教育', icon: '📚' },
      { id: 9, name: 'Travel', name_zh: '旅游', icon: '✈️' },
      { id: 10, name: 'Food', name_zh: '美食', icon: '🍔' },
    ];
  }
}

export const userService = new UserService();
export default userService;
