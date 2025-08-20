"""
任务模型
Task model for task management
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import BaseModel


class TaskStatus(enum.Enum):
    """任务状态枚举"""
    TODO = "todo"              # 待办
    IN_PROGRESS = "in_progress" # 进行中
    REVIEW = "review"          # 待审核
    COMPLETED = "completed"    # 已完成
    CANCELLED = "cancelled"    # 已取消


class TaskPriority(enum.Enum):
    """任务优先级枚举"""
    LOW = "low"        # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"      # 高
    URGENT = "urgent"  # 紧急


class Task(BaseModel):
    """任务模型"""
    
    __tablename__ = "tasks"
    
    # 基本信息
    title = Column(String(200), nullable=False, comment="任务标题")
    description = Column(Text, nullable=True, comment="任务描述")
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, comment="优先级")
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, comment="状态")
    
    # 时间相关
    start_date = Column(DateTime, nullable=True, comment="开始时间")
    due_date = Column(DateTime, nullable=True, comment="截止时间")
    estimated_hours = Column(Float, nullable=True, comment="预估工时")
    actual_hours = Column(Float, nullable=True, comment="实际工时")
    
    # 完成相关
    is_completed = Column(Boolean, default=False, comment="是否完成")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    completion_note = Column(Text, nullable=True, comment="完成备注")
    
    # 任务设置
    is_recurring = Column(Boolean, default=False, comment="是否重复任务")
    recurring_pattern = Column(String(50), nullable=True, comment="重复模式")
    
    # 提醒设置
    reminder_enabled = Column(Boolean, default=True, comment="是否启用提醒")
    reminder_time = Column(DateTime, nullable=True, comment="提醒时间")
    
    # 关联字段
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True, comment="目标ID")
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, comment="父任务ID")
    
    # 排序字段
    order_index = Column(Integer, default=0, comment="排序索引")
    
    # 关联关系
    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    progresses = relationship("Progress", back_populates="task", cascade="all, delete-orphan")
    
    # 自关联（父子任务）
    parent_task = relationship("Task", remote_side="Task.id", backref="sub_tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status.value}')>"
    
    @property
    def is_overdue(self) -> bool:
        """是否已过期"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and not self.is_completed
    
    @property
    def days_remaining(self) -> int:
        """剩余天数"""
        if not self.due_date:
            return -1
        delta = self.due_date - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def hours_remaining(self) -> float:
        """剩余工时"""
        if not self.estimated_hours:
            return 0.0
        actual = self.actual_hours or 0.0
        return max(0.0, self.estimated_hours - actual)
    
    def mark_completed(self, completion_note: str = None):
        """标记任务完成"""
        self.is_completed = True
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if completion_note:
            self.completion_note = completion_note
            
        # 更新关联目标的进度
        if self.goal:
            self.goal.completed_tasks += 1
            self.goal.update_progress()
