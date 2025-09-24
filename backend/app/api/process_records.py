"""
过程记录API接口
Process records API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models.process_record import ProcessRecord, ProcessRecordType, ProcessRecordSource
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.process_record import (
    ProcessRecordCreate, ProcessRecordUpdate, ProcessRecordResponse,
    ProcessRecordListResponse, ProcessRecordTimelineResponse,
    ProcessRecordStatsResponse, VoiceProcessRecordRequest, VoiceProcessRecordResponse
)
from app.utils.process_analyzer import process_analyzer
from app.utils.voice_parser import voice_goal_parser
from app.services.voice_recognition import voice_recognition_service
from app.services.goal_progress_service import GoalProgressService
from app.schemas.goals import VoiceRecognitionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/process-records", tags=["process-records"])


@router.post("/", response_model=ProcessRecordResponse)
async def create_process_record(
    record_data: ProcessRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建过程记录"""
    try:
        # 分析内容
        analysis = process_analyzer.analyze_content(record_data.content)
        
        # 创建记录
        record_dict = record_data.dict()
        
        # 优先使用用户输入的标签，如果用户没有输入标签则不添加标签
        user_tags = record_dict.get('tags', [])
        ai_tags = analysis['tags']
        # 只有当用户明确输入了标签时才使用，否则保持空数组
        final_tags = user_tags if user_tags and len(user_tags) > 0 else []
        
        record_dict.update({
            'user_id': current_user.id,
            'sentiment': analysis['sentiment'],
            'energy_level': analysis['energy_level'],
            'difficulty_level': analysis['difficulty_level'],
            'keywords': analysis['keywords'],
            'tags': final_tags,  # 使用最终确定的标签
            'is_important': analysis['is_important'],
            'is_milestone': analysis['is_milestone'],
            'is_breakthrough': analysis['is_breakthrough'],
            'confidence_score': analysis['confidence_score']
        })
        
        db_record = ProcessRecord(**record_dict)
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # 如果有关联目标，更新目标进度
        if record_data.goal_id:
            progress_service = GoalProgressService(db)
            progress_service.update_goal_progress_from_record(record_data.goal_id, db_record)
        
        logger.info(f"创建过程记录成功: {db_record.id}")
        return ProcessRecordResponse.from_orm(db_record)
        
    except Exception as e:
        logger.error(f"创建过程记录失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建过程记录失败: {str(e)}")


