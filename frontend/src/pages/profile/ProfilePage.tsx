import React from 'react'
import { Outlet, useNavigate, useLocation, Navigate } from 'react-router-dom'
import { Menu, Card, Typography } from 'antd'
import {
  UserOutlined,
  HistoryOutlined,
  HeartOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import './ProfilePage.css'

const { Title } = Typography

const ProfilePage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/profile/history',
      icon: <HistoryOutlined />,
      label: '浏览历史',
    },
    {
      key: '/profile/collections',
      icon: <HeartOutlined />,
      label: '我的收藏',
    },
    {
      key: '/profile/settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  // Default redirect to history page
  if (location.pathname === '/profile' || location.pathname === '/profile/') {
    return <Navigate to="/profile/history" replace />
  }

  return (
    <div className="profile-page">
      <div className="profile-header">
        <Card className="header-card" bordered={false}>
          <Title level={2} style={{ margin: 0 }}>
            <UserOutlined style={{ marginRight: 8 }} />
            个人中心
          </Title>
        </Card>
      </div>

      <div className="profile-content">
        <div className="profile-sidebar">
          <Card className="sidebar-card" bordered={false}>
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              items={menuItems}
              onClick={handleMenuClick}
              className="profile-menu"
            />
          </Card>
        </div>

        <div className="profile-main">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default ProfilePage