"""
腾讯云语音识别服务
Tencent Cloud ASR Service
"""

import base64
import logging
from typing import Optional, Dict
from tencentcloud.asr.v20190614 import models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from app.config.tencent_cloud import tencent_cloud

logger = logging.getLogger(__name__)


class TencentASRService:
    """腾讯云语音识别服务类"""
    
    def __init__(self):
        self.client = tencent_cloud.get_asr_client()
    
    async def sentence_recognition(self, audio_data: bytes, audio_format: str = "wav") -> Optional[Dict]:
        """
        一句话识别
        
        Args:
            audio_data: 音频数据
            audio_format: 音频格式 (wav, mp3, m4a)
            
        Returns:
            识别结果
        """
        if not self.client:
            logger.error("ASR客户端未初始化")
            return None
        
        try:
            req = models.SentenceRecognitionRequest()
            req.ProjectId = 0
            req.SubServiceType = 2
            req.EngSerViceType = "16k_zh"  # 16k中文
            req.SourceType = 1  # 语音数据来源
            req.VoiceFormat = self._get_voice_format(audio_format)
            req.Data = base64.b64encode(audio_data).decode('utf-8')
            
            resp = self.client.SentenceRecognition(req)
            
            result = {
                "text": resp.Result,
                "audio_duration": resp.AudioDuration,
                "request_id": resp.RequestId
            }
            
            logger.info(f"语音识别成功: {resp.Result}")
            return result
            
        except TencentCloudSDKException as e:
            logger.error(f"语音识别失败: {e}")
            return None
        except Exception as e:
            logger.error(f"语音识别服务异常: {e}")
            return None
    
    async def create_rec_task(self, audio_url: str, callback_url: str = None) -> Optional[Dict]:
        """
        创建录音文件识别任务（适用于长音频）
        
        Args:
            audio_url: 音频文件URL
            callback_url: 回调URL
            
        Returns:
            任务信息
        """
        if not self.client:
            logger.error("ASR客户端未初始化")
            return None
        
        try:
            req = models.CreateRecTaskRequest()
            req.EngineModelType = "16k_zh"
            req.ChannelNum = 1
            req.ResTextFormat = 0
            req.SourceType = 0  # URL方式
            req.Url = audio_url
            
            if callback_url:
                req.CallbackUrl = callback_url
            
            resp = self.client.CreateRecTask(req)
            
            result = {
                "task_id": resp.Data.TaskId,
                "request_id": resp.RequestId
            }
            
            logger.info(f"创建识别任务成功: {resp.Data.TaskId}")
            return result
            
        except TencentCloudSDKException as e:
            logger.error(f"创建识别任务失败: {e}")
            return None
        except Exception as e:
            logger.error(f"创建识别任务异常: {e}")
            return None
    
    async def describe_task_status(self, task_id: int) -> Optional[Dict]:
        """
        查询识别任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        if not self.client:
            logger.error("ASR客户端未初始化")
            return None
        
        try:
            req = models.DescribeTaskStatusRequest()
            req.TaskId = task_id
            
            resp = self.client.DescribeTaskStatus(req)
            
            result = {
                "task_id": task_id,
                "status": resp.Data.Status,
                "status_str": resp.Data.StatusStr,
                "result": resp.Data.Result if hasattr(resp.Data, 'Result') else None,
                "error_msg": resp.Data.ErrorMsg if hasattr(resp.Data, 'ErrorMsg') else None,
                "request_id": resp.RequestId
            }
            
            logger.info(f"查询任务状态成功: {resp.Data.StatusStr}")
            return result
            
        except TencentCloudSDKException as e:
            logger.error(f"查询任务状态失败: {e}")
            return None
        except Exception as e:
            logger.error(f"查询任务状态异常: {e}")
            return None
    
    def _get_voice_format(self, audio_format: str) -> int:
        """
        获取语音格式代码
        
        Args:
            audio_format: 音频格式
            
        Returns:
            格式代码
        """
        format_map = {
            "wav": 1,
            "pcm": 1,
            "mp3": 3,
            "m4a": 4
        }
        return format_map.get(audio_format.lower(), 1)
    
    def process_audio_file(self, file_path: str) -> bytes:
        """
        处理音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            音频数据
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"处理音频文件失败: {e}")
            return b""


# 全局ASR服务实例
asr_service = TencentASRService()
