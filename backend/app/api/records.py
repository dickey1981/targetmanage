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
    data: Optional[list] = None

@router.get("/recent", response_model=RecordResponse)
async def get_recent_records(
    db: Session = Depends(get_db)
):
    """获取最近记录"""
    try:
        # 从过程记录表查询最近的记录
        from sqlalchemy import text
        
        # 查询最近的过程记录
        query = text("""
            SELECT id, content, record_type, source, recorded_at, sentiment
            FROM process_records 
            WHERE is_deleted = FALSE 
            ORDER BY recorded_at DESC 
            LIMIT 10
        """)
        
        result = db.execute(query)
        records = result.fetchall()
        
        # 转换为前端需要的格式
        recent_records = []
        for record in records:
            recent_records.append({
                "id": str(record[0]),
                "type": record[2],  # record_type
                "content": record[1],  # content
                "source": record[3],  # source
                "sentiment": record[5],  # sentiment
                "created_at": record[4].isoformat() if record[4] else None
            })
        
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
