import React from 'react'
import { useParams } from 'react-router-dom'
import { Typography, Card } from 'antd'
import { Helmet } from 'react-helmet-async'

const { Title } = Typography

const NewsDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  return (
    <>
      <Helmet>
        <title>新闻详情 - 新闻推荐系统</title>
        <meta name="description" content="新闻详情页面" />
      </Helmet>

      <div className="max-w-4xl mx-auto">
        <Card>
          <Title level={2}>新闻详情页面</Title>
          <p>新闻ID: {id}</p>
          <p>这里将显示完整的新闻内容...</p>
        </Card>
      </div>
    </>
  )
}

export default NewsDetailPage