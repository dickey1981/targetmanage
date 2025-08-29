"""
目标相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import logging
from datetime import datetime, date
from ..database import get_db
from ..models.user import User
from ..api.auth import get_current_user
from ..schemas import GoalCreate, GoalUpdate, GoalItem, GoalResponse, VoiceGoalCreate, VoiceGoalParseResponse, VoiceRecognitionResponse
from ..services.voice_recognition import voice_recognition_service
from ..utils.voice_parser import voice_goal_parser
from ..utils.goal_validator import goal_validator

router = APIRouter(prefix="/api/goals", tags=["目标"])
logger = logging.getLogger(__name__)

def calculate_goal_status_and_remaining_days(start_date: Optional[date], end_date: Optional[date], progress: int) -> tuple[str, int]:
    """
    计算目标状态和剩余天数
    
    状态规则：
    - 未开始：当前日期早于开始时间
    - 进行中：当前时间晚于开始时间，早于结束时间，并且进度未到达100%
    - 延期：当前日期晚于结束时间，但进度未达到100%
    - 结束：进度达到100%
    
    剩余天数计算：
    - 当前日期据结束日期的天数
    - 当前日期超过结束日期的情况下，统一为0天
    """
    today = date.today()
    
    # 计算剩余天数
    remaining_days = 0
    if end_date:
        if today <= end_date:
            remaining_days = (end_date - today).days
        else:
            remaining_days = 0
    
    # 计算状态
    if progress >= 100:
        status = "结束"
    elif not start_date or not end_date:
        # 如果没有设置开始或结束时间，默认为进行中
        status = "进行中"
    elif today < start_date:
        status = "未开始"
    elif start_date <= today <= end_date:
        status = "进行中"
    else:  # today > end_date
        status = "延期"
    
    return status, remaining_days

@router.get("/today", response_model=GoalResponse)
async def get_today_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日目标"""
    try:
        print(f"🔍 获取今日目标 - 用户ID: {current_user.id}")
        
        # 首先确保表存在并且结构完整
        try:
            # 检查goals表是否存在
            result = db.execute(text("SHOW TABLES LIKE 'goals'"))
            if not result.fetchone():
                print("🔨 goals表不存在，正在创建...")
                # 创建goals表 - 使用完整的结构
                db.execute(text("""
                    CREATE TABLE IF NOT EXISTS goals (
                        id VARCHAR(36) PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        category VARCHAR(50) DEFAULT 'personal',
                        priority VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'draft',
                        start_date DATE,
                        end_date DATE,
                        target_date DATE,
                        target_value VARCHAR(100),
                        current_value VARCHAR(100),
                        unit VARCHAR(50),
                        daily_reminder BOOLEAN DEFAULT TRUE,
                        deadline_reminder BOOLEAN DEFAULT TRUE,
                        estimated_hours FLOAT,
                        is_public BOOLEAN DEFAULT FALSE,
                        allow_collaboration BOOLEAN DEFAULT FALSE,
                        reminder_enabled BOOLEAN DEFAULT TRUE,
                        reminder_frequency VARCHAR(20) DEFAULT 'daily',
                        user_id VARCHAR(36) NOT NULL,
                        parent_goal_id VARCHAR(36),
                        total_tasks INT DEFAULT 0,
                        completed_tasks INT DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT FALSE
                    )
                """))
                db.commit()
                print("✅ goals表创建成功")
            else:
                # 如果表已存在，检查是否需要添加新列
                print("🔍 goals表已存在，检查列结构...")
                try:
                    # 使用更兼容的MySQL语法添加新列
                    # 先检查列是否存在，再添加
                    
                    # 检查start_date列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'start_date'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN start_date DATE"))
                        print("✅ 添加start_date列")
                    
                    # 检查end_date列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'end_date'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN end_date DATE"))
                        print("✅ 添加end_date列")
                    
                    # 检查target_value列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'target_value'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN target_value VARCHAR(100)"))
                        print("✅ 添加target_value列")
                    
                    # 检查current_value列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'current_value'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN current_value VARCHAR(100)"))
                        print("✅ 添加current_value列")
                    
                    # 检查unit列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'unit'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN unit VARCHAR(50)"))
                        print("✅ 添加unit列")
                    
                    # 检查daily_reminder列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'daily_reminder'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN daily_reminder BOOLEAN DEFAULT TRUE"))
                        print("✅ 添加daily_reminder列")
                    
                    # 检查deadline_reminder列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'deadline_reminder'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN deadline_reminder BOOLEAN DEFAULT TRUE"))
                        print("✅ 添加deadline_reminder列")
                    
                    db.commit()
                    print("✅ goals表结构更新完成")
                except Exception as alter_error:
                    print(f"⚠️ 更新表结构时出现警告: {alter_error}")
                    # 继续执行，可能列已经存在
        except Exception as e:
            print(f"⚠️ 创建表时出现警告: {e}")
            # 继续执行，可能表已经存在
        
        # 从数据库查询今日目标
        today = datetime.now().date()
        
        # 使用原生SQL查询，适配实际的数据库表结构
        result = db.execute(text("""
            SELECT id, title, description, category, priority, status, 
                   start_date, end_date, target_date, target_value, current_value, unit,
                   daily_reminder, deadline_reminder, created_at
            FROM goals 
            WHERE user_id = :user_id 
            AND target_date = :today
        """), {
            "user_id": current_user.id,
            "today": today
        })
        
        goals_data = result.fetchall()
        
        # 转换为响应格式
        today_goals = []
        for goal_row in goals_data:
            # 计算进度（如果有目标值和当前值）
            progress = 0
            if goal_row[9] and goal_row[10]:  # target_value 和 current_value
                try:
                    target_val = float(goal_row[9])
                    current_val = float(goal_row[10])
                    if target_val > 0:
                        progress = min(round((current_val / target_val) * 100), 100)
                except:
                    progress = 0
            
            # 计算状态和剩余天数
            start_date = goal_row[6]  # start_date
            end_date = goal_row[7]    # end_date
            status, remaining_days = calculate_goal_status_and_remaining_days(start_date, end_date, progress)
            
            today_goals.append(GoalItem(
                id=str(goal_row[0]),  # id
                title=goal_row[1],    # title
                category=goal_row[3] or "其他",  # category
                progress=progress,  # 计算出的进度
                status=status,  # 计算出的状态
                remaining_days=remaining_days,  # 计算出的剩余天数
                created_at=goal_row[14].isoformat() if goal_row[14] else None  # created_at
            ))
        
        print(f"✅ 成功获取今日目标: {len(today_goals)} 个")
        
        return GoalResponse(
            success=True,
            message="获取今日目标成功",
            data=today_goals
        )
        
    except Exception as e:
        print(f"❌ 获取今日目标失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取今日目标失败: {str(e)}"
        )

