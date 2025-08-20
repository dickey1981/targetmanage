// app.js
App({
  onLaunch() {
    console.log('目标管理小程序启动')
    
    // 检查登录状态
    this.checkLogin()
    
    // 初始化云开发
    if (wx.cloud) {
      wx.cloud.init({
        // env 参数说明：
        //   env 参数决定接下来小程序发起的云开发调用（wx.cloud.xxx）会默认请求到哪个云环境的资源
        //   此处请填入环境 ID, 环境 ID 可打开云控制台查看
        // traceUser: true,
      })
    }
  },

  onShow() {
    // 小程序显示时执行
  },

  onHide() {
    // 小程序隐藏时执行
  },

  onError(error) {
    console.error('小程序错误:', error)
  },

  // 全局数据
  globalData: {
    userInfo: null,
    token: null,
    baseUrl: 'http://localhost:8000/api/v1', // 后端API地址
    isLogin: false
  },

  // 检查登录状态
  checkLogin() {
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
      this.globalData.isLogin = true
      
      // 验证token有效性
      this.validateToken()
    }
  },

  // 验证token
  validateToken() {
    const { request } = require('./utils/request')
    
    request({
      url: '/auth/me',
      method: 'GET'
    }).then(res => {
      this.globalData.userInfo = res.data
      this.globalData.isLogin = true
    }).catch(err => {
      console.log('token验证失败:', err)
      this.logout()
    })
  },

  // 登录
  login(userInfo) {
    this.globalData.userInfo = userInfo
    this.globalData.isLogin = true
  },

  // 登出
  logout() {
    this.globalData.userInfo = null
    this.globalData.token = null
    this.globalData.isLogin = false
    
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    
    // 跳转到登录页面
    wx.reLaunch({
      url: '/pages/auth/login'
    })
  },

  // 设置token
  setToken(token) {
    this.globalData.token = token
    wx.setStorageSync('token', token)
  }
})
