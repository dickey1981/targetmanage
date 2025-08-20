"""
腾讯云服务配置
Tencent Cloud services configuration
"""

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client
from tencentcloud.asr.v20190614 import asr_client
from qcloud_cos import CosConfig, CosS3Client
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class TencentCloudConfig:
    """腾讯云服务配置类"""
    
    def __init__(self):
        self.cred = credential.Credential(
            settings.TENCENT_SECRET_ID,
            settings.TENCENT_SECRET_KEY
        )
        
        # HTTP配置
        self.http_profile = HttpProfile()
        self.http_profile.endpoint = "ocr.tencentcloudapi.com"
        
        # 客户端配置
        self.client_profile = ClientProfile()
        self.client_profile.httpProfile = self.http_profile
    
    def get_ocr_client(self):
        """获取OCR客户端"""
        try:
            client = ocr_client.OcrClient(self.cred, settings.TENCENT_REGION, self.client_profile)
            return client
        except Exception as e:
            logger.error(f"创建OCR客户端失败: {e}")
            return None
    
    def get_asr_client(self):
        """获取ASR客户端"""
        try:
            client = asr_client.AsrClient(self.cred, settings.TENCENT_REGION, self.client_profile)
            return client
        except Exception as e:
            logger.error(f"创建ASR客户端失败: {e}")
            return None
    
    def get_cos_client(self):
        """获取COS客户端"""
        try:
            cos_config = CosConfig(
                Region=settings.TENCENT_REGION,
                SecretId=settings.TENCENT_SECRET_ID,
                SecretKey=settings.TENCENT_SECRET_KEY
            )
            client = CosS3Client(cos_config)
            return client
        except Exception as e:
            logger.error(f"创建COS客户端失败: {e}")
            return None


# 全局实例
tencent_cloud = TencentCloudConfig()
