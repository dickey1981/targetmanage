#!/usr/bin/env python3
"""
测试过程记录功能
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://127.0.0.1:8000"

def test_process_records():
    """测试过程记录功能"""
    print("🔍 测试过程记录功能...")
    
    # 测试用例
    test_cases = [
        {
            'name': '进度记录',
            'content': '今天跑了5公里，感觉很好，比上周轻松多了',
            'expected_type': 'progress'
        },
        {
            'name': '困难记录',
            'name': '困难记录',
            'content': '今天学习Python遇到了困难，有些概念不太理解，需要多练习',
            'expected_type': 'difficulty'
        },
        {
            'name': '方法记录',
            'content': '发现早上跑步效果更好，空气清新，精力充沛',
            'expected_type': 'method'
        },
        {
            'name': '反思记录',
            'content': '这个月总体进展不错，但需要更好地管理时间，提高效率',
            'expected_type': 'reflection'
        },
        {
            'name': '里程碑记录',
            'content': '终于完成了第一个项目，这是一个重要的里程碑',
            'expected_type': 'milestone'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {test_case['name']} ---")
        print(f"内容: {test_case['content']}")
        
        try:
            # 创建过程记录
            response = requests.post(
                f"{base_url}/api/process-records/",
                json={
                    "content": test_case['content'],
                    "record_type": "process",  # 让系统自动分类
                    "source": "manual"
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 创建过程记录成功")
                print(f"记录ID: {data['id']}")
                print(f"自动分类类型: {data['record_type']}")
                print(f"情感分析: {data['sentiment']}")
                print(f"是否重要: {data['is_important']}")
                print(f"是否里程碑: {data['is_milestone']}")
                print(f"置信度: {data['confidence_score']}")
                print(f"关键词: {data['keywords']}")
                print(f"标签: {data['tags']}")
                
                # 验证自动分类是否正确
                if data['record_type'] == test_case['expected_type']:
                    print("✅ 自动分类正确")
                else:
                    print(f"❌ 自动分类不正确，期望: {test_case['expected_type']}, 实际: {data['record_type']}")
                
            else:
                print(f"❌ 创建过程记录失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_voice_process_records():
    """测试语音过程记录功能"""
    print("\n🔍 测试语音过程记录功能...")
    
    voice_test_cases = [
        {
            'name': '语音进度记录',
            'voice_text': '今天跑了5公里，用时30分钟，感觉比上周轻松多了',
            'goal_id': None
        },
        {
            'name': '语音困难记录',
            'voice_text': '学习Python遇到了困难，有些概念不太理解，需要多练习',
            'goal_id': None
        },
        {
            'name': '语音方法记录',
            'voice_text': '发现早上跑步效果更好，空气清新，精力充沛',
            'goal_id': None
        }
    ]
    
    for i, test_case in enumerate(voice_test_cases, 1):
        print(f"\n--- 语音测试用例 {i}: {test_case['name']} ---")
        print(f"语音内容: {test_case['voice_text']}")
        
        try:
            # 创建语音过程记录
            response = requests.post(
                f"{base_url}/api/process-records/voice",
                json={
                    "voice_text": test_case['voice_text'],
                    "goal_id": test_case['goal_id']
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print("✅ 创建语音过程记录成功")
                    record = data['record']
                    analysis = data['analysis']
                    print(f"记录ID: {record['id']}")
                    print(f"自动分类类型: {record['record_type']}")
                    print(f"情感分析: {record['sentiment']}")
                    print(f"分析结果: {analysis}")
                else:
                    print(f"❌ 创建语音过程记录失败: {data['message']}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_process_records_list():
    """测试过程记录列表功能"""
    print("\n🔍 测试过程记录列表功能...")
    
    try:
        # 获取过程记录列表
        response = requests.get(
            f"{base_url}/api/process-records/",
            params={
                "page": 1,
                "page_size": 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取过程记录列表成功")
            print(f"总记录数: {data['total']}")
            print(f"当前页: {data['page']}")
            print(f"每页数量: {data['page_size']}")
            print(f"是否有下一页: {data['has_next']}")
            print(f"记录数量: {len(data['records'])}")
            
            # 显示前3条记录
            for i, record in enumerate(data['records'][:3], 1):
                print(f"\n记录 {i}:")
                print(f"  ID: {record['id']}")
                print(f"  内容: {record['content'][:50]}...")
                print(f"  类型: {record['record_type']}")
                print(f"  情感: {record['sentiment']}")
                print(f"  时间: {record['recorded_at']}")
        else:
            print(f"❌ 获取过程记录列表失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_process_records_timeline():
    """测试过程记录时间线功能"""
    print("\n🔍 测试过程记录时间线功能...")
    
    try:
        # 获取过程记录时间线
        response = requests.get(
            f"{base_url}/api/process-records/timeline",
            params={
                "days": 7
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取过程记录时间线成功")
            print(f"时间线天数: {len(data)}")
            
            # 显示时间线数据
            for timeline_item in data[:3]:  # 显示前3天
                print(f"\n日期: {timeline_item['date']}")
                print(f"记录数: {len(timeline_item['records'])}")
                print(f"里程碑数: {timeline_item['milestone_count']}")
                print(f"突破数: {timeline_item['breakthrough_count']}")
        else:
            print(f"❌ 获取过程记录时间线失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_process_records_stats():
    """测试过程记录统计功能"""
    print("\n🔍 测试过程记录统计功能...")
    
    try:
        # 获取过程记录统计
        response = requests.get(
            f"{base_url}/api/process-records/stats",
            params={
                "days": 30
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取过程记录统计成功")
            print(f"总记录数: {data['total_records']}")
            print(f"按类型统计: {data['records_by_type']}")
            print(f"按心情统计: {data['records_by_mood']}")
            print(f"里程碑数: {data['milestone_count']}")
            print(f"突破数: {data['breakthrough_count']}")
            print(f"平均精力水平: {data['avg_energy_level']}")
            print(f"平均困难程度: {data['avg_difficulty_level']}")
            print(f"积极情感比例: {data['positive_sentiment_ratio']}")
        else:
            print(f"❌ 获取过程记录统计失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试过程记录功能...")
    
    # 测试基础功能
    test_process_records()
    
    # 测试语音功能
    test_voice_process_records()
    
    # 测试列表功能
    test_process_records_list()
    
    # 测试时间线功能
    test_process_records_timeline()
    
    # 测试统计功能
    test_process_records_stats()
    
    print("\n🎉 过程记录功能测试完成！")

if __name__ == "__main__":
    main()
