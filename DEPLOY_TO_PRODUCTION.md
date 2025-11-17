# 🚀 切换到生产环境（HTTPS）

域名备案已通过，SSL证书已上传，现在可以启用HTTPS了！

---

## 📋 部署步骤

### 步骤1: 提交代码
```bash
git add .
git commit -m "切换到HTTPS生产环境"
git push origin main
```

### 步骤2: SSH连接服务器
```bash
ssh lighthouse@106.54.212.67
```

### 步骤3: 在服务器上执行
```bash
cd /home/lighthouse/targetmanage

# 拉取最新代码
git pull origin main

# 停止服务
docker-compose -f docker-compose.lighthouse.yml down

# 启动服务（使用HTTPS配置）
docker-compose -f docker-compose.lighthouse.yml up -d

# 查看日志
docker-compose -f docker-compose.lighthouse.yml logs -f
```

### 步骤4: 验证部署
```bash
# 测试HTTPS
curl https://targetmanage.cn/health

# 应该返回: healthy
```

---

## 📱 小程序配置

### 1. 微信公众平台配置

登录 [微信公众平台](https://mp.weixin.qq.com/)

**开发 → 开发管理 → 开发设置 → 服务器域名**

配置以下域名：
```
request合法域名：
https://targetmanage.cn

uploadFile合法域名：
https://targetmanage.cn

downloadFile合法域名：
https://targetmanage.cn
```

### 2. 小程序自动切换

小程序代码已配置好环境自动切换：
- **开发者工具**：使用 `http://localhost:8000`（本地开发）
- **真机预览/调试**：自动使用 `https://targetmanage.cn`（生产环境）

无需修改任何代码！

---

## 🧪 测试

### 1. 开发者工具预览
1. 点击工具栏的 **"预览"** 按钮
2. 用手机微信扫描二维码
3. 在手机上测试所有功能

### 2. 真机调试
1. 点击工具栏的 **"真机调试"** 按钮
2. 用手机微信扫描二维码
3. 可以看到真机的控制台输出

### 3. 测试清单
- [ ] 登录功能
- [ ] 创建目标
- [ ] 语音记录
- [ ] 拍照记录
- [ ] 文字记录
- [ ] 时间线查看
- [ ] 记录详情

---

## 🎯 完成后

✅ 服务器运行在 HTTPS  
✅ 小程序可以在真机上使用  
✅ 可以开始真实用户测试  
✅ 准备提交小程序审核  

---

## 📝 快速命令

```bash
# 查看服务状态
ssh lighthouse@106.54.212.67 "cd /home/lighthouse/targetmanage && docker-compose -f docker-compose.lighthouse.yml ps"

# 查看日志
ssh lighthouse@106.54.212.67 "cd /home/lighthouse/targetmanage && docker-compose -f docker-compose.lighthouse.yml logs --tail=50"

# 重启服务
ssh lighthouse@106.54.212.67 "cd /home/lighthouse/targetmanage && docker-compose -f docker-compose.lighthouse.yml restart"
```

---

**祝部署顺利！** 🎉

