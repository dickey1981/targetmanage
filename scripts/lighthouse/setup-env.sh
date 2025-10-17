#!/bin/bash
# 在服务器上设置环境变量配置
# 使用方法：./setup-env.sh

echo "🔧 配置 Lighthouse 环境变量"
echo "================================"
echo ""

# 进入项目目录
cd /opt/targetmanage || exit 1

# 检查是否已存在 .env 文件
if [ -f .env ]; then
    echo "⚠️  .env 文件已存在"
    read -p "是否备份并重新创建？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv .env .env.backup.$(date +%Y%m%d%H%M%S)
        echo "✅ 已备份旧配置"
    else
        echo "❌ 取消操作"
        exit 0
    fi
fi

# 提示用户输入配置
echo "请输入以下配置信息："
echo ""

read -p "腾讯云 Secret ID: " TENCENT_SECRET_ID
read -p "腾讯云 Secret Key: " TENCENT_SECRET_KEY
read -p "微信小程序 AppID: " WECHAT_APP_ID
read -p "微信小程序 AppSecret: " WECHAT_APP_SECRET
read -p "启用 ASR 开发模式？(true/false，默认 true): " ASR_DEV_MODE
ASR_DEV_MODE=${ASR_DEV_MODE:-true}

# 创建 .env 文件
cat > .env << EOF
# 腾讯云配置（ASR语音识别服务）
TENCENT_SECRET_ID=${TENCENT_SECRET_ID}
TENCENT_SECRET_KEY=${TENCENT_SECRET_KEY}

# 微信小程序配置
WECHAT_APP_ID=${WECHAT_APP_ID}
WECHAT_APP_SECRET=${WECHAT_APP_SECRET}

# 应用密钥
SECRET_KEY=lighthouse-secret-key-$(date +%Y%m%d)

# 腾讯云COS配置（可选）
COS_BUCKET_NAME=

# ASR开发模式
ASR_DEV_MODE=${ASR_DEV_MODE}
EOF

# 设置文件权限
chmod 600 .env

echo ""
echo "✅ .env 文件创建成功"
echo ""
echo "🔄 正在重启服务..."

# 重启服务
docker-compose -f docker-compose.lighthouse.yml down
docker-compose -f docker-compose.lighthouse.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 验证配置
echo ""
echo "🔍 验证环境变量配置："
docker exec targetmanage_backend_lighthouse env | grep -E "(TENCENT_SECRET_ID|ASR_DEV_MODE|WECHAT_APP_ID)" | sed 's/=.*/=***/' || echo "❌ 无法验证环境变量"

echo ""
echo "📝 查看启动日志："
docker logs --tail 20 targetmanage_backend_lighthouse

echo ""
echo "✨ 配置完成！"

