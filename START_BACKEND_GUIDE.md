# 🚀 启动本地后端服务指南

## ✅ 依赖已安装

所有必需的依赖包已安装：
- ✅ cos-python-sdk-v5
- ✅ tencentcloud-sdk-python  
- ✅ pydantic-settings
- ✅ cryptography
- ✅ requests

## 🎯 启动步骤

### 方法1: 使用 VS Code（推荐）

1. **打开项目**
   - 在 VS Code 中打开 `D:\Github\targemanage\targetmanage`

2. **打开终端**
   - 菜单：终端 → 新建终端
   - 或按快捷键 `Ctrl + ~`

3. **切换到backend目录**
   ```bash
   cd backend
   ```

4. **启动服务**
   ```bash
   python start_dev.py
   ```

5. **查看启动日志**
   应该看到：
   ```
   ☁️ 使用远程数据库: mysql+pymysql://root:targetM123@...
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Started parent process [xxxx]
   INFO:     Started server process [xxxx]
   INFO:     Waiting for application startup.
   🚀 智能目标管理系统启动中...
   INFO:     Application startup complete.
   ```

6. **测试服务**
   - 在浏览器打开：`http://localhost:8000/health`
   - 或在新终端运行：`curl http://localhost:8000/health`

### 方法2: 使用 uvicorn 直接启动

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 方法3: 使用 VS Code 调试模式

1. 按 `F5` 或点击左侧"运行和调试"图标
2. 如果没有配置，创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

3. 选择 "Python: FastAPI" 并点击运行

## 🔍 验证服务

### 1. 健康检查

在浏览器或新终端中：

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "service": "智能目标管理系统",
  "version": "1.0.0"
}
```

### 2. API文档

在浏览器中打开：
```
http://localhost:8000/docs
```

应该看到完整的API文档界面。

### 3. 测试拍照记录API

在API文档中找到 `/api/photo-records/recognize-and-create` 并测试。

## 📱 配置小程序

### 1. 确认小程序配置

`wechat-miniprogram/config/env.js` 应该是：

```javascript
development: {
  baseUrl: 'http://localhost:8000',  // ✅ 已配置
  apiVersion: 'v1',
  debug: true
}
```

### 2. 微信开发者工具设置

1. 打开微信开发者工具
2. 详情 → 本地设置
3. ✅ 勾选 "不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"
4. 清除缓存
5. 重新编译

### 3. 测试连接

在小程序控制台应该看到：
```
页面加载 - 环境配置信息:
全局baseUrl: http://localhost:8000
当前环境: devtools
```

## 🐛 常见问题

### Q1: 端口被占用

**症状**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程（替换<PID>为实际进程ID）
taskkill /PID <PID> /F

# 或使用不同端口
uvicorn app.main:app --reload --port 8001
```

### Q2: 模块导入错误

**症状**: `ModuleNotFoundError`

**解决**:
```bash
# 重新安装依赖
cd backend
pip install -r requirements.txt

# 或单独安装缺失的包
pip install cos-python-sdk-v5
```

### Q3: 数据库连接失败

**症状**: `Can't connect to MySQL server`

**解决**:
1. 检查网络连接
2. 确认数据库地址正确
3. 测试连接：
   ```bash
   ping sh-cynosdbmysql-grp-hocwbafo.sql.tencentcdb.com
   ```

### Q4: 小程序连接失败

**症状**: `request:fail`

**解决**:
1. 确认后端已启动（访问 `http://localhost:8000/health`）
2. 确认域名校验已关闭
3. 清除小程序缓存并重新编译
4. 检查 `env.js` 配置

## 📊 开发流程

```
1. VS Code 启动后端
   ↓
2. 浏览器测试 /health
   ↓
3. 打开微信开发者工具
   ↓
4. 小程序连接到 localhost:8000
   ↓
5. 开始开发和调试
```

## 💡 调试技巧

### 1. 查看后端日志

在 VS Code 终端中可以看到所有请求日志：
```
INFO:     127.0.0.1:52341 - "POST /api/auth/wechat-login HTTP/1.1" 200 OK
🔐 开始微信登录流程
✅ 登录成功
```

### 2. 设置断点

在 VS Code 中：
1. 在代码行号左侧点击设置断点（红点）
2. 按 `F5` 启动调试模式
3. 在小程序中触发相应操作
4. VS Code 会在断点处暂停

### 3. 查看变量

调试暂停时：
- 查看左侧"变量"面板
- 鼠标悬停在变量上查看值
- 在"调试控制台"中输入变量名查看

### 4. 单步执行

- `F10`: 单步跳过
- `F11`: 单步进入
- `Shift+F11`: 单步跳出
- `F5`: 继续执行

## 🎯 测试拍照记录功能

### 1. 启动后端

```bash
cd backend
python start_dev.py
```

### 2. 启动小程序

在微信开发者工具中编译运行

### 3. 测试流程

```
登录 → 点击"拍照记录" → 选择图片 → 等待识别 → 查看结果
```

### 4. 查看日志

**后端日志**（VS Code终端）：
```
📷 照片识别请求 - 用户ID: xxx
📸 开始识别图片: 大小=xxx字节
🔧 开发模式：使用模拟OCR识别
✅ 照片记录创建成功: xxx
```

**前端日志**（开发者工具控制台）：
```
📷 选择图片成功: wxfile://tmp_...
📤 开始上传图片
📤 上传响应: {success: true, ...}
📸 照片识别结果: {...}
```

## ✅ 成功标志

当看到以下内容时，说明环境配置成功：

1. ✅ 后端启动无错误
2. ✅ `/health` 接口返回正常
3. ✅ API文档可以访问
4. ✅ 小程序显示正确的 baseUrl
5. ✅ 小程序可以成功登录
6. ✅ 拍照记录功能正常工作

## 📞 需要帮助？

如果遇到问题：
1. 查看后端终端的错误信息
2. 查看小程序控制台的错误
3. 检查本文档的"常见问题"部分
4. 确认所有依赖都已安装

---

**文档版本**: v1.0.0  
**最后更新**: 2025-01-01  
**适用环境**: Windows + VS Code + Python 3.13

