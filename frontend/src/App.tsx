import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'

import { useAuthStore } from '@/store/authStore'
import MainLayout from '@/components/layout/MainLayout'
import AuthLayout from '@/components/layout/AuthLayout'

// Pages
import HomePage from '@/pages/home/HomePage'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import NewsDetailPage from '@/pages/news/NewsDetailPage'
import ProfilePage from '@/pages/profile/ProfilePage'
import SearchPage from '@/pages/news/SearchPage'
import CategoryPage from '@/pages/news/CategoryPage'
import TrendingPage from '@/pages/trending/TrendingPage'
import DiscoverPage from '@/pages/discover/DiscoverPage'
import FavoritesPage from '@/pages/favorites/FavoritesPage'
import HistoryPage from '@/pages/profile/HistoryPage'
import CollectionsPage from '@/pages/profile/CollectionsPage'
import SettingsPage from '@/pages/profile/SettingsPage'

// Components
import ProtectedRoute from '@/components/common/ProtectedRoute'
import LoadingScreen from '@/components/common/LoadingScreen'

const App: React.FC = () => {
  const { isAuthenticated, isInitialized } = useAuthStore()

  // Show loading screen while auth is being initialized
  if (!isInitialized) {
    return <LoadingScreen />
  }

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 8,
        },
      }}
    >
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route
            path="/auth/*"
            element={
              isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <AuthLayout />
              )
            }
          >
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
          </Route>

          {/* Protected routes */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<HomePage />} />
            <Route path="news/:id" element={<NewsDetailPage />} />
            <Route path="category/:category" element={<CategoryPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="trending" element={<TrendingPage />} />
            <Route path="discover" element={<DiscoverPage />} />
            <Route path="favorites" element={<FavoritesPage />} />
            <Route path="profile/*" element={<ProfilePage />}>
              <Route path="history" element={<HistoryPage />} />
              <Route path="collections" element={<CollectionsPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Route>

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </ConfigProvider>
  )
}

export default App