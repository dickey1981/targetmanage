"""
拍照记录API接口
Photo records API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
import base64
import os

from app.database import get_db
from app.models.process_record import ProcessRecord, ProcessRecordType, ProcessRecordSource
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.process_record import ProcessRecordResponse
# 延迟导入 ocr_service，避免在开发模式下初始化失败
# from app.services.tencent_ocr_service import ocr_service
from app.utils.process_analyzer import process_analyzer
from app.services.goal_progress_service import GoalProgressService
from app.config.settings import get_settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/photo-records", tags=["photo-records"])


class PhotoRecognitionResponse(BaseModel):
    """照片识别响应"""
    success: bool
    message: str
    data: Optional[dict] = None


class PhotoRecordCreateResponse(BaseModel):
    """照片记录创建响应"""
    success: bool
    message: str
    record: Optional[ProcessRecordResponse] = None
    analysis: Optional[dict] = None


@router.post("/recognize", response_model=PhotoRecognitionResponse)
async def recognize_photo(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    识别照片中的文字
    
    Args:
        photo: 上传的照片文件
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        识别结果
    """
    try:
        logger.info(f"📷 照片识别请求 - 用户ID: {current_user.id}")
        
        # 读取图片文件
        photo_content = await photo.read()
        
        # 检查文件大小 (限制为5MB)
        if len(photo_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="图片文件过大，请上传5MB以内的文件"
            )
        
        # 检查是否配置了OCR服务
        settings = get_settings()
        is_dev_mode = settings.OCR_DEV_MODE
        logger.info(f"🔍 recognize_photo - OCR_DEV_MODE: {is_dev_mode}")
        
        if is_dev_mode:
            # 开发模式：返回模拟数据
            logger.info("🔧 开发模式：使用模拟OCR识别")
            mock_text = "今天完成了Python学习任务，进度80%。学习了装饰器和生成器的使用。"
            
            return PhotoRecognitionResponse(
                success=True,
                message="照片识别成功（开发模式）",
                data={
                    "text": mock_text,
                    "confidence": 0.95,
                    "blocks": [
                        {
                            "text": "今天完成了Python学习任务，进度80%",
                            "confidence": 0.96
                        },
                        {
                            "text": "学习了装饰器和生成器的使用",
                            "confidence": 0.94
                        }
                    ]
                }
            )
        
        # 真实OCR识别
        from app.services.tencent_ocr_service import ocr_service
        
        # 将图片转换为base64
        image_base64 = base64.b64encode(photo_content).decode('utf-8')
        
        logger.info(f"📸 开始识别图片: 大小={len(photo_content)}字节")
        
        # 调用OCR服务识别
        ocr_results = await ocr_service.general_basic_ocr(image_base64)
        
        if not ocr_results:
            raise HTTPException(
                status_code=500,
                detail="OCR识别失败，请稍后重试"
            )
        
        # 拼接所有识别的文本
        full_text = " ".join([block["text"] for block in ocr_results])
        
        # 计算平均置信度
        avg_confidence = sum([block["confidence"] for block in ocr_results]) / len(ocr_results)
        
        logger.info(f"✅ OCR识别成功: 识别到{len(ocr_results)}个文本块")
        
        return PhotoRecognitionResponse(
            success=True,
            message="照片识别成功",
            data={
                "text": full_text,
                "confidence": avg_confidence / 100,  # 转换为0-1范围
                "blocks": [
                    {
                        "text": block["text"],
                        "confidence": block["confidence"] / 100
                    }
                    for block in ocr_results
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"照片识别失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"照片识别失败: {str(e)}"
        )


@router.post("/create", response_model=PhotoRecordCreateResponse)
async def create_photo_record(
    photo_text: str = Form(...),
    goal_id: Optional[str] = Form(None),
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建照片记录
    
    Args:
        photo_text: 照片识别的文字内容
        goal_id: 关联的目标ID（可选）
        photo: 照片文件
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建结果
    """
    try:
        logger.info(f"📝 创建照片记录 - 用户ID: {current_user.id}")
        
        # 分析照片文本内容
        analysis = process_analyzer.analyze_content(photo_text)
        
        # 保存照片文件（可选，这里简化处理）
        # TODO: 将照片上传到COS或本地存储
        photo_url = None  # 暂时不保存照片
        
        # 创建记录
        db_record = ProcessRecord(
            content=photo_text,
            record_type=ProcessRecordType(analysis['record_type']),
            source=ProcessRecordSource.photo,
            goal_id=goal_id,
            event_date=datetime.utcnow(),
            sentiment=analysis['sentiment'],
            energy_level=analysis['energy_level'],
            difficulty_level=analysis['difficulty_level'],
            keywords=analysis['keywords'],
            tags=analysis['tags'],
            is_important=analysis['is_important'],
            is_milestone=analysis['is_milestone'],
            is_breakthrough=analysis['is_breakthrough'],
            confidence_score=analysis['confidence_score'],
            user_id=current_user.id,
            # 可以添加photo_url字段存储照片地址
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # 如果有关联目标，更新目标进度
        if goal_id:
            try:
                progress_service = GoalProgressService(db)
                progress_service.update_goal_progress_from_record(goal_id, db_record)
                logger.info(f"✅ 目标进度已更新: {goal_id}")
            except Exception as e:
                logger.warning(f"⚠️ 更新目标进度失败: {str(e)}")
                # 不影响记录创建
        
        logger.info(f"✅ 照片记录创建成功: {db_record.id}")
        
        return PhotoRecordCreateResponse(
            success=True,
            message="照片记录创建成功",
            record=ProcessRecordResponse.from_orm(db_record),
            analysis=analysis
        )
        
    except Exception as e:
        logger.error(f"创建照片记录失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"创建照片记录失败: {str(e)}"
        )


@router.post("/recognize-and-create", response_model=PhotoRecordCreateResponse)
async def recognize_and_create_photo_record(
    photo: UploadFile = File(...),
    goal_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    一步完成：识别照片并创建记录
    
    Args:
        photo: 照片文件
        goal_id: 关联的目标ID（可选）
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建结果
    """
    try:
        logger.info(f"📷 一步式照片记录 - 用户ID: {current_user.id}")
        logger.info(f"📷 收到照片文件: {photo.filename if photo.filename else 'unknown'}")
        
        # 第一步：识别照片
        photo_content = await photo.read()
        logger.info(f"📷 照片读取成功，大小: {len(photo_content)} 字节")
        
        # 检查文件大小
        if len(photo_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="图片文件过大，请上传5MB以内的文件"
            )
        
        # 检查是否配置了OCR服务
        settings = get_settings()
        is_dev_mode = settings.OCR_DEV_MODE
        logger.info(f"🔍 OCR_DEV_MODE配置: {is_dev_mode}")
        logger.info(f"🔍 开发模式状态: {is_dev_mode}")
        
        if is_dev_mode:
            # 开发模式：使用模拟数据
            photo_text = "今天完成了Python学习任务，进度80%。学习了装饰器和生成器的使用。"
            logger.info("🔧 开发模式：使用模拟OCR识别")
        else:
            # 真实OCR识别
            try:
                # 懒加载 OCR 服务
                logger.info("🔧 导入OCR服务...")
                from app.services.tencent_ocr_service import ocr_service
                
                logger.info(f"🔧 OCR客户端状态: {ocr_service.client is not None}")
                
                if not ocr_service.client:
                    logger.error("❌ OCR客户端未初始化")
                    raise HTTPException(
                        status_code=503,
                        detail="OCR服务未配置，请联系管理员"
                    )
                
                image_base64 = base64.b64encode(photo_content).decode('utf-8')
                logger.info(f"📸 开始调用OCR识别，图片大小: {len(photo_content)} 字节")
                
                ocr_results = await ocr_service.general_basic_ocr(image_base64)
                
                logger.info(f"📸 OCR调用完成，结果: {ocr_results is not None}")
                
                if not ocr_results:
                    logger.warning("⚠️ OCR识别返回空结果（可能图片中无文字）")
                    raise HTTPException(
                        status_code=400,
                        detail="图片中未检测到文字，请拍摄包含清晰文字的图片"
                    )
                
                photo_text = " ".join([block["text"] for block in ocr_results])
                logger.info(f"✅ OCR识别成功: {photo_text[:50]}...")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ OCR识别异常: {str(e)}")
                logger.exception("详细堆栈:")
                raise HTTPException(
                    status_code=500,
                    detail=f"OCR识别失败: {str(e)}"
                )
        
        # 第二步：分析内容
        analysis = process_analyzer.analyze_content(photo_text)
        
        # 第三步：智能匹配目标（如果未指定goal_id）
        if not goal_id:
            try:
                from app.models.goal import Goal
                from app.services.goal_matcher import goal_matcher
                
                logger.info("🎯 开始智能匹配目标...")
                
                # 获取用户的所有活跃目标
                goals = db.query(Goal).filter(
                    Goal.user_id == current_user.id,
                    Goal.status == 'active'
                ).all()
                
                if goals:
                    # 使用新的智能匹配服务
                    match_result = goal_matcher.match_goal(
                        content=photo_text,
                        goals=goals,
                        user_id=current_user.id,
                        db=db
                    )
                    
                    if match_result:
                        goal_id = match_result['matched_goal'].id
                        logger.info(
                            f"✅ 自动匹配到目标: {match_result['matched_goal'].title} "
                            f"(分数: {match_result['score']:.2f}, "
                            f"置信度: {match_result['confidence']}, "
                            f"原因: {match_result['reason']})"
                        )
                    else:
                        logger.info("ℹ️ 未找到匹配的目标")
                else:
                    logger.info("ℹ️ 用户暂无活跃目标")
                    
            except Exception as e:
                logger.warning(f"⚠️ 目标匹配失败: {str(e)}")
                # 继续创建记录，不影响主流程
        
        # 第四步：创建记录
        db_record = ProcessRecord(
            content=photo_text,
            record_type=ProcessRecordType(analysis['record_type']),
            source=ProcessRecordSource.photo,
            goal_id=goal_id,
            event_date=datetime.utcnow(),
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
        
        # 第四步：更新目标进度
        if goal_id:
            try:
                progress_service = GoalProgressService(db)
                progress_service.update_goal_progress_from_record(goal_id, db_record)
                logger.info(f"✅ 目标进度已更新: {goal_id}")
            except Exception as e:
                logger.warning(f"⚠️ 更新目标进度失败: {str(e)}")
        
        logger.info(f"✅ 照片记录创建成功: {db_record.id}")
        
        return PhotoRecordCreateResponse(
            success=True,
            message="照片识别并记录成功",
            record=ProcessRecordResponse.from_orm(db_record),
            analysis=analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 照片记录处理失败: {str(e)}")
        logger.exception("详细错误信息:")  # 打印完整的堆栈跟踪
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"照片记录处理失败: {str(e)}"
        )

