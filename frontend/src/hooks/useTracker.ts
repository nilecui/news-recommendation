/**
 * Hook for tracking user behaviors
 */

import { useCallback, useEffect, useRef } from 'react';
import { trackingService, type BehaviorType } from '../services/trackingService';

export interface TrackerOptions {
  /**
   * Recommendation ID for context
   */
  recommendationId?: string;

  /**
   * Page number for context
   */
  page?: number;

  /**
   * Position in list for context
   */
  position?: number;

  /**
   * Auto-track on mount (for impressions)
   */
  autoTrackOnMount?: boolean;
}

export const useTracker = (newsId: number, options: TrackerOptions = {}) => {
  const { recommendationId, page = 1, position, autoTrackOnMount = false } = options;

  const readStartTime = useRef<number | null>(null);
  const hasTrackedImpression = useRef(false);
  const hasTrackedClick = useRef(false);

  /**
   * Track impression
   */
  const trackImpression = useCallback(async () => {
    if (hasTrackedImpression.current) return;

    await trackingService.trackImpression({
      news_ids: [newsId],
      page,
      recommendation_id: recommendationId,
    });

    hasTrackedImpression.current = true;
  }, [newsId, page, recommendationId]);

  /**
   * Track click
   */
  const trackClick = useCallback(async () => {
    if (hasTrackedClick.current) return;

    await trackingService.trackClick({
      news_id: newsId,
      position,
      page,
      recommendation_id: recommendationId,
    });

    hasTrackedClick.current = true;
  }, [newsId, position, page, recommendationId]);

  /**
   * Start reading session
   */
  const startReading = useCallback(() => {
    readStartTime.current = Date.now();
  }, []);

  /**
   * End reading session and track
   */
  const endReading = useCallback(
    async (scrollPercentage?: number, readPercentage?: number) => {
      if (!readStartTime.current) return;

      const duration = (Date.now() - readStartTime.current) / 1000; // seconds

      await trackingService.trackRead({
        news_id: newsId,
        duration,
        scroll_percentage: scrollPercentage,
        read_percentage: readPercentage,
      });

      readStartTime.current = null;
    },
    [newsId]
  );

  /**
   * Track interaction (like, share, bookmark)
   */
  const trackInteraction = useCallback(
    async (interactionType: 'like' | 'share' | 'bookmark' | 'comment', feedbackText?: string) => {
      await trackingService.trackInteraction({
        news_id: newsId,
        interaction_type: interactionType,
        feedback_text: feedbackText,
      });
    },
    [newsId]
  );

  /**
   * Track like
   */
  const trackLike = useCallback(async () => {
    await trackInteraction('like');
  }, [trackInteraction]);

  /**
   * Track share
   */
  const trackShare = useCallback(async () => {
    await trackInteraction('share');
  }, [trackInteraction]);

  /**
   * Track bookmark
   */
  const trackBookmark = useCallback(async () => {
    await trackInteraction('bookmark');
  }, [trackInteraction]);

  // Auto-track impression on mount if enabled
  useEffect(() => {
    if (autoTrackOnMount) {
      trackImpression();
    }
  }, [autoTrackOnMount, trackImpression]);

  // Cleanup: track read duration on unmount if reading
  useEffect(() => {
    return () => {
      if (readStartTime.current) {
        const duration = (Date.now() - readStartTime.current) / 1000;
        // Fire and forget - don't wait for response
        trackingService.trackRead({
          news_id: newsId,
          duration,
        });
      }
    };
  }, [newsId]);

  return {
    trackImpression,
    trackClick,
    startReading,
    endReading,
    trackLike,
    trackShare,
    trackBookmark,
    trackInteraction,
  };
};

export default useTracker;
