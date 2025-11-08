import axios, { AxiosInstance, AxiosResponse } from 'axios'

import { User, AuthTokens, LoginCredentials, RegisterData } from '@/types'
import { getStoredTokens, storeTokens, clearStoredTokens } from '@/utils/tokenStorage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

class AuthService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const tokens = getStoredTokens()
        if (tokens?.access_token) {
          config.headers.Authorization = `Bearer ${tokens.access_token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const tokens = getStoredTokens()
            if (tokens?.refresh_token) {
              const response = await this.refreshToken(tokens.refresh_token)
              storeTokens(response)

              // Retry the original request
              originalRequest.headers.Authorization = `Bearer ${response.access_token}`
              return this.api(originalRequest)
            }
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            clearStoredTokens()
            window.location.href = '/auth/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Login
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const formData = new FormData()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)

    const response: AxiosResponse<AuthTokens> = await this.api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    const tokens = response.data
    storeTokens(tokens)
    return tokens
  }

  // Register
  async register(data: RegisterData): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/auth/register', data)
    return response.data
  }

  // Logout
  async logout(refreshToken: string): Promise<void> {
    try {
      await this.api.post('/auth/logout', { refresh_token: refreshToken })
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      clearStoredTokens()
    }
  }

  // Refresh token
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post('/auth/refresh', {
      refresh_token: refreshToken,
    })

    return response.data
  }

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/users/me')
    return response.data
  }

  // Update user profile
  async updateProfile(data: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.api.put('/users/me', data)
    return response.data
  }

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.api.post('/users/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  // Request password reset
  async requestPasswordReset(email: string): Promise<void> {
    await this.api.post('/auth/password-reset', { email })
  }

  // Confirm password reset
  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    await this.api.post('/auth/password-reset/confirm', {
      token,
      new_password: newPassword,
    })
  }

  // Verify email
  async verifyEmail(token: string): Promise<void> {
    await this.api.post('/auth/verify-email', { token })
  }

  // Resend verification email
  async resendVerificationEmail(): Promise<void> {
    await this.api.post('/auth/resend-verification')
  }
}

export const authService = new AuthService()