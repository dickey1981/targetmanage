"""
语音识别服务模块
集成腾讯云ASR服务，提供语音转文字功能
"""
import os
import base64
import logging
from typing import Optional, Dict, Any
import uuid
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
            
            # 创建腾讯云ASR客户端（地区可配置，默认 ap-shanghai）
            cred = credential.Credential(secret_id, secret_key)
            region = os.getenv('TENCENT_ASR_REGION', 'ap-shanghai')
            self.client = asr_client.AsrClient(cred, region)
            logger.info(f"✅ 语音识别服务初始化成功，区域: {region}")
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
            # 检查音频文件大小（限制为5MB）
            if len(audio_file) > 5 * 1024 * 1024:
                return {
                    'success': False,
                    'error': '音频文件过大，请控制在5MB以内',
                    'text': ''
                }
            
            # 开发环境模拟识别（微信开发者工具录音格式问题）
            # 检查多种方式来确定是否启用开发模式
            is_dev_mode = (
                os.getenv('ASR_DEV_MODE', 'false').lower() == 'true' or
                os.getenv('DEBUG', 'false').lower() == 'true' or
                not self.client  # 如果没有配置腾讯云凭证，自动启用开发模式
            )
            if is_dev_mode:
                logger.info("🔧 开发模式：使用模拟语音识别")
                return self._mock_voice_recognition(audio_file, audio_format)
            
            # 将音频文件转换为base64编码
            audio_base64 = base64.b64encode(audio_file).decode('utf-8')
            
            logger.info(f"🎤 准备识别音频: 格式={audio_format}, 大小={len(audio_file)}字节, Base64长度={len(audio_base64)}")
            
            # 创建识别请求（短音频一次性识别）
            req = models.SentenceRecognitionRequest()
            
            # 必填参数
            req.EngSerViceType = "16k_zh"  # 引擎服务类型
            req.SourceType = 1  # 语音数据随请求传入
            req.VoiceFormat = "mp3" if audio_format.lower() in ["mp3", "m4a"] else "wav"  # 标准化格式
            req.UsrAudioKey = str(uuid.uuid4())  # 本次音频唯一标识
            
            # 可选参数
            req.FilterPunc = 0  # 保留标点符号
            req.ConvertNumMode = 1  # 中文数字转阿拉伯数字
            req.FilterModal = 0  # 不过滤语气词
            req.FilterDirty = 0  # 不过滤脏话
            
            # 音频数据
            req.Data = audio_base64
            req.DataLen = len(audio_file)
            
            logger.info(f"🔍 发送识别请求: EngSerViceType={req.EngSerViceType}, VoiceFormat={req.VoiceFormat}")
            
            # 调用语音识别API
            resp = self.client.SentenceRecognition(req)
            
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
            # 友好提示：未开通/未授权 等
            hint = None
            error_code = getattr(e, 'code', '')
            
            if error_code in [
                'FailedOperation.UserNotRegistered',
                'UnauthorizedOperation',
                'UnauthorizedOperation.NoCAMAuthed'
            ]:
                hint = (
                    "腾讯云语音识别未开通或权限不足，请在腾讯云控制台开通'一句话识别'（ASR_OneSentence），"
                    "并确保账户已完成实名认证与计费启用。"
                )
            elif error_code == 'FailedOperation.ErrorRecognize':
                hint = (
                    "语音识别失败，可能原因：音频格式不支持、音频质量差、音频内容为空或噪音过大。"
                    "建议：录音时保持安静环境，说话清晰，录音时长控制在1-60秒。"
                )
            elif error_code in ['InvalidParameter', 'InvalidParameterValue']:
                hint = "请求参数错误，请检查音频格式和参数设置。"
            
            return {
                'success': False,
                'error': f"语音识别服务调用失败: {str(e)}" + (f"；{hint}" if hint else ''),
                'text': ''
            }
        except Exception as e:
            logger.error(f"语音识别处理失败: {e}")
            return {
                'success': False,
                'error': f'语音识别处理失败: {str(e)}',
                'text': ''
            }
    
    def _mock_voice_recognition(self, audio_file: bytes, audio_format: str) -> Dict[str, Any]:
        """模拟语音识别（开发环境使用）"""
        import random
        import time
        
        # 模拟识别延迟
        time.sleep(0.5)
        
        # 根据音频大小和时长模拟不同的识别结果
        file_size = len(audio_file)
        duration_ms = file_size // 10  # 粗略估算时长
        
        # 预设的测试语音内容
        mock_texts = [
            "我要在3个月内减重10斤",
            "半年内学会游泳",
            "这个季度要完成5个项目",
            "下个月开始学习Python编程",
            "每天跑步30分钟",
            "每周读一本书",
            "提高工作效率",
            "学习英语口语"
        ]
        
        # 随机选择一个测试文本
        selected_text = random.choice(mock_texts)
        
        logger.info(f"🎭 模拟识别结果: {selected_text} (文件大小: {file_size}字节, 格式: {audio_format})")
        
        return {
            'success': True,
            'text': selected_text,
            'confidence': random.uniform(0.8, 0.95),
            'duration': duration_ms
        }
    
    def is_available(self) -> bool:
        """检查语音识别服务是否可用"""
        # 开发模式下总是返回可用
        is_dev_mode = (
            os.getenv('ASR_DEV_MODE', 'false').lower() == 'true' or
            os.getenv('DEBUG', 'false').lower() == 'true' or
            not self.client  # 如果没有配置腾讯云凭证，自动启用开发模式
        )
        if is_dev_mode:
            return True
        return self.client is not None

# 创建全局实例
voice_recognition_service = VoiceRecognitionService()
