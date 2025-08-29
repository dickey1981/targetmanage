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
import uuid

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
    
    def wechat_login(self, code: str, user_info: dict, request: Request) -> dict:
        """微信登录/注册"""
        try:
            # 调试信息
            print(f"接收到的微信code: {code}")
            print(f"接收到的微信用户信息: {user_info}")
            
            # 1. 通过code获取微信openId
            wechat_id = self._get_wechat_openid(code)
            if not wechat_id:
                raise Exception("无法获取微信openId")
            
            print(f"获取到的微信ID: {wechat_id}")
            
            # 2. 检查用户是否已存在（通过微信ID）
            existing_user = self.db.query(User).filter(
                User.wechat_id == wechat_id
            ).first()
            
            if existing_user:
                # 用户已存在，直接登录
                user = existing_user
                is_new_user = False
                
                # 更新用户信息
                user.nickname = user_info.get('nickName', user.nickname)
                user.avatar = user_info.get('avatarUrl', user.avatar)
                user.updated_at = datetime.utcnow()
                
            else:
                # 用户不存在，创建新用户
                user = User(
                    id=str(uuid.uuid4()),
                    wechat_id=wechat_id,
                    nickname=user_info.get('nickName', ''),
                    avatar=user_info.get('avatarUrl', ''),
                    phone_number='',  # 暂时为空，后续可以通过其他方式获取
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(user)
                is_new_user = True
            
            # 3. 保存更改
            self.db.commit()
            self.db.refresh(user)
            
            # 4. 创建会话和token
            session = self.create_user_session(str(user.id), request)
            
            # 5. 记录登录尝试
            self._record_login_attempt(str(user.id), request, True)
            
            return {
                "user": {
                    "id": str(user.id),
                    "wechat_id": user.wechat_id,
                    "nickname": user.nickname,
                    "avatar": user.avatar,
                    "phone_number": user.phone_number
                },
                "token": session.session_token,
                "isNewUser": is_new_user
            }
            
        except Exception as e:
            self.db.rollback()
            # 记录失败的登录尝试
            self._record_login_attempt(None, request, False)
            raise e
    
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

    def phone_login(self, code: str, user_info: dict, request: Request) -> dict:
        """手机号登录/注册"""
        try:
            # 1. 通过code获取手机号
            phone_number = self._get_phone_number_from_code(code)
            
            # 2. 检查用户是否已存在
            existing_user = self.db.query(User).filter(
                User.phone_number == phone_number
            ).first()
            
            if existing_user:
                # 用户已存在，直接登录
                user = existing_user
                is_new_user = False
                
                # 更新用户信息
                user.nickname = user_info.get('nickName', user.nickname)
                user.avatar = user_info.get('avatarUrl', user.avatar)
                user.wechat_id = user_info.get('openId', user.wechat_id)
                user.updated_at = datetime.utcnow()
                
            else:
                # 用户不存在，创建新用户
                user = User(
                    id=str(uuid.uuid4()),
                    wechat_id=user_info.get('openId', ''),
                    nickname=user_info.get('nickName', ''),
                    avatar=user_info.get('avatarUrl', ''),
                    phone_number=phone_number,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(user)
                is_new_user = True
            
            # 3. 保存更改
            self.db.commit()
            self.db.refresh(user)
            
            # 4. 创建会话和token
            session = self.create_user_session(str(user.id), request)
            
            # 5. 记录登录尝试
            self._record_login_attempt(str(user.id), request, True)
            
            return {
                "user": {
                    "id": str(user.id),
                    "wechat_id": user.wechat_id,
                    "nickname": user.nickname,
                    "avatar": user.avatar,
                    "phone_number": user.phone_number
                },
                "token": session.session_token,
                "isNewUser": is_new_user
            }
            
        except Exception as e:
            self.db.rollback()
            # 记录失败的登录尝试
            self._record_login_attempt(None, request, False)
            raise e

    def _get_phone_number_from_code(self, code: str) -> str:
        """通过code获取手机号"""
        # TODO: 调用微信API获取手机号
        # 这里需要实现微信手机号解密逻辑
        # 暂时返回模拟数据
        return "13800138000"

    def _record_login_attempt(self, user_id: str, request: Request, success: bool):
        """记录登录尝试"""
        try:
            login_attempt = LoginAttempt(
                id=str(uuid.uuid4()),
                user_id=user_id,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent", ""),
                success=success
            )
            self.db.add(login_attempt)
            self.db.commit()
            print(f"✅ 登录尝试记录成功: user_id={user_id}, success={success}")
        except Exception as e:
            # 记录登录尝试失败不影响主流程
            print(f"❌ 记录登录尝试失败: {e}")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误详情: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
    
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
