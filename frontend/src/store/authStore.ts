import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import { User, AuthTokens, LoginCredentials, RegisterData } from '@/types'
import { authService } from '@/services/authService'

interface AuthState {
  // State
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isInitialized: boolean
  isLoading: boolean
  error: string | null

  // Actions
  initialize: () => Promise<void>
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      tokens: null,
      isAuthenticated: false,
      isInitialized: false,
      isLoading: false,
      error: null,

      // Initialize auth state from stored data
      initialize: async () => {
        const { tokens, isInitialized } = get()
        
        // Already initialized, skip
        if (isInitialized) {
          return
        }

        if (!tokens) {
          set({ isInitialized: true })
          return
        }

        try {
          set({ isLoading: true })

          // Verify current token and get user data
          const user = await authService.getCurrentUser()

          if (user) {
            set({
              user,
              isAuthenticated: true,
              error: null
            })
          } else {
            // Token invalid, clear auth state
            set({
              user: null,
              tokens: null,
              isAuthenticated: false
            })
          }
        } catch (error: any) {
          console.error('Auth initialization failed:', error)
          // If it's a 401 error, token is invalid, clear it silently
          if (error.response?.status === 401) {
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              error: null
            })
          } else {
            // Other errors, keep tokens but mark as not authenticated
            set({
              isAuthenticated: false,
              error: null // Don't show error on initialization failure
            })
          }
        } finally {
          set({ isLoading: false, isInitialized: true })
        }
      },

      // Login
      login: async (credentials) => {
        try {
          set({ isLoading: true, error: null })

          const tokens = await authService.login(credentials)
          const user = await authService.getCurrentUser()

          set({
            user,
            tokens,
            isAuthenticated: true,
            error: null
          })
        } catch (error: any) {
          const message = error.response?.data?.message || 'Login failed'
          set({
            error: message,
            isAuthenticated: false
          })
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      // Register
      register: async (data) => {
        try {
          set({ isLoading: true, error: null })

          await authService.register(data)

          // Auto-login after registration
          await get().login({
            email: data.email,
            password: data.password
          })
        } catch (error: any) {
          const message = error.response?.data?.message || 'Registration failed'
          set({ error: message })
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      // Logout
      logout: async () => {
        try {
          const { tokens } = get()
          if (tokens) {
            await authService.logout(tokens.refresh_token)
          }
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            error: null
          })
        }
      },

      // Refresh token
      refreshToken: async () => {
        try {
          const { tokens } = get()

          if (!tokens?.refresh_token) {
            throw new Error('No refresh token available')
          }

          const newTokens = await authService.refreshToken(tokens.refresh_token)

          set({
            tokens: newTokens,
            error: null
          })
        } catch (error) {
          console.error('Token refresh failed:', error)

          // Refresh failed, clear auth state
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            error: 'Session expired'
          })
        }
      },

      // Update profile
      updateProfile: async (data) => {
        try {
          set({ isLoading: true, error: null })

          const updatedUser = await authService.updateProfile(data)

          set({
            user: updatedUser,
            error: null
          })
        } catch (error: any) {
          const message = error.response?.data?.message || 'Profile update failed'
          set({ error: message })
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      // Clear error
      clearError: () => {
        set({ error: null })
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        tokens: state.tokens,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)