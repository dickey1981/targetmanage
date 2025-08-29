"""
语音识别服务模块
集成腾讯云ASR服务，提供语音转文字功能
"""
import os
import base64
import logging
from typing import Optional, Dict, Any
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class VoiceRecognitionService:
    """语音识别服务类"""
    
    def __init__(self):
        """初始化语音识别服务"""
        try:
            # 从环境变量获取腾讯云凭证
            secret_id = os.getenv('TENCENT_SECRET_ID')
            secret_key = os.getenv('TENCENT_SECRET_KEY')
            
            logger.info(f"🔍 腾讯云凭证检查 - Secret ID: {'已设置' if secret_id else '未设置'}, Secret Key: {'已设置' if secret_key else '未设置'}")
            
            if not secret_id or not secret_key:
                logger.warning("腾讯云凭证未配置，语音识别功能将不可用")
                self.client = None
                return
            
            # 创建腾讯云ASR客户端
            cred = credential.Credential(secret_id, secret_key)
            self.client = asr_client.AsrClient(cred, "ap-beijing")
            logger.info("✅ 语音识别服务初始化成功")
            
        except Exception as e:
            logger.error(f"语音识别服务初始化失败: {e}")
            self.client = None
    
    async def recognize_voice(self, audio_file: bytes, audio_format: str = "mp3") -> Dict[str, Any]:
        """
        识别语音文件
        
        Args:
            audio_file: 音频文件字节数据
            audio_format: 音频格式 (mp3, wav, m4a等)
        
        Returns:
            Dict包含识别结果和状态信息
        """
        if not self.client:
            return {
                'success': False,
                'error': '语音识别服务未初始化',
                'text': ''
            }
        
        try:
            # 将音频文件转换为base64编码
            audio_base64 = base64.b64encode(audio_file).decode('utf-8')
            
            # 创建识别请求
            req = models.CreateRecognitionRequest()
            req.EngineModelType = "16k_zh"  # 16k采样率中文模型
            req.ChannelNum = 1  # 单声道
            req.ResTextFormat = 0  # 返回纯文本
            req.SourceType = 1  # 语音数据
            
            # 设置音频数据
            req.Data = audio_base64
            req.DataLen = len(audio_file)
            
            # 调用语音识别API
            resp = self.client.CreateRecognition(req)
            
            # 解析响应结果
            if resp.Result:
                return {
                    'success': True,
                    'text': resp.Result,
                    'confidence': getattr(resp, 'Confidence', 0.8),
                    'duration': getattr(resp, 'Duration', 0)
                }
            else:
                return {
                    'success': False,
                    'error': '语音识别结果为空',
                    'text': ''
                }
                
        except TencentCloudSDKException as e:
            logger.error(f"腾讯云ASR调用失败: {e}")
            return {
                'success': False,
                'error': f'语音识别服务调用失败: {str(e)}',
                'text': ''
            }
        except Exception as e:
            logger.error(f"语音识别处理失败: {e}")
            return {
                'success': False,
                'error': f'语音识别处理失败: {str(e)}',
                'text': ''
            }
    
    def is_available(self) -> bool:
        """检查语音识别服务是否可用"""
        return self.client is not None

# 创建全局实例
voice_recognition_service = VoiceRecognitionService()
