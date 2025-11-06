import React from 'react'
import { useSearchParams } from 'react-router-dom'
import { Typography, Card } from 'antd'
import { Helmet } from 'react-helmet-async'

const { Title } = Typography

const SearchPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''

  return (
    <>
      <Helmet>
        <title>搜索结果 - 新闻推荐系统</title>
        <meta name="description" content="搜索结果页面" />
      </Helmet>

      <div className="space-y-6">
        <div>
          <Title level={2}>搜索结果</Title>
          <p>关键词: {query}</p>
        </div>

        <Card>
          <p>搜索结果将在这里显示...</p>
        </Card>
      </div>
    </>
  )
}

export default SearchPage