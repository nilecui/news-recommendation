/**
 * Hook for tracking element visibility (impressions)
 */

import { useEffect, useRef, useCallback } from 'react';
import { useInView } from 'react-intersection-observer';
import { trackingService } from '../services/trackingService';

export interface VisibilityTrackerOptions {
  /**
   * News ID to track
   */
  newsId: number;

  /**
   * Position in list
   */
  position?: number;

  /**
   * Page number
   */
  page?: number;

  /**
   * Recommendation ID for context
   */
  recommendationId?: string;

  /**
   * Minimum visibility ratio (0-1) to trigger tracking
   * Default: 0.5 (50% visible)
   */
  threshold?: number;

  /**
   * Minimum time visible (ms) before tracking
   * Default: 1000ms (1 second)
   */
  minVisibleTime?: number;

  /**
   * Whether to track only once
   * Default: true
   */
  trackOnce?: boolean;
}

export const useVisibilityTracker = (options: VisibilityTrackerOptions) => {
  const {
    newsId,
    position,
    page = 1,
    recommendationId,
    threshold = 0.5,
    minVisibleTime = 1000,
    trackOnce = true,
  } = options;

  const hasTracked = useRef(false);
  const visibilityTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { ref, inView } = useInView({
    threshold,
    triggerOnce: trackOnce,
  });

  const trackImpression = useCallback(async () => {
    if (trackOnce && hasTracked.current) return;

    try {
      await trackingService.trackImpression({
        news_ids: [newsId],
        page,
        recommendation_id: recommendationId,
      });

      hasTracked.current = true;
    } catch (error) {
      console.error('Failed to track impression:', error);
    }
  }, [newsId, page, recommendationId, trackOnce]);

  useEffect(() => {
    if (inView) {
      // Start timer when element becomes visible
      visibilityTimer.current = setTimeout(() => {
        trackImpression();
      }, minVisibleTime);
    } else {
      // Clear timer if element becomes invisible before min time
      if (visibilityTimer.current) {
        clearTimeout(visibilityTimer.current);
        visibilityTimer.current = null;
      }
    }

    // Cleanup
    return () => {
      if (visibilityTimer.current) {
        clearTimeout(visibilityTimer.current);
      }
    };
  }, [inView, trackImpression, minVisibleTime]);

  return { ref, inView, hasTracked: hasTracked.current };
};

export default useVisibilityTracker;
