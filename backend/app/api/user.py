"""
用户相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..api.auth import get_current_user
from ..models.user import User
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/user", tags=["用户"])

# 请求模型
class NotificationSettingsRequest(BaseModel):
    enabled: bool

class UserStatsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户统计数据"""
    try:
        # 这里应该从数据库查询实际的统计数据
        # 目前返回模拟数据
        stats = {
            "totalGoals": "5",
            "activeGoals": "3", 
            "completedGoals": "2",
            "completionRate": "40"
        }
        
        return UserStatsResponse(
            success=True,
            message="获取统计数据成功",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )

@router.post("/notification-settings")
async def update_notification_settings(
    request: NotificationSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户通知设置"""
    try:
        current_user.notification_enabled = request.enabled
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "通知设置更新成功",
            "data": {
                "notification_enabled": request.enabled
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新通知设置失败: {str(e)}"
        )

@router.post("/sync-data")
async def sync_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """同步用户数据"""
    try:
        # 这里应该实现实际的数据同步逻辑
        # 比如从第三方平台同步数据
        
        # 更新最后同步时间
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "数据同步成功",
            "data": {
                "sync_time": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据同步失败: {str(e)}"
        )

@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """获取用户个人资料"""
    try:
        return {
            "success": True,
            "message": "获取个人资料成功",
            "data": {
                "id": str(current_user.id),
                "wechat_id": current_user.wechat_id,
                "nickname": current_user.nickname,
                "avatar": current_user.avatar,
                "phone_number": current_user.phone_number,
                "email": current_user.email,
                "notification_enabled": current_user.notification_enabled,
                "privacy_level": current_user.privacy_level,
                "total_goals": current_user.total_goals,
                "completed_goals": current_user.completed_goals,
                "streak_days": current_user.streak_days,
                "created_at": current_user.created_at.isoformat(),
                "updated_at": current_user.updated_at.isoformat(),
                "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取个人资料失败: {str(e)}"
        )
