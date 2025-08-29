#!/usr/bin/env python3
"""
快速测试目标详情API
"""

import requests
import time

def test_api():
    print("开始测试...")
    
    # 等待服务启动
    time.sleep(3)
    
    # 测试健康检查
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"健康检查: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            
            # 测试登录
            login_data = {
                "wechat_id": "test_user_123",
                "nickname": "测试用户",
                "avatar": "https://example.com/avatar.jpg"
            }
            
            response = requests.post("http://localhost:8000/api/auth/wechat-login", 
                                  json=login_data, timeout=5)
            print(f"登录测试: {response.status_code}")
            
            if response.status_code == 200:
                token = response.json()["token"]
                print("✅ 登录成功")
                
                # 测试获取目标列表
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get("http://localhost:8000/api/goals/", 
                                     headers=headers, timeout=5)
                print(f"获取目标列表: {response.status_code}")
                
                if response.status_code == 200:
                    goals = response.json()
                    print(f"✅ 获取到 {len(goals)} 个目标")
                    
                    if goals:
                        goal_id = goals[0]["id"]
                        print(f"第一个目标ID: {goal_id}")
                        
                        # 测试获取目标详情
                        response = requests.get(f"http://localhost:8000/api/goals/{goal_id}", 
                                             headers=headers, timeout=5)
                        print(f"获取目标详情: {response.status_code}")
                        
                        if response.status_code == 200:
                            goal_detail = response.json()
                            print("✅ 目标详情获取成功")
                            print(f"标题: {goal_detail.get('title', 'N/A')}")
                        else:
                            print(f"❌ 获取目标详情失败: {response.text}")
                    else:
                        print("⚠️ 没有目标，无法测试详情API")
                else:
                    print(f"❌ 获取目标列表失败: {response.text}")
            else:
                print(f"❌ 登录失败: {response.text}")
        else:
            print(f"❌ 健康检查失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("测试完成")

if __name__ == "__main__":
    test_api()