@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新目标"""
    try:
        print(f"🔍 创建目标 - 用户ID: {current_user.id}")
        print(f"🔍 目标数据: {goal_data}")
        
        # 首先确保表存在
        try:
            # 检查goals表是否存在
            result = db.execute(text("SHOW TABLES LIKE 'goals'"))
            if not result.fetchone():
                print("🔨 goals表不存在，正在创建...")
                # 创建goals表 - 使用与create_goal一致的结构
                db.execute(text("""
                    CREATE TABLE IF NOT EXISTS goals (
                        id VARCHAR(36) PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        category VARCHAR(50) DEFAULT 'personal',
                        priority VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'draft',
                        start_date DATE,
                        end_date DATE,
                        target_date DATE,
                        target_value VARCHAR(100),
                        current_value VARCHAR(100),
                        unit VARCHAR(50),
                        daily_reminder BOOLEAN DEFAULT TRUE,
                        deadline_reminder BOOLEAN DEFAULT TRUE,
                        estimated_hours FLOAT,
                        is_public BOOLEAN DEFAULT FALSE,
                        allow_collaboration BOOLEAN DEFAULT FALSE,
                        reminder_enabled BOOLEAN DEFAULT TRUE,
                        reminder_frequency VARCHAR(20) DEFAULT 'daily',
                        user_id VARCHAR(36) NOT NULL,
                        parent_goal_id VARCHAR(36),
                        total_tasks INT DEFAULT 0,
                        completed_tasks INT DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT FALSE
                    )
                """))
                db.commit()
                print("✅ goals表创建成功")
            else:
                # 如果表已存在，检查是否需要添加新列
                print("🔍 goals表已存在，检查列结构...")
                try:
                    # 尝试添加新列（如果不存在的话）
                    db.execute(text("ALTER TABLE goals ADD COLUMN IF NOT EXISTS start_date DATE"))
                    db.execute(text("ALTER TABLE goals ADD COLUMN IF NOT EXISTS end_date DATE"))
                    db.execute(text("ALTER TABLE goals ADD COLUMN IF NOT EXISTS target_value VARCHAR(100)"))
                    db.execute(text("ALTER TABLE goals ADD COLUMN IF NOT EXISTS current_value VARCHAR(100)"))
                    db.execute(text("ALTER TABLE goals ADD COLUMN IF NOT EXISTS unit VARCHAR(50)"))
                    db.execute(text("ALTER TABLE goals ADD COLUMN IF NOT EXISTS daily_reminder BOOLEAN DEFAULT TRUE"))
                    db.execute(text("ALTER TABLE goals ADD COLUMN IF NOT EXISTS deadline_reminder BOOLEAN DEFAULT TRUE"))
                    db.commit()
                    print("✅ goals表结构更新完成")
                except Exception as alter_error:
                    print(f"⚠️ 更新表结构时出现警告: {alter_error}")
                    # 继续执行，可能列已经存在
        except Exception as e:
            print(f"⚠️ 创建表时出现警告: {e}")
            # 继续执行，可能表已经存在
        
        # 转换分类和优先级
        category_map = {
            "学习": GoalCategory.STUDY,
            "工作": GoalCategory.WORK,
            "健康": GoalCategory.HEALTH,
            "财务": GoalCategory.FINANCE,
            "人际关系": GoalCategory.RELATIONSHIP,
            "个人发展": GoalCategory.PERSONAL,
            "兴趣爱好": GoalCategory.HOBBY,
            "其他": GoalCategory.OTHER
        }
        
        priority_map = {
            "low": GoalPriority.LOW,
            "medium": GoalPriority.MEDIUM,
            "high": GoalPriority.HIGH,
            "urgent": GoalPriority.URGENT
        }
        
        # 使用原生SQL创建目标
        import uuid
        
        goal_id = str(uuid.uuid4())
        
        # 处理日期字段
        start_date = None
        end_date = None
        if goal_data.startDate:
            try:
                start_date = datetime.strptime(goal_data.startDate, '%Y-%m-%d').date()
            except:
                start_date = None
        
        if goal_data.endDate:
            try:
                end_date = datetime.strptime(goal_data.endDate, '%Y-%m-%d').date()
            except:
                end_date = None
        
        # 插入目标数据 - 包含所有前端字段
        db.execute(text("""
            INSERT INTO goals (id, title, description, category, priority, status, 
                              start_date, end_date, target_date, target_value, current_value, unit,
                              daily_reminder, deadline_reminder, user_id, created_at, updated_at)
            VALUES (:goal_id, :title, :description, :category, :priority, :status,
                    :start_date, :end_date, :target_date, :target_value, :current_value, :unit,
                    :daily_reminder, :deadline_reminder, :user_id, NOW(), NOW())
        """), {
            "goal_id": goal_id,
            "title": goal_data.title,
            "description": goal_data.description,
            "category": goal_data.category,
            "priority": goal_data.priority,
            "status": "active",
            "start_date": start_date,
            "end_date": end_date,
            "target_date": datetime.now().date(),  # 使用当前日期作为目标日期
            "target_value": goal_data.targetValue,
            "current_value": goal_data.currentValue,
            "unit": goal_data.unit,
            "daily_reminder": goal_data.dailyReminder,
            "deadline_reminder": goal_data.deadlineReminder,
            "user_id": current_user.id
        })
        
        db.commit()
        
        print(f"✅ 目标创建成功: {goal_data.title}")
        
        # 返回创建的目标数据
        created_goal = {
            "id": goal_id,
            "title": goal_data.title,
            "category": goal_data.category,
            "description": goal_data.description,
            "startDate": goal_data.startDate,
            "endDate": goal_data.endDate,
            "targetValue": goal_data.targetValue,
            "currentValue": goal_data.currentValue,
            "unit": goal_data.unit,
            "priority": goal_data.priority,
            "dailyReminder": goal_data.dailyReminder,
            "deadlineReminder": goal_data.deadlineReminder,
            "progress": 0,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        return GoalResponse(
            success=True,
            message="目标创建成功",
            data=created_goal
        )
        
    except Exception as e:
        print(f"❌ 创建目标失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        
        # 回滚数据库事务
        if 'db' in locals():
            db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建目标失败: {str(e)}"
        )

@router.get("/", response_model=GoalResponse)
async def get_all_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有目标"""
    try:
        print(f"🔍 获取所有目标 - 用户ID: {current_user.id}")
        
        # 首先确保表存在并且结构完整
        try:
            # 检查goals表是否存在
            result = db.execute(text("SHOW TABLES LIKE 'goals'"))
            if not result.fetchone():
                print("🔨 goals表不存在，正在创建...")
                # 创建goals表 - 使用完整的结构
                db.execute(text("""
                    CREATE TABLE IF NOT EXISTS goals (
                        id VARCHAR(36) PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        category VARCHAR(50) DEFAULT 'personal',
                        priority VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'draft',
                        start_date DATE,
                        end_date DATE,
                        target_date DATE,
                        target_value VARCHAR(100),
                        current_value VARCHAR(100),
                        unit VARCHAR(50),
                        daily_reminder BOOLEAN DEFAULT TRUE,
                        deadline_reminder BOOLEAN DEFAULT TRUE,
                        estimated_hours FLOAT,
                        is_public BOOLEAN DEFAULT FALSE,
                        allow_collaboration BOOLEAN DEFAULT FALSE,
                        reminder_enabled BOOLEAN DEFAULT TRUE,
                        reminder_frequency VARCHAR(20) DEFAULT 'daily',
                        user_id VARCHAR(36) NOT NULL,
                        parent_goal_id VARCHAR(36),
                        total_tasks INT DEFAULT 0,
                        completed_tasks INT DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT FALSE
                    )
                """))
                db.commit()
                print("✅ goals表创建成功")
            else:
                # 如果表已存在，检查是否需要添加新列
                print("🔍 goals表已存在，检查列结构...")
                try:
                    # 使用更兼容的MySQL语法添加新列
                    # 先检查列是否存在，再添加
                    
                    # 检查start_date列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'start_date'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN start_date DATE"))
                        print("✅ 添加start_date列")
                    
                    # 检查end_date列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'end_date'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN end_date DATE"))
                        print("✅ 添加end_date列")
                    
                    # 检查target_value列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'target_value'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN target_value VARCHAR(100)"))
                        print("✅ 添加target_value列")
                    
                    # 检查current_value列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'current_value'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN current_value VARCHAR(100)"))
                        print("✅ 添加current_value列")
                    
                    # 检查unit列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'unit'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN unit VARCHAR(50)"))
                        print("✅ 添加unit列")
                    
                    # 检查daily_reminder列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'daily_reminder'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN daily_reminder BOOLEAN DEFAULT TRUE"))
                        print("✅ 添加daily_reminder列")
                    
                    # 检查deadline_reminder列
                    result = db.execute(text("SHOW COLUMNS FROM goals LIKE 'deadline_reminder'"))
                    if not result.fetchone():
                        db.execute(text("ALTER TABLE goals ADD COLUMN deadline_reminder BOOLEAN DEFAULT TRUE"))
                        print("✅ 添加deadline_reminder列")
                    
                    db.commit()
                    print("✅ goals表结构更新完成")
                except Exception as alter_error:
                    print(f"⚠️ 更新表结构时出现警告: {alter_error}")
                    # 继续执行，可能列已经存在
        except Exception as e:
            print(f"⚠️ 创建表时出现警告: {e}")
            # 继续执行，可能表已经存在
        
        # 从数据库查询用户的所有目标
        result = db.execute(text("""
            SELECT id, title, description, category, priority, status, 
                   start_date, end_date, target_date, target_value, current_value, unit,
                   daily_reminder, deadline_reminder, created_at
            FROM goals 
            WHERE user_id = :user_id
        """), {
            "user_id": current_user.id
        })
        
        goals_data = result.fetchall()
        
        # 转换为响应格式
        all_goals = []
        for goal_row in goals_data:
            # 计算进度（如果有目标值和当前值）
            progress = 0
            if goal_row[9] and goal_row[10]:  # target_value 和 current_value
                try:
                    target_val = float(goal_row[9])
                    current_val = float(goal_row[10])
                    if target_val > 0:
                        progress = min(round((current_val / target_val) * 100), 100)
                except:
                    progress = 0
            
            # 计算状态和剩余天数
            start_date = goal_row[6]  # start_date
            end_date = goal_row[7]    # end_date
            status, remaining_days = calculate_goal_status_and_remaining_days(start_date, end_date, progress)
            
            all_goals.append(GoalItem(
                id=str(goal_row[0]),  # id
                title=goal_row[1],    # title
                category=goal_row[3] or "其他",  # category
                progress=progress,  # 计算出的进度
                status=status,  # 计算出的状态
                remaining_days=remaining_days,  # 计算出的剩余天数
                created_at=goal_row[14].isoformat() if goal_row[14] else None  # created_at
            ))
        
        print(f"✅ 成功获取所有目标: {len(all_goals)} 个")
        
        return GoalResponse(
            success=True,
            message="获取所有目标成功",
            data=all_goals
        )
        
    except Exception as e:
        print(f"❌ 获取所有目标失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取所有目标失败: {str(e)}"
        )

