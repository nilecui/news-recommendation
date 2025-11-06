import React, { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Spin } from 'antd'

import { useAuthStore } from '@/store/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode
  redirectTo?: string
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/auth/login'
}) => {
  const location = useLocation()
  const { isAuthenticated, isInitialized, initialize } = useAuthStore()

  useEffect(() => {
    // Initialize auth if not already done
    if (!isInitialized) {
      initialize()
    }
  }, [isInitialized, initialize])

  // Show loading spinner while initializing
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save the current location to redirect back after login
    const returnTo = location.pathname + location.search + location.hash
    const loginUrl = `${redirectTo}${returnTo !== '/' ? `?returnTo=${encodeURIComponent(returnTo)}` : ''}`
    return <Navigate to={loginUrl} replace state={{ from: location }} />
  }

  // Render children if authenticated
  return <>{children}</>
}

export default ProtectedRoute