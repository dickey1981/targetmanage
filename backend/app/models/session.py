"""
用户会话和登录记录模型
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..database import Base

class UserSession(Base):
    """用户会话表"""
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(Text, nullable=True)  # 设备信息
    ip_address = Column(String(45), nullable=True)  # IP地址
    user_agent = Column(Text, nullable=True)  # 用户代理
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系 - 暂时注释掉，避免循环导入
    # user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"

class LoginAttempt(Base):
    """登录尝试记录表"""
    __tablename__ = "login_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    wechat_id = Column(String(100), nullable=True, index=True)
    phone_number = Column(String(20), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=False)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系 - 暂时注释掉，避免循环导入
    # user = relationship("User", back_populates="login_attempts")

    def __repr__(self):
        return f"<LoginAttempt(id={self.id}, success={self.success})>"

class UserVerification(Base):
    """用户验证表"""
    __tablename__ = "user_verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    verification_type = Column(String(50), nullable=False)  # phone, email, wechat
    verification_code = Column(String(10), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系 - 暂时注释掉，避免循环导入
    # user = relationship("User", back_populates="verifications")

    def __repr__(self):
        return f"<UserVerification(id={self.id}, type={self.verification_type})>"

# Pydantic模型
class UserSessionBase(BaseModel):
    user_id: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserSessionCreate(UserSessionBase):
    session_token: str
    refresh_token: str
    expires_at: datetime

class UserSessionResponse(UserSessionBase):
    id: str
    session_token: str
    refresh_token: str
    is_active: bool
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoginAttemptBase(BaseModel):
    wechat_id: Optional[str] = None
    phone_number: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class LoginAttemptCreate(LoginAttemptBase):
    success: bool
    failure_reason: Optional[str] = None

class LoginAttemptResponse(LoginAttemptBase):
    id: str
    user_id: Optional[str] = None
    success: bool
    failure_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserVerificationBase(BaseModel):
    user_id: str
    verification_type: str
    verification_code: str
    expires_at: datetime

class UserVerificationCreate(UserVerificationBase):
    pass

class UserVerificationResponse(UserVerificationBase):
    id: str
    is_used: bool
    created_at: datetime

    class Config:
        from_attributes = True
