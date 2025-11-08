import React, { useState, useEffect } from 'react'
import { Typography, Card, Row, Col, Tabs, Button, Space, Spin, Empty, Tag, Alert } from 'antd'
import { ReloadOutlined, FireOutlined, StarOutlined, ClockCircleOutlined, RocketOutlined } from '@ant-design/icons'
import { Helmet } from 'react-helmet-async'
import { useNavigate } from 'react-router-dom'
import InfiniteScroll from 'react-infinite-scroll-component'

import { NewsCard } from '@/components/news/NewsCard'
import { recommendationService, type RecommendationResponse } from '@/services/recommendationService'
import { newsService } from '@/services/newsService'
import type { News } from '@/types'
import './HomePage.css'

const { Title, Text, Paragraph } = Typography

const HomePage: React.FC = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('recommend')
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null)
  const [featuredNews, setFeaturedNews] = useState<News[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  // Load initial data
  useEffect(() => {
    loadInitialData()
  }, [activeTab])

  const loadInitialData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Load recommendations based on active tab
      let data: RecommendationResponse

      if (activeTab === 'recommend') {
        data = await recommendationService.getPersonalizedRecommendations({ page: 1, page_size: 20 })
      } else if (activeTab === 'popular') {
        data = await recommendationService.getPopularNews({ timeframe: '24h', page: 1, page_size: 20 })
      } else {
        data = await recommendationService.getDiscoveryRecommendations(20)
      }

      setRecommendations(data)
      setPage(1)

      // Load featured news for hero section (only on first load)
      if (featuredNews.length === 0) {
        try {
          const trending = await newsService.getTrendingNews({ timeframe: 'day', limit: 3 })
          setFeaturedNews(trending)
        } catch (err) {
          console.error('Failed to load featured news:', err)
          // Continue even if featured news fails
        }
      }
    } catch (error: any) {
      console.error('Failed to load data:', error)
      setError(error?.message || '加载数据失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const loadMore = async () => {
    if (!recommendations?.has_next) return

    try {
      const nextPage = page + 1
      let data: RecommendationResponse

      if (activeTab === 'recommend') {
        data = await recommendationService.getPersonalizedRecommendations({ page: nextPage, page_size: 20 })
      } else if (activeTab === 'popular') {
        data = await recommendationService.getPopularNews({ timeframe: '24h', page: nextPage, page_size: 20 })
      } else {
        data = await recommendationService.getDiscoveryRecommendations(20)
      }

      setRecommendations(prev => ({
        ...data,
        items: [...(prev?.items || []), ...data.items]
      }))
      setPage(nextPage)
    } catch (error) {
      console.error('Failed to load more:', error)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadInitialData()
    setRefreshing(false)
  }

  const tabItems = [
    {
      key: 'recommend',
      label: (
        <Space>
          <StarOutlined />
          <span>为您推荐</span>
        </Space>
      ),
    },
    {
      key: 'popular',
      label: (
        <Space>
          <FireOutlined />
          <span>热门</span>
        </Space>
      ),
    },
    {
      key: 'discover',
      label: (
        <Space>
          <ClockCircleOutlined />
          <span>发现</span>
        </Space>
      ),
    },
  ]

  // Empty State Component
  const EmptyState = () => (
    <div className="empty-state-container">
      <Empty
        image={<RocketOutlined style={{ fontSize: 80, color: '#1890ff' }} />}
        imageStyle={{ height: 120 }}
        description={
          <Space direction="vertical" size="small">
            <Title level={4}>暂无内容</Title>
            <Paragraph type="secondary">
              {activeTab === 'recommend' && '系统正在学习您的偏好，稍后将为您推荐精彩内容'}
              {activeTab === 'popular' && '暂时没有热门新闻，请稍后再来'}
              {activeTab === 'discover' && '暂时没有新内容，请稍后再来'}
            </Paragraph>
          </Space>
        }
      >
        <Button type="primary" onClick={handleRefresh} loading={refreshing}>
          刷新试试
        </Button>
      </Empty>
    </div>
  )

  // Error State Component
  const ErrorState = () => (
    <div className="error-state-container">
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" danger onClick={handleRefresh} loading={refreshing}>
            重试
          </Button>
        }
      />
    </div>
  )

  return (
    <>
      <Helmet>
        <title>首页 - 新闻推荐系统</title>
        <meta name="description" content="为您推荐个性化的新闻内容" />
      </Helmet>

      <div className="home-page">
        {/* Hero Section with Featured News */}
        {featuredNews.length > 0 && (
          <div className="hero-section fade-in-scale">
            <Card className="hero-card glass-effect" bordered={false}>
              <Row gutter={[24, 24]}>
                <Col xs={24} lg={14}>
                  <div className="hero-main" onClick={() => navigate(`/news/${featuredNews[0]?.id}`)}>
                    {featuredNews[0]?.image_url ? (
                      <div className="hero-image">
                        <img src={featuredNews[0].image_url} alt={featuredNews[0].title} />
                        <div className="hero-overlay">
                          <Tag color="red" className="featured-tag">
                            <FireOutlined /> 今日头条
                          </Tag>
                        </div>
                      </div>
                    ) : (
                      <div className="hero-image-placeholder">
                        <FireOutlined style={{ fontSize: 48, color: '#fff' }} />
                      </div>
                    )}
                    <div className="hero-content">
                      <Title level={2} className="hero-title">
                        {featuredNews[0]?.title_zh || featuredNews[0]?.title}
                      </Title>
                      <Paragraph className="hero-description" ellipsis={{ rows: 2 }}>
                        {featuredNews[0]?.summary_zh || featuredNews[0]?.summary}
                      </Paragraph>
                      <Space>
                        <Text type="secondary">{featuredNews[0]?.source}</Text>
                        <Text type="secondary">•</Text>
                        <Text type="secondary">{featuredNews[0]?.view_count || 0} 阅读</Text>
                      </Space>
                    </div>
                  </div>
                </Col>

                <Col xs={24} lg={10}>
                  <div className="hero-sidebar">
                    <Title level={4} className="sidebar-title">
                      <FireOutlined /> 热门推荐
                    </Title>
                    <Space direction="vertical" size="middle" className="w-full">
                      {featuredNews.slice(1, 3).map((news, index) => (
                        <Card
                          key={news.id}
                          className="sidebar-card hover-lift"
                          size="small"
                          hoverable
                          onClick={() => navigate(`/news/${news.id}`)}
                        >
                          <Space align="start">
                            <div className="sidebar-number gradient-bg">
                              {index + 2}
                            </div>
                            <div className="sidebar-content">
                              <Title level={5} ellipsis={{ rows: 2 }} className="sidebar-news-title">
                                {news.title_zh || news.title}
                              </Title>
                              <Text type="secondary" className="text-xs">
                                {news.source} · {news.view_count || 0} 阅读
                              </Text>
                            </div>
                          </Space>
                        </Card>
                      ))}
                    </Space>
                  </div>
                </Col>
              </Row>
            </Card>
          </div>
        )}

        {/* Main Content Section */}
        <div className="content-section slide-in-up">
          <Card className="content-card" bordered={false}>
            <div className="content-header">
              <Tabs
                activeKey={activeTab}
                items={tabItems}
                onChange={setActiveTab}
                size="large"
                className="content-tabs"
              />
              <Button
                icon={<ReloadOutlined spin={refreshing} />}
                onClick={handleRefresh}
                loading={refreshing}
                type="text"
              >
                刷新
              </Button>
            </div>

            {/* Loading State */}
            {loading ? (
              <div className="loading-container">
                <Spin size="large" tip="加载中..." />
              </div>
            ) : error ? (
              /* Error State */
              <ErrorState />
            ) : recommendations && recommendations.items.length > 0 ? (
              /* Content with Data */
              <InfiniteScroll
                dataLength={recommendations.items.length}
                next={loadMore}
                hasMore={recommendations.has_next}
                loader={
                  <div className="loading-container">
                    <Spin />
                  </div>
                }
                endMessage={
                  <div className="end-message">
                    <Text type="secondary">没有更多内容了</Text>
                  </div>
                }
              >
                <Row gutter={[16, 16]}>
                  {recommendations.items.map((item, index) => (
                    <Col xs={24} sm={12} lg={8} xl={6} key={`${item.id}-${index}`}>
                      <div className="news-card-wrapper fade-in">
                        <NewsCard
                          news={item}
                          position={item.position}
                          page={recommendations.page}
                          recommendationId={recommendations.recommendation_id}
                          layout="vertical"
                          showActions={true}
                          showImage={true}
                        />
                      </div>
                    </Col>
                  ))}
                </Row>
              </InfiniteScroll>
            ) : (
              /* Empty State */
              <EmptyState />
            )}
          </Card>
        </div>
      </div>
    </>
  )
}

export default HomePage
