/**
 * News service for fetching and managing news articles
 */

import { get, post } from './apiClient';
import type { News, PaginatedResponse } from '../types';

export interface NewsSearchParams {
  query?: string;
  category_id?: number;
  categories?: number[];
  tags?: string[];
  source?: string;
  sources?: string[];
  language?: string;
  is_featured?: boolean;
  is_breaking?: boolean;
  published_after?: string;
  published_before?: string;
  min_quality_score?: number;
  min_popularity_score?: number;
  sort_by?: 'published_at' | 'popularity_score' | 'trending_score' | 'created_at' | 'view_count';
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export interface NewsTrendingParams {
  timeframe?: 'hour' | 'day' | 'week';
  category?: string;
  limit?: number;
}

class NewsService {
  /**
   * Get news detail by ID
   */
  async getNewsDetail(newsId: number): Promise<News> {
    return get<News>(`/news/${newsId}`);
  }

  /**
   * Get news by category
   */
  async getNewsByCategory(
    category: string,
    page: number = 1,
    limit: number = 20
  ): Promise<PaginatedResponse<News>> {
    return get<PaginatedResponse<News>>(`/news/category/${category}`, {
      page,
      limit,
    });
  }

  /**
   * Get trending news
   */
  async getTrendingNews(params: NewsTrendingParams = {}): Promise<News[]> {
    const { timeframe = 'day', category, limit = 20 } = params;
    return get<News[]>('/news/trending', {
      timeframe,
      category,
      limit,
    });
  }

  /**
   * Search news
   */
  async searchNews(params: NewsSearchParams): Promise<PaginatedResponse<News>> {
    return post<PaginatedResponse<News>>('/news/search', params);
  }

  /**
   * Get latest news
   */
  async getLatestNews(
    page: number = 1,
    limit: number = 20,
    category?: string
  ): Promise<PaginatedResponse<News>> {
    return get<PaginatedResponse<News>>('/news/latest', {
      page,
      limit,
      category,
    });
  }

  /**
   * Like/unlike news
   */
  async likeNews(newsId: number): Promise<{ success: boolean; message: string; new_count: number }> {
    return post(`/news/${newsId}/like`);
  }

  /**
   * Collect/uncollect news (bookmark)
   */
  async collectNews(newsId: number): Promise<{ success: boolean; message: string; new_count: number }> {
    return post(`/news/${newsId}/collect`);
  }

  /**
   * Share news
   */
  async shareNews(
    newsId: number,
    platform: 'wechat' | 'weibo' | 'twitter' | 'facebook'
  ): Promise<{ success: boolean; message: string }> {
    return post(`/news/${newsId}/share`, null, {
      params: { platform },
    });
  }

  /**
   * Get featured news
   */
  async getFeaturedNews(limit: number = 10): Promise<News[]> {
    return get<News[]>('/news/featured', { limit });
  }

  /**
   * Get breaking news
   */
  async getBreakingNews(limit: number = 5): Promise<News[]> {
    return get<News[]>('/news/breaking', { limit });
  }
}

export const newsService = new NewsService();
export default newsService;
