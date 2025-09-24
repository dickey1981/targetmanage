"""
目标进度更新服务
Goal progress update service
"""

from sqlalchemy.orm import Session
from app.models.goal import Goal, GoalStatus
from app.models.process_record import ProcessRecord, ProcessRecordType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GoalProgressService:
    """目标进度更新服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def update_goal_progress_from_record(self, goal_id: str, record: ProcessRecord) -> bool:
        """基于过程记录更新目标进度"""
        try:
            # 使用原生SQL查询目标，避免模型字段不匹配问题
            from sqlalchemy import text
            result = self.db.execute(text("""
                SELECT id, title, target_value, current_value, status, completed_at
                FROM goals WHERE id = :goal_id
            """), {"goal_id": goal_id})
            
            goal_row = result.fetchone()
            if not goal_row:
                logger.warning(f"目标不存在: {goal_id}")
                return False
            
            # 创建简单的目标对象
            class SimpleGoal:
                def __init__(self, row):
                    self.id = row[0]
                    self.title = row[1]
                    self.target_value = row[2]
                    self.current_value = row[3]
                    self.status = row[4]
                    self.completed_at = row[5]
            
            goal = SimpleGoal(goal_row)
            
            # 根据记录类型更新进度
            progress_increment = self._calculate_progress_increment(record)
            
            if progress_increment > 0:
                # 计算新进度（基于current_value和target_value）
                try:
                    target_value = float(goal.target_value) if goal.target_value else 100.0
                    current_value = float(goal.current_value) if goal.current_value else 0.0
                    
                    # 根据进度增量更新current_value
                    new_current_value = min(target_value, current_value + (target_value * progress_increment / 100.0))
                    new_progress = (new_current_value / target_value) * 100.0 if target_value > 0 else 0.0
                    
                    # 使用原生SQL更新目标
                    if new_progress >= 100.0 and goal.status != 'completed':
                        # 完成目标
                        self.db.execute(text("""
                            UPDATE goals SET 
                                current_value = :current_value,
                                status = 'completed',
                                completed_at = NOW()
                            WHERE id = :goal_id
                        """), {
                            "current_value": str(new_current_value),
                            "goal_id": goal_id
                        })
                    else:
                        # 更新进度
                        self.db.execute(text("""
                            UPDATE goals SET current_value = :current_value WHERE id = :goal_id
                        """), {
                            "current_value": str(new_current_value),
                            "goal_id": goal_id
                        })
                    
                    self.db.commit()
                    
                    logger.info(f"目标 {goal_id} 进度更新: {current_value} -> {new_current_value} ({new_progress:.1f}%)")
                    return True
                except (ValueError, TypeError) as e:
                    logger.error(f"进度计算失败: {e}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"更新目标进度失败: {e}")
            self.db.rollback()
            return False
    
    def _calculate_progress_increment(self, record: ProcessRecord) -> float:
        """计算进度增量"""
        # 根据记录类型和内容计算进度增量
        base_increment = 0.0
        
        if record.record_type == ProcessRecordType.progress:
            # 进度记录：根据内容中的数值计算
            base_increment = self._extract_progress_from_content(record.content)
        elif record.record_type == ProcessRecordType.milestone:
            # 里程碑：较大进度增量
            base_increment = 10.0
        elif record.record_type == ProcessRecordType.achievement:
            # 成就：中等进度增量
            base_increment = 5.0
        elif record.record_type == ProcessRecordType.process:
            # 过程记录：小进度增量
            base_increment = 1.0
        elif record.record_type == ProcessRecordType.method:
            # 方法记录：小进度增量
            base_increment = 0.5
        elif record.record_type == ProcessRecordType.reflection:
            # 反思记录：小进度增量
            base_increment = 0.5
        
        # 根据重要程度调整
        if record.is_important:
            base_increment *= 1.5
        if record.is_breakthrough:
            base_increment *= 2.0
        if record.is_milestone:
            base_increment *= 3.0
        
        # 根据情感调整
        if record.sentiment == "positive":
            base_increment *= 1.2
        elif record.sentiment == "negative":
            base_increment *= 0.8
        
        return min(20.0, base_increment)  # 单次最大增量20%
    
    def _extract_progress_from_content(self, content: str) -> float:
        """从内容中提取进度数值"""
        import re
        
        # 匹配百分比
        percentage_match = re.search(r'(\d+(?:\.\d+)?)%', content)
        if percentage_match:
            return float(percentage_match.group(1))
        
        # 匹配分数
        fraction_match = re.search(r'(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)', content)
        if fraction_match:
            numerator = float(fraction_match.group(1))
            denominator = float(fraction_match.group(2))
            if denominator > 0:
                return (numerator / denominator) * 100
        
        # 匹配"完成了X"模式
        completion_match = re.search(r'完成了?\s*(\d+(?:\.\d+)?)', content)
        if completion_match:
            return float(completion_match.group(1))
        
        # 匹配"进度X"模式
        progress_match = re.search(r'进度\s*(\d+(?:\.\d+)?)', content)
        if progress_match:
            return float(progress_match.group(1))
        
        return 0.0
    
    def get_goal_progress_summary(self, goal_id: str) -> dict:
        """获取目标进度摘要"""
        try:
            # 使用原生SQL查询目标
            from sqlalchemy import text
            result = self.db.execute(text("""
                SELECT id, title, target_value, current_value, status, completed_at
                FROM goals WHERE id = :goal_id
            """), {"goal_id": goal_id})
            
            goal_row = result.fetchone()
            if not goal_row:
                return {}
            
            # 创建简单的目标对象
            class SimpleGoal:
                def __init__(self, row):
                    self.id = row[0]
                    self.title = row[1]
                    self.target_value = row[2]
                    self.current_value = row[3]
                    self.status = row[4]
                    self.completed_at = row[5]
            
            goal = SimpleGoal(goal_row)
            
            # 获取相关记录统计
            records = self.db.query(ProcessRecord).filter(
                ProcessRecord.goal_id == goal_id
            ).all()
            
            # 按类型统计
            records_by_type = {}
            for record in records:
                type_name = record.record_type.value
                records_by_type[type_name] = records_by_type.get(type_name, 0) + 1
            
            # 里程碑和突破统计
            milestone_count = sum(1 for r in records if r.is_milestone)
            breakthrough_count = sum(1 for r in records if r.is_breakthrough)
            
            # 计算当前进度
            try:
                target_value = float(goal.target_value) if goal.target_value else 100.0
                current_value = float(goal.current_value) if goal.current_value else 0.0
                current_progress = (current_value / target_value * 100) if target_value > 0 else 0.0
            except (ValueError, TypeError):
                current_progress = 0.0
            
            return {
                "goal_id": goal_id,
                "current_progress": current_progress,
                "current_value": current_value,
                "target_value": target_value,
                "status": str(goal.status),
                "total_records": len(records),
                "records_by_type": records_by_type,
                "milestone_count": milestone_count,
                "breakthrough_count": breakthrough_count,
                "is_completed": goal.status == 'completed',
                "completed_at": goal.completed_at.isoformat() if goal.completed_at else None
            }
            
        except Exception as e:
            logger.error(f"获取目标进度摘要失败: {e}")
            return {}
