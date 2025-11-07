/**
 * NewsCard component for displaying news articles
 */

import { useState } from 'react';
import { Card, Space, Tag, Typography, Button, message } from 'antd';
import {
  HeartOutlined,
  HeartFilled,
  ShareAltOutlined,
  BookOutlined,
  BookFilled,
  EyeOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import type { News } from '../../types';
import { newsService } from '../../services/newsService';
import { useTracker } from '../../hooks/useTracker';
import { useVisibilityTracker } from '../../hooks/useVisibilityTracker';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';
import './NewsCard.css';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Text, Title, Paragraph } = Typography;
const { Meta } = Card;

export interface NewsCardProps {
  news: News;
  position?: number;
  page?: number;
  recommendationId?: string;
  layout?: 'vertical' | 'horizontal';
  showActions?: boolean;
  showImage?: boolean;
  onClick?: () => void;
}

export const NewsCard: React.FC<NewsCardProps> = ({
  news,
  position,
  page = 1,
  recommendationId,
  layout = 'vertical',
  showActions = true,
  showImage = true,
  onClick,
}) => {
  const [isLiked, setIsLiked] = useState(false);
  const [isCollected, setIsCollected] = useState(false);
  const [likeCount, setLikeCount] = useState(news.like_count || 0);

  // Tracking hooks
  const { trackClick, trackLike, trackShare, trackBookmark } = useTracker(news.id, {
    position,
    page,
    recommendationId,
  });

  const { ref } = useVisibilityTracker({
    newsId: news.id,
    position,
    page,
    recommendationId,
    threshold: 0.5,
    minVisibleTime: 1000,
  });

  // Handlers
  const handleClick = () => {
    trackClick();
    onClick?.();
  };

  const handleLike = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();

    try {
      const result = await newsService.likeNews(news.id);
      setIsLiked(!isLiked);
      setLikeCount(result.new_count);
      trackLike();
      message.success(isLiked ? '已取消点赞' : '点赞成功');
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleCollect = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();

    try {
      await newsService.collectNews(news.id);
      setIsCollected(!isCollected);
      trackBookmark();
      message.success(isCollected ? '已取消收藏' : '收藏成功');
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleShare = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();

    try {
      // For now, just copy link to clipboard
      await navigator.clipboard.writeText(window.location.origin + `/news/${news.id}`);
      trackShare();
      message.success('链接已复制到剪贴板');
    } catch (error) {
      message.error('分享失败');
    }
  };

  // Render content
  const cover = showImage && news.image_url ? (
    <img
      alt={news.title}
      src={news.image_url}
      style={{
        width: '100%',
        height: layout === 'horizontal' ? 120 : 200,
        objectFit: 'cover',
      }}
      loading="lazy"
    />
  ) : undefined;

  const actions = showActions
    ? [
        <Button
          key="like"
          type="text"
          icon={isLiked ? <HeartFilled style={{ color: '#ff4d4f' }} /> : <HeartOutlined />}
          onClick={handleLike}
        >
          {likeCount > 0 ? likeCount : '点赞'}
        </Button>,
        <Button
          key="collect"
          type="text"
          icon={isCollected ? <BookFilled style={{ color: '#1890ff' }} /> : <BookOutlined />}
          onClick={handleCollect}
        >
          收藏
        </Button>,
        <Button
          key="share"
          type="text"
          icon={<ShareAltOutlined />}
          onClick={handleShare}
        >
          分享
        </Button>,
      ]
    : undefined;

  return (
    <Link to={`/news/${news.id}`} onClick={handleClick} style={{ textDecoration: 'none' }}>
      <Card
        ref={ref}
        hoverable
        cover={cover}
        actions={actions}
        className={`news-card ${layout === 'horizontal' ? 'news-card-horizontal' : ''}`}
      >
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          {/* Tags */}
          <Space wrap>
            {news.is_breaking && <Tag color="red">突发</Tag>}
            {news.is_featured && <Tag color="gold">精选</Tag>}
            {news.tags?.slice(0, 3).map((tag) => (
              <Tag key={tag}>{tag}</Tag>
            ))}
          </Space>

          {/* Title */}
          <Title level={5} ellipsis={{ rows: 2 }} className="news-card-title">
            {news.title_zh || news.title}
          </Title>

          {/* Summary */}
          {news.summary && (
            <Paragraph
              ellipsis={{ rows: 2 }}
              type="secondary"
              className="news-card-summary"
            >
              {news.summary_zh || news.summary}
            </Paragraph>
          )}

          {/* Metadata */}
          <Space split={<Text type="secondary">•</Text>} wrap>
            <Text type="secondary">{news.source}</Text>
            {news.author && <Text type="secondary">{news.author}</Text>}
            <Space size={4}>
              <ClockCircleOutlined />
              <Text type="secondary">{dayjs(news.published_at).fromNow()}</Text>
            </Space>
            {news.reading_time > 0 && (
              <Text type="secondary">{news.reading_time}分钟阅读</Text>
            )}
            {news.view_count > 0 && (
              <Space size={4}>
                <EyeOutlined />
                <Text type="secondary">{news.view_count}</Text>
              </Space>
            )}
          </Space>
        </Space>
      </Card>
    </Link>
  );
};

export default NewsCard;
