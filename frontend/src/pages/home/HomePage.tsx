import React from 'react'
import { Typography, Card, Row, Col, Space } from 'antd'
import { Helmet } from 'react-helmet-async'

const { Title, Text } = Typography

const HomePage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>首页 - 新闻推荐系统</title>
        <meta name="description" content="为您推荐个性化的新闻内容" />
      </Helmet>

      <div className="space-y-6">
        <div>
          <Title level={2}>为您推荐</Title>
          <Text type="secondary">基于您的阅读历史和兴趣偏好</Text>
        </div>

        <Row gutter={[16, 16]}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Col xs={24} sm={12} lg={8} xl={6} key={i}>
              <Card
                hoverable
                cover={
                  <div className="h-48 bg-gray-200 flex items-center justify-center">
                    <Text type="secondary">新闻图片 {i}</Text>
                  </div>
                }
                className="h-full"
              >
                <Card.Meta
                  title={`新闻标题 ${i}`}
                  description={
                    <Space direction="vertical" size="small">
                      <Text type="secondary" className="text-truncate-2">
                        这是一段新闻摘要内容，描述了新闻的主要内容和要点...
                      </Text>
                      <Text type="secondary" className="text-xs">
                        科技频道 · 2小时前
                      </Text>
                    </Space>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    </>
  )
}

export default HomePage