import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Layout,
  Menu,
  Button,
  Avatar,
  Dropdown,
  Typography,
  Input,
  Space,
  Badge,
  Drawer
} from 'antd'
import {
  HomeOutlined,
  SearchOutlined,
  UserOutlined,
  BellOutlined,
  LogoutOutlined,
  SettingOutlined,
  FireOutlined,
  CompassOutlined,
  StarOutlined,
  HistoryOutlined,
  HeartOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons'

import { useAuthStore } from '@/store/authStore'
import './MainLayout.css'

const { Header, Sider, Content } = Layout
const { Title } = Typography
const { Search } = Input

const MainLayout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileDrawerVisible, setMobileDrawerVisible] = useState(false)

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/auth/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile')
    },
    {
      key: 'history',
      icon: <HistoryOutlined />,
      label: '浏览历史',
      onClick: () => navigate('/profile/history')
    },
    {
      key: 'collections',
      icon: <HeartOutlined />,
      label: '我的收藏',
      onClick: () => navigate('/profile/collections')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/profile/settings')
    },
    {
      type: 'divider' as const
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
      danger: true
    }
  ]

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '推荐',
      title: '推荐'
    },
    {
      key: '/trending',
      icon: <FireOutlined />,
      label: '热门',
      title: '热门'
    },
    {
      key: '/discover',
      icon: <CompassOutlined />,
      label: '发现',
      title: '发现'
    },
    {
      key: '/favorites',
      icon: <StarOutlined />,
      label: '收藏',
      title: '收藏'
    }
  ]

  const handleSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/search?q=${encodeURIComponent(value.trim())}`)
    }
  }

  // Sidebar Menu Component
  const SidebarMenu = () => (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={({ key }) => {
        navigate(key)
        setMobileDrawerVisible(false)
      }}
      className="sidebar-menu"
    />
  )

  return (
    <Layout className="main-layout">
      {/* Desktop Sidebar */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        className="main-sider"
        width={220}
        collapsedWidth={80}
        breakpoint="lg"
        onBreakpoint={(broken) => {
          if (broken) {
            setCollapsed(true)
          }
        }}
      >
        {/* Logo */}
        <div className="sider-logo" onClick={() => navigate('/')}>
          <div className="logo-icon gradient-bg">
            <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
              <path d="M20 5L25 15H35L27 22L30 32L20 26L10 32L13 22L5 15H15L20 5Z" fill="white"/>
            </svg>
          </div>
          {!collapsed && (
            <Title level={5} className="logo-text">
              新闻推荐
            </Title>
          )}
        </div>

        <SidebarMenu />

        {/* User Info in Sidebar */}
        {!collapsed && (
          <div className="sider-user">
            <Avatar src={user?.avatar_url} icon={<UserOutlined />} size={40} />
            <div className="user-info">
              <div className="user-name">{user?.full_name || user?.username || '用户'}</div>
              <div className="user-email">{user?.email}</div>
            </div>
          </div>
        )}
      </Sider>

      {/* Mobile Drawer */}
      <Drawer
        placement="left"
        onClose={() => setMobileDrawerVisible(false)}
        open={mobileDrawerVisible}
        className="mobile-drawer"
        width={280}
        styles={{ body: { padding: 0 } }}
      >
        <div className="drawer-logo">
          <div className="logo-icon gradient-bg">
            <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
              <path d="M20 5L25 15H35L27 22L30 32L20 26L10 32L13 22L5 15H15L20 5Z" fill="white"/>
            </svg>
          </div>
          <Title level={5} className="logo-text">新闻推荐</Title>
        </div>
        <SidebarMenu />
      </Drawer>

      <Layout className="main-content-layout">
        {/* Header */}
        <Header className="main-header">
          <div className="header-left">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="trigger-btn hidden-mobile"
            />
            <Button
              type="text"
              icon={<MenuUnfoldOutlined />}
              onClick={() => setMobileDrawerVisible(true)}
              className="trigger-btn hidden-desktop"
            />

            <div className="header-search">
              <Search
                placeholder="搜索感兴趣的新闻..."
                allowClear
                enterButton={<SearchOutlined />}
                size="large"
                onSearch={handleSearch}
              />
            </div>
          </div>

          <Space size="large" className="header-right">
            <Badge count={0} showZero={false} dot>
              <Button
                type="text"
                icon={<BellOutlined style={{ fontSize: 20 }} />}
                className="icon-btn"
              />
            </Badge>

            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              trigger={['click']}
              arrow
            >
              <div className="user-dropdown">
                <Avatar
                  src={user?.avatar_url}
                  icon={<UserOutlined />}
                  size={36}
                />
                <span className="user-name-text">
                  {user?.full_name || user?.username || '用户'}
                </span>
              </div>
            </Dropdown>
          </Space>
        </Header>

        {/* Content */}
        <Content className="main-content">
          <div className="content-wrapper">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
