import React from 'react'
import { Spin } from 'antd'

const LoadingScreen: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <Spin size="large" />
        <div className="mt-4 text-gray-600">加载中...</div>
      </div>
    </div>
  )
}

export default LoadingScreen