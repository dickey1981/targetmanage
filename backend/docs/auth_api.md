# 🔐 用户认证API文档

## 概述

本文档描述了目标管理系统的用户认证相关API接口，包括微信登录、令牌管理、用户资料等功能。

## 基础信息

- **Base URL**: `http://localhost:8000/api/auth`
- **认证方式**: Bearer Token (JWT)
- **数据格式**: JSON

## 认证流程

### 1. 微信登录流程

```
用户 -> 微信授权 -> 获取code -> 调用登录API -> 返回token -> 后续请求携带token
```

### 2. 令牌刷新流程

```
访问令牌过期 -> 使用刷新令牌 -> 获取新的访问令牌和刷新令牌
```

## API接口详情

### 1. 微信登录

**接口**: `POST /wechat-login`

**描述**: 用户通过微信小程序授权登录

**请求参数**:
```json
{
  "code": "string",           // 微信授权码
  "userInfo": {               // 微信用户信息
    "nickName": "string",     // 昵称
    "avatarUrl": "string",    // 头像URL
    "gender": 0,              // 性别
    "country": "string",      // 国家
    "province": "string",     // 省份
    "city": "string"          // 城市
  },
  "phoneNumber": "string"     // 手机号（可选）
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "user": {
      "id": "uuid",
      "wechat_id": "openid",
      "nickname": "用户昵称",
      "avatar": "头像URL",
      "phone_number": "手机号",
      "email": "邮箱",
      "notification_enabled": true,
      "privacy_level": "public",
      "total_goals": "0",
      "completed_goals": "0",
      "streak_days": "0",
      "is_verified": false,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "last_login_at": "2024-01-01T00:00:00Z"
    },
    "tokens": {
      "access_token": "jwt_token",
      "refresh_token": "refresh_token",
      "token_type": "bearer"
    }
  }
}
```

### 2. 刷新令牌

**接口**: `POST /refresh-token`

**描述**: 使用刷新令牌获取新的访问令牌

**请求参数**:
```json
{
  "refresh_token": "string"   // 刷新令牌
}
```

**响应示例**:
```json
{
  "access_token": "new_jwt_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. 用户登出

**接口**: `POST /logout`

**描述**: 用户登出，撤销当前会话

**请求参数**:
```json
{
  "access_token": "string"    // 访问令牌
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 4. 验证令牌

**接口**: `GET /validate`

**描述**: 验证当前访问令牌的有效性

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "success": true,
  "message": "Token有效",
  "data": {
    "userId": "uuid",
    "nickname": "用户昵称",
    "isActive": true,
    "isVerified": false
  }
}
```

### 5. 获取当前用户信息

**接口**: `GET /me`

**描述**: 获取当前登录用户的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "id": "uuid",
  "wechat_id": "openid",
  "nickname": "用户昵称",
  "avatar": "头像URL",
  "phone_number": "手机号",
  "email": "邮箱",
  "notification_enabled": true,
  "privacy_level": "public",
  "total_goals": "0",
  "completed_goals": "0",
  "streak_days": "0",
  "is_verified": false,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "last_login_at": "2024-01-01T00:00:00Z"
}
```

### 6. 更新用户资料

**接口**: `PUT /profile`

**描述**: 更新当前用户的个人资料

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求参数**:
```json
{
  "nickname": "新昵称",           // 可选
  "avatar": "新头像URL",         // 可选
  "phone_number": "新手机号",     // 可选
  "email": "新邮箱",             // 可选
  "notification_enabled": true,   // 可选
  "privacy_level": "private"     // 可选
}
```

**响应示例**: 返回更新后的用户信息（同GET /me）

### 7. 获取用户会话列表

**接口**: `GET /sessions`

**描述**: 获取当前用户的所有活跃会话

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
[
  {
    "id": "uuid",
    "user_id": "user_uuid",
    "session_token": "token",
    "refresh_token": "refresh_token",
    "device_info": "wechat",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "is_active": true,
    "expires_at": "2024-01-08T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 8. 撤销指定会话

**接口**: `DELETE /sessions/{session_id}`

**描述**: 撤销指定的用户会话

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `session_id`: 会话ID

**响应示例**:
```json
{
  "success": true,
  "message": "会话已撤销"
}
```

### 9. 解密手机号

**接口**: `POST /decrypt-phone`

**描述**: 解密微信小程序获取的加密手机号

**请求参数**:
```json
{
  "code": "string"            // 微信手机号授权码
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "手机号解密成功",
  "data": {
    "phoneNumber": "13800138000"
  }
}
```

## 错误处理

### 常见HTTP状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 认证失败或令牌无效
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `423 Locked`: 账户被锁定
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 安全说明

### 1. 令牌安全

- 访问令牌有效期为30分钟
- 刷新令牌有效期为7天
- 令牌使用JWT格式，包含用户ID和类型信息

### 2. 账户安全

- 连续5次登录失败后账户将被锁定15分钟
- 支持多设备同时登录
- 可手动撤销指定会话

### 3. 数据保护

- 用户密码不存储，使用微信授权
- 敏感信息传输使用HTTPS
- 支持用户隐私级别设置

## 使用示例

### Python客户端示例

```python
import requests

# 微信登录
login_data = {
    "code": "wx_auth_code",
    "userInfo": {
        "nickName": "测试用户",
        "avatarUrl": "https://example.com/avatar.jpg"
    }
}

response = requests.post(
    "http://localhost:8000/api/auth/wechat-login",
    json=login_data
)

if response.status_code == 200:
    data = response.json()
    access_token = data["data"]["tokens"]["access_token"]
    
    # 使用访问令牌调用其他API
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info = requests.get(
        "http://localhost:8000/api/auth/me",
        headers=headers
    )
```

### JavaScript客户端示例

```javascript
// 微信登录
async function wechatLogin(code, userInfo) {
    const response = await fetch('/api/auth/wechat-login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            userInfo: userInfo
        })
    });
    
    const data = await response.json();
    if (data.success) {
        // 保存令牌
        localStorage.setItem('access_token', data.data.tokens.access_token);
        localStorage.setItem('refresh_token', data.data.tokens.refresh_token);
    }
}

// 获取用户信息
async function getUserInfo() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/auth/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return await response.json();
}
```

## 注意事项

1. **令牌管理**: 客户端应妥善保存访问令牌和刷新令牌
2. **自动刷新**: 建议在访问令牌过期前自动使用刷新令牌
3. **错误重试**: 遇到401错误时应尝试刷新令牌
4. **会话管理**: 支持多设备登录，用户可管理所有活跃会话
5. **安全退出**: 登出时会撤销当前会话，但其他设备会话仍有效

## 更新日志

- **v1.0.0**: 初始版本，支持微信登录和基础认证功能
- **v1.1.0**: 添加会话管理和多设备支持
- **v1.2.0**: 增强安全性和错误处理
