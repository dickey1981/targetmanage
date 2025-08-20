"""
目标管理API
Goal management APIs
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse, GoalListResponse
from app.services.goal_service import GoalService
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/", response_model=GoalResponse, summary="创建目标")
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
    """
    创建新目标
    
    - **title**: 目标标题（必填）
    - **description**: 目标描述
    - **category**: 目标分类
    - **priority**: 优先级
    - **start_date**: 开始时间
    - **end_date**: 截止时间
    """
    goal_service = GoalService(db)
    goal = await goal_service.create_goal(current_user.id, goal_data)
    return GoalResponse.from_orm(goal)


@router.get("/", response_model=List[GoalListResponse], summary="获取目标列表")
async def get_goals(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    status: Optional[str] = Query(None, description="目标状态筛选"),
    category: Optional[str] = Query(None, description="目标分类筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
    """
    获取当前用户的目标列表
    
    支持分页和筛选功能
    """
    goal_service = GoalService(db)
    goals = await goal_service.get_user_goals(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        category=category,
        priority=priority
    )
    return [GoalListResponse.from_orm(goal) for goal in goals]


@router.get("/{goal_id}", response_model=GoalResponse, summary="获取目标详情")
async def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
    """获取指定目标的详细信息"""
    goal_service = GoalService(db)
    goal = await goal_service.get_goal(goal_id, current_user.id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    
    return GoalResponse.from_orm(goal)


@router.put("/{goal_id}", response_model=GoalResponse, summary="更新目标")
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
    """更新指定目标的信息"""
    goal_service = GoalService(db)
    goal = await goal_service.update_goal(goal_id, current_user.id, goal_data)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    
    return GoalResponse.from_orm(goal)


@router.delete("/{goal_id}", summary="删除目标")
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
    """删除指定目标"""
    goal_service = GoalService(db)
    success = await goal_service.delete_goal(goal_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    
    return {"message": "目标删除成功"}


@router.post("/{goal_id}/complete", response_model=GoalResponse, summary="完成目标")
async def complete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
    """标记目标为已完成"""
    goal_service = GoalService(db)
    goal = await goal_service.complete_goal(goal_id, current_user.id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    
    return GoalResponse.from_orm(goal)


@router.get("/{goal_id}/analytics", summary="获取目标分析数据")
async def get_goal_analytics(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
    """获取目标的分析数据和统计信息"""
    goal_service = GoalService(db)
    analytics = await goal_service.get_goal_analytics(goal_id, current_user.id)
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    
    return analytics
