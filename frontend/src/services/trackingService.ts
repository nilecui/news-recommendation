/**
 * Tracking service for user behavior analytics
 */

import { post, get } from './apiClient';

export type BehaviorType = 'impression' | 'click' | 'read' | 'like' | 'share' | 'comment' | 'bookmark';

export interface BehaviorItem {
  news_id: number;
  behavior_type: BehaviorType;
  position?: number;
  page?: number;
  context?: Record<string, any>;
  duration?: number;
  scroll_percentage?: number;
  read_percentage?: number;
  timestamp?: string;
}

export interface BatchTrackingParams {
  behaviors: BehaviorItem[];
  session_id?: string;
  device_type?: 'mobile' | 'desktop' | 'tablet';
  platform?: 'web' | 'ios' | 'android';
  recommendation_id?: string;
  algorithm_version?: string;
}

export interface TrackingResponse {
  success: boolean;
  message: string;
  total_processed: number;
  total_failed: number;
  failed_indices: number[];
}

export interface ImpressionParams {
  news_ids: number[];
  page?: number;
  recommendation_id?: string;
}

export interface ClickParams {
  news_id: number;
  position?: number;
  page?: number;
  recommendation_id?: string;
}

export interface ReadParams {
  news_id: number;
  duration: number;
  scroll_percentage?: number;
  read_percentage?: number;
}

export interface InteractionParams {
  news_id: number;
  interaction_type: 'like' | 'share' | 'bookmark' | 'comment';
  feedback_text?: string;
}

export interface SessionStartParams {
  device_type?: 'mobile' | 'desktop' | 'tablet';
  platform?: 'web' | 'ios' | 'android';
}

export interface BehaviorStatsResponse {
  total_count: number;
  unique_users?: number;
  unique_news?: number;
  avg_duration?: number;
  avg_scroll_percentage?: number;
  time_series: Array<Record<string, any>>;
  top_news?: Array<Record<string, any>>;
  top_categories?: Array<Record<string, any>>;
}

class TrackingService {
  private behaviorQueue: BehaviorItem[] = [];
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly BATCH_SIZE = 50;
  private readonly FLUSH_INTERVAL = 30000; // 30 seconds
  private sessionId: string | null = null;

  constructor() {
    // Auto-flush on page unload
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.flushImmediately();
      });
    }
  }

  /**
   * Track behaviors in batch (queued and auto-flushed)
   */
  async trackBehaviors(behaviors: BehaviorItem[]): Promise<void> {
    this.behaviorQueue.push(...behaviors);

    // Auto-flush if batch size reached
    if (this.behaviorQueue.length >= this.BATCH_SIZE) {
      await this.flush();
    } else {
      // Schedule auto-flush
      this.scheduleFlush();
    }
  }

  /**
   * Track single behavior (adds to queue)
   */
  async trackBehavior(behavior: BehaviorItem): Promise<void> {
    return this.trackBehaviors([behavior]);
  }

  /**
   * Flush queued behaviors immediately
   */
  async flushImmediately(): Promise<void> {
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
    await this.flush();
  }

  /**
   * Internal flush implementation
   */
  private async flush(): Promise<void> {
    if (this.behaviorQueue.length === 0) return;

    const behaviors = [...this.behaviorQueue];
    this.behaviorQueue = [];

    try {
      await post<TrackingResponse>('/tracking/behaviors', {
        behaviors,
        session_id: this.sessionId || undefined,
        device_type: this.getDeviceType(),
        platform: 'web',
      });
    } catch (error) {
      console.error('Failed to track behaviors:', error);
      // Re-queue failed behaviors (optional)
      // this.behaviorQueue.unshift(...behaviors);
    }
  }

  /**
   * Schedule automatic flush
   */
  private scheduleFlush(): void {
    if (this.flushTimer) return;

    this.flushTimer = setTimeout(() => {
      this.flush();
      this.flushTimer = null;
    }, this.FLUSH_INTERVAL);
  }

  /**
   * Track impressions (batch)
   */
  async trackImpression(params: ImpressionParams): Promise<void> {
    const { news_ids, page = 1, recommendation_id } = params;

    const behaviors: BehaviorItem[] = news_ids.map((news_id, index) => ({
      news_id,
      behavior_type: 'impression',
      position: index,
      page,
      context: { recommendation_id },
    }));

    return this.trackBehaviors(behaviors);
  }

  /**
   * Track click
   */
  async trackClick(params: ClickParams): Promise<void> {
    const { news_id, position, page = 1, recommendation_id } = params;

    return this.trackBehavior({
      news_id,
      behavior_type: 'click',
      position,
      page,
      context: { recommendation_id },
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Track read
   */
  async trackRead(params: ReadParams): Promise<void> {
    const { news_id, duration, scroll_percentage, read_percentage } = params;

    return this.trackBehavior({
      news_id,
      behavior_type: 'read',
      duration,
      scroll_percentage,
      read_percentage,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Track interaction (like, share, bookmark, comment)
   */
  async trackInteraction(params: InteractionParams): Promise<void> {
    const { news_id, interaction_type, feedback_text } = params;

    return this.trackBehavior({
      news_id,
      behavior_type: interaction_type as BehaviorType,
      context: feedback_text ? { feedback_text } : undefined,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Start new session
   */
  async startSession(params: SessionStartParams = {}): Promise<string> {
    const { device_type, platform = 'web' } = params;

    const response = await post<{ session_id: string; user_id: number; started_at: string }>(
      '/tracking/session/start',
      {
        device_type: device_type || this.getDeviceType(),
        platform,
      }
    );

    this.sessionId = response.session_id;
    return this.sessionId;
  }

  /**
   * Get user behavior statistics
   */
  async getUserBehaviorStats(): Promise<BehaviorStatsResponse> {
    return get<BehaviorStatsResponse>('/tracking/stats/user');
  }

  /**
   * Get device type
   */
  private getDeviceType(): 'mobile' | 'desktop' | 'tablet' {
    if (typeof window === 'undefined') return 'desktop';

    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }
}

export const trackingService = new TrackingService();
export default trackingService;
