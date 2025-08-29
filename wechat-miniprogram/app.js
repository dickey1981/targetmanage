// app.js
const { getBaseUrl } = require('./config/env.js')

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
    // 检查登录状态
    this.checkLoginStatus()
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
  }
})
