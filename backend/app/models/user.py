"""
用户数据模型
"""
from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from ..database import Base

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wechat_id = Column(String(100), unique=True, nullable=False, index=True)
    nickname = Column(String(100), nullable=False)
    avatar = Column(Text, nullable=True)
    phone_number = Column(String(20), nullable=True, index=True)
    email = Column(String(100), nullable=True, index=True)
    
    # 用户偏好设置
    notification_enabled = Column(Boolean, default=True)
    privacy_level = Column(String(20), default="public")  # public, friends, private
    
    # 统计信息
    total_goals = Column(String(10), default="0")
    completed_goals = Column(String(10), default="0")
    streak_days = Column(String(10), default="0")
    
    # 安全相关
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(String(10), default="0")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # 软删除
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    login_attempts = relationship("LoginAttempt", back_populates="user", cascade="all, delete-orphan")
    verifications = relationship("UserVerification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, nickname='{self.nickname}')>"

    @property
    def is_locked_out(self):
        """检查用户是否被锁定"""
        if not self.is_locked:
            return False
        if self.locked_until and datetime.utcnow() > self.locked_until:
            self.is_locked = False
            self.locked_until = None
            return False
        return True

    def increment_failed_login_attempts(self):
        """增加失败登录次数"""
        current = int(self.failed_login_attempts)
        self.failed_login_attempts = str(current + 1)
        if current + 1 >= 5:  # 5次失败后锁定
            self.is_locked = True
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def reset_failed_login_attempts(self):
        """重置失败登录次数"""
        self.failed_login_attempts = "0"
        self.is_locked = False
        self.locked_until = None

# Pydantic模型
class UserBase(BaseModel):
    wechat_id: str
    nickname: str
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    notification_enabled: Optional[bool] = None
    privacy_level: Optional[str] = None

class UserInDB(UserBase):
    id: uuid.UUID
    notification_enabled: bool
    privacy_level: str
    total_goals: str
    completed_goals: str
    streak_days: str
    is_verified: bool
    is_active: bool
    is_locked: bool
    locked_until: Optional[datetime] = None
    failed_login_attempts: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    wechat_id: str
    nickname: str
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    notification_enabled: bool
    privacy_level: str
    total_goals: str
    completed_goals: str
    streak_days: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    notification_enabled: Optional[bool] = None
    privacy_level: Optional[str] = None

class UserStats(BaseModel):
    total_goals: str
    completed_goals: str
    streak_days: str
    completion_rate: float
    current_streak: int
