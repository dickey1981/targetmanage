#!/usr/bin/env python3
"""
简单测试过程记录功能
"""

import requests
import json
from datetime import datetime

base_url = "http://127.0.0.1:8000"

def test_create_process_record():
    """测试创建过程记录"""
    print("🔍 测试创建过程记录...")
    
    test_data = {
        "content": "今天跑了5公里，感觉很好，比上周轻松多了",
        "record_type": "progress",
        "source": "manual",
        "goal_id": None
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/process-records/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 创建过程记录成功")
            print(f"记录ID: {data['id']}")
            print(f"记录类型: {data['record_type']}")
            print(f"情感分析: {data['sentiment']}")
            print(f"是否重要: {data['is_important']}")
            print(f"关键词: {data['keywords']}")
            return data['id']
        else:
            print(f"❌ 创建过程记录失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return None

def test_voice_process_record():
    """测试语音过程记录"""
    print("\n🔍 测试语音过程记录...")
    
    test_data = {
        "voice_text": "今天学习Python遇到了困难，有些概念不太理解，需要多练习",
        "goal_id": None
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/process-records/voice",
            json=test_data,
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
                return record['id']
            else:
                print(f"❌ 创建语音过程记录失败: {data['message']}")
                return None
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return None

def test_get_process_records():
    """测试获取过程记录列表"""
    print("\n🔍 测试获取过程记录列表...")
    
    try:
        response = requests.get(
            f"{base_url}/api/process-records/",
            params={
                "page": 1,
                "page_size": 5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取过程记录列表成功")
            print(f"总记录数: {data['total']}")
            print(f"当前页: {data['page']}")
            print(f"记录数量: {len(data['records'])}")
            
            # 显示前3条记录
            for i, record in enumerate(data['records'][:3], 1):
                print(f"\n记录 {i}:")
                print(f"  ID: {record['id']}")
                print(f"  内容: {record['content'][:50]}...")
                print(f"  类型: {record['record_type']}")
                print(f"  情感: {record['sentiment']}")
        else:
            print(f"❌ 获取过程记录列表失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_get_timeline():
    """测试获取时间线"""
    print("\n🔍 测试获取时间线...")
    
    try:
        response = requests.get(
            f"{base_url}/api/process-records/timeline",
            params={
                "days": 7
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取时间线成功")
            print(f"时间线天数: {len(data)}")
            
            # 显示时间线数据
            for timeline_item in data[:2]:  # 显示前2天
                print(f"\n日期: {timeline_item['date']}")
                print(f"记录数: {len(timeline_item['records'])}")
                print(f"里程碑数: {timeline_item['milestone_count']}")
                print(f"突破数: {timeline_item['breakthrough_count']}")
        else:
            print(f"❌ 获取时间线失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_get_stats():
    """测试获取统计信息"""
    print("\n🔍 测试获取统计信息...")
    
    try:
        response = requests.get(
            f"{base_url}/api/process-records/stats",
            params={
                "days": 30
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取统计信息成功")
            print(f"总记录数: {data['total_records']}")
            print(f"按类型统计: {data['records_by_type']}")
            print(f"按心情统计: {data['records_by_mood']}")
            print(f"里程碑数: {data['milestone_count']}")
            print(f"突破数: {data['breakthrough_count']}")
        else:
            print(f"❌ 获取统计信息失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试过程记录功能...")
    
    # 测试创建记录
    record_id = test_create_process_record()
    
    # 测试语音记录
    voice_record_id = test_voice_process_record()
    
    # 测试获取列表
    test_get_process_records()
    
    # 测试时间线
    test_get_timeline()
    
    # 测试统计
    test_get_stats()
    
    print("\n🎉 过程记录功能测试完成！")

if __name__ == "__main__":
    main()