@router.get("/{goal_id}")
def get_goal_detail(goal_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取单个目标详情"""
    try:
        # 确保表结构存在
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS goals (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                priority VARCHAR(20),
                status VARCHAR(20) DEFAULT 'active',
                target_date DATE,
                start_date DATE,
                end_date DATE,
                target_value VARCHAR(100),
                current_value VARCHAR(100),
                unit VARCHAR(50),
                daily_reminder BOOLEAN DEFAULT TRUE,
                deadline_reminder BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """))
        
        # 检查并添加缺失的列
        columns_to_check = [
            ('start_date', 'start_date DATE'),
            ('end_date', 'end_date DATE'),
            ('target_value', 'target_value VARCHAR(100)'),
            ('current_value', 'current_value VARCHAR(100)'),
            ('unit', 'unit VARCHAR(50)'),
            ('daily_reminder', 'daily_reminder BOOLEAN DEFAULT TRUE'),
            ('deadline_reminder', 'deadline_reminder BOOLEAN DEFAULT TRUE')
        ]
        
        for column_name, column_definition in columns_to_check:
            result = db.execute(text(f"SHOW COLUMNS FROM goals LIKE '{column_name}'"))
            if not result.fetchone():
                db.execute(text(f"ALTER TABLE goals ADD COLUMN {column_definition}"))
        
        db.commit()
        
        # 查询目标详情 - 使用命名参数避免格式化问题
        result = db.execute(text("""
            SELECT id, title, description, category, priority, status,
                   target_date, start_date, end_date, target_value, current_value, unit,
                   daily_reminder, deadline_reminder, created_at, updated_at
            FROM goals
            WHERE id = :goal_id AND user_id = :user_id
        """), {
            "goal_id": goal_id,
            "user_id": current_user.id
        })
        
        goal_row = result.fetchone()
        if not goal_row:
            raise HTTPException(status_code=404, detail="目标不存在")
        
        # 构建响应数据
        goal_data = {
            "id": goal_row[0],
            "title": goal_row[1],
            "description": goal_row[2],
            "category": goal_row[3],
            "priority": goal_row[4],
            "status": goal_row[5],
            "targetDate": goal_row[6].isoformat() if goal_row[6] else None,
            "startDate": goal_row[7].isoformat() if goal_row[7] else None,
            "endDate": goal_row[8].isoformat() if goal_row[8] else None,
            "targetValue": goal_row[9],
            "currentValue": goal_row[10],
            "unit": goal_row[11],
            "dailyReminder": goal_row[12],
            "deadlineReminder": goal_row[13],
            "createdAt": goal_row[14].isoformat() if goal_row[14] else None,
            "updatedAt": goal_row[15].isoformat() if goal_row[15] else None
        }
        
        return goal_data
        
    except Exception as e:
        db.rollback()
        logger.error(f"获取目标详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取目标详情失败")

