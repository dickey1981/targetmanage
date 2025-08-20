# 腾讯云部署指南

本文档详细介绍如何将目标管理系统部署到腾讯云，并使用腾讯云数据库进行开发。

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        腾讯云架构                             │
├─────────────────────────────────────────────────────────────┤
│  CLB (负载均衡)                                             │
│    ├── 域名: targetmanage.example.com                       │
│    └── SSL证书                                              │
├─────────────────────────────────────────────────────────────┤
│  CVM (云服务器)                                             │
│    ├── 后端服务 (FastAPI) - 8000端口                        │
│    ├── 前端服务 (Nginx) - 80/443端口                       │
│    └── Redis (本地或云Redis)                               │
├─────────────────────────────────────────────────────────────┤
│  TencentDB for PostgreSQL                                  │
│    ├── 主实例: 读写                                         │
│    └── 只读实例: 读取 (可选)                                │
├─────────────────────────────────────────────────────────────┤
│  腾讯云AI服务                                               │
│    ├── OCR文字识别                                          │
│    ├── ASR语音识别                                          │
│    └── COS对象存储 (文件存储)                               │
├─────────────────────────────────────────────────────────────┤
│  监控告警                                                   │
│    ├── 云监控                                              │
│    └── 日志服务 CLS                                         │
└─────────────────────────────────────────────────────────────┘
```

## 📋 前置准备

### 1. 腾讯云账号和权限
- 注册腾讯云账号
- 开通以下服务：
  - 云服务器 CVM
  - 云数据库 TencentDB for PostgreSQL
  - 云数据库 Redis
  - 对象存储 COS
  - 文字识别 OCR
  - 语音识别 ASR
  - 负载均衡 CLB
  - SSL证书

### 2. 域名和SSL证书
- 购买域名并完成备案
- 申请SSL证书

### 3. 开发工具
- 腾讯云CLI工具
- Docker
- Git

## 🗄️ 数据库配置

### 1. 创建PostgreSQL实例

```bash
# 使用腾讯云CLI创建PostgreSQL实例
tccli postgres CreateDBInstances \
    --region ap-beijing \
    --zone ap-beijing-1 \
    --memory 2 \
    --storage 50 \
    --instancecount 1 \
    --period 1 \
    --username postgres \
    --password "YourStrongPassword123!" \
    --dbversion 13.3 \
    --instancename "targetmanage-db"
```

### 2. 数据库连接配置

更新 `backend/.env` 文件：

```env
# 腾讯云PostgreSQL配置
DATABASE_URL=postgresql://postgres:YourPassword@your-db-host:5432/targetmanage
DATABASE_TEST_URL=postgresql://postgres:YourPassword@your-db-host:5432/targetmanage_test

# 腾讯云Redis配置
REDIS_URL=redis://:password@your-redis-host:6379/0
```

### 3. 数据库安全配置

```sql
-- 创建应用专用数据库用户
CREATE USER targetmanage_user WITH PASSWORD 'app_user_password';

-- 创建数据库
CREATE DATABASE targetmanage OWNER targetmanage_user;
CREATE DATABASE targetmanage_test OWNER targetmanage_user;

-- 授权
GRANT ALL PRIVILEGES ON DATABASE targetmanage TO targetmanage_user;
GRANT ALL PRIVILEGES ON DATABASE targetmanage_test TO targetmanage_user;
```

## 🚀 服务器部署

### 1. CVM服务器配置

推荐配置：
- **实例规格**: 标准型S5.LARGE8 (4核8GB)
- **操作系统**: Ubuntu 20.04 LTS
- **系统盘**: 高性能云硬盘 50GB
- **网络**: VPC网络，分配公网IP

### 2. 服务器环境准备

```bash
#!/bin/bash
# 服务器初始化脚本

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础软件
sudo apt install -y curl wget git vim nginx

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装Node.js (用于前端构建)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装Python
sudo apt install -y python3 python3-pip python3-venv
```

### 3. 项目部署

```bash
# 克隆项目
git clone https://github.com/your-repo/targetmanage.git
cd targetmanage

# 配置环境变量
cp backend/.env.example backend/.env.production
# 编辑生产环境配置

# 构建和启动服务
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 腾讯云服务配置

### 1. 对象存储 COS

```python
# backend/app/config/tencent_cloud.py
from qcloud_cos import CosConfig, CosS3Client
from app.config.settings import settings

# COS配置
cos_config = CosConfig(
    Region=settings.TENCENT_REGION,
    SecretId=settings.TENCENT_SECRET_ID,
    SecretKey=settings.TENCENT_SECRET_KEY
)

cos_client = CosS3Client(cos_config)
```

### 2. OCR文字识别

