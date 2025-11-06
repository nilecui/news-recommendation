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
  Badge
} from 'antd'
import {
  HomeOutlined,
  SearchOutlined,
  UserOutlined,
  BellOutlined,
  LogoutOutlined,
  SettingOutlined,
  BookOutlined,
  TagsOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons'

import { useAuthStore } from '@/store/authStore'

const { Header, Sider, Content } = Layout
const { Title } = Typography
const { Search } = Input

const MainLayout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)

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
      label: '个人资料',
      onClick: () => navigate('/profile')
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
      onClick: handleLogout
    }
  ]

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页推荐'
    },
    {
      key: '/trending',
      icon: <TagsOutlined />,
      label: '热门新闻'
    },
    {
      key: '/categories',
      icon: <BookOutlined />,
      label: '新闻分类',
      children: [
        {
          key: '/category/technology',
          label: '科技'
        },
        {
          key: '/category/business',
          label: '商业'
        },
        {
          key: '/category/sports',
          label: '体育'
        },
        {
          key: '/category/entertainment',
          label: '娱乐'
        }
      ]
    }
  ]

  const handleSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/search?q=${encodeURIComponent(value.trim())}`)
    }
  }

  return (
    <Layout className="min-h-screen">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        className="bg-white shadow-md"
        width={200}
      >
        <div className="p-4">
          <Title level={4} className="!mb-0 text-center">
            {collapsed ? '新闻' : '新闻推荐'}
          </Title>
        </div>

        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          className="border-r-0"
        />
      </Sider>

      <Layout>
        <Header className="bg-white shadow-sm px-6 flex items-center justify-between">
          <div className="flex items-center flex-1">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="mr-4"
            />

            <div className="max-w-md flex-1">
              <Search
                placeholder="搜索新闻..."
                allowClear
                enterButton={<SearchOutlined />}
                size="middle"
                onSearch={handleSearch}
                className="w-full"
              />
            </div>
          </div>

          <Space size="middle">
            <Badge count={0} showZero={false}>
              <Button type="text" icon={<BellOutlined />} size="large" />
            </Badge>

            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              trigger={['click']}
            >
              <div className="flex items-center cursor-pointer hover:bg-gray-50 rounded-lg px-3 py-2">
                <Avatar
                  size="small"
                  src={user?.avatar_url}
                  icon={<UserOutlined />}
                  className="mr-2"
                />
                <span className="hidden sm:inline">
                  {user?.full_name || user?.username}
                </span>
              </div>
            </Dropdown>
          </Space>
        </Header>

        <Content className="bg-gray-50">
          <div className="p-6">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout