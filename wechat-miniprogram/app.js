// app.js
App({
  globalData: {
    userInfo: null,
    token: null,
    baseUrl: 'http://your-lighthouse-ip:8000', // 替换为您的Lighthouse服务器IP
    isLoggedIn: false
  },

  onLaunch() {
    console.log('小程序启动')
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
      
      // 验证token有效性
      this.validateToken()
    }
  },

  // 验证token有效性
  validateToken() {
    wx.request({
      url: `${this.globalData.baseUrl}/api/auth/validate`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${this.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode !== 200) {
          this.logout()
        }
      },
      fail: () => {
        this.logout()
      }
    })
  },

  // 登录
  login(userInfo, phoneNumber) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.baseUrl}/api/auth/login`,
        method: 'POST',
        data: {
          userInfo: userInfo,
          phoneNumber: phoneNumber
        },
        success: (res) => {
          if (res.statusCode === 200 && res.data.success) {
            const { token, user } = res.data.data
            
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
          reject(err)
        }
      })
    })
  },

  // 登出
  logout() {
    this.globalData.token = null
    this.globalData.userInfo = null
    this.globalData.isLoggedIn = false
    
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    
    // 跳转到登录页
    wx.reLaunch({
      url: '/pages/login/login'
    })
  },

  // 获取用户信息
  getUserInfo() {
    return this.globalData.userInfo
  },

  // 检查是否已登录
  checkIsLoggedIn() {
    return this.globalData.isLoggedIn
  }
})