```python
# backend/app/services/tencent_ocr_service.py
from tencentcloud.common import credential
from tencentcloud.ocr.v20181119 import ocr_client, models

class TencentOCRService:
    def __init__(self):
        cred = credential.Credential(
            settings.TENCENT_SECRET_ID,
            settings.TENCENT_SECRET_KEY
        )
        self.client = ocr_client.OcrClient(cred, settings.TENCENT_REGION)
    
    async def general_basic_ocr(self, image_base64: str):
        """通用文字识别"""
        req = models.GeneralBasicOCRRequest()
        req.ImageBase64 = image_base64
        
        resp = self.client.GeneralBasicOCR(req)
        return resp.TextDetections
```

### 3. 语音识别 ASR

```python
# backend/app/services/tencent_asr_service.py
from tencentcloud.asr.v20190614 import asr_client, models

class TencentASRService:
    def __init__(self):
        cred = credential.Credential(
            settings.TENCENT_SECRET_ID,
            settings.TENCENT_SECRET_KEY
        )
        self.client = asr_client.AsrClient(cred, settings.TENCENT_REGION)
    
    async def sentence_recognition(self, audio_data: bytes):
        """一句话识别"""
        req = models.SentenceRecognitionRequest()
        req.ProjectId = 0
        req.SubServiceType = 2
        req.EngSerViceType = "16k_zh"
        req.SourceType = 1
        req.Data = audio_data
        
        resp = self.client.SentenceRecognition(req)
        return resp.Result
```

## 📦 生产环境Docker配置

创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - DEBUG=False
      - TENCENT_SECRET_ID=${TENCENT_SECRET_ID}
      - TENCENT_SECRET_KEY=${TENCENT_SECRET_KEY}
    ports:
      - "8000:8000"
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    
  frontend:
    build:
      context: ./admin-frontend
      dockerfile: Dockerfile.prod
    ports:
      - "3000:80"
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

## 🔒 安全配置

### 1. 防火墙配置

```bash
# 配置ufw防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # 后端服务只允许内部访问
```

### 2. SSL证书配置

```nginx
# nginx/nginx.prod.conf
server {
    listen 443 ssl http2;
    server_name targetmanage.example.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 监控和日志

### 1. 云监控配置

```python
# backend/app/utils/monitoring.py
from tencentcloud.monitor.v20180724 import monitor_client, models

class CloudMonitoring:
    def __init__(self):
        self.client = monitor_client.MonitorClient(cred, region)
    
    def send_custom_metric(self, metric_name: str, value: float):
        """发送自定义指标"""
        req = models.PutMonitorDataRequest()
        req.Metrics = [
            {
                "MetricName": metric_name,
                "Value": value,
                "Timestamp": int(time.time())
            }
        ]
        self.client.PutMonitorData(req)
```

### 2. 日志服务CLS

```python
# backend/app/utils/cls_logger.py
import json
from tencentcloud.cls.v20201016 import cls_client, models

class CLSLogger:
    def __init__(self):
        self.client = cls_client.ClsClient(cred, region)
        self.topic_id = settings.CLS_TOPIC_ID
    
    def send_log(self, level: str, message: str, extra_data: dict = None):
        """发送日志到CLS"""
        log_data = {
            "timestamp": int(time.time() * 1000),
            "level": level,
            "message": message,
            "service": "targetmanage-backend"
        }
        if extra_data:
            log_data.update(extra_data)
        
        req = models.UploadLogRequest()
        req.TopicId = self.topic_id
        req.HashKey = "targetmanage"
        req.CompressType = "gzip"
        req.LogData = json.dumps([log_data])
        
        self.client.UploadLog(req)
```

## 🚀 自动化部署

### 1. GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Tencent Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/targetmanage
            git pull origin main
            docker-compose -f docker-compose.prod.yml down
            docker-compose -f docker-compose.prod.yml up -d --build
```

### 2. 部署脚本

```bash
#!/bin/bash
# scripts/tencent-cloud/deploy.sh

set -e

echo "🚀 开始部署到腾讯云..."

# 更新代码
git pull origin main

# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 数据库迁移
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 重启服务
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

echo "✅ 部署完成！"
```

## 💰 成本估算

### 月度费用预估（北京地域）

| 服务 | 规格 | 月费用 |
|------|------|--------|
| CVM云服务器 | 4核8GB | ¥200-300 |
| PostgreSQL | 2核4GB | ¥150-250 |
| Redis | 1GB | ¥50-100 |
| CLB负载均衡 | 标准型 | ¥20-50 |
| COS存储 | 10GB | ¥5-10 |
| OCR调用 | 1000次/月 | ¥10-20 |
| ASR调用 | 100小时/月 | ¥30-50 |
| **总计** | | **¥465-780** |

## 📞 技术支持

如遇到部署问题，可以：
1. 查看腾讯云官方文档
2. 联系腾讯云技术支持
3. 在项目Issues中提问

---

**注意**: 请妥善保管腾讯云密钥，不要将敏感信息提交到代码仓库中。
