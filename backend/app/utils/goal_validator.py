"""
目标验证工具模块
验证目标是否符合SMART原则，并提供智能建议
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

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
            'weight': {
                'min': 1,       # 最小减重：1斤
                'max': 50,      # 最大减重：50斤
                'recommended': 20   # 推荐减重：20斤
            },
            'study': {
                'min': 1,       # 最少学习：1本书
                'max': 100,     # 最多学习：100本书
                'recommended': 10   # 推荐学习：10本书
            },
            'exercise': {
                'min': 1,       # 最少运动：1公里
                'max': 1000,    # 最多运动：1000公里
                'recommended': 100  # 推荐运动：100公里
            }
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
        
        # 构建验证结果
        validation_result = {
            'is_valid': len(errors) == 0,
            'has_warnings': len(warnings) > 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'score': self._calculate_validation_score(goal_data, errors, warnings)
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
            
            # 检查开始时间合理性
            if start < datetime.now():
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
                
                if target < category_rules['min']:
                    warnings.append(f'目标值较小，可能缺乏挑战性')
                    suggestions.append(f'建议设置{category_rules["recommended"]}作为目标值')
                
                elif target > category_rules['max']:
                    warnings.append(f'目标值较大，可能难以实现')
                    suggestions.append(f'建议分解为多个阶段，每阶段{category_rules["recommended"]}')
                
                elif target > category_rules['recommended']:
                    warnings.append(f'目标值较高，建议分阶段实现')
                    suggestions.append(f'可以考虑先实现{category_rules["recommended"]}，再逐步提升')
            
            # 检查目标值与当前值的差异
            if target <= current:
                warnings.append('目标值应该大于当前值')
                suggestions.append('请设置一个高于当前值的目标')
            
        except ValueError:
            errors.append('目标值必须是有效的数字')
            suggestions.append('请使用数字格式，如"10"、"5.5"等')
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_description(self, goal_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证目标描述"""
        errors = []
        warnings = []
        suggestions = []
        
        title = goal_data.get('title', '')
        description = goal_data.get('description', '')
        
        if not title or len(title.strip()) < 5:
            errors.append('目标标题过短，请提供更详细的描述')
            suggestions.append('建议描述包含：做什么、怎么做、达到什么效果')
        
        if len(title) > 100:
            warnings.append('目标标题过长，建议简洁明了')
            suggestions.append('建议控制在50字以内，突出核心要点')
        
        if not description or len(description.strip()) < 10:
            warnings.append('目标描述不够详细，可能影响执行效果')
            suggestions.append('建议补充实现方法、关键步骤等信息')
        
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
        """验证目标可实现性"""
        errors = []
        warnings = []
        suggestions = []
        
        # 这里可以添加更复杂的可实现性检查逻辑
        # 比如基于用户历史数据、目标难度评估等
        
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

# 创建全局实例
goal_validator = GoalValidator()
