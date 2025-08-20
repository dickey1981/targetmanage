"""
用户模型
User model for authentication and profile management
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    
    # 个人信息
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    gender = Column(Integer, default=0, comment="性别：0-未知，1-男，2-女")
    birthday = Column(DateTime, nullable=True, comment="生日")
    bio = Column(Text, nullable=True, comment="个人简介")
    
    # 微信信息
    wechat_openid = Column(String(100), unique=True, index=True, nullable=True, comment="微信OpenID")
    wechat_unionid = Column(String(100), unique=True, index=True, nullable=True, comment="微信UnionID")
    wechat_nickname = Column(String(100), nullable=True, comment="微信昵称")
    wechat_avatar = Column(String(255), nullable=True, comment="微信头像")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否验证")
    is_superuser = Column(Boolean, default=False, comment="是否超级用户")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 设置信息
    timezone = Column(String(50), default="Asia/Shanghai", comment="时区")
    language = Column(String(10), default="zh-CN", comment="语言")
    
    # 关联关系
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    progresses = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
    
    @property
    def display_name(self):
        """显示名称"""
        return self.nickname or self.username
    
    def is_goal_owner(self, goal_id: int) -> bool:
        """检查是否为目标的所有者"""
        return any(goal.id == goal_id for goal in self.goals)
