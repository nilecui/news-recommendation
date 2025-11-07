/**
 * Recommendation service for personalized news recommendations
 */

import { get, post } from './apiClient';
import type { News } from '../types';

export interface RecommendationParams {
  page?: number;
  page_size?: number;
  category_id?: number;
  include_breaking?: boolean;
  include_featured?: boolean;
  diversify?: boolean;
  fresh_ratio?: number;
  explore_ratio?: number;
}

export interface ColdStartParams {
  categories: number[];
  tags?: string[];
  page?: number;
  page_size?: number;
}

export interface RecommendationResponse {
  items: Array<News & {
    position: number;
    recommendation_score: number;
    recommendation_reason?: string;
    recall_strategy?: string;
  }>;
  total: number;
  page: number;
  page_size: number;
  recommendation_id: string;
  algorithm_version: string;
  timestamp: string;
  has_next: boolean;
  metadata?: Record<string, any>;
}

export interface PopularNewsParams {
  timeframe?: '1h' | '6h' | '24h' | '7d' | '30d';
  category_id?: number;
  page?: number;
  page_size?: number;
}

export interface SimilarNewsParams {
  news_id: number;
  limit?: number;
  min_similarity?: number;
}

export interface FeedbackParams {
  recommendation_id: string;
  news_id: number;
  feedback_type: 'positive' | 'negative' | 'neutral';
  reason?: string;
}

class RecommendationService {
  /**
   * Get personalized recommendations for current user
   */
  async getPersonalizedRecommendations(
    params: RecommendationParams = {}
  ): Promise<RecommendationResponse> {
    const {
      page = 1,
      page_size = 20,
      category_id,
      include_breaking = true,
      include_featured = true,
      diversify = true,
      fresh_ratio = 0.2,
      explore_ratio = 0.1,
    } = params;

    return get<RecommendationResponse>('/recommendations/', {
      page,
      page_size,
      category_id,
      include_breaking,
      include_featured,
      diversify,
      fresh_ratio,
      explore_ratio,
    });
  }

  /**
   * Get cold start recommendations for new users
   */
  async getColdStartRecommendations(params: ColdStartParams): Promise<RecommendationResponse> {
    const { categories, tags, page = 1, page_size = 20 } = params;

    return get<RecommendationResponse>('/recommendations/cold-start', {
      categories: categories.join(','),
      tags: tags?.join(','),
      page,
      page_size,
    });
  }

  /**
   * Get similar news recommendations
   */
  async getSimilarNews(params: SimilarNewsParams): Promise<{ items: News[]; total: number; reference_news_id: number }> {
    const { news_id, limit = 10, min_similarity = 0.5 } = params;

    return get(`/recommendations/similar/${news_id}`, {
      limit,
      min_similarity,
    });
  }

  /**
   * Get popular/hot news
   */
  async getPopularNews(params: PopularNewsParams = {}): Promise<RecommendationResponse> {
    const { timeframe = '24h', category_id, page = 1, page_size = 20 } = params;

    return get<RecommendationResponse>('/recommendations/popular', {
      timeframe,
      category_id,
      page,
      page_size,
    });
  }

  /**
   * Get discovery recommendations (explore new content)
   */
  async getDiscoveryRecommendations(
    limit: number = 20
  ): Promise<RecommendationResponse> {
    return get<RecommendationResponse>('/recommendations/discovery', {
      limit,
    });
  }

  /**
   * Submit feedback on recommendation
   */
  async submitFeedback(params: FeedbackParams): Promise<{ success: boolean; message: string }> {
    return post<{ success: boolean; message: string }>('/recommendations/feedback', params);
  }

  /**
   * Refresh recommendations (clear cache and get new ones)
   */
  async refreshRecommendations(params: RecommendationParams = {}): Promise<RecommendationResponse> {
    return this.getPersonalizedRecommendations({ ...params, _timestamp: Date.now() } as any);
  }
}

export const recommendationService = new RecommendationService();
export default recommendationService;
