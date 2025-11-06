import { message } from 'antd'

export const handleApiError = (error: any, defaultMessage: string = '操作失败') => {
  console.error('API Error:', error)

  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const { status, data } = error.response

    switch (status) {
      case 400:
        message.error(data.message || '请求参数错误')
        break
      case 401:
        message.error('请重新登录')
        // Redirect to login page after a delay
        setTimeout(() => {
          window.location.href = '/auth/login'
        }, 1000)
        break
      case 403:
        message.error('权限不足')
        break
      case 404:
        message.error('请求的资源不存在')
        break
      case 429:
        message.error('请求过于频繁，请稍后再试')
        break
      case 500:
        message.error('服务器内部错误')
        break
      default:
        message.error(data.message || defaultMessage)
    }
  } else if (error.request) {
    // The request was made but no response was received
    message.error('网络连接失败，请检查网络设置')
  } else {
    // Something happened in setting up the request that triggered an Error
    message.error(error.message || defaultMessage)
  }
}

export const handleNetworkError = (error: any) => {
  console.error('Network Error:', error)

  if (error.code === 'NETWORK_ERROR') {
    message.error('网络连接失败，请检查网络设置')
  } else if (error.code === 'TIMEOUT') {
    message.error('请求超时，请稍后重试')
  } else {
    message.error('网络错误，请稍后重试')
  }
}

export const handleValidationError = (errors: any) => {
  Object.keys(errors).forEach(key => {
    const errorMessages = errors[key].map((error: any) => error.message)
    message.error(`${key}: ${errorMessages.join(', ')}`)
  })
}