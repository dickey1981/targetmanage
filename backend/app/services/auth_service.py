"""
认证服务
处理用户登录、注册、令牌管理等
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import secrets
import hashlib
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request

from ..config.settings import get_settings
from ..models.user import User, UserCreate
from ..models.session import UserSession, UserSessionCreate, LoginAttempt, LoginAttemptCreate
from ..database import get_db

settings = get_settings()

class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tokens(self, user_id: str) -> Tuple[str, str]:
        """创建访问令牌和刷新令牌"""
        # 访问令牌 - 30分钟
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_jwt_token(
            data={"sub": user_id, "type": "access"},
            expires_delta=access_token_expires
        )
        
        # 刷新令牌 - 7天
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = self._create_jwt_token(
            data={"sub": user_id, "type": "refresh"},
            expires_delta=refresh_token_expires
        )
        
        return access_token, refresh_token
    
    def _create_jwt_token(self, data: dict, expires_delta: timedelta) -> str:
        """创建JWT令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> dict:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌类型不匹配"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效"
            )
    
    def create_user_session(self, user_id: str, request: Request) -> UserSession:
        """创建用户会话"""
        access_token, refresh_token = self.create_tokens(user_id)
        
        # 获取客户端信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        device_info = self._parse_device_info(user_agent)
        
        # 创建会话记录
        session_data = UserSessionCreate(
            user_id=user_id,
            session_token=access_token,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=client_ip,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        session = UserSession(**session_data.dict())
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _parse_device_info(self, user_agent: str) -> str:
        """解析设备信息"""
        if not user_agent:
            return "unknown"
        
        # 简单的设备识别
        user_agent_lower = user_agent.lower()
        
        if "micromessenger" in user_agent_lower:
            return "wechat"
        elif "android" in user_agent_lower:
            return "android"
        elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
            return "ios"
        elif "windows" in user_agent_lower:
            return "windows"
        elif "macintosh" in user_agent_lower:
            return "mac"
        else:
            return "other"
    
    def record_login_attempt(self, wechat_id: str = None, phone_number: str = None, 
                           success: bool = True, failure_reason: str = None, 
                           request: Request = None) -> LoginAttempt:
        """记录登录尝试"""
        client_ip = self._get_client_ip(request) if request else None
        user_agent = request.headers.get("user-agent", "") if request else None
        
        # 查找用户ID
        user_id = None
        if wechat_id:
            user = self.db.query(User).filter(User.wechat_id == wechat_id).first()
            user_id = str(user.id) if user else None
        
        login_attempt_data = LoginAttemptCreate(
            user_id=user_id,
            wechat_id=wechat_id,
            phone_number=phone_number,
            ip_address=client_ip,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        
        login_attempt = LoginAttempt(**login_attempt_data.dict())
        self.db.add(login_attempt)
        self.db.commit()
        self.db.refresh(login_attempt)
        
        return login_attempt
    
    def wechat_login(self, code: str, user_info: dict, phone_number: str = None, 
                    request: Request = None) -> dict:
        """微信登录"""
        try:
            # 获取微信openid
            openid = self._get_wechat_openid(code)
            if not openid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="微信授权失败"
                )
            
            # 检查用户是否已存在
            user = self.db.query(User).filter(User.wechat_id == openid).first()
            
            if user:
                # 检查用户是否被锁定
                if user.is_locked_out:
                    self.record_login_attempt(
                        wechat_id=openid, 
                        success=False, 
                        failure_reason="账户被锁定",
                        request=request
                    )
                    raise HTTPException(
                        status_code=status.HTTP_423_LOCKED,
                        detail="账户被锁定，请15分钟后再试"
                    )
                
                # 更新用户信息
                user.nickname = user_info.get("nickName", user.nickname)
                user.avatar = user_info.get("avatarUrl", user.avatar)
                if phone_number and phone_number != "未授权":
                    user.phone_number = phone_number
                user.last_login_at = datetime.utcnow()
                user.updated_at = datetime.utcnow()
                
                # 重置失败登录次数
                user.reset_failed_login_attempts()
                
            else:
                # 创建新用户
                user_data = UserCreate(
                    wechat_id=openid,
                    nickname=user_info.get("nickName", "微信用户"),
                    avatar=user_info.get("avatarUrl", ""),
                    phone_number=phone_number if phone_number != "未授权" else None
                )
                user = User(**user_data.dict())
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            
            # 创建会话
            session = self.create_user_session(str(user.id), request)
            
            # 记录成功登录
            self.record_login_attempt(
                wechat_id=openid, 
                success=True,
                request=request
            )
            
            return {
                "user": user,
                "access_token": session.session_token,
                "refresh_token": session.refresh_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            self.db.rollback()
            # 记录失败登录
            self.record_login_attempt(
                wechat_id=user_info.get("openId"), 
                success=False, 
                failure_reason=str(e),
                request=request
            )
            raise
    
    def _get_wechat_openid(self, code: str) -> Optional[str]:
        """获取微信openid"""
        try:
            # 调用微信API获取openid
            url = "https://api.weixin.qq.com/sns/jscode2session"
            params = {
                "appid": settings.WECHAT_APP_ID,
                "secret": settings.WECHAT_APP_SECRET,
                "js_code": code,
                "grant_type": "authorization_code"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "openid" in data:
                return data["openid"]
            else:
                # 记录错误日志
                print(f"微信API错误: {data}")
                return None
                
        except Exception as e:
            print(f"获取微信openid失败: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> dict:
        """刷新访问令牌"""
        try:
            # 验证刷新令牌
            payload = self.verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
            
            # 检查用户是否存在且活跃
            user = self.db.query(User).filter(User.id == user_id, User.is_active == True).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在或已被禁用"
                )
            
            # 创建新的访问令牌
            access_token, new_refresh_token = self.create_tokens(user_id)
            
            # 更新会话
            session = self.db.query(UserSession).filter(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            ).first()
            
            if session:
                session.session_token = access_token
                session.refresh_token = new_refresh_token
                session.updated_at = datetime.utcnow()
                self.db.commit()
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"刷新令牌失败: {str(e)}"
            )
    
    def logout(self, access_token: str) -> bool:
        """用户登出"""
        try:
            # 验证令牌
            payload = self.verify_token(access_token, "access")
            user_id = payload.get("sub")
            
            if user_id:
                # 禁用会话
                session = self.db.query(UserSession).filter(
                    UserSession.session_token == access_token,
                    UserSession.is_active == True
                ).first()
                
                if session:
                    session.is_active = False
                    session.updated_at = datetime.utcnow()
                    self.db.commit()
                    return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            return False
    
    def validate_session(self, access_token: str) -> Optional[User]:
        """验证会话有效性"""
        try:
            payload = self.verify_token(access_token, "access")
            user_id = payload.get("sub")
            
            if not user_id:
                return None
            
            # 检查会话是否活跃
            session = self.db.query(UserSession).filter(
                UserSession.session_token == access_token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                return None
            
            # 获取用户信息
            user = self.db.query(User).filter(
                User.id == user_id,
                User.is_active == True,
                User.is_deleted == False
            ).first()
            
            return user
            
        except Exception:
            return None