@router.put("/{goal_id}")
def update_goal(goal_id: str, goal_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新目标"""
    try:
        # 确保表结构存在
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS goals (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                priority VARCHAR(20),
                status VARCHAR(20) DEFAULT 'active',
                target_date DATE,
                start_date DATE,
                end_date DATE,
                target_value VARCHAR(100),
                current_value VARCHAR(100),
                unit VARCHAR(50),
                daily_reminder BOOLEAN DEFAULT TRUE,
                deadline_reminder BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """))
        
        # 检查并添加缺失的列
        columns_to_check = [
            ('start_date', 'start_date DATE'),
            ('end_date', 'end_date DATE'),
            ('target_value', 'target_value VARCHAR(100)'),
            ('current_value', 'current_value VARCHAR(100)'),
            ('unit', 'unit VARCHAR(50)'),
            ('daily_reminder', 'daily_reminder BOOLEAN DEFAULT TRUE'),
            ('deadline_reminder', 'deadline_reminder BOOLEAN DEFAULT TRUE')
        ]
        
        for column_name, column_definition in columns_to_check:
            result = db.execute(text(f"SHOW COLUMNS FROM goals LIKE '{column_name}'"))
            if not result.fetchone():
                db.execute(text(f"ALTER TABLE goals ADD COLUMN {column_definition}"))
        
        # 检查目标是否存在且属于当前用户
        result = db.execute(text("""
            SELECT id FROM goals WHERE id = :goal_id AND user_id = :user_id
        """), {
            "goal_id": goal_id,
            "user_id": current_user.id
        })
        
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="目标不存在")
        
        # 解析日期
        start_date = None
        end_date = None
        if goal_data.get('startDate'):
            try:
                start_date = datetime.strptime(goal_data['startDate'], '%Y-%m-%d').date()
            except ValueError:
                start_date = None
                
        if goal_data.get('endDate'):
            try:
                end_date = datetime.strptime(goal_data['endDate'], '%Y-%m-%d').date()
            except ValueError:
                end_date = None
        
        # 更新目标 - 使用命名参数
        db.execute(text("""
            UPDATE goals SET
                title = :title,
                description = :description,
                category = :category,
                start_date = :start_date,
                end_date = :end_date,
                target_value = :target_value,
                current_value = :current_value,
                unit = :unit,
                priority = :priority,
                daily_reminder = :daily_reminder,
                deadline_reminder = :deadline_reminder,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :goal_id AND user_id = :user_id
        """), {
            "title": goal_data.get('title', ''),
            "description": goal_data.get('description', ''),
            "category": goal_data.get('category', ''),
            "start_date": start_date,
            "end_date": end_date,
            "target_value": goal_data.get('targetValue', ''),
            "current_value": goal_data.get('currentValue', ''),
            "unit": goal_data.get('unit', ''),
            "priority": goal_data.get('priority', ''),
            "daily_reminder": goal_data.get('dailyReminder', True),
            "deadline_reminder": goal_data.get('deadlineReminder', True),
            "goal_id": goal_id,
            "user_id": current_user.id
        })
        
        db.commit()
        
        return {"message": "目标更新成功"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"更新目标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新目标失败")

