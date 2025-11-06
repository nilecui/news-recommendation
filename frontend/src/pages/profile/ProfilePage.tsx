import React from 'react'
import { Outlet } from 'react-router-dom'
import { Typography } from 'antd'

const { Title } = Typography

const ProfilePage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <Title level={2}>个人中心</Title>
      <Outlet />
    </div>
  )
}

export default ProfilePage