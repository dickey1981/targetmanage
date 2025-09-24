"""
过程记录智能分析器
Process record intelligent analyzer
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessRecordAnalyzer:
    """过程记录智能分析器"""
    
    def __init__(self):
        """初始化分析器"""
        # 记录类型关键词映射
        self.type_keywords = {
            'progress': [
                '完成', '达成', '实现', '达到', '获得', '取得', '进步', '提升', '改善',
                '跑了', '读了', '学了', '做了', '写了', '画了', '练了', '减了', '增了',
                '今天', '这周', '这个月', '已经', '终于', '成功'
            ],
            'milestone': [
                '里程碑', '重要', '突破', '第一次', '首次', '终于', '成功', '达成',
                '完成目标', '达到预期', '超越', '创纪录', '历史性', '意义重大'
            ],
            'difficulty': [
                '困难', '问题', '挑战', '障碍', '阻碍', '卡住', '停滞', '退步',
                '失败', '挫折', '沮丧', '焦虑', '压力', '疲惫', '累', '难',
                '不会', '不懂', '不明白', '搞不定', '解决不了'
            ],
            'method': [
                '方法', '技巧', '策略', '方式', '做法', '经验', '心得', '体会',
                '发现', '学会', '掌握', '总结', '改进', '优化', '调整', '改变',
                '有效', '有用', '好用', '推荐', '建议'
            ],
            'reflection': [
                '反思', '思考', '总结', '回顾', '分析', '感悟', '体会', '感受',
                '觉得', '认为', '感觉', '意识到', '明白', '理解', '领悟',
                '收获', '成长', '进步', '改变', '影响'
            ],
            'adjustment': [
                '调整', '修改', '改变', '优化', '改进', '重新', '重新开始',
                '计划', '安排', '安排时间', '时间管理', '优先级', '重点'
            ],
            'achievement': [
                '成就', '成功', '胜利', '获奖', '认可', '表扬', '称赞', '满意',
                '骄傲', '自豪', '开心', '高兴', '兴奋', '激动'
            ],
            'insight': [
                '洞察', '发现', '领悟', '明白', '理解', '意识到', '认识到',
                '启发', '灵感', '创意', '想法', '观点', '看法'
            ]
        }
        
        # 情感关键词
        self.sentiment_keywords = {
            'positive': [
                '好', '棒', '优秀', '完美', '成功', '开心', '高兴', '满意', '兴奋',
                '激动', '自豪', '骄傲', '轻松', '愉快', '顺利', '有效', '有用',
                '进步', '提升', '改善', '突破', '成就', '胜利', '完成', '达成'
            ],
            'negative': [
                '差', '糟糕', '失败', '困难', '问题', '挑战', '沮丧', '焦虑',
                '压力', '疲惫', '累', '难', '卡住', '停滞', '退步', '挫折',
                '失望', '担心', '害怕', '紧张', '困惑', '迷茫'
            ]
        }
        
        # 精力水平关键词
        self.energy_keywords = {
            'high': ['精力充沛', '活力满满', '精神很好', '状态很好', '充满活力'],
            'medium': ['一般', '正常', '还可以', '还行', '过得去'],
            'low': ['疲惫', '累', '没精神', '状态不好', '困', '乏力']
        }
        
        # 困难程度关键词
        self.difficulty_keywords = {
            'high': ['很难', '非常难', '极其困难', '挑战很大', '压力很大'],
            'medium': ['有点难', '不太容易', '需要努力', '有一定挑战'],
            'low': ['简单', '容易', '轻松', '不难', '小菜一碟']
        }
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        分析过程记录内容
        
        Args:
            content: 记录内容
            
        Returns:
            分析结果字典
        """
        try:
            # 基础分析
            analysis = {
                'record_type': self._classify_record_type(content),
                'sentiment': self._analyze_sentiment(content),
                'energy_level': self._analyze_energy_level(content),
                'difficulty_level': self._analyze_difficulty_level(content),
                'keywords': self._extract_keywords(content),
                'tags': self._generate_tags(content),
                'is_important': self._is_important(content),
                'is_milestone': self._is_milestone(content),
                'is_breakthrough': self._is_breakthrough(content),
                'confidence_score': self._calculate_confidence(content)
            }
            
            logger.info(f"内容分析完成: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return self._get_default_analysis()
    
    def _classify_record_type(self, content: str) -> str:
        """分类记录类型"""
        content_lower = content.lower()
        
        # 计算每种类型的匹配分数
        type_scores = {}
        for record_type, keywords in self.type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            type_scores[record_type] = score
        
        # 返回得分最高的类型
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return 'process'  # 默认类型
    
    def _analyze_sentiment(self, content: str) -> str:
        """分析情感倾向"""
        content_lower = content.lower()
        
        positive_score = sum(1 for keyword in self.sentiment_keywords['positive'] if keyword in content_lower)
        negative_score = sum(1 for keyword in self.sentiment_keywords['negative'] if keyword in content_lower)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_energy_level(self, content: str) -> Optional[int]:
        """分析精力水平"""
        content_lower = content.lower()
        
        for level, keywords in self.energy_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if level == 'high':
                    return 8
                elif level == 'medium':
                    return 5
                elif level == 'low':
                    return 3
        
        return None
    
    def _analyze_difficulty_level(self, content: str) -> Optional[int]:
        """分析困难程度"""
        content_lower = content.lower()
        
        for level, keywords in self.difficulty_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if level == 'high':
                    return 8
                elif level == 'medium':
                    return 5
                elif level == 'low':
                    return 2
        
        return None
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取，可以后续优化为更复杂的NLP算法
        keywords = []
        
        # 提取数字
        numbers = re.findall(r'\d+', content)
        keywords.extend(numbers)
        
        # 提取常见动词和名词
        important_words = [
            '完成', '学习', '练习', '跑步', '读书', '工作', '项目', '目标',
            '进步', '提升', '改善', '突破', '成功', '失败', '困难', '挑战'
        ]
        
        for word in important_words:
            if word in content:
                keywords.append(word)
        
        return list(set(keywords))  # 去重
    
    def _generate_tags(self, content: str) -> List[str]:
        """生成标签"""
        tags = []
        
        # 基于内容生成标签
        if '跑步' in content or '运动' in content:
            tags.append('运动')
        if '学习' in content or '读书' in content:
            tags.append('学习')
        if '工作' in content or '项目' in content:
            tags.append('工作')
        if '健康' in content or '减肥' in content:
            tags.append('健康')
        
        # 基于情感生成标签
        sentiment = self._analyze_sentiment(content)
        if sentiment == 'positive':
            tags.append('积极')
        elif sentiment == 'negative':
            tags.append('消极')
        
        return tags
    
    def _is_important(self, content: str) -> bool:
        """判断是否重要"""
        important_indicators = [
            '重要', '关键', '里程碑', '突破', '第一次', '首次', '成功',
            '完成目标', '达到预期', '创纪录', '历史性', '意义重大'
        ]
        
        return any(indicator in content for indicator in important_indicators)
    
    def _is_milestone(self, content: str) -> bool:
        """判断是否里程碑"""
        milestone_indicators = [
            '里程碑', '重要节点', '关键节点', '阶段性', '第一次', '首次',
            '完成目标', '达到预期', '突破', '创纪录'
        ]
        
        return any(indicator in content for indicator in milestone_indicators)
    
    def _is_breakthrough(self, content: str) -> bool:
        """判断是否突破"""
        breakthrough_indicators = [
            '突破', '超越', '创新', '新发现', '新方法', '新技巧',
            '突然明白', '豁然开朗', '灵感', '创意'
        ]
        
        return any(indicator in content for indicator in breakthrough_indicators)
    
    def _calculate_confidence(self, content: str) -> int:
        """计算置信度分数"""
        confidence = 50  # 基础分数
        
        # 内容长度影响置信度
        if len(content) > 50:
            confidence += 20
        elif len(content) > 20:
            confidence += 10
        
        # 关键词匹配影响置信度
        total_keywords = sum(len(keywords) for keywords in self.type_keywords.values())
        matched_keywords = sum(1 for keywords in self.type_keywords.values() 
                             for keyword in keywords if keyword in content.lower())
        
        if matched_keywords > 0:
            confidence += min(30, matched_keywords * 5)
        
        return min(100, confidence)
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """获取默认分析结果"""
        return {
            'record_type': 'process',
            'sentiment': 'neutral',
            'energy_level': None,
            'difficulty_level': None,
            'keywords': [],
            'tags': [],
            'is_important': False,
            'is_milestone': False,
            'is_breakthrough': False,
            'confidence_score': 50
        }


# 全局分析器实例
process_analyzer = ProcessRecordAnalyzer()