# ==================== 语音目标创建相关API ====================

@router.post("/recognize-voice", response_model=VoiceRecognitionResponse)
async def recognize_voice(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """语音识别API - 上传音频文件进行识别"""
    try:
        logger.info(f"🔍 语音识别请求 - 用户ID: {current_user.id}")
        
        # 检查语音识别服务是否可用
        if not voice_recognition_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="语音识别服务暂时不可用，请稍后重试"
            )
        
        # 读取音频文件
        audio_content = await audio.read()
        
        # 检查文件大小 (限制为10MB)
        if len(audio_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail="音频文件过大，请上传10MB以内的文件"
            )
        
        # 调用语音识别服务
        recognition_result = await voice_recognition_service.recognize_voice(audio_content)
        
        if recognition_result['success']:
            logger.info(f"✅ 语音识别成功: {recognition_result['text']}")
            return VoiceRecognitionResponse(
                success=True,
                message="语音识别成功",
                data={
                    'text': recognition_result['text'],
                    'confidence': recognition_result.get('confidence', 0.8),
                    'duration': recognition_result.get('duration', 0)
                }
            )
        else:
            logger.error(f"❌ 语音识别失败: {recognition_result['error']}")
            raise HTTPException(
                status_code=400, 
                detail=f"语音识别失败: {recognition_result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音识别处理失败: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"语音识别处理失败: {str(e)}"
        )

