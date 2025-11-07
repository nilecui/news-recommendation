/**
 * Hook for infinite scrolling news list with React Query
 */

import { useInfiniteQuery, UseInfiniteQueryOptions } from '@tanstack/react-query';
import type { News, PaginatedResponse } from '../types';

export type NewsFetcher = (page: number, pageSize: number) => Promise<PaginatedResponse<News>>;

export interface UseInfiniteNewsOptions {
  /**
   * Function to fetch news
   */
  fetcher: NewsFetcher;

  /**
   * Query key for caching
   */
  queryKey: string[];

  /**
   * Page size
   */
  pageSize?: number;

  /**
   * Whether to enable the query
   */
  enabled?: boolean;

  /**
   * Additional React Query options
   */
  queryOptions?: Partial<UseInfiniteQueryOptions<PaginatedResponse<News>>>;
}

export const useInfiniteNews = (options: UseInfiniteNewsOptions) => {
  const { fetcher, queryKey, pageSize = 20, enabled = true, queryOptions } = options;

  const query = useInfiniteQuery<PaginatedResponse<News>>({
    queryKey,
    queryFn: ({ pageParam = 1 }) => fetcher(pageParam as number, pageSize),
    getNextPageParam: (lastPage) => {
      if (lastPage.has_next) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    enabled,
    ...queryOptions,
  });

  // Flatten all pages into single array
  const allNews: News[] = query.data?.pages.flatMap((page) => page.items) ?? [];

  // Total count from first page
  const total = query.data?.pages[0]?.total ?? 0;

  return {
    news: allNews,
    total,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    isFetching: query.isFetching,
    isFetchingNextPage: query.isFetchingNextPage,
    hasNextPage: query.hasNextPage,
    fetchNextPage: query.fetchNextPage,
    refetch: query.refetch,
  };
};

export default useInfiniteNews;
