"""
记录相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..api.auth import get_current_user
from ..models.user import User
from ..database import get_db

router = APIRouter(prefix="/api/records", tags=["记录"])

# 请求模型
class CreateRecordRequest(BaseModel):
    type: str
    content: str
    goal_id: Optional[str] = None

# 响应模型
class RecordResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

@router.get("/recent", response_model=RecordResponse)
async def get_recent_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取最近记录"""
    try:
        # 这里应该从数据库查询实际的最近记录
        # 目前返回模拟数据
        recent_records = [
            {
                "id": "1",
                "type": "voice",
                "content": "今天完成了项目文档的编写",
                "created_at": "2024-01-01T10:00:00Z"
            },
            {
                "id": "2",
                "type": "photo",
                "content": "拍摄了工作环境的照片",
                "created_at": "2024-01-01T09:30:00Z"
            },
            {
                "id": "3",
                "type": "text",
                "content": "记录了一个新的想法",
                "created_at": "2024-01-01T09:00:00Z"
            }
        ]
        
        return RecordResponse(
            success=True,
            message="获取最近记录成功",
            data=recent_records
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取最近记录失败: {str(e)}"
        )

@router.post("/create", response_model=RecordResponse)
async def create_record(
    request: CreateRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新记录"""
    try:
        # 这里应该将记录保存到数据库
        # 目前返回模拟的成功响应
        new_record = {
            "id": "4",
            "type": request.type,
            "content": request.content,
            "goal_id": request.goal_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return RecordResponse(
            success=True,
            message="记录创建成功",
            data=new_record
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建记录失败: {str(e)}"
        )
