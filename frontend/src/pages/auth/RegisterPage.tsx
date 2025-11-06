import React, { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, message, Checkbox, Select } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { Helmet } from 'react-helmet-async'

import { useAuthStore } from '@/store/authStore'
import { RegisterData } from '@/types'
import { handleApiError } from '@/utils/errorHandling'

const { Title, Text } = Typography
const { Option } = Select

const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { register, isAuthenticated, isLoading, error, clearError } = useAuthStore()
  const [form] = Form.useForm()

  useEffect(() => {
    // Redirect if already authenticated
    if (isAuthenticated) {
      navigate('/', { replace: true })
    }

    // Clear any previous errors when component mounts
    clearError()
  }, [isAuthenticated, navigate, clearError])

  useEffect(() => {
    if (error) {
      message.error(error)
      clearError()
    }
  }, [error, clearError])

  const onFinish = async (values: RegisterData & { confirmPassword: string }) => {
    const { confirmPassword, ...registerData } = values

    try {
      await register(registerData)
      message.success('注册成功！')
      navigate('/', { replace: true })
    } catch (error) {
      handleApiError(error, '注册失败，请稍后重试')
    }
  }

  const prefixSelector = (
    <Form.Item name="prefix" noStyle>
      <Select style={{ width: 100 }} defaultValue="+86">
        <Option value="+86">+86</Option>
        <Option value="+1">+1</Option>
        <Option value="+44">+44</Option>
      </Select>
    </Form.Item>
  )

  return (
    <>
      <Helmet>
        <title>注册 - 新闻推荐系统</title>
        <meta name="description" content="注册新闻推荐系统账号，开启个性化新闻推荐体验" />
      </Helmet>

      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <Title level={2}>创建账户</Title>
            <Text type="secondary">加入我们，获取个性化新闻推荐</Text>
          </div>

          <Card className="shadow-lg">
            <Form
              form={form}
              name="register"
              onFinish={onFinish}
              layout="vertical"
              size="large"
              autoComplete="off"
              scrollToFirstError
            >
              <Form.Item
                label="用户名"
                name="username"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名至少3个字符' },
                  { max: 20, message: '用户名最多20个字符' },
                  { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' }
                ]}
              >
                <Input
                  prefix={<UserOutlined className="text-gray-400" />}
                  placeholder="请输入用户名"
                  autoComplete="username"
                />
              </Form.Item>

              <Form.Item
                label="邮箱地址"
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱地址' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input
                  prefix={<MailOutlined className="text-gray-400" />}
                  placeholder="请输入邮箱地址"
                  autoComplete="email"
                />
              </Form.Item>

              <Form.Item
                label="真实姓名"
                name="full_name"
                rules={[
                  { max: 50, message: '姓名最多50个字符' }
                ]}
              >
                <Input
                  placeholder="请输入真实姓名（可选）"
                  autoComplete="name"
                />
              </Form.Item>

              <Form.Item
                label="密码"
                name="password"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 8, message: '密码至少8个字符' },
                  {
                    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                    message: '密码必须包含大小写字母和数字'
                  }
                ]}
                hasFeedback
              >
                <Input.Password
                  prefix={<LockOutlined className="text-gray-400" />}
                  placeholder="请输入密码"
                  autoComplete="new-password"
                />
              </Form.Item>

              <Form.Item
                label="确认密码"
                name="confirmPassword"
                dependencies={['password']}
                rules={[
                  { required: true, message: '请确认密码' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve()
                      }
                      return Promise.reject(new Error('两次输入的密码不一致'))
                    },
                  }),
                ]}
                hasFeedback
              >
                <Input.Password
                  prefix={<LockOutlined className="text-gray-400" />}
                  placeholder="请再次输入密码"
                  autoComplete="new-password"
                />
              </Form.Item>

              <Form.Item
                name="agreement"
                valuePropName="checked"
                rules={[
                  {
                    validator: (_, value) =>
                      value ? Promise.resolve() : Promise.reject(new Error('请同意服务条款')),
                  },
                ]}
              >
                <Checkbox>
                  我已阅读并同意{' '}
                  <Link to="/terms" target="_blank" className="text-blue-600 hover:text-blue-500">
                    服务条款
                  </Link>{' '}
                  和{' '}
                  <Link to="/privacy" target="_blank" className="text-blue-600 hover:text-blue-500">
                    隐私政策
                  </Link>
                </Checkbox>
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isLoading}
                  block
                  className="h-12 text-base"
                >
                  {isLoading ? '注册中...' : '注册账户'}
                </Button>
              </Form.Item>
            </Form>

            <Divider>或</Divider>

            <div className="text-center">
              <Text type="secondary">
                已有账户？{' '}
                <Link to="/auth/login" className="text-blue-600 hover:text-blue-500">
                  立即登录
                </Link>
              </Text>
            </div>
          </Card>
        </div>
      </div>
    </>
  )
}

export default RegisterPage