@router.post("/parse-voice", response_model=VoiceGoalParseResponse)
async def parse_voice_to_goal(
    voice_data: VoiceGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解析语音文本为目标数据"""
    try:
        logger.info(f"🔍 语音解析请求 - 用户ID: {current_user.id}, 文本: {voice_data.voice_text}")
        
        # 使用语音解析器解析文本
        parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_data.voice_text)
        
        # 使用目标验证器验证解析结果
        validation_result = goal_validator.validate_goal(parsed_goal)
        
        logger.info(f"✅ 语音解析完成 - 验证评分: {validation_result['score']}")
        
        return VoiceGoalParseResponse(
            success=True,
            message="语音解析成功",
            data=parsed_goal,
            validation=validation_result
        )
        
    except Exception as e:
        logger.error(f"语音解析失败: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"语音解析失败: {str(e)}"
        )

@router.post("/create-from-voice", response_model=GoalResponse)
async def create_goal_from_voice(
    voice_data: VoiceGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """通过语音创建目标"""
    try:
        logger.info(f"🔍 语音创建目标 - 用户ID: {current_user.id}, 文本: {voice_data.voice_text}")
        
        # 1. 解析语音文本
        parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_data.voice_text)
        
        # 2. 验证目标数据
        validation_result = goal_validator.validate_goal(parsed_goal)
        
        # 3. 如果有严重错误，阻止创建
        if not validation_result['is_valid']:
            logger.warning(f"⚠️ 目标验证失败: {validation_result['errors']}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "目标数据验证失败",
                    "errors": validation_result['errors'],
                    "suggestions": validation_result['suggestions']
                }
            )
        
        # 4. 确保goals表存在
        try:
            result = db.execute(text("SHOW TABLES LIKE 'goals'"))
            if not result.fetchone():
                logger.info("🔨 goals表不存在，正在创建...")
                db.execute(text("""
                    CREATE TABLE IF NOT EXISTS goals (
                        id VARCHAR(36) PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        category VARCHAR(50) DEFAULT 'personal',
                        priority VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'active',
                        target_date DATE,
                        start_date DATE,
                        end_date DATE,
                        target_value VARCHAR(100),
                        current_value VARCHAR(100),
                        unit VARCHAR(50),
                        daily_reminder BOOLEAN DEFAULT TRUE,
                        deadline_reminder BOOLEAN DEFAULT TRUE,
                        user_id VARCHAR(36) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """))
                db.commit()
                logger.info("✅ goals表创建成功")
        except Exception as e:
            logger.warning(f"⚠️ 创建表时出现警告: {e}")
        
        # 5. 生成目标ID
        import uuid
        goal_id = str(uuid.uuid4())
        
        # 6. 解析日期
        start_date = None
        end_date = None
        if parsed_goal.get('startDate'):
            try:
                start_date = datetime.fromisoformat(parsed_goal['startDate']).date()
            except ValueError:
                start_date = None
                
        if parsed_goal.get('endDate'):
            try:
                end_date = datetime.fromisoformat(parsed_goal['endDate']).date()
            except ValueError:
                end_date = None
        
        # 7. 插入目标记录
        db.execute(text("""
            INSERT INTO goals (
                id, user_id, title, description, category, priority, status,
                start_date, end_date, target_value, current_value, unit,
                daily_reminder, deadline_reminder, created_at, updated_at
            ) VALUES (
                :goal_id, :user_id, :title, :description, :category, :priority, :status,
                :start_date, :end_date, :target_value, :current_value, :unit,
                :daily_reminder, :deadline_reminder, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """), {
            "goal_id": goal_id,
            "user_id": current_user.id,
            "title": parsed_goal.get('title', ''),
            "description": parsed_goal.get('description', ''),
            "category": parsed_goal.get('category', ''),
            "priority": parsed_goal.get('priority', 'medium'),
            "status": 'active',
            "start_date": start_date,
            "end_date": end_date,
            "target_value": parsed_goal.get('targetValue', ''),
            "current_value": parsed_goal.get('currentValue', '0'),
            "unit": parsed_goal.get('unit', ''),
            "daily_reminder": parsed_goal.get('dailyReminder', True),
            "deadline_reminder": parsed_goal.get('deadlineReminder', True)
        })
        
        db.commit()
        
        # 8. 构建响应数据
        created_goal = {
            'id': goal_id,
            'title': parsed_goal.get('title', ''),
            'category': parsed_goal.get('category', ''),
            'progress': 0,
            'status': '进行中',
            'remaining_days': (end_date - datetime.now().date()).days if end_date else 0,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 语音目标创建成功: {goal_id}")
        
        return GoalResponse(
            success=True,
            message="语音目标创建成功",
            data=created_goal
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"语音创建目标失败: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"语音创建目标失败: {str(e)}"
        )
