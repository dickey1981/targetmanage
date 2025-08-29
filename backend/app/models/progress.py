"""
进度记录模型
Progress tracking model
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class Progress(BaseModel):
    """进度记录模型"""
    
    __tablename__ = "progresses"
    
    # 基本信息
    title = Column(String(200), nullable=True, comment="进度标题")
    description = Column(Text, nullable=True, comment="进度描述")
    progress_type = Column(String(50), default="manual", comment="进度类型：manual-手动，auto-自动")
    
    # 进度数据
    progress_value = Column(Float, nullable=False, comment="进度值")
    progress_unit = Column(String(20), default="percent", comment="进度单位：percent-百分比，count-计数，hours-小时")
    previous_value = Column(Float, nullable=True, comment="前一次进度值")
    
    # 时间信息
    recorded_at = Column(DateTime, default=datetime.utcnow, comment="记录时间")
    
    # 附加信息
    notes = Column(Text, nullable=True, comment="进度备注")
    attachments = Column(JSON, nullable=True, comment="附件信息")
    location = Column(String(200), nullable=True, comment="记录地点")
    
    # 数据来源
    source = Column(String(50), default="manual", comment="数据来源：manual-手动，wechat-微信，voice-语音，image-图片")
    source_data = Column(JSON, nullable=True, comment="源数据")
    
    # 关联字段
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True, comment="目标ID")
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, comment="任务ID")
    
    # 关联关系 - 暂时注释掉，避免循环导入
    # user = relationship("User", back_populates="progresses")
    # goal = relationship("Goal", back_populates="progresses")
    # task = relationship("Task", back_populates="progresses")
    
    def __repr__(self):
        return f"<Progress(id={self.id}, value={self.progress_value}, type='{self.progress_type}')>"
    
    @property
    def progress_change(self) -> float:
        """进度变化量"""
        if self.previous_value is None:
            return self.progress_value
        return self.progress_value - self.previous_value
    
    @property
    def is_improvement(self) -> bool:
        """是否为进步"""
        return self.progress_change > 0
    
    def to_dict_with_change(self):
        """包含变化信息的字典"""
        data = self.to_dict()
        data.update({
            "progress_change": self.progress_change,
            "is_improvement": self.is_improvement
        })
        return data
