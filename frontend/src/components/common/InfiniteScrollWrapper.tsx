/**
 * InfiniteScrollWrapper component
 * Wraps react-infinite-scroll-component with better TypeScript support
 */

import { ReactNode } from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import { Spin, Empty, Space } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

export interface InfiniteScrollWrapperProps {
  /**
   * Child elements to render
   */
  children: ReactNode;

  /**
   * Whether there are more items to load
   */
  hasMore: boolean;

  /**
   * Function to call when reaching the end
   */
  onLoadMore: () => void;

  /**
   * Total number of items loaded
   */
  dataLength: number;

  /**
   * Whether initial loading
   */
  isLoading?: boolean;

  /**
   * Custom loader component
   */
  loader?: ReactNode;

  /**
   * Custom end message
   */
  endMessage?: ReactNode;

  /**
   * Custom empty message
   */
  emptyMessage?: ReactNode;

  /**
   * Height of scrollable container (default: auto = window scroll)
   */
  height?: number | string;

  /**
   * Scroll threshold (distance from bottom in pixels)
   */
  scrollThreshold?: number | string;
}

export const InfiniteScrollWrapper: React.FC<InfiniteScrollWrapperProps> = ({
  children,
  hasMore,
  onLoadMore,
  dataLength,
  isLoading = false,
  loader,
  endMessage,
  emptyMessage,
  height,
  scrollThreshold = '200px',
}) => {
  // Show loading state for initial load
  if (isLoading && dataLength === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin
          indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
          tip="加载中..."
        />
      </div>
    );
  }

  // Show empty state
  if (!isLoading && dataLength === 0) {
    return (
      <div style={{ padding: '50px 0' }}>
        {emptyMessage || (
          <Empty
            description="暂无内容"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </div>
    );
  }

  // Default loader
  const defaultLoader = (
    <div style={{ textAlign: 'center', padding: '20px 0' }}>
      <Space>
        <Spin />
        <span>加载更多...</span>
      </Space>
    </div>
  );

  // Default end message
  const defaultEndMessage = (
    <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
      已加载全部内容
    </div>
  );

  return (
    <InfiniteScroll
      dataLength={dataLength}
      next={onLoadMore}
      hasMore={hasMore}
      loader={loader || defaultLoader}
      endMessage={endMessage || defaultEndMessage}
      height={height}
      scrollThreshold={scrollThreshold}
    >
      {children}
    </InfiniteScroll>
  );
};

export default InfiniteScrollWrapper;
