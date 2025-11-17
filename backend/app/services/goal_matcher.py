"""
目标智能匹配服务
Goal Intelligent Matching Service
"""

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GoalMatcher:
    """目标智能匹配器"""
    
    def __init__(self):
        """初始化匹配器，加载关键词库"""
        self.keyword_categories = self._load_keyword_categories()
        self.unit_variants = self._load_unit_variants()
    
    def _load_keyword_categories(self) -> Dict[str, Dict[str, List[str]]]:
        """
        加载关键词分类库
        
        每个类别包含三层关键词：
        - primary: 主关键词（权重 1.0）
        - related: 相关关键词（权重 0.3）
        - context: 上下文关键词（权重 0.2）
        """
        return {
            '学习': {
                'primary': ['学习', '学', '读书', '阅读', '看书', '复习', '预习', '背', '记', '温习'],
                'related': ['python', 'java', 'javascript', '编程', '代码', '课程', '教程', 
                           '知识', '技能', '考试', '作业', '笔记', '英语', '数学', '算法'],
                'context': ['完成', '学会', '掌握', '理解', '记住', '看完', '读完', '背会']
            },
            '健身': {
                'primary': ['跑步', '健身', '运动', '锻炼', '瑜伽', '游泳', '爬山', '骑行', 
                           '篮球', '足球', '羽毛球', '网球', '打球'],
                'related': ['公里', 'km', '步', '米', '减肥', '塑形', '增肌', '力量', 
                           '有氧', '无氧', '训练', '卡路里', '体重', '肌肉', '马拉松'],
                'context': ['跑了', '练了', '做了', '完成', '坚持', '打卡']
            },
            '工作': {
                'primary': ['工作', '项目', '任务', '会议', '开发', '设计', '测试', 
                           '部署', '上线', '需求', '文档'],
                'related': ['代码', '程序', 'bug', '功能', '接口', 'api', '数据库', 
                           '前端', '后端', '客户', '方案', '报告', '汇报'],
                'context': ['完成', '交付', '解决', '实现', '优化', '修复', '提交']
            },
            '生活': {
                'primary': ['做饭', '购物', '整理', '打扫', '洗衣', '买菜', '收拾', 
                           '清洁', '家务', '洗碗', '拖地'],
                'related': ['房间', '家里', '衣服', '菜', '超市', '市场', '垃圾', 
                           '卫生', '干净', '整洁'],
                'context': ['做了', '完成', '整理', '收拾', '打扫', '洗了']
            },
            '财务': {
                'primary': ['赚钱', '理财', '投资', '存钱', '收入', '挣钱', '盈利', 
                           '营收', '副业', '兼职'],
                'related': ['元', '块', '钱', '工资', '奖金', '收益', '利润', '成本', 
                           '基金', '股票', '储蓄', '账单'],
                'context': ['赚了', '存了', '投资', '收到', '赚到', '挣了']
            },
            '创作': {
                'primary': ['写作', '画画', '音乐', '视频', '文章', '创作', '设计', 
                           '拍摄', '剪辑', '博客'],
                'related': ['字', '篇', '幅', '首', '个', '张', '期', '集', '作品', 
                           '内容', '素材', '灵感'],
                'context': ['写了', '画了', '创作', '完成', '发布', '更新', '做了']
            },
            '阅读': {
                'primary': ['读', '看', '阅读', '读书', '看书', '翻阅', '浏览'],
                'related': ['书', '页', '章', '本', '小说', '文章', '资料', '文档', 
                           '材料', '报告'],
                'context': ['读了', '看了', '读完', '看完', '翻了', '浏览']
            },
            '社交': {
                'primary': ['社交', '交友', '聚会', '约会', '见面', '聊天', '沟通'],
                'related': ['朋友', '同学', '同事', '家人', '客户', '伙伴', '社群', 
                           '活动', '派对'],
                'context': ['见了', '聊了', '约了', '参加', '认识']
            }
        }
    
    def _load_unit_variants(self) -> Dict[str, List[str]]:
        """
        加载单位变体
        
        用于识别不同形式的单位表达
        """
        return {
            '公里': ['km', 'kilometer', '千米'],
            '米': ['m', 'meter'],
            '小时': ['h', 'hour', '钟头', '个小时'],
            '分钟': ['min', 'minute', '分'],
            '秒': ['s', 'second', '秒钟'],
            '页': ['page', 'p'],
            '字': ['word', '个字'],
            '%': ['percent', '百分之', '百分比'],
            '元': ['块', '块钱', '元钱', '人民币'],
            '斤': ['公斤', 'kg', '千克'],
            '本': ['册'],
            '篇': ['文'],
            '次': ['遍', '回']
        }
    
    def match_goal(
        self, 
        content: str, 
        goals: list, 
        user_id: str = None,
        db = None
    ) -> Optional[Dict]:
        """
        智能匹配目标
        
        Args:
            content: 记录内容
            goals: 候选目标列表
            user_id: 用户ID（用于历史记录学习）
            db: 数据库会话（用于查询历史）
        
        Returns:
            {
                'matched_goal': Goal对象,
                'score': 匹配分数,
                'confidence': 置信度 (high/medium/low),
                'reason': 匹配原因
            }
            如果没有找到匹配，返回 None
        """
        if not goals:
            logger.info("📊 没有可匹配的目标")
            return None
        
        logger.info(f"🎯 开始匹配，候选目标数: {len(goals)}")
        
        best_match = None
        best_score = 0
        match_reason = ""
        
        content_lower = content.lower()
        
        # 遍历所有目标，计算匹配分数
        for goal in goals:
            score = 0
            reasons = []
            
            # 1. 类别关键词匹配
            category_score, category_reasons = self._match_category(
                content_lower, 
                goal.category
            )
            score += category_score
            reasons.extend(category_reasons)
            
            # 2. 目标标题匹配
            title_score, title_reasons = self._match_title(
                content_lower, 
                goal.title
            )
            score += title_score
            reasons.extend(title_reasons)
            
            # 3. 目标描述匹配
            if goal.description:
                desc_score, desc_reasons = self._match_description(
                    content_lower, 
                    goal.description
                )
                score += desc_score
                reasons.extend(desc_reasons)
            
            # 4. 单位匹配
            if goal.unit:
                unit_score, unit_reasons = self._match_unit(
                    content_lower, 
                    goal.unit
                )
                score += unit_score
                reasons.extend(unit_reasons)
            
            # 5. 历史记录加成
            if user_id and db:
                history_score, history_reason = self._match_history(
                    user_id, 
                    goal.id, 
                    db
                )
                score += history_score
                if history_reason:
                    reasons.append(history_reason)
            
            # 记录匹配详情
            if score > 0:
                logger.debug(
                    f"  目标 '{goal.title}': {score:.2f}分 "
                    f"[{', '.join(reasons)}]"
                )
            
            # 更新最佳匹配
            if score > best_score:
                best_score = score
                best_match = goal
                match_reason = "; ".join(reasons)
        
        # 判断是否达到匹配阈值
        # 提高阈值到0.6，避免低分强制匹配
        if best_score < 0.6:
            logger.info(f"❌ 未找到匹配目标（最高分: {best_score:.2f} < 0.6）")
            return None
        
        # 根据分数判断置信度
        if best_score >= 1.5:
            confidence = "high"
        elif best_score >= 0.8:
            confidence = "medium"
        else:
            confidence = "low"
        
        logger.info(
            f"✅ 匹配成功: '{best_match.title}' "
            f"(分数: {best_score:.2f}, 置信度: {confidence})"
        )
        
        return {
            'matched_goal': best_match,
            'score': best_score,
            'confidence': confidence,
            'reason': match_reason
        }
    
    def _match_category(
        self, 
        content: str, 
        category: Optional[str]
    ) -> tuple[float, List[str]]:
        """匹配类别关键词"""
        score = 0
        reasons = []
        
        if not category:
            return score, reasons
        
        category = category.strip()
        if category not in self.keyword_categories:
            return score, reasons
        
        keywords = self.keyword_categories[category]
        
        # 主关键词匹配（权重 1.0）
        for keyword in keywords['primary']:
            if keyword in content:
                score += 1.0
                reasons.append(f"主关键词'{keyword}'")
                break  # 只匹配一次
        
        # 相关关键词匹配（权重 0.3/个）
        related_matches = [kw for kw in keywords['related'] if kw in content]
        if related_matches:
            related_score = min(len(related_matches) * 0.3, 0.9)  # 最多0.9分
            score += related_score
            reasons.append(f"相关词×{len(related_matches)}")
        
        # 上下文关键词匹配（权重 0.2/个）
        context_matches = [kw for kw in keywords['context'] if kw in content]
        if context_matches:
            context_score = min(len(context_matches) * 0.2, 0.6)  # 最多0.6分
            score += context_score
            reasons.append(f"上下文×{len(context_matches)}")
        
        return score, reasons
    
    def _match_title(
        self, 
        content: str, 
        title: Optional[str]
    ) -> tuple[float, List[str]]:
        """匹配目标标题"""
        score = 0
        reasons = []
        
        if not title:
            return score, reasons
        
        # 去除常见的修饰词
        title_clean = title.lower().replace('计划', '').replace('目标', '')\
                           .replace('任务', '').replace('的', '')
        
        # 分词并过滤短词
        title_words = set(title_clean.split())
        title_words = {w for w in title_words if len(w) >= 2}
        
        # 检查每个标题词是否在内容中
        matched_words = [word for word in title_words if word in content]
        
        if matched_words:
            # 每个匹配的标题词 +0.5分，最多1.5分
            word_score = min(len(matched_words) * 0.5, 1.5)
            score += word_score
            reasons.append(f"标题词×{len(matched_words)}")
        
        return score, reasons
    
    def _match_description(
        self, 
        content: str, 
        description: str
    ) -> tuple[float, List[str]]:
        """匹配目标描述"""
        score = 0
        reasons = []
        
        # 分词并过滤短词
        desc_words = set(description.lower().split())
        desc_words = {w for w in desc_words if len(w) >= 2}
        
        # 检查匹配数量
        matched_words = [word for word in desc_words if word in content]
        
        if matched_words:
            # 每个匹配的描述词 +0.1分，最多0.5分
            desc_score = min(len(matched_words) * 0.1, 0.5)
            score += desc_score
            reasons.append(f"描述词×{len(matched_words)}")
        
        return score, reasons
    
    def _match_unit(
        self, 
        content: str, 
        unit: str
    ) -> tuple[float, List[str]]:
        """匹配单位"""
        score = 0
        reasons = []
        
        unit_lower = unit.lower()
        
        # 直接匹配
        if unit_lower in content:
            score += 0.4
            reasons.append(f"单位'{unit}'")
            return score, reasons
        
        # 变体匹配
        if unit_lower in self.unit_variants:
            for variant in self.unit_variants[unit_lower]:
                if variant in content:
                    score += 0.4
                    reasons.append(f"单位'{variant}'")
                    break
        
        return score, reasons
    
    def _match_history(
        self, 
        user_id: str, 
        goal_id: str, 
        db
    ) -> tuple[float, str]:
        """基于历史记录的匹配加成"""
        score = 0
        reason = ""
        
        try:
            from app.models.process_record import ProcessRecord
            
            # 查询最近30天的记录
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # 统计该目标的记录次数
            record_count = db.query(ProcessRecord).filter(
                ProcessRecord.user_id == user_id,
                ProcessRecord.goal_id == goal_id,
                ProcessRecord.created_at >= thirty_days_ago
            ).count()
            
            if record_count > 0:
                # 历史记录加成：最多0.5分
                history_score = min(record_count * 0.05, 0.5)
                score += history_score
                reason = f"历史记录×{record_count}"
        
        except Exception as e:
            logger.warning(f"查询历史记录失败: {str(e)}")
        
        return score, reason


# 创建全局单例
goal_matcher = GoalMatcher()

