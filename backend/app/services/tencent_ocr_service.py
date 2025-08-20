"""
腾讯云OCR服务
Tencent Cloud OCR Service
"""

import base64
import logging
from typing import List, Dict, Optional
from tencentcloud.ocr.v20181119 import models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from app.config.tencent_cloud import tencent_cloud

logger = logging.getLogger(__name__)


class TencentOCRService:
    """腾讯云OCR服务类"""
    
    def __init__(self):
        self.client = tencent_cloud.get_ocr_client()
    
    async def general_basic_ocr(self, image_base64: str) -> Optional[List[Dict]]:
        """
        通用印刷体识别
        
        Args:
            image_base64: base64编码的图片数据
            
        Returns:
            识别结果列表
        """
        if not self.client:
            logger.error("OCR客户端未初始化")
            return None
        
        try:
            req = models.GeneralBasicOCRRequest()
            req.ImageBase64 = image_base64
            req.LanguageType = "zh"  # 中文识别
            
            resp = self.client.GeneralBasicOCR(req)
            
            # 解析结果
            results = []
            for detection in resp.TextDetections:
                results.append({
                    "text": detection.DetectedText,
                    "confidence": detection.Confidence,
                    "polygon": [
                        {"x": point.X, "y": point.Y} 
                        for point in detection.Polygon
                    ]
                })
            
            logger.info(f"OCR识别成功，识别到{len(results)}个文本块")
            return results
            
        except TencentCloudSDKException as e:
            logger.error(f"OCR识别失败: {e}")
            return None
        except Exception as e:
            logger.error(f"OCR服务异常: {e}")
            return None
    
    async def general_accurate_ocr(self, image_base64: str) -> Optional[List[Dict]]:
        """
        通用印刷体识别（高精度版）
        
        Args:
            image_base64: base64编码的图片数据
            
        Returns:
            识别结果列表
        """
        if not self.client:
            logger.error("OCR客户端未初始化")
            return None
        
        try:
            req = models.GeneralAccurateOCRRequest()
            req.ImageBase64 = image_base64
            req.LanguageType = "zh"
            
            resp = self.client.GeneralAccurateOCR(req)
            
            results = []
            for detection in resp.TextDetections:
                results.append({
                    "text": detection.DetectedText,
                    "confidence": detection.Confidence,
                    "polygon": [
                        {"x": point.X, "y": point.Y} 
                        for point in detection.Polygon
                    ]
                })
            
            logger.info(f"高精度OCR识别成功，识别到{len(results)}个文本块")
            return results
            
        except TencentCloudSDKException as e:
            logger.error(f"高精度OCR识别失败: {e}")
            return None
        except Exception as e:
            logger.error(f"高精度OCR服务异常: {e}")
            return None
    
    async def handwriting_ocr(self, image_base64: str) -> Optional[List[Dict]]:
        """
        手写体识别
        
        Args:
            image_base64: base64编码的图片数据
            
        Returns:
            识别结果列表
        """
        if not self.client:
            logger.error("OCR客户端未初始化")
            return None
        
        try:
            req = models.GeneralHandwritingOCRRequest()
            req.ImageBase64 = image_base64
            
            resp = self.client.GeneralHandwritingOCR(req)
            
            results = []
            for detection in resp.TextDetections:
                results.append({
                    "text": detection.DetectedText,
                    "confidence": detection.Confidence,
                    "polygon": [
                        {"x": point.X, "y": point.Y} 
                        for point in detection.Polygon
                    ]
                })
            
            logger.info(f"手写体识别成功，识别到{len(results)}个文本块")
            return results
            
        except TencentCloudSDKException as e:
            logger.error(f"手写体识别失败: {e}")
            return None
        except Exception as e:
            logger.error(f"手写体识别服务异常: {e}")
            return None
    
    def process_image_file(self, file_path: str) -> str:
        """
        处理图片文件，转换为base64格式
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            base64编码的图片数据
        """
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"处理图片文件失败: {e}")
            return ""


# 全局OCR服务实例
ocr_service = TencentOCRService()
