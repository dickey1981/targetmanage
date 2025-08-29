"""
用户认证相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..config.settings import get_settings
from ..models.user import User, UserCreate, UserResponse, UserProfileUpdate
from ..models.session import UserSessionResponse
from ..services.auth_service import AuthService
from ..database import get_db
from ..models.session import UserSession

router = APIRouter(prefix="/api/auth", tags=["认证"])
security = HTTPBearer()

# 配置
settings = get_settings()

# 请求模型
class WechatLoginRequest(BaseModel):
    code: str
    userInfo: dict
    phoneNumber: Optional[str] = None

class PhoneDecryptRequest(BaseModel):
    code: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    access_token: str



# 响应模型
class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class UserInfoResponse(BaseModel):
    user: UserResponse
    session: Optional[UserSessionResponse] = None

# 依赖函数
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """获取认证服务实例"""
    return AuthService(db)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    auth_service = AuthService(db)
    token = credentials.credentials
    
    user = auth_service.validate_session(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据或会话已过期"
        )
    
    return user

@router.post("/wechat-login", response_model=LoginResponse)
async def wechat_login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """微信登录/注册"""
    try:
        # 从请求体获取code和用户信息
        body = await request.json()
        code = body.get('code', '')
        user_info = body.get('userInfo', {})
        
        if not code:
            return LoginResponse(
                success=False,
                message="微信登录code不能为空"
            )
        
        if not user_info:
            return LoginResponse(
                success=False,
                message="用户信息不能为空"
            )
        
        result = auth_service.wechat_login(
            code=code,
            user_info=user_info,
            request=request
        )
        
        # 调试信息
        print(f"认证服务返回结果: {result}")
        print(f"用户数据类型: {type(result.get('user'))}")
        
        # 确保用户数据是字典格式
        user_data = result.get("user", {})
        if hasattr(user_data, '__dict__'):
            # 如果是对象，转换为字典
            user_data = {
                "id": str(user_data.id),
                "wechat_id": user_data.wechat_id,
                "nickname": user_data.nickname,
                "avatar": user_data.avatar,
                "phone_number": user_data.phone_number
            }
        
        return LoginResponse(
            success=True,
            message="登录成功",
            data={
                "user": user_data,
                "token": result["token"],
                "isNewUser": result["isNewUser"]
            }
        )
        
    except Exception as e:
        return LoginResponse(
            success=False,
            message=f"登录失败: {str(e)}"
        )

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """刷新访问令牌"""
    try:
        result = auth_service.refresh_token(request.refresh_token)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )

@router.post("/logout")
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登出"""
    try:
        success = auth_service.logout(request.access_token)
        
        if success:
            return {
                "success": True,
                "message": "登出成功"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="登出失败"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )



@router.get("/validate")
async def validate_token(current_user: User = Depends(get_current_user)):
    """验证令牌有效性"""
    return {
        "success": True,
        "message": "Token有效",
        "data": {
            "userId": str(current_user.id),
            "nickname": current_user.nickname,
            "isActive": current_user.is_active,
            "isVerified": current_user.is_verified
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=str(current_user.id),
        wechat_id=current_user.wechat_id,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        phone_number=current_user.phone_number,
        email=current_user.email,
        notification_enabled=current_user.notification_enabled,
        privacy_level=current_user.privacy_level,
        total_goals=current_user.total_goals,
        completed_goals=current_user.completed_goals,
        streak_days=current_user.streak_days,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login_at=current_user.last_login_at
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    try:
        # 更新用户信息
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        return UserResponse(
            id=str(current_user.id),
            wechat_id=current_user.wechat_id,
            nickname=current_user.nickname,
            avatar=current_user.avatar,
            phone_number=current_user.phone_number,
            email=current_user.email,
            notification_enabled=current_user.notification_enabled,
            privacy_level=current_user.privacy_level,
            total_goals=current_user.total_goals,
            completed_goals=current_user.completed_goals,
            streak_days=current_user.streak_days,
            is_verified=current_user.is_verified,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            last_login_at=current_user.last_login_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )

@router.post("/decrypt-phone")
async def decrypt_phone(request: PhoneDecryptRequest):
    """解密手机号（微信小程序专用）"""
    try:
        # 这里应该调用微信API解密手机号
        # 由于需要小程序的AppSecret，这里只是示例
        # 实际实现需要根据微信官方文档进行
        
        # 模拟解密过程
        # 注意：实际项目中需要调用微信API
        decrypted_phone = "13800138000"  # 示例手机号
        
        return {
            "success": True,
            "message": "手机号解密成功",
            "data": {"phoneNumber": decrypted_phone}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"手机号解密失败: {str(e)}"
        )

@router.get("/sessions", response_model=list[UserSessionResponse])
async def get_user_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取用户会话列表"""
    try:
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).all()
        
        return sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """撤销指定会话"""
    try:
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        
        session.is_active = False
        session.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "会话已撤销"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"撤销会话失败: {str(e)}"
        )
