// pages/login/login.js
const app = getApp()

Page({
  data: {
    hasUserInfo: false,
    hasPhoneNumber: false,
    userInfo: null,
    phoneNumber: null,
    maskedPhoneNumber: '',
    isLoading: false,
    loadingText: '正在处理...'
  },

  onLoad() {
    // 检查是否已经登录
    if (app.checkIsLoggedIn()) {
      this.redirectToIndex()
    }
  },

  // 获取微信用户信息
  onGetUserInfo(e) {
    console.log('获取用户信息:', e)
    
    if (e.detail.userInfo) {
      // 用户同意授权
      this.setData({
        hasUserInfo: true,
        userInfo: e.detail.userInfo
      })
      
      wx.showToast({
        title: '微信授权成功',
        icon: 'success',
        duration: 1500
      })
    } else {
      // 用户拒绝授权
      wx.showModal({
        title: '授权提示',
        content: '需要获取您的微信信息才能正常使用小程序，是否重新授权？',
        confirmText: '重新授权',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            // 引导用户重新授权
            this.showAuthGuide()
          }
        }
      })
    }
  },

  // 获取手机号
  onGetPhoneNumber(e) {
    console.log('获取手机号:', e)
    
    if (e.detail.errMsg === 'getPhoneNumber:ok') {
      // 用户同意授权手机号
      const { code } = e.detail
      
      this.setData({
        isLoading: true,
        loadingText: '正在获取手机号...'
      })

      // 调用后端API解密手机号
      this.decryptPhoneNumber(code)
    } else {
      // 用户拒绝授权手机号
      wx.showModal({
        title: '手机号授权提示',
        content: '手机号用于重要通知和账户安全，建议您授权使用。是否重新授权？',
        confirmText: '重新授权',
        cancelText: '跳过',
        success: (res) => {
          if (res.confirm) {
            // 用户选择重新授权，这里可以重新显示手机号授权按钮
            // 由于微信限制，需要用户手动触发
            wx.showToast({
              title: '请点击手机号授权按钮',
              icon: 'none',
              duration: 2000
            })
          } else {
            // 用户选择跳过，直接进入登录流程
            this.setData({
              hasPhoneNumber: true,
              phoneNumber: '未授权',
              maskedPhoneNumber: '***'
            })
          }
        }
      })
    }
  },

  // 解密手机号
  decryptPhoneNumber(code) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/auth/decrypt-phone`,
      method: 'POST',
      data: {
        code: code
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const phoneNumber = res.data.data.phoneNumber
          const maskedPhone = this.maskPhoneNumber(phoneNumber)
          
          this.setData({
            hasPhoneNumber: true,
            phoneNumber: phoneNumber,
            maskedPhoneNumber: maskedPhone,
            isLoading: false
          })
          
          wx.showToast({
            title: '手机号授权成功',
            icon: 'success',
            duration: 1500
          })
        } else {
          this.setData({ isLoading: false })
          wx.showToast({
            title: res.data.message || '获取手机号失败',
            icon: 'none',
            duration: 2000
          })
        }
      },
      fail: (err) => {
        console.error('解密手机号失败:', err)
        this.setData({ isLoading: false })
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none',
          duration: 2000
        })
      }
    })
  },

  // 手机号脱敏处理
  maskPhoneNumber(phone) {
    if (!phone || phone.length !== 11) return phone
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
  },

  // 执行登录
  onLogin() {
    if (!this.data.hasUserInfo) {
      wx.showToast({
        title: '请先授权微信信息',
        icon: 'none',
        duration: 2000
      })
      return
    }

    this.setData({
      isLoading: true,
      loadingText: '正在登录...'
    })

    // 调用全局登录方法
    app.login(this.data.userInfo, this.data.phoneNumber)
      .then((user) => {
        this.setData({ isLoading: false })
        
        wx.showToast({
          title: '登录成功',
          icon: 'success',
          duration: 1500
        })

        // 延迟跳转，让用户看到成功提示
        setTimeout(() => {
          this.redirectToIndex()
        }, 1500)
      })
      .catch((err) => {
        console.error('登录失败:', err)
        this.setData({ isLoading: false })
        
        wx.showModal({
          title: '登录失败',
          content: err.message || '登录过程中出现错误，请重试',
          showCancel: false,
          confirmText: '确定'
        })
      })
  },

  // 跳转到首页
  redirectToIndex() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  // 显示授权引导
  showAuthGuide() {
    wx.showModal({
      title: '授权说明',
      content: '1. 点击"微信授权登录"按钮\n2. 在弹出的授权弹窗中点击"允许"\n3. 授权成功后继续下一步',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  // 查看隐私政策
  onViewPrivacy() {
    wx.showModal({
      title: '用户协议和隐私政策',
      content: '我们承诺保护您的个人信息安全，详细内容请访问我们的官方网站。',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  // 页面分享
  onShareAppMessage() {
    return {
      title: '智能目标管理 - 让目标管理变得简单智能',
      path: '/pages/login/login',
      imageUrl: '/images/share-cover.png'
    }
  }
})
