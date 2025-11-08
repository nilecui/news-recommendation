/**
 * Unified API client with interceptors and error handling
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { getAccessToken, getRefreshToken, storeTokens, clearStoredTokens } from '../utils/tokenStorage';
import { handleApiError } from '../utils/errorHandling';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          // Store new tokens
          storeTokens({
            access_token,
            refresh_token: newRefreshToken
          });

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        clearStoredTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle other errors
    handleApiError(error);
    return Promise.reject(error);
  }
);

// Helper functions for common patterns
export const get = <T>(url: string, params?: any): Promise<T> => {
  return apiClient.get(url, { params }).then((res) => res.data);
};

export const post = <T>(url: string, data?: any): Promise<T> => {
  return apiClient.post(url, data).then((res) => res.data);
};

export const put = <T>(url: string, data?: any): Promise<T> => {
  return apiClient.put(url, data).then((res) => res.data);
};

export const del = <T>(url: string): Promise<T> => {
  return apiClient.delete(url).then((res) => res.data);
};

export const patch = <T>(url: string, data?: any): Promise<T> => {
  return apiClient.patch(url, data).then((res) => res.data);
};

export default apiClient;
