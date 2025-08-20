"""
腾讯云COS对象存储服务
Tencent Cloud COS Service
"""

import os
import uuid
import logging
from typing import Optional, Dict
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosException

from app.config.settings import settings

logger = logging.getLogger(__name__)


class TencentCOSService:
    """腾讯云COS服务类"""
    
    def __init__(self):
        self.config = CosConfig(
            Region=settings.COS_REGION,
            SecretId=settings.TENCENT_SECRET_ID,
            SecretKey=settings.TENCENT_SECRET_KEY
        )
        self.client = CosS3Client(self.config)
        self.bucket_name = settings.COS_BUCKET_NAME
    
    async def upload_file(self, file_data: bytes, file_name: str, content_type: str = None) -> Optional[Dict]:
        """
        上传文件到COS
        
        Args:
            file_data: 文件数据
            file_name: 文件名
            content_type: 文件类型
            
        Returns:
            上传结果
        """
        try:
            # 生成唯一文件名
            file_extension = os.path.splitext(file_name)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # 按日期分目录
            from datetime import datetime
            date_path = datetime.now().strftime("%Y/%m/%d")
            object_key = f"uploads/{date_path}/{unique_filename}"
            
            # 上传参数
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': object_key,
                'Body': file_data
            }
            
            if content_type:
                upload_params['ContentType'] = content_type
            
            # 执行上传
            response = self.client.put_object(**upload_params)
            
            # 构建访问URL
            file_url = f"{settings.COS_DOMAIN}/{object_key}"
            
            result = {
                "file_url": file_url,
                "object_key": object_key,
                "bucket": self.bucket_name,
                "etag": response.get('ETag', '').strip('"'),
                "size": len(file_data),
                "content_type": content_type
            }
            
            logger.info(f"文件上传成功: {file_url}")
            return result
            
        except CosException as e:
            logger.error(f"COS上传失败: {e}")
            return None
        except Exception as e:
            logger.error(f"文件上传异常: {e}")
            return None
    
    async def delete_file(self, object_key: str) -> bool:
        """
        删除COS中的文件
        
        Args:
            object_key: 对象键
            
        Returns:
            是否删除成功
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            logger.info(f"文件删除成功: {object_key}")
            return True
            
        except CosException as e:
            logger.error(f"COS删除失败: {e}")
            return False
        except Exception as e:
            logger.error(f"文件删除异常: {e}")
            return False
    
    async def get_file_url(self, object_key: str, expires: int = 3600) -> Optional[str]:
        """
        生成文件的预签名URL
        
        Args:
            object_key: 对象键
            expires: 过期时间（秒）
            
        Returns:
            预签名URL
        """
        try:
            url = self.client.get_presigned_download_url(
                Bucket=self.bucket_name,
                Key=object_key,
                Expired=expires
            )
            
            logger.info(f"生成预签名URL成功: {object_key}")
            return url
            
        except CosException as e:
            logger.error(f"生成预签名URL失败: {e}")
            return None
        except Exception as e:
            logger.error(f"生成预签名URL异常: {e}")
            return None
    
    async def list_files(self, prefix: str = "", max_keys: int = 100) -> Optional[list]:
        """
        列出文件
        
        Args:
            prefix: 前缀过滤
            max_keys: 最大返回数量
            
        Returns:
            文件列表
        """
        try:
            response = self.client.list_objects(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag'].strip('"')
                    })
            
            logger.info(f"列出文件成功，共{len(files)}个文件")
            return files
            
        except CosException as e:
            logger.error(f"列出文件失败: {e}")
            return None
        except Exception as e:
            logger.error(f"列出文件异常: {e}")
            return None
    
    async def upload_from_local(self, local_path: str, object_key: str = None) -> Optional[Dict]:
        """
        从本地文件上传到COS
        
        Args:
            local_path: 本地文件路径
            object_key: COS对象键，如果不指定则自动生成
            
        Returns:
            上传结果
        """
        try:
            if not os.path.exists(local_path):
                logger.error(f"本地文件不存在: {local_path}")
                return None
            
            # 读取文件
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            # 获取文件名
            file_name = os.path.basename(local_path)
            
            # 如果未指定object_key，则自动生成
            if not object_key:
                file_extension = os.path.splitext(file_name)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                from datetime import datetime
                date_path = datetime.now().strftime("%Y/%m/%d")
                object_key = f"uploads/{date_path}/{unique_filename}"
            
            # 上传文件
            return await self.upload_file(file_data, file_name)
            
        except Exception as e:
            logger.error(f"本地文件上传异常: {e}")
            return None


# 全局COS服务实例
cos_service = TencentCOSService()
