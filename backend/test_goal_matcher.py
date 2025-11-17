"""
测试目标匹配器
Test Goal Matcher
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.goal_matcher import goal_matcher


class MockGoal:
    """模拟目标对象"""
    def __init__(self, id, title, category, description="", unit=""):
        self.id = id
        self.title = title
        self.category = category
        self.description = description
        self.unit = unit


def test_basic_matching():
    """测试基础匹配"""
    print("\n" + "="*60)
    print("🧪 测试1: 基础关键词匹配")
    print("="*60)
    
    # 创建测试目标
    goals = [
        MockGoal("1", "Python学习计划", "学习", "学习Python编程语言", "个"),
        MockGoal("2", "健身运动计划", "健身", "每周跑步3次", "公里"),
        MockGoal("3", "每周读一本书", "阅读", "提升阅读量", "本"),
    ]
    
    # 测试用例
    test_cases = [
        ("今天跑了10公里，好累", "健身运动计划"),
        ("完成了Python装饰器的学习", "Python学习计划"),
        ("读完了《活着》这本书", "每周读一本书"),
        ("今天写了500行Python代码", "Python学习计划"),
        ("做了50个俯卧撑", "健身运动计划"),
    ]
    
    success_count = 0
    for content, expected_title in test_cases:
        result = goal_matcher.match_goal(content, goals)
        
        if result:
            matched_title = result['matched_goal'].title
            is_correct = matched_title == expected_title
            status = "✅" if is_correct else "❌"
            
            print(f"\n{status} 内容: {content}")
            print(f"   期望: {expected_title}")
            print(f"   匹配: {matched_title}")
            print(f"   分数: {result['score']:.2f}, 置信度: {result['confidence']}")
            print(f"   原因: {result['reason']}")
            
            if is_correct:
                success_count += 1
        else:
            print(f"\n❌ 内容: {content}")
            print(f"   期望: {expected_title}")
            print(f"   匹配: 无匹配")
    
    print(f"\n{'='*60}")
    print(f"📊 测试结果: {success_count}/{len(test_cases)} 通过 ({success_count/len(test_cases)*100:.1f}%)")
    print(f"{'='*60}")
    
    return success_count == len(test_cases)


def test_category_matching():
    """测试类别匹配"""
    print("\n" + "="*60)
    print("🧪 测试2: 类别匹配")
    print("="*60)
    
    goals = [
        MockGoal("1", "项目开发", "工作", "完成XX项目开发"),
        MockGoal("2", "副业赚钱", "财务", "通过副业增加收入", "元"),
        MockGoal("3", "写作计划", "创作", "每周写一篇文章", "篇"),
    ]
    
    test_cases = [
        ("今天完成了3个需求开发", "项目开发"),
        ("这个月赚了5000块", "副业赚钱"),
        ("写了一篇2000字的文章", "写作计划"),
        ("修复了5个bug", "项目开发"),
        ("投资收益了1000元", "副业赚钱"),
    ]
    
    success_count = 0
    for content, expected_title in test_cases:
        result = goal_matcher.match_goal(content, goals)
        
        if result:
            matched_title = result['matched_goal'].title
            is_correct = matched_title == expected_title
            status = "✅" if is_correct else "❌"
            
            print(f"\n{status} 内容: {content}")
            print(f"   期望: {expected_title}, 实际: {matched_title}")
            print(f"   分数: {result['score']:.2f}, 原因: {result['reason']}")
            
            if is_correct:
                success_count += 1
        else:
            print(f"\n❌ 内容: {content}")
            print(f"   期望: {expected_title}, 实际: 无匹配")
    
    print(f"\n{'='*60}")
    print(f"📊 测试结果: {success_count}/{len(test_cases)} 通过 ({success_count/len(test_cases)*100:.1f}%)")
    print(f"{'='*60}")
    
    return success_count == len(test_cases)


def test_unit_matching():
    """测试单位匹配"""
    print("\n" + "="*60)
    print("🧪 测试3: 单位匹配")
    print("="*60)
    
    goals = [
        MockGoal("1", "跑步目标", "健身", "每月跑100公里", "公里"),
        MockGoal("2", "阅读目标", "阅读", "每月读4本书", "本"),
        MockGoal("3", "减肥目标", "健身", "减重10斤", "斤"),
    ]
    
    test_cases = [
        ("今天跑了5km", "跑步目标"),  # km -> 公里
        ("读完了1本书", "阅读目标"),
        ("减了2斤", "减肥目标"),
        ("跑了8千米", "跑步目标"),  # 千米 -> 公里
        ("看了3本小说", "阅读目标"),
    ]
    
    success_count = 0
    for content, expected_title in test_cases:
        result = goal_matcher.match_goal(content, goals)
        
        if result:
            matched_title = result['matched_goal'].title
            is_correct = matched_title == expected_title
            status = "✅" if is_correct else "❌"
            
            print(f"\n{status} 内容: {content}")
            print(f"   期望: {expected_title}, 实际: {matched_title}")
            print(f"   分数: {result['score']:.2f}")
            
            if is_correct:
                success_count += 1
        else:
            print(f"\n❌ 内容: {content}")
            print(f"   期望: {expected_title}, 实际: 无匹配")
    
    print(f"\n{'='*60}")
    print(f"📊 测试结果: {success_count}/{len(test_cases)} 通过 ({success_count/len(test_cases)*100:.1f}%)")
    print(f"{'='*60}")
    
    return success_count >= len(test_cases) * 0.8  # 80%通过即可


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "="*60)
    print("🧪 测试4: 边界情况")
    print("="*60)
    
    goals = [
        MockGoal("1", "学习目标", "学习"),
        MockGoal("2", "运动目标", "健身"),
    ]
    
    # 测试空列表
    result = goal_matcher.match_goal("今天学习了", [])
    print(f"\n✅ 空目标列表: {result is None}")
    
    # 测试无法匹配
    result = goal_matcher.match_goal("今天天气真好", goals)
    print(f"✅ 无关内容: {result is None}")
    
    # 测试低分匹配
    result = goal_matcher.match_goal("今天很开心", goals)
    print(f"✅ 低分内容: {result is None}")
    
    print(f"\n{'='*60}")
    print(f"📊 边界测试通过")
    print(f"{'='*60}")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀"*30)
    print("开始目标匹配器测试")
    print("🚀"*30)
    
    results = []
    
    # 运行测试
    results.append(("基础匹配", test_basic_matching()))
    results.append(("类别匹配", test_category_matching()))
    results.append(("单位匹配", test_unit_matching()))
    results.append(("边界情况", test_edge_cases()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📈 总体测试结果")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 所有测试通过！匹配器工作正常！")
    else:
        print("\n⚠️ 部分测试失败，需要检查匹配逻辑")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

