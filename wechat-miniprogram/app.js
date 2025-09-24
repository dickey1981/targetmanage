// app.js
const { getBaseUrl } = require('./config/env.js')
const { safeReportRealtimeAction, getEnvironmentInfo } = require('./utils/api-compat.js')
const { initDevWarnings } = require('./utils/dev-warnings.js')

App({
  globalData: {
    // 根据环境自动选择API地址
    baseUrl: getBaseUrl(),
    token: null,
    userInfo: null,
    isLoggedIn: false,
    // 创建目标弹窗显示标志
    showCreateGoalModal: false
  },

  onLaunch() {
    // 初始化开发环境警告处理
    initDevWarnings()
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 检查环境兼容性
    this.checkEnvironmentCompatibility()
    
    // 调试信息
    console.log('🚀 App启动，baseUrl:', this.globalData.baseUrl)
  },

  // 检查环境兼容性
  checkEnvironmentCompatibility() {
    const envInfo = getEnvironmentInfo()
    console.log('🔍 环境兼容性检查:', envInfo)
    
    // 如果某些API不支持，记录警告但不影响功能
    if (!envInfo.isRealtimeActionSupported) {
      console.warn('⚠️ reportRealtimeAction API 不支持，将跳过实时数据上报')
    }
    
    if (!envInfo.isWorkerSupported) {
      console.warn('⚠️ Worker API 不支持，某些后台功能可能受限')
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      this.globalData.isLoggedIn = true
    }
  },

  // 登出
  logout() {
    this.globalData.token = null
    this.globalData.userInfo = null
    this.globalData.isLoggedIn = false
    
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    
    // 不需要跳转，因为现在默认在首页
  },

  // 获取用户信息
  getUserInfo() {
    return this.globalData.userInfo
  },

  // 检查是否已登录
  checkIsLoggedIn() {
    return this.globalData.isLoggedIn && this.globalData.token
  },

  // 微信登录方法
  login(userInfo, phoneNumber) {
    return new Promise((resolve, reject) => {
      // 获取微信登录code
      wx.login({
        success: (loginRes) => {
          if (loginRes.code) {
            // 调用后端登录接口
            wx.request({
              url: `${this.globalData.baseUrl}/api/auth/wechat-login`,
              method: 'POST',
              data: {
                code: loginRes.code,
                userInfo: userInfo,
                phoneNumber: phoneNumber
              },
              success: (res) => {
                if (res.statusCode === 200 && res.data.success) {
                  const { user, token } = res.data.data
                  
                  // 保存登录信息
                  this.globalData.token = token
                  this.globalData.userInfo = user
                  this.globalData.isLoggedIn = true
                  
                  wx.setStorageSync('token', token)
                  wx.setStorageSync('userInfo', user)
                  
                  resolve(user)
                } else {
                  reject(new Error(res.data.message || '登录失败'))
                }
              },
              fail: (err) => {
                console.error('登录请求失败:', err)
                reject(new Error('网络错误，请重试'))
              }
            })
          } else {
            reject(new Error('获取微信登录code失败'))
          }
        },
        fail: (err) => {
          console.error('微信登录失败:', err)
          reject(new Error('微信登录失败'))
        }
      })
    })
  }
})
