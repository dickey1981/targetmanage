// 调试认证状态
// 用于检查用户登录状态和token有效性

const debugAuth = {
  // 检查登录状态
  checkLoginStatus() {
    const app = getApp()
    const token = app.globalData.token
    const userInfo = app.globalData.userInfo
    const isLoggedIn = app.globalData.isLoggedIn
    
    console.log('🔍 认证状态检查:')
    console.log('  Token:', token ? '已设置' : '未设置')
    console.log('  用户信息:', userInfo ? '已设置' : '未设置')
    console.log('  登录状态:', isLoggedIn ? '已登录' : '未登录')
    
    if (token) {
      console.log('  Token长度:', token.length)
      console.log('  Token前20字符:', token.substring(0, 20) + '...')
    }
    
    return {
      hasToken: !!token,
      hasUserInfo: !!userInfo,
      isLoggedIn: isLoggedIn,
      token: token
    }
  },

  // 测试token有效性
  testTokenValidity() {
    const app = getApp()
    const token = app.globalData.token
    
    if (!token) {
      console.log('❌ 没有token，无法测试')
      return
    }
    
    console.log('🧪 测试token有效性...')
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/auth/validate`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        console.log('✅ Token有效:', res.data)
      },
      fail: (error) => {
        console.error('❌ Token无效:', error)
        if (error.statusCode === 401) {
          console.log('🔑 Token已过期或无效，需要重新登录')
        } else if (error.statusCode === 403) {
          console.log('🚫 权限不足，可能是token格式错误')
        }
      }
    })
  },

  // 获取存储的认证信息
  getStoredAuth() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    console.log('💾 存储的认证信息:')
    console.log('  存储的Token:', token ? '已设置' : '未设置')
    console.log('  存储的用户信息:', userInfo ? '已设置' : '未设置')
    
    return {
      storedToken: token,
      storedUserInfo: userInfo
    }
  },

  // 同步存储和全局状态
  syncAuthState() {
    const app = getApp()
    const storedAuth = this.getStoredAuth()
    
    console.log('🔄 同步认证状态...')
    
    if (storedAuth.storedToken && storedAuth.storedUserInfo) {
      // 同步到全局状态
      app.globalData.token = storedAuth.storedToken
      app.globalData.userInfo = storedAuth.storedUserInfo
      app.globalData.isLoggedIn = true
      
      console.log('✅ 已同步存储的认证信息到全局状态')
    } else {
      console.log('⚠️ 没有存储的认证信息')
    }
  },

  // 完整的认证调试
  debugFullAuth() {
    console.log('🔍 开始完整认证调试...')
    
    // 1. 检查存储状态
    this.getStoredAuth()
    
    // 2. 同步状态
    this.syncAuthState()
    
    // 3. 检查全局状态
    this.checkLoginStatus()
    
    // 4. 测试token有效性
    this.testTokenValidity()
    
    console.log('🔍 认证调试完成')
  }
}

// 导出调试对象
module.exports = debugAuth
