"""
认证相关API
Authentication related APIs
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.config.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.utils.security import verify_password, create_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - **username**: 用户名（必填）
    - **email**: 邮箱（可选）
    - **password**: 密码（必填）
    - **nickname**: 昵称（可选）
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.create_user(user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@router.post("/wechat-login", response_model=Token, summary="微信登录")
async def wechat_login(code: str, db: Session = Depends(get_db)):
    """
    微信小程序登录接口
    
    - **code**: 微信授权码
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.wechat_login(code)
        access_token = create_access_token(data={"sub": user.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user = Depends(auth_service.get_current_user)):
    """获取当前登录用户的信息"""
    return UserResponse.from_orm(current_user)


@router.post("/logout", summary="用户登出")
async def logout():
    """
    用户登出接口
    注意：JWT无法在服务端主动失效，建议客户端删除token
    """
    return {"message": "登出成功，请删除本地token"}


@router.post("/refresh", response_model=Token, summary="刷新Token")
async def refresh_token(current_user = Depends(auth_service.get_current_user)):
    """刷新访问令牌"""
    access_token = create_access_token(data={"sub": current_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(current_user)
    }
