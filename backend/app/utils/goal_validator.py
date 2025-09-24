"""
目标验证工具模块
验证目标是否符合SMART原则，并提供智能建议
"""
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

class GoalValidator:
    """目标验证器"""
    
    def __init__(self):
        """初始化验证器"""
        # 时间合理性检查规则
        self.time_rules = {
            'min_days': 7,      # 最短时间：7天
            'max_days': 365,    # 最长时间：1年
            'recommended_min': 30,   # 推荐最短：30天
            'recommended_max': 180   # 推荐最长：180天
        }
        
        # 数值合理性检查规则
        self.value_rules = {
            '健康': {
                'weight': {'min': 1, 'max': 50, 'recommended': 20},
                'exercise': {'min': 1, 'max': 1000, 'recommended': 100},
                'fitness': {'min': 1, 'max': 365, 'recommended': 30}
            },
            '学习': {
                'books': {'min': 1, 'max': 100, 'recommended': 10},
                'courses': {'min': 1, 'max': 50, 'recommended': 5},
                'skills': {'min': 1, 'max': 20, 'recommended': 3}
            },
            '工作': {
                'projects': {'min': 1, 'max': 50, 'recommended': 5},
                'tasks': {'min': 1, 'max': 200, 'recommended': 20},
                'clients': {'min': 1, 'max': 100, 'recommended': 10}
            },
            '生活': {
                'travel': {'min': 1, 'max': 20, 'recommended': 3},
                'finance': {'min': 1000, 'max': 1000000, 'recommended': 50000},
                'hobbies': {'min': 1, 'max': 50, 'recommended': 5}
            }
        }
        
        # SMART原则权重配置
        self.smart_weights = {
            'specific': 20,     # 具体性权重
            'measurable': 25,   # 可衡量性权重
            'achievable': 20,   # 可实现性权重
            'relevant': 15,     # 相关性权重
            'time_bound': 20    # 时限性权重
        }
        
        # 关键词模式用于智能分析
        self.analysis_patterns = {
            'specific_keywords': ['具体', '明确', '详细', '清晰', '准确'],
            'vague_keywords': ['大概', '可能', '也许', '差不多', '左右'],
            'action_keywords': ['完成', '实现', '达到', '获得', '掌握', '学会'],
            'measurement_keywords': ['数量', '质量', '时间', '频率', '程度', '比例']
        }
    
    def validate_goal(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证目标是否符合SMART原则
        
        Args:
            goal_data: 目标数据
        
        Returns:
            验证结果和建议
        """
        logger.info(f"开始验证目标: {goal_data}")
        
        errors = []
        warnings = []
        suggestions = []
        
        # 1. 检查时间设置 (Time-bound)
        time_validation = self._validate_time_setting(goal_data)
        errors.extend(time_validation['errors'])
        warnings.extend(time_validation['warnings'])
        suggestions.extend(time_validation['suggestions'])
        
        # 2. 检查量化指标 (Measurable)
        quantity_validation = self._validate_quantification(goal_data)
        errors.extend(quantity_validation['errors'])
        warnings.extend(quantity_validation['warnings'])
        suggestions.extend(quantity_validation['suggestions'])
        
        # 3. 检查目标描述 (Specific)
        description_validation = self._validate_description(goal_data)
        errors.extend(description_validation['errors'])
        warnings.extend(description_validation['warnings'])
        suggestions.extend(description_validation['suggestions'])
        
        # 4. 检查目标类别 (Relevant)
        category_validation = self._validate_category(goal_data)
        errors.extend(category_validation['errors'])
        warnings.extend(category_validation['warnings'])
        suggestions.extend(category_validation['suggestions'])
        
        # 5. 检查可实现性 (Achievable)
        achievability_validation = self._validate_achievability(goal_data)
        errors.extend(achievability_validation['errors'])
        warnings.extend(achievability_validation['warnings'])
        suggestions.extend(achievability_validation['suggestions'])
        
        # 计算SMART原则各项得分
        smart_scores = self._calculate_smart_scores(goal_data)
        
        # 构建验证结果
        validation_result = {
            'is_valid': len(errors) == 0,
            'has_warnings': len(warnings) > 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'score': self._calculate_validation_score(goal_data, errors, warnings),
            'smart_scores': smart_scores,
            'smart_analysis': self._generate_smart_analysis(goal_data, smart_scores)
        }
        
        logger.info(f"目标验证完成: {validation_result}")
        return validation_result
    
    def _validate_time_setting(self, goal_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证时间设置"""
        errors = []
        warnings = []
        suggestions = []
        
        start_date = goal_data.get('startDate')
        end_date = goal_data.get('endDate')
        
        if not start_date or not end_date:
            errors.append('目标必须设置明确的开始和结束时间')
            suggestions.append('建议设置具体的时间范围，如"3个月内"')
            return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
        
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            duration = (end - start).days
            
            # 检查时间范围合理性
            if duration < self.time_rules['min_days']:
                errors.append(f'目标时间过短，建议至少设置{self.time_rules["min_days"]}天以上')
                suggestions.append(f'建议将时间调整为{self.time_rules["recommended_min"]}-{self.time_rules["recommended_max"]}天')
            
            elif duration > self.time_rules['max_days']:
                errors.append(f'目标时间过长，建议分解为阶段性目标')
                suggestions.append(f'建议将时间控制在{self.time_rules["recommended_max"]}天以内')
            
            elif duration < self.time_rules['recommended_min']:
                warnings.append(f'目标时间较短，可能难以实现预期效果')
                suggestions.append(f'建议考虑延长到{self.time_rules["recommended_min"]}天以上')
            
            elif duration > self.time_rules['recommended_max']:
                warnings.append(f'目标时间较长，建议分解为多个阶段')
                suggestions.append(f'建议每{self.time_rules["recommended_max"]}天为一个阶段')
            
            # 检查开始时间合理性（只比较日期部分）
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date_only = start.replace(hour=0, minute=0, second=0, microsecond=0)
            if start_date_only < today:
                warnings.append('目标开始时间已过，建议调整为今天或未来时间')
                suggestions.append('建议从今天开始，重新计算时间范围')
            
        except Exception as e:
            errors.append(f'时间格式错误: {str(e)}')
            suggestions.append('请使用正确的日期格式：YYYY-MM-DD')
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_quantification(self, goal_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证量化指标"""
        errors = []
        warnings = []
        suggestions = []
        
        target_value = goal_data.get('targetValue')
        current_value = goal_data.get('currentValue', '0')
        unit = goal_data.get('unit')
        
        if not target_value or not unit:
            errors.append('目标必须设置具体的数值和单位')
            suggestions.append('建议设置明确的数值，如"减重10斤"、"学习5本书"')
            return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
        
        try:
            target = float(target_value)
            current = float(current_value)
            
            # 检查数值合理性
            if target <= 0:
                errors.append('目标值必须大于0')
                suggestions.append('请设置一个正数的目标值')
                return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
            
            # 根据类别检查数值范围
            category = goal_data.get('category', '其他')
            if category in self.value_rules:
                category_rules = self.value_rules[category]
                # 找到合适的规则类型（根据单位或其他特征）
                applicable_rules = None
                for rule_type, rules in category_rules.items():
                    if 'min' in rules and 'max' in rules:
                        applicable_rules = rules
                        break
                
                if applicable_rules:
                    if target < applicable_rules['min']:
                        warnings.append(f'目标值较小，可能缺乏挑战性')
                        suggestions.append(f'建议设置{applicable_rules["recommended"]}作为目标值')
                    
                    elif target > applicable_rules['max']:
                        warnings.append(f'目标值较大，可能难以实现')
                        suggestions.append(f'建议分解为多个阶段，每阶段{applicable_rules["recommended"]}')
                    
                    elif target > applicable_rules['recommended']:
                        warnings.append(f'目标值较高，建议分阶段实现')
                        suggestions.append(f'可以考虑先实现{applicable_rules["recommended"]}，再逐步提升')
            
            # 检查目标值与当前值的差异
            if target <= current:
                warnings.append('目标值应该大于当前值')
                suggestions.append('请设置一个高于当前值的目标')
            
        except ValueError:
            errors.append('目标值必须是有效的数字')
            suggestions.append('请使用数字格式，如"10"、"5.5"等')
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_description(self, goal_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证目标描述 (Specific - 具体性)"""
        errors = []
        warnings = []
        suggestions = []
        
        title = goal_data.get('title', '')
        description = goal_data.get('description', '')
        full_text = f"{title} {description}"
        
        # 检查标题长度
        if not title or len(title.strip()) < 5:
            errors.append('目标标题过短，请提供更详细的描述')
            suggestions.append('建议描述包含：做什么、怎么做、达到什么效果')
        elif len(title) > 100:
            warnings.append('目标标题过长，建议简洁明了')
            suggestions.append('建议控制在50字以内，突出核心要点')
        
        # 检查描述详细程度
        if not description or len(description.strip()) < 10:
            warnings.append('目标描述不够详细，可能影响执行效果')
            suggestions.append('建议补充实现方法、关键步骤等信息')
        
        # 检查具体性关键词
        specific_score = self._analyze_specificity(full_text)
        if specific_score < 0.3:
            warnings.append('目标描述较为模糊，建议更加具体明确')
            suggestions.append('建议使用具体数字、时间、地点等明确信息')
        elif specific_score > 0.8:
            suggestions.append('目标描述非常具体，这有助于执行和跟踪')
        
        # 检查是否包含行动关键词
        if not any(keyword in full_text for keyword in self.analysis_patterns['action_keywords']):
            warnings.append('目标描述缺少明确的行动动词')
            suggestions.append('建议使用"完成"、"实现"、"达到"等明确的行动词')
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_category(self, goal_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证目标类别"""
        errors = []
        warnings = []
        suggestions = []
        
        category = goal_data.get('category', '')
        valid_categories = ['健康', '学习', '工作', '生活', '其他']
        
        if not category:
            errors.append('必须选择目标类别')
            suggestions.append('请从预设类别中选择一个')
        elif category not in valid_categories:
            warnings.append(f'目标类别"{category}"不在预设范围内')
            suggestions.append(f'建议选择：{", ".join(valid_categories)}')
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_achievability(self, goal_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证目标可实现性 (Achievable)"""
        errors = []
        warnings = []
        suggestions = []
        
        target_value = goal_data.get('targetValue')
        start_date = goal_data.get('startDate')
        end_date = goal_data.get('endDate')
        category = goal_data.get('category', '其他')
        
        if not target_value or not start_date or not end_date:
            return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
        
        try:
            target = float(target_value)
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            duration_days = (end - start).days
            
            # 计算每日目标量
            daily_target = target / duration_days if duration_days > 0 else 0
            
            # 根据类别和数值评估可实现性
            achievability_score = self._assess_achievability(category, target, duration_days, daily_target)
            
            if achievability_score < 0.3:
                errors.append('目标可能过于困难，建议降低难度或延长时间')
                suggestions.append('建议分解为更小的阶段性目标，逐步实现')
            elif achievability_score < 0.6:
                warnings.append('目标具有一定挑战性，需要持续努力')
                suggestions.append('建议制定详细的执行计划，定期检查进度')
            elif achievability_score > 0.8:
                warnings.append('目标可能过于简单，缺乏挑战性')
                suggestions.append('建议适当提高目标难度，增加挑战性')
            
            # 检查每日目标量是否合理
            if daily_target > 0:
                if daily_target > 10:  # 每日目标过大
                    warnings.append('每日目标量较大，可能难以坚持')
                    suggestions.append('建议调整时间范围或降低总目标量')
                elif daily_target < 0.1:  # 每日目标过小
                    warnings.append('每日目标量较小，可能缺乏紧迫感')
                    suggestions.append('建议适当提高目标量或缩短时间范围')
            
        except (ValueError, TypeError):
            pass
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _calculate_validation_score(self, goal_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> int:
        """计算验证评分 (0-100)"""
        base_score = 100
        
        # 错误扣分：每个错误扣20分
        error_penalty = len(errors) * 20
        
        # 警告扣分：每个警告扣5分
        warning_penalty = len(warnings) * 5
        
        # 时间合理性加分：合理时间范围加10分
        time_bonus = 0
        start_date = goal_data.get('startDate')
        end_date = goal_data.get('endDate')
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                duration = (end - start).days
                if self.time_rules['recommended_min'] <= duration <= self.time_rules['recommended_max']:
                    time_bonus = 10
            except:
                pass
        
        # 量化指标加分：有明确数值和单位加10分
        quantity_bonus = 0
        if goal_data.get('targetValue') and goal_data.get('unit'):
            quantity_bonus = 10
        
        final_score = max(0, base_score - error_penalty - warning_penalty + time_bonus + quantity_bonus)
        return final_score
    
    def _analyze_specificity(self, text: str) -> float:
        """分析文本的具体性得分 (0-1)"""
        if not text:
            return 0.0
        
        specific_count = sum(1 for keyword in self.analysis_patterns['specific_keywords'] if keyword in text)
        vague_count = sum(1 for keyword in self.analysis_patterns['vague_keywords'] if keyword in text)
        
        # 检查数字、时间、地点等具体信息
        has_numbers = bool(re.search(r'\d+', text))
        has_time = bool(re.search(r'\d+[天月年周]', text))
        has_measurement = any(keyword in text for keyword in self.analysis_patterns['measurement_keywords'])
        
        # 计算具体性得分
        specificity_score = 0.0
        specificity_score += specific_count * 0.2
        specificity_score -= vague_count * 0.3
        specificity_score += 0.3 if has_numbers else 0
        specificity_score += 0.2 if has_time else 0
        specificity_score += 0.2 if has_measurement else 0
        
        return max(0.0, min(1.0, specificity_score))
    
    def _assess_achievability(self, category: str, target: float, duration_days: int, daily_target: float) -> float:
        """评估目标可实现性 (0-1)"""
        achievability_score = 0.5  # 基础分数
        
        # 根据类别调整
        if category in self.value_rules:
            category_rules = self.value_rules[category]
            for rule_type, rules in category_rules.items():
                try:
                    if 'min' in rules and 'max' in rules:
                        if rules['min'] <= target <= rules['max']:
                            achievability_score += 0.2
                        elif target > rules['max']:
                            achievability_score -= 0.3
                        elif target < rules['min']:
                            achievability_score += 0.1
                except (TypeError, ValueError):
                    # 如果target不是数字，跳过数值比较
                    pass
        
        # 根据时间范围调整
        if self.time_rules['recommended_min'] <= duration_days <= self.time_rules['recommended_max']:
            achievability_score += 0.2
        elif duration_days < self.time_rules['min_days']:
            achievability_score -= 0.3
        elif duration_days > self.time_rules['max_days']:
            achievability_score -= 0.2
        
        # 根据每日目标量调整
        if 0.1 <= daily_target <= 5:
            achievability_score += 0.1
        elif daily_target > 10:
            achievability_score -= 0.2
        elif daily_target < 0.01:
            achievability_score -= 0.1
        
        return max(0.0, min(1.0, achievability_score))
    
    def _calculate_smart_scores(self, goal_data: Dict[str, Any]) -> Dict[str, float]:
        """计算SMART原则各项得分"""
        scores = {}
        
        # Specific (具体性)
        title = goal_data.get('title', '')
        description = goal_data.get('description', '')
        full_text = f"{title} {description}"
        scores['specific'] = self._analyze_specificity(full_text)
        
        # Measurable (可衡量性)
        target_value = goal_data.get('targetValue')
        unit = goal_data.get('unit')
        if target_value and unit:
            scores['measurable'] = 1.0
        elif target_value or unit:
            scores['measurable'] = 0.5
        else:
            scores['measurable'] = 0.0
        
        # Achievable (可实现性)
        if target_value and goal_data.get('startDate') and goal_data.get('endDate'):
            try:
                target = float(target_value) if target_value else 0
                start = datetime.fromisoformat(goal_data['startDate'])
                end = datetime.fromisoformat(goal_data['endDate'])
                duration_days = (end - start).days
                daily_target = target / duration_days if duration_days > 0 else 0
                scores['achievable'] = self._assess_achievability(
                    goal_data.get('category', '其他'), target, duration_days, daily_target
                )
            except (ValueError, TypeError, AttributeError):
                scores['achievable'] = 0.5
        else:
            scores['achievable'] = 0.0
        
        # Relevant (相关性)
        category = goal_data.get('category', '')
        valid_categories = ['健康', '学习', '工作', '生活', '其他']
        if category in valid_categories:
            scores['relevant'] = 1.0
        elif category:
            scores['relevant'] = 0.7
        else:
            scores['relevant'] = 0.0
        
        # Time-bound (时限性)
        start_date = goal_data.get('startDate')
        end_date = goal_data.get('endDate')
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                duration = (end - start).days
                if self.time_rules['recommended_min'] <= duration <= self.time_rules['recommended_max']:
                    scores['time_bound'] = 1.0
                elif self.time_rules['min_days'] <= duration <= self.time_rules['max_days']:
                    scores['time_bound'] = 0.7
                else:
                    scores['time_bound'] = 0.3
            except:
                scores['time_bound'] = 0.5
        else:
            scores['time_bound'] = 0.0
        
        return scores
    
    def _generate_smart_analysis(self, goal_data: Dict[str, Any], smart_scores: Dict[str, float]) -> Dict[str, Any]:
        """生成SMART原则分析报告"""
        analysis = {
            'overall_score': sum(smart_scores.values()) / len(smart_scores),
            'strengths': [],
            'weaknesses': [],
            'improvements': []
        }
        
        # 分析各项得分
        for principle, score in smart_scores.items():
            if score >= 0.8:
                analysis['strengths'].append(f"{self._get_principle_name(principle)}表现优秀")
            elif score < 0.5:
                analysis['weaknesses'].append(f"{self._get_principle_name(principle)}需要改进")
                analysis['improvements'].extend(self._get_improvement_suggestions(principle, score))
        
        return analysis
    
    def _get_principle_name(self, principle: str) -> str:
        """获取SMART原则中文名称"""
        names = {
            'specific': '具体性',
            'measurable': '可衡量性',
            'achievable': '可实现性',
            'relevant': '相关性',
            'time_bound': '时限性'
        }
        return names.get(principle, principle)
    
    def _get_improvement_suggestions(self, principle: str, score: float) -> List[str]:
        """获取改进建议"""
        suggestions = {
            'specific': [
                '使用更具体的描述，包含数字、时间、地点等明确信息',
                '避免使用模糊词汇，如"大概"、"可能"等'
            ],
            'measurable': [
                '设置明确的数值目标和单位',
                '定义清晰的衡量标准和评估方法'
            ],
            'achievable': [
                '评估目标的现实可行性',
                '考虑分解为更小的阶段性目标'
            ],
            'relevant': [
                '确保目标与个人或组织目标相关',
                '选择合适的目标类别'
            ],
            'time_bound': [
                '设置明确的开始和结束时间',
                '确保时间范围合理，既不过短也不过长'
            ]
        }
        return suggestions.get(principle, [])

# 创建全局实例
goal_validator = GoalValidator()
