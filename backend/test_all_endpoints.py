#!/usr/bin/env python3
"""
完整 API 接口测试脚本 - 测试所有端点
"""
import requests
import json
from typing import Optional, List

BASE_URL = "http://192.168.12.225:8311"
API_V1 = f"{BASE_URL}/api/v1"

class FullAPITester:
    def __init__(self):
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.results = []
    
    def get_headers(self, auth: bool = False) -> dict:
        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_endpoint(self, method: str, path: str, name: str, auth: bool = False, 
                     json_data: dict = None, params: dict = None, data: dict = None):
        """测试单个端点"""
        url = f"{BASE_URL}{path}" if path.startswith("/") else f"{API_V1}{path}"
        headers = self.get_headers(auth=auth)
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method == "POST":
                if json_data:
                    response = self.session.post(url, headers=headers, json=json_data)
                elif data:
                    response = self.session.post(url, headers=headers, data=data)
                else:
                    response = self.session.post(url, headers=headers)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=json_data)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                return False
            
            success = response.status_code < 400
            self.results.append({
                "name": name,
                "method": method,
                "path": path,
                "status": response.status_code,
                "success": success
            })
            
            if not success:
                print(f"❌ {name}: {response.status_code} - {response.text[:200]}")
            else:
                print(f"✅ {name}: {response.status_code}")
            
            return success
        except Exception as e:
            print(f"❌ {name}: Exception - {str(e)}")
            self.results.append({
                "name": name,
                "method": method,
                "path": path,
                "status": 0,
                "success": False,
                "error": str(e)
            })
            return False
    
    def login(self):
        """登录获取 token"""
        response = self.session.post(
            f"{API_V1}/auth/login",
            data={"username": "cwt@gmai.com", "password": "Admin123456"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            try:
                self.token = response.json().get("access_token")
                return True
            except:
                return False
        return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("开始完整 API 接口测试")
        print("=" * 70)
        
        # 基础端点
        print("\n【基础端点】")
        self.test_endpoint("GET", "/health", "健康检查")
        self.test_endpoint("GET", "/", "根路径")
        
        # 认证端点
        print("\n【认证端点】")
        self.test_endpoint("POST", "/api/v1/auth/register", "用户注册", 
                          json_data={"email": "test2@example.com", "username": "test2", 
                                   "password": "Test123456", "full_name": "Test User 2"})
        self.test_endpoint("POST", "/api/v1/auth/login", "用户登录",
                          data={"username": "cwt@gmai.com", "password": "Admin123456"})
        
        # 登录获取 token
        if not self.login():
            print("⚠️  登录失败，跳过需要认证的接口")
            return
        
        # 用户端点
        print("\n【用户端点】")
        self.test_endpoint("GET", "/api/v1/users/me", "获取当前用户", auth=True)
        self.test_endpoint("PUT", "/api/v1/users/me", "更新用户信息", auth=True,
                          json_data={"full_name": "Updated Name"})
        self.test_endpoint("GET", "/api/v1/users/me/profile", "获取用户资料", auth=True)
        self.test_endpoint("PUT", "/api/v1/users/me/profile", "更新用户资料", auth=True,
                          json_data={"preferred_language": "en"})
        self.test_endpoint("GET", "/api/v1/users/me/history", "获取阅读历史", auth=True, params={"page": 1, "limit": 20})
        self.test_endpoint("GET", "/api/v1/users/me/collections", "获取收藏", auth=True, params={"page": 1, "limit": 20})
        
        # 新闻端点
        print("\n【新闻端点】")
        self.test_endpoint("GET", "/api/v1/news/latest", "获取最新新闻", auth=True, params={"page": 1, "limit": 20})
        self.test_endpoint("GET", "/api/v1/news/trending", "获取热门新闻", auth=True, params={"timeframe": "day"})
        self.test_endpoint("GET", "/api/v1/news/category/technology", "按分类获取新闻", auth=True, params={"page": 1, "limit": 20})
        self.test_endpoint("POST", "/api/v1/news/search", "搜索新闻", auth=True,
                          json_data={"query": "test", "page": 1, "page_size": 20})
        
        # 需要先有新闻数据才能测试这些
        # self.test_endpoint("GET", "/api/v1/news/1", "获取新闻详情", auth=True)
        # self.test_endpoint("POST", "/api/v1/news/1/like", "点赞新闻", auth=True)
        # self.test_endpoint("POST", "/api/v1/news/1/collect", "收藏新闻", auth=True)
        # self.test_endpoint("POST", "/api/v1/news/1/share", "分享新闻", auth=True, params={"platform": "wechat"})
        
        # 推荐端点
        print("\n【推荐端点】")
        self.test_endpoint("GET", "/api/v1/recommendations/", "获取推荐", auth=True, params={"page": 1, "limit": 20})
        self.test_endpoint("GET", "/api/v1/recommendations/cold-start", "冷启动推荐", auth=True, params={"limit": 20})
        self.test_endpoint("GET", "/api/v1/recommendations/discovery", "发现推荐", auth=True, params={"limit": 20})
        self.test_endpoint("GET", "/api/v1/recommendations/popular", "热门推荐", auth=True, params={"timeframe": "day", "limit": 20})
        
        # 追踪端点
        print("\n【追踪端点】")
        self.test_endpoint("GET", "/api/v1/tracking/stats", "获取追踪统计", auth=True)
        self.test_endpoint("POST", "/api/v1/tracking/impression", "记录曝光", auth=True, params={"news_id": 1, "position": 1})
        self.test_endpoint("POST", "/api/v1/tracking/click", "记录点击", auth=True, params={"news_id": 1, "position": 1})
        self.test_endpoint("POST", "/api/v1/tracking/read", "记录阅读", auth=True, params={"news_id": 1, "duration": 120})
        self.test_endpoint("POST", "/api/v1/tracking/behaviors", "批量记录行为", auth=True,
                          json_data={"behaviors": [{"news_id": 1, "behavior_type": "impression", "position": 1}]})
        
        # 认证其他端点
        print("\n【认证其他端点】")
        self.test_endpoint("POST", "/api/v1/auth/refresh", "刷新token", json_data={"refresh_token": "test"})
        self.test_endpoint("POST", "/api/v1/auth/logout", "登出", auth=True)
        
        # 打印总结
        print("\n" + "=" * 70)
        print("测试结果总结")
        print("=" * 70)
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['method']} {result['path']}: {result['status']}")
        
        print(f"\n总计: {passed}/{total} 通过 ({passed*100//total if total > 0 else 0}%)")
        print("=" * 70)

if __name__ == "__main__":
    tester = FullAPITester()
    tester.run_all_tests()

