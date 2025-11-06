import { AuthTokens } from '@/types'

const TOKEN_STORAGE_KEY = 'auth_tokens'

export const getStoredTokens = (): AuthTokens | null => {
  try {
    const stored = localStorage.getItem(TOKEN_STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  } catch (error) {
    console.error('Error reading tokens from storage:', error)
    return null
  }
}

export const storeTokens = (tokens: AuthTokens): void => {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens))
  } catch (error) {
    console.error('Error storing tokens:', error)
  }
}

export const clearStoredTokens = (): void => {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  } catch (error) {
    console.error('Error clearing tokens:', error)
  }
}

export const getAccessToken = (): string | null => {
  const tokens = getStoredTokens()
  return tokens?.access_token || null
}

export const getRefreshToken = (): string | null => {
  const tokens = getStoredTokens()
  return tokens?.refresh_token || null
}

export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000 // Convert to milliseconds
    return Date.now() >= exp
  } catch (error) {
    return true // If we can't parse the token, assume it's expired
  }
}

export const isAccessTokenExpired = (): boolean => {
  const token = getAccessToken()
  return token ? isTokenExpired(token) : true
}