import React from 'react'
import { useParams } from 'react-router-dom'
import { Typography, Card } from 'antd'
import { Helmet } from 'react-helmet-async'

const { Title } = Typography

const CategoryPage: React.FC = () => {
  const { category } = useParams<{ category: string }>()

  return (
    <>
      <Helmet>
        <title>{category} - 新闻推荐系统</title>
        <meta name="description" content={`${category}分类新闻`} />
      </Helmet>

      <div className="space-y-6">
        <div>
          <Title level={2}>{category}</Title>
          <p>该分类下的新闻内容</p>
        </div>

        <Card>
          <p>分类新闻将在这里显示...</p>
        </Card>
      </div>
    </>
  )
}

export default CategoryPage