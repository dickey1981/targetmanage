"""
目标模型
Goal model for goal management
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import BaseModel


class GoalStatus(enum.Enum):
    """目标状态枚举"""
    DRAFT = "draft"          # 草稿
    ACTIVE = "active"        # 进行中
    PAUSED = "paused"        # 暂停
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class GoalPriority(enum.Enum):
    """目标优先级枚举"""
    LOW = "low"        # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"      # 高
    URGENT = "urgent"  # 紧急


class GoalCategory(enum.Enum):
    """目标分类枚举"""
    WORK = "work"              # 工作
    STUDY = "study"            # 学习
    HEALTH = "health"          # 健康
    FINANCE = "finance"        # 财务
    RELATIONSHIP = "relationship"  # 人际关系
    PERSONAL = "personal"      # 个人发展
    HOBBY = "hobby"            # 兴趣爱好
    OTHER = "other"            # 其他


class Goal(BaseModel):
    """目标模型"""
    
    __tablename__ = "goals"
    
    # 基本信息
    title = Column(String(200), nullable=False, comment="目标标题")
    description = Column(Text, nullable=True, comment="目标描述")
    category = Column(String(50), default="personal", comment="目标分类")
    priority = Column(String(20), default="medium", comment="优先级")
    status = Column(String(20), default="draft", comment="状态")
    
    # 时间相关
    start_date = Column(DateTime, nullable=True, comment="开始时间")
    end_date = Column(DateTime, nullable=True, comment="截止时间")
    target_date = Column(DateTime, nullable=True, comment="目标日期")
    
    # 目标值相关
    target_value = Column(String(100), nullable=True, comment="目标值")
    current_value = Column(String(100), nullable=True, comment="当前值")
    unit = Column(String(50), nullable=True, comment="单位")
    
    # 提醒设置
    daily_reminder = Column(Boolean, default=True, comment="每日提醒")
    deadline_reminder = Column(Boolean, default=True, comment="截止提醒")
    
    # 关联字段
    user_id = Column(String(36), nullable=False, comment="用户ID")
    
    # 关联关系 - 暂时简化，只保留必要的
    # user = relationship("User", back_populates="goals", lazy="select")
    
    # 暂时注释掉其他关系，避免循环导入
    # tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan", lazy="select")
    # progresses = relationship("Progress", back_populates="goal", cascade="all, delete-orphan", lazy="select")
    # parent_goal = relationship("Goal", remote_side="Goal.id", backref="sub_goals", lazy="select")
    
    def __repr__(self):
        return f"<Goal(id={self.id}, title='{self.title}', status='{self.status.value}')>"
    
    @property
    def is_overdue(self) -> bool:
        """是否已过期"""
        if not self.end_date:
            return False
        return datetime.utcnow() > self.end_date and not self.is_completed
    
    @property
    def days_remaining(self) -> int:
        """剩余天数"""
        if not self.end_date:
            return -1
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)
    
    def update_progress(self):
        """更新目标进度"""
        if self.total_tasks > 0:
            self.progress_percentage = (self.completed_tasks / self.total_tasks) * 100
            if self.progress_percentage >= 100:
                self.is_completed = True
                self.status = GoalStatus.COMPLETED
                self.completed_at = datetime.utcnow()
