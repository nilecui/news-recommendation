#!/usr/bin/env python3
"""
实际服务接口测试脚本
测试运行在 http://192.168.12.225:8311 的服务
"""
import requests
import json
from typing import Optional

BASE_URL = "http://192.168.12.225:8311"
API_V1 = f"{BASE_URL}/api/v1"

class APITester:
    def __init__(self):
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def get_headers(self, auth: bool = False) -> dict:
        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_health_check(self):
        """测试健康检查"""
        print("\n=== 测试健康检查 ===")
        response = self.session.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    
    def test_root(self):
        """测试根路径"""
        print("\n=== 测试根路径 ===")
        response = self.session.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    
    def test_register(self, email: str, username: str, password: str, full_name: str):
        """测试用户注册"""
        print(f"\n=== 测试用户注册: {email} ===")
        data = {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name
        }
        response = self.session.post(
            f"{API_V1}/auth/register",
            json=data,
            headers=self.get_headers()
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 201:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_login(self, username: str, password: str):
        """测试用户登录"""
        print(f"\n=== 测试用户登录: {username} ===")
        data = {
            "username": username,
            "password": password
        }
        response = self.session.post(
            f"{API_V1}/auth/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            self.token = result.get("access_token")
            print(f"登录成功，获取到 token: {self.token[:50]}...")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_get_current_user(self):
        """测试获取当前用户信息"""
        print("\n=== 测试获取当前用户信息 ===")
        response = self.session.get(
            f"{API_V1}/users/me",
            headers=self.get_headers(auth=True)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_update_user(self, **kwargs):
        """测试更新用户信息"""
        print("\n=== 测试更新用户信息 ===")
        response = self.session.put(
            f"{API_V1}/users/me",
            json=kwargs,
            headers=self.get_headers(auth=True)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_get_user_profile(self):
        """测试获取用户资料"""
        print("\n=== 测试获取用户资料 ===")
        response = self.session.get(
            f"{API_V1}/users/me/profile",
            headers=self.get_headers(auth=True)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_get_latest_news(self):
        """测试获取最新新闻"""
        print("\n=== 测试获取最新新闻 ===")
        response = self.session.get(
            f"{API_V1}/news/latest",
            headers=self.get_headers(auth=True)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应类型: {type(result)}")
            if isinstance(result, dict):
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print(f"响应: {result}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_get_trending_news(self):
        """测试获取热门新闻"""
        print("\n=== 测试获取热门新闻 ===")
        response = self.session.get(
            f"{API_V1}/news/trending",
            headers=self.get_headers(auth=True)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应类型: {type(result)}")
            if isinstance(result, dict):
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print(f"响应: {result}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_get_recommendations(self):
        """测试获取推荐"""
        print("\n=== 测试获取推荐 ===")
        response = self.session.get(
            f"{API_V1}/recommendations/",
            headers=self.get_headers(auth=True)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def test_get_tracking_stats(self):
        """测试获取追踪统计"""
        print("\n=== 测试获取追踪统计 ===")
        response = self.session.get(
            f"{API_V1}/tracking/stats",
            headers=self.get_headers(auth=True)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("开始测试 API 接口")
        print("=" * 60)
        
        results = []
        
        # 基础端点测试
        results.append(("健康检查", self.test_health_check()))
        results.append(("根路径", self.test_root()))
        
        # 认证测试
        test_email = "apitest@example.com"
        test_username = "apitest"
        test_password = "Test123456"
        
        # 先尝试注册（可能已存在）
        self.test_register(test_email, test_username, test_password, "API Test User")
        
        # 登录
        if self.test_login(test_email, test_password):
            results.append(("用户登录", True))
            
            # 需要认证的接口
            results.append(("获取当前用户", self.test_get_current_user()))
            results.append(("更新用户信息", self.test_update_user(
                full_name="Updated API Test User",
                bio="API Test Bio"
            )))
            results.append(("获取用户资料", self.test_get_user_profile()))
            results.append(("获取最新新闻", self.test_get_latest_news()))
            results.append(("获取热门新闻", self.test_get_trending_news()))
            results.append(("获取推荐", self.test_get_recommendations()))
            results.append(("获取追踪统计", self.test_get_tracking_stats()))
        else:
            results.append(("用户登录", False))
        
        # 打印总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)
        passed = sum(1 for _, result in results if result)
        total = len(results)
        for name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{name}: {status}")
        print(f"\n总计: {passed}/{total} 通过")
        print("=" * 60)

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()

