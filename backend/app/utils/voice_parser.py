"""
语音解析工具模块
将语音识别的自然语言文本解析为结构化的目标数据
"""
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class VoiceGoalParser:
    """语音目标解析器"""
    
    def __init__(self):
        """初始化解析器"""
        # 时间表达式模式
        self.time_patterns = {
            r'(\d+)个月内': self._parse_months,
            r'(\d+)周内': self._parse_weeks,
            r'(\d+)天内': self._parse_days,
            r'半年内': self._parse_half_year,
            r'一年内': self._parse_one_year,
            r'下个月': self._parse_next_month,
            r'下周': self._parse_next_week,
            r'明天': self._parse_tomorrow,
        }
        
        # 量化指标模式
        self.quantification_patterns = [
            (r'减重(\d+)(斤|公斤|kg)', '减重', 'weight'),
            (r'增重(\d+)(斤|公斤|kg)', '增重', 'weight'),
            (r'学习(\d+)(本书|门课程|个技能)', '学习', 'study'),
            (r'读完(\d+)(本书|篇文章)', '阅读', 'reading'),
            (r'完成(\d+)(个项目|个任务)', '工作', 'work'),
            (r'跑(\d+)(公里|km)', '运动', 'exercise'),
            (r'存(\d+)(万|千)元', '理财', 'finance'),
            (r'去(\d+)个地方', '旅行', 'travel'),
        ]
        
        # 类别关键词映射
        self.category_keywords = {
            '健康': ['减重', '增重', '跑步', '健身', '减肥', '运动', '锻炼', '减肥', '增肌'],
            '学习': ['学习', '读书', '考试', '技能', '编程', '语言', '证书', '培训'],
            '工作': ['项目', '任务', '业绩', '升职', '工作', '创业', '客户', '销售'],
            '生活': ['旅行', '理财', '兴趣', '爱好', '生活', '存钱', '投资', '购物']
        }
    
    def parse_voice_to_goal(self, voice_text: str) -> Dict[str, Any]:
        """
        解析语音文本为目标数据
        
        Args:
            voice_text: 语音识别的文本内容
        
        Returns:
            解析后的目标数据结构
        """
        logger.info(f"开始解析语音文本: {voice_text}")
        
        # 清理文本
        cleaned_text = self._clean_text(voice_text)
        
        # 解析各个部分
        title = self._extract_title(cleaned_text)
        category = self._identify_category(cleaned_text)
        start_date, end_date = self._parse_time_expression(cleaned_text)
        target_value, unit = self._parse_quantification(cleaned_text)
        description = self._generate_description(cleaned_text, target_value, unit)
        
        # 构建目标数据
        goal_data = {
            'title': title,
            'category': category,
            'description': description,
            'startDate': start_date.isoformat() if start_date else None,
            'endDate': end_date.isoformat() if end_date else None,
            'targetValue': target_value,
            'currentValue': '0',
            'unit': unit,
            'priority': 'medium',
            'dailyReminder': True,
            'deadlineReminder': True
        }
        
        logger.info(f"语音解析完成: {goal_data}")
        return goal_data
    
    def _clean_text(self, text: str) -> str:
        """清理和标准化文本"""
        # 去除多余空格和标点
        cleaned = re.sub(r'\s+', ' ', text.strip())
        # 标准化数字表达
        cleaned = re.sub(r'(\d+)个', r'\1个', cleaned)
        return cleaned
    
    def _extract_title(self, text: str) -> str:
        """提取目标标题"""
        # 简单的标题提取逻辑
        # 可以后续优化为更智能的提取
        return text[:50] if len(text) > 50 else text
    
    def _identify_category(self, text: str) -> str:
        """智能识别目标类别"""
        for category, keywords in self.category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return '其他'
    
    def _parse_time_expression(self, text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """解析时间表达式"""
        today = datetime.now()
        
        for pattern, parser_func in self.time_patterns.items():
            match = re.search(pattern, text)
            if match:
                try:
                    return parser_func(match, today)
                except Exception as e:
                    logger.warning(f"时间解析失败: {e}")
                    continue
        
        # 默认时间范围：3个月
        start_date = today
        end_date = today + timedelta(days=90)
        return start_date, end_date
    
    def _parse_months(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析月份表达式：3个月内"""
        months = int(match.group(1))
        start_date = today
        end_date = today + timedelta(days=months * 30)
        return start_date, end_date
    
    def _parse_weeks(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析周数表达式：2周内"""
        weeks = int(match.group(1))
        start_date = today
        end_date = today + timedelta(weeks=weeks)
        return start_date, end_date
    
    def _parse_days(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析天数表达式：30天内"""
        days = int(match.group(1))
        start_date = today
        end_date = today + timedelta(days=days)
        return start_date, end_date
    
    def _parse_half_year(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析半年表达式"""
        start_date = today
        end_date = today + timedelta(days=180)
        return start_date, end_date
    
    def _parse_one_year(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析一年表达式"""
        start_date = today
        end_date = today + timedelta(days=365)
        return start_date, end_date
    
    def _parse_next_month(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析下个月表达式"""
        start_date = today
        # 计算下个月1号
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        end_date = next_month + timedelta(days=30)
        return start_date, end_date
    
    def _parse_next_week(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析下周表达式"""
        start_date = today
        # 计算下周一
        days_ahead = 7 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        end_date = next_monday + timedelta(days=7)
        return start_date, end_date
    
    def _parse_tomorrow(self, match, today: datetime) -> Tuple[datetime, datetime]:
        """解析明天表达式"""
        start_date = today
        end_date = today + timedelta(days=1)
        return start_date, end_date
    
    def _parse_quantification(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析量化信息"""
        for pattern, action, goal_type in self.quantification_patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                unit = match.group(2)
                return value, unit
        
        return None, None
    
    def _generate_description(self, text: str, target_value: str, unit: str) -> str:
        """生成目标描述"""
        if target_value and unit:
            return f"通过{text}实现目标：{target_value}{unit}"
        return text

# 创建全局实例
voice_goal_parser = VoiceGoalParser()
