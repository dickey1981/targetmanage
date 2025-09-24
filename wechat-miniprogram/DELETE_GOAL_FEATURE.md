# 目标删除功能实现总结

## 功能描述
在目标详情页最下方添加删除按钮，实现目标删除功能，包含二次确认弹窗。

## 实现内容

### 1. JavaScript 逻辑 (`goal-detail.js`)

**添加删除方法：**
```javascript
// 删除目标
deleteGoal() {
  const app = getApp()
  const token = app.globalData.token
  const baseUrl = app.globalData.baseUrl
  
  if (!token) {
    wx.showToast({
      title: '请先登录',
      icon: 'none'
    })
    return
  }

  if (!baseUrl) {
    wx.showToast({
      title: 'API地址未配置',
      icon: 'none'
    })
    return
  }

  // 二次确认弹窗
  wx.showModal({
    title: '确认删除',
    content: `确定要删除目标"${this.data.goalData.title}"吗？\n\n删除后无法恢复，包括所有相关的进度记录。`,
    confirmText: '确认删除',
    cancelText: '取消',
    confirmColor: '#ff4757',
    success: (res) => {
      if (res.confirm) {
        this.performDeleteGoal()
      }
    }
  })
},

// 执行删除操作
performDeleteGoal() {
  const app = getApp()
  
  wx.showLoading({
    title: '删除中...',
    mask: true
  })

  wx.request({
    url: `${app.globalData.baseUrl}/api/goals/${this.data.goalId}`,
    method: 'DELETE',
    header: {
      'Authorization': `Bearer ${app.globalData.token}`
    },
    success: (res) => {
      wx.hideLoading()
      console.log('删除目标响应:', res)
      
      if (res.statusCode === 200) {
        wx.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        // 延迟返回上一页，让用户看到成功提示
        setTimeout(() => {
          // 通知上一页刷新
          const pages = getCurrentPages()
          if (pages.length > 1) {
            const prevPage = pages[pages.length - 2]
            if (prevPage && prevPage.refreshGoals) {
              prevPage.refreshGoals()
            }
          }
          
          // 返回上一页
          wx.navigateBack()
        }, 1500)
      } else {
        wx.showToast({
          title: res.data.message || '删除失败',
          icon: 'none'
        })
      }
    },
    fail: (error) => {
      wx.hideLoading()
      console.error('删除目标失败:', error)
      wx.showToast({
        title: '网络错误，请重试',
        icon: 'none'
      })
    }
  })
}
```

### 2. UI 界面 (`goal-detail.wxml`)

**添加删除按钮区域：**
```xml
<!-- 删除按钮区域 -->
<view class="delete-section">
  <button class="delete-btn" bindtap="deleteGoal">
    <text class="delete-icon">🗑️</text>
    <text class="delete-text">删除目标</text>
  </button>
</view>
```

### 3. 样式设计 (`goal-detail.wxss`)

**删除按钮样式：**
```css
/* 删除按钮样式 */
.delete-section {
  padding: 40rpx 30rpx;
  margin-top: 40rpx;
}

.delete-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #ff4757 0%, #ff3742 100%);
  border: none;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(255, 71, 87, 0.3);
  transition: all 0.3s ease;
}

.delete-btn:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(255, 71, 87, 0.4);
}

.delete-icon {
  font-size: 32rpx;
}

.delete-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
}
```

## 功能特点

### ✅ 安全特性
- **二次确认弹窗**：防止误删操作
- **详细警告信息**：明确告知删除后果
- **红色确认按钮**：视觉上突出危险操作

### ✅ 用户体验
- **加载状态**：删除过程中显示加载提示
- **成功反馈**：删除成功后显示成功提示
- **自动返回**：删除成功后自动返回上一页
- **页面刷新**：通知上一页刷新数据

### ✅ 错误处理
- **登录检查**：确保用户已登录
- **API配置检查**：确保API地址已配置
- **网络错误处理**：处理网络请求失败情况
- **服务器错误处理**：处理服务器返回的错误

### ✅ 视觉设计
- **醒目的红色渐变**：突出删除操作的严重性
- **垃圾桶图标**：直观的删除操作标识
- **阴影效果**：增强按钮的立体感
- **按压反馈**：点击时的缩放动画

## 操作流程

1. **用户点击删除按钮**
   - 检查登录状态和API配置
   - 显示二次确认弹窗

2. **用户确认删除**
   - 显示加载状态
   - 发送DELETE请求到后端API

3. **删除成功**
   - 显示成功提示
   - 通知上一页刷新数据
   - 延迟1.5秒后返回上一页

4. **删除失败**
   - 显示错误提示
   - 保持当前页面状态

## API 接口

**请求方式：** `DELETE`  
**请求路径：** `/api/goals/{goalId}`  
**请求头：** `Authorization: Bearer {token}`  
**响应：** 标准HTTP状态码和JSON响应

## 注意事项

- 删除操作不可逆，请谨慎使用
- 删除目标会同时删除所有相关的进度记录
- 建议在删除前备份重要数据
- 删除按钮位置醒目，避免误操作