@router.post("/voice", response_model=VoiceProcessRecordResponse)
async def create_voice_process_record(
    request: VoiceProcessRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """通过语音创建过程记录"""
    try:
        # 分析语音内容
        analysis = process_analyzer.analyze_content(request.voice_text)
        
        # 创建记录
        db_record = ProcessRecord(
            content=request.voice_text,
            record_type=ProcessRecordType(analysis['record_type']),
            source=ProcessRecordSource.voice,
            goal_id=request.goal_id,
            event_date=request.event_date or datetime.utcnow(),
            sentiment=analysis['sentiment'],
            energy_level=analysis['energy_level'],
            difficulty_level=analysis['difficulty_level'],
            keywords=analysis['keywords'],
            tags=analysis['tags'],
            is_important=analysis['is_important'],
            is_milestone=analysis['is_milestone'],
            is_breakthrough=analysis['is_breakthrough'],
            confidence_score=analysis['confidence_score'],
            user_id=current_user.id
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # 如果有关联目标，更新目标进度
        if request.goal_id:
            progress_service = GoalProgressService(db)
            progress_service.update_goal_progress_from_record(request.goal_id, db_record)
        
        logger.info(f"创建语音过程记录成功: {db_record.id}")
        
        return VoiceProcessRecordResponse(
            success=True,
            message="语音过程记录创建成功",
            record=ProcessRecordResponse.from_orm(db_record),
            analysis=analysis
        )
        
    except Exception as e:
        logger.error(f"创建语音过程记录失败: {e}")
        db.rollback()
        return VoiceProcessRecordResponse(
            success=False,
            message=f"创建语音过程记录失败: {str(e)}"
        )


@router.put("/{record_id}", response_model=ProcessRecordResponse)
async def update_process_record(
    record_id: int,
    record_data: ProcessRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新过程记录"""
    try:
        # 查找记录
        record = db.query(ProcessRecord).filter(
            ProcessRecord.id == record_id,
            ProcessRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 更新记录数据
        update_data = record_data.dict(exclude_unset=True)
        
        # 如果内容有变化，重新分析
        if 'content' in update_data and update_data['content'] != record.content:
            analysis = process_analyzer.analyze_content(update_data['content'])
            
            # 优先使用用户输入的标签，如果用户没有输入标签则不添加标签
            user_tags = update_data.get('tags', [])
            ai_tags = analysis['tags']
            # 只有当用户明确输入了标签时才使用，否则保持空数组
            final_tags = user_tags if user_tags and len(user_tags) > 0 else []
            
            update_data.update({
                'sentiment': analysis['sentiment'],
                'energy_level': analysis['energy_level'],
                'difficulty_level': analysis['difficulty_level'],
                'keywords': analysis['keywords'],
                'tags': final_tags,  # 使用最终确定的标签
                'is_important': analysis['is_important'],
                'is_milestone': analysis['is_milestone'],
                'is_breakthrough': analysis['is_breakthrough'],
                'confidence_score': analysis['confidence_score']
            })
        
        # 更新记录
        for field, value in update_data.items():
            if hasattr(record, field):
                setattr(record, field, value)
        
        record.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(record)
        
        logger.info(f"更新过程记录成功: {record.id}")
        return ProcessRecordResponse.from_orm(record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新过程记录失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新过程记录失败: {str(e)}")


@router.post("/suggest-goal", response_model=dict)
async def suggest_goal_for_content(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根据内容智能推荐最相关的目标"""
    try:
        from app.models.goal import Goal
        from app.utils.voice_parser import voice_goal_parser
        
        # 从请求中获取内容
        content = request.get('content', '')
        if not content:
            return {
                "success": False,
                "message": "内容不能为空"
            }
        
        # 获取用户的所有活跃目标
        goals = db.query(Goal).filter(
            Goal.user_id == current_user.id,
            Goal.status == 'active'
        ).all()
        
        if not goals:
            return {
                "success": True,
                "suggested_goal": None,
                "confidence": 0,
                "message": "没有可关联的目标"
            }
        
        # 使用语音解析器分析内容，获取类别和关键词
        parsed_content = voice_goal_parser.parse_voice_to_goal(content)
        content_category = parsed_content.get('category', '')
        content_title = parsed_content.get('title', '')
        
        # 简单的目标匹配逻辑
        best_match = None
        best_score = 0
        
        for goal in goals:
            score = 0
            
            # 类别匹配
            if goal.category and content_category:
                if goal.category == content_category:
                    score += 0.5
            
            # 标题关键词匹配
            if goal.title and content_title:
                title_words = set(goal.title.lower().split())
                content_words = set(content_title.lower().split())
                common_words = title_words.intersection(content_words)
                if common_words:
                    score += len(common_words) * 0.2
            
            # 内容关键词匹配
            content_lower = content.lower()
            if '学习' in content_lower and '学习' in goal.title.lower():
                score += 0.3
            if 'python' in content_lower and 'python' in goal.title.lower():
                score += 0.4
            if '编程' in content_lower and '编程' in goal.title.lower():
                score += 0.3
            if '项目' in content_lower and '项目' in goal.title.lower():
                score += 0.3
            if '减肥' in content_lower and '减肥' in goal.title.lower():
                score += 0.4
            if '跑步' in content_lower and '跑步' in goal.title.lower():
                score += 0.3
            if '赚钱' in content_lower and '赚钱' in goal.title.lower():
                score += 0.4
            
            if score > best_score:
                best_score = score
                best_match = goal
        
        if best_match and best_score > 0.3:
            return {
                "success": True,
                "suggested_goal": {
                    "id": best_match.id,
                    "title": best_match.title,
                    "category": best_match.category
                },
                "confidence": min(best_score, 1.0),
                "message": f"推荐关联目标: {best_match.title}"
            }
        else:
            return {
                "success": True,
                "suggested_goal": None,
                "confidence": 0,
                "message": "未找到相关目标"
            }
            
    except Exception as e:
        logger.error(f"目标推荐失败: {e}")
        return {
            "success": False,
            "message": f"目标推荐失败: {str(e)}"
        }


@router.get("/", response_model=ProcessRecordListResponse)
async def get_process_records(
    goal_id: Optional[str] = Query(None, description="目标ID"),
    record_type: Optional[ProcessRecordType] = Query(None, description="记录类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取过程记录列表"""
    try:
        query = db.query(ProcessRecord).filter(ProcessRecord.user_id == current_user.id)
        
        if goal_id:
            query = query.filter(ProcessRecord.goal_id == goal_id)
        
        if record_type:
            query = query.filter(ProcessRecord.record_type == record_type)
        
        # 按时间倒序排列
        query = query.order_by(ProcessRecord.recorded_at.desc())
        
        # 分页
        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return ProcessRecordListResponse(
            records=[ProcessRecordResponse.from_orm(record) for record in records],
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total
        )
        
    except Exception as e:
        logger.error(f"获取过程记录列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取过程记录列表失败: {str(e)}")


@router.get("/timeline", response_model=List[ProcessRecordTimelineResponse])
async def get_process_records_timeline(
    goal_id: Optional[str] = Query(None, description="目标ID"),
    days: int = Query(30, ge=1, le=365, description="天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取过程记录时间线"""
    try:
        # 计算时间范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(ProcessRecord).filter(
            ProcessRecord.user_id == current_user.id,
            ProcessRecord.recorded_at >= start_date,
            ProcessRecord.recorded_at <= end_date
        )
        
        if goal_id:
            query = query.filter(ProcessRecord.goal_id == goal_id)
        
        records = query.order_by(ProcessRecord.recorded_at.desc()).all()
        
        # 按日期分组
        timeline_dict = {}
        for record in records:
            date_str = record.recorded_at.strftime("%Y-%m-%d")
            if date_str not in timeline_dict:
                timeline_dict[date_str] = {
                    'records': [],
                    'milestone_count': 0,
                    'breakthrough_count': 0
                }
            
            timeline_dict[date_str]['records'].append(ProcessRecordResponse.from_orm(record))
            
            if record.is_milestone:
                timeline_dict[date_str]['milestone_count'] += 1
            if record.is_breakthrough:
                timeline_dict[date_str]['breakthrough_count'] += 1
        
        # 转换为响应格式
        timeline = []
        for date_str in sorted(timeline_dict.keys(), reverse=True):
            data = timeline_dict[date_str]
            timeline.append(ProcessRecordTimelineResponse(
                date=date_str,
                records=data['records'],
                milestone_count=data['milestone_count'],
                breakthrough_count=data['breakthrough_count']
            ))
        
        return timeline
        
    except Exception as e:
        logger.error(f"获取过程记录时间线失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取过程记录时间线失败: {str(e)}")


@router.get("/stats", response_model=ProcessRecordStatsResponse)
async def get_process_records_stats(
    goal_id: Optional[str] = Query(None, description="目标ID"),
    days: int = Query(30, ge=1, le=365, description="天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取过程记录统计"""
    try:
        # 计算时间范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(ProcessRecord).filter(
            ProcessRecord.user_id == current_user.id,
            ProcessRecord.recorded_at >= start_date,
            ProcessRecord.recorded_at <= end_date
        )
        
        if goal_id:
            query = query.filter(ProcessRecord.goal_id == goal_id)
        
        records = query.all()
        
        # 统计计算
        total_records = len(records)
        
        # 按类型统计
        records_by_type = {}
        for record in records:
            type_name = record.record_type.value
            records_by_type[type_name] = records_by_type.get(type_name, 0) + 1
        
        # 按心情统计
        records_by_mood = {}
        for record in records:
            if record.sentiment:
                records_by_mood[record.sentiment] = records_by_mood.get(record.sentiment, 0) + 1
        
        # 里程碑和突破统计
        milestone_count = sum(1 for record in records if record.is_milestone)
        breakthrough_count = sum(1 for record in records if record.is_breakthrough)
        
        # 平均精力水平和困难程度
        energy_levels = [r.energy_level for r in records if r.energy_level is not None]
        difficulty_levels = [r.difficulty_level for r in records if r.difficulty_level is not None]
        
        avg_energy_level = sum(energy_levels) / len(energy_levels) if energy_levels else None
        avg_difficulty_level = sum(difficulty_levels) / len(difficulty_levels) if difficulty_levels else None
        
        # 积极情感比例
        positive_count = sum(1 for record in records if record.sentiment == 'positive')
        positive_sentiment_ratio = positive_count / total_records if total_records > 0 else None
        
        return ProcessRecordStatsResponse(
            total_records=total_records,
            records_by_type=records_by_type,
            records_by_mood=records_by_mood,
            milestone_count=milestone_count,
            breakthrough_count=breakthrough_count,
            avg_energy_level=avg_energy_level,
            avg_difficulty_level=avg_difficulty_level,
            positive_sentiment_ratio=positive_sentiment_ratio
        )
        
    except Exception as e:
        logger.error(f"获取过程记录统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取过程记录统计失败: {str(e)}")


@router.get("/{record_id}", response_model=ProcessRecordResponse)
async def get_process_record(
    record_id: int = Path(..., description="记录ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个过程记录"""
    try:
        record = db.query(ProcessRecord).filter(
            ProcessRecord.id == record_id,
            ProcessRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="过程记录不存在")
        
        # 增加查看数
        record.view_count += 1
        db.commit()
        
        return ProcessRecordResponse.from_orm(record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取过程记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取过程记录失败: {str(e)}")


@router.put("/{record_id}", response_model=ProcessRecordResponse)
async def update_process_record(
    record_id: int = Path(..., description="记录ID"),
    update_data: ProcessRecordUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新过程记录"""
    try:
        record = db.query(ProcessRecord).filter(
            ProcessRecord.id == record_id,
            ProcessRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="过程记录不存在")
        
        # 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(record, field, value)
        
        # 如果内容有变化，重新分析
        if 'content' in update_dict:
            analysis = process_analyzer.analyze_content(update_dict['content'])
            record.sentiment = analysis['sentiment']
            record.energy_level = analysis['energy_level']
            record.difficulty_level = analysis['difficulty_level']
            record.keywords = analysis['keywords']
            record.tags = analysis['tags']
            record.is_important = analysis['is_important']
            record.is_milestone = analysis['is_milestone']
            record.is_breakthrough = analysis['is_breakthrough']
            record.confidence_score = analysis['confidence_score']
        
        db.commit()
        db.refresh(record)
        
        logger.info(f"更新过程记录成功: {record_id}")
        return ProcessRecordResponse.from_orm(record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新过程记录失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新过程记录失败: {str(e)}")


@router.delete("/{record_id}")
async def delete_process_record(
    record_id: int = Path(..., description="记录ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除过程记录"""
    try:
        record = db.query(ProcessRecord).filter(
            ProcessRecord.id == record_id,
            ProcessRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="过程记录不存在")
        
        db.delete(record)
        db.commit()
        
        logger.info(f"删除过程记录成功: {record_id}")
        return {"message": "过程记录删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除过程记录失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除过程记录失败: {str(e)}")


@router.post("/recognize-voice", response_model=VoiceRecognitionResponse)
async def recognize_voice(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """语音识别API - 上传音频文件进行识别"""
    try:
        logger.info(f"🔍 过程记录语音识别请求 - 用户ID: {current_user.id}")
        
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
        
        if recognition_result.get("success"):
            logger.info(f"✅ 语音识别成功 - 用户ID: {current_user.id}")
            return VoiceRecognitionResponse(
                success=True,
                message="语音识别成功",
                data={
                    "voice_text": recognition_result.get("text", ""),
                    "confidence": recognition_result.get("confidence", 0),
                    "duration": recognition_result.get("duration", 0)
                }
            )
        else:
            logger.warning(f"⚠️ 语音识别失败 - 用户ID: {current_user.id}, 错误: {recognition_result.get('message', '未知错误')}")
            raise HTTPException(
                status_code=400,
                detail=recognition_result.get("message", "语音识别失败")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音识别异常 - 用户ID: {current_user.id}, 错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"语音识别服务异常: {str(e)}"
        )


@router.get("/goal-progress/{goal_id}")
async def get_goal_progress_summary(
    goal_id: str = Path(..., description="目标ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取目标进度摘要"""
    try:
        progress_service = GoalProgressService(db)
        summary = progress_service.get_goal_progress_summary(goal_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="目标不存在")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取目标进度摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取目标进度摘要失败: {str(e)}")
