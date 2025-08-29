// pages/index/index.js
const app = getApp()

Page({
  data: {
    isLoggedIn: false,
    userInfo: null,
    showLoginModal: false,
    isLoggingIn: false,
    todayGoals: [],
    completedGoalsCount: 0,
    pendingGoalsCount: 0,
    // 语音交互相关
    isRecording: false,
    recordingText: '按住说话',
    voiceHint: '松开结束',
    // 问候语
    greetingText: '早上好',
    // 快捷操作
    quickActions: [
      { id: 'photo', name: '拍照记录', icon: '📷', color: '#28a745' },
      { id: 'create', name: '创建目标', icon: '➕', color: '#667eea' },
      { id: 'sync', name: '数据同步', icon: '🔄', color: '#ffc107' }
    ]
  },

  onLoad() {
    this.checkLoginStatus()
    this.loadTodayGoals()
    this.updateGreeting()
    
    // 调试信息
    console.log('页面加载 - 环境配置信息:')
    console.log('全局baseUrl:', app.globalData.baseUrl)
    console.log('当前环境:', wx.getSystemInfoSync().platform)
  },

  onShow() {
    this.checkLoginStatus()
    if (this.data.isLoggedIn) {
      this.loadTodayGoals()
    }
    this.updateGreeting()
  },

  // 更新问候语
  updateGreeting() {
    const hour = new Date().getHours()
    let greeting = ''
    
    if (hour >= 5 && hour < 12) {
      greeting = '早上好'
    } else if (hour >= 12 && hour < 18) {
      greeting = '下午好'
    } else {
      greeting = '晚上好'
    }
    
    this.setData({
      greetingText: greeting
    })
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      })
      // 验证token有效性
      this.validateToken()
    } else {
      this.setData({
        isLoggedIn: false,
        userInfo: null
      })
    }
  },

  // 验证token有效性
  validateToken() {
    wx.request({
      url: `${app.globalData.baseUrl}/api/auth/validate`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
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

  // 显示登录浮窗
  showLoginModal() {
    this.setData({
      showLoginModal: true
    })
  },

  // 隐藏登录浮窗
  hideLoginModal() {
    this.setData({
      showLoginModal: false
    })
  },

  // 获取微信用户信息
  onGetUserInfo(e) {
    if (e.detail.userInfo) {
      this.setData({
        userInfo: e.detail.userInfo
      })
      
      // 先获取微信登录code，然后调用登录接口
      this.loginWithWeChat(e.detail.userInfo)
    } else {
      wx.showToast({
        title: '需要授权才能使用',
        icon: 'none'
      })
    }
  },

  // 使用微信信息登录/注册
  loginWithWeChat(userInfo) {
    this.setData({
      isLoggingIn: true
    })

    // 先获取微信登录code
    wx.login({
      success: (loginRes) => {
        if (loginRes.code) {
          // 获取到code后，发送给后端
          this.sendLoginRequest(loginRes.code, userInfo)
        } else {
          wx.showToast({
            title: '获取登录凭证失败',
            icon: 'none'
          })
          this.setData({
            isLoggingIn: false
          })
        }
      },
      fail: (err) => {
        console.error('wx.login失败:', err)
        wx.showToast({
          title: '微信登录失败',
          icon: 'none'
        })
        this.setData({
          isLoggingIn: false
        })
      }
    })
  },

  // 发送登录请求到后端
  sendLoginRequest(code, userInfo) {
    // 调试信息
    const apiUrl = `${app.globalData.baseUrl}/api/auth/wechat-login`
    console.log('API地址:', apiUrl)
    console.log('全局baseUrl:', app.globalData.baseUrl)
    console.log('微信code:', code)
    console.log('用户信息:', userInfo)

    wx.request({
      url: apiUrl,
      method: 'POST',
      data: {
        code: code,
        userInfo: userInfo
      },
      success: (res) => {
        console.log('登录响应:', res)
        console.log('响应数据:', res.data)
        
        if (res.statusCode === 200 && res.data.success) {
          // 后端返回的数据结构：{ success: true, message: "登录成功", data: {...} }
          const responseData = res.data.data || {}
          const { token, user, isNewUser } = responseData
          
          console.log('提取的数据:', { token, user, isNewUser })
          
          // 验证必要字段
          if (!token || !user) {
            console.error('登录响应数据不完整:', responseData)
            wx.showToast({
              title: '登录数据不完整',
              icon: 'none'
            })
            return
          }
          
          // 保存登录信息
          wx.setStorageSync('token', token)
          wx.setStorageSync('userInfo', user)
          
          // 更新全局状态
          app.globalData.token = token
          app.globalData.userInfo = user
          app.globalData.isLoggedIn = true
          
          this.setData({
            isLoggedIn: true,
            userInfo: user,
            showLoginModal: false,
            isLoggingIn: false
          })

          // 显示欢迎信息
          if (isNewUser) {
            wx.showToast({
              title: '欢迎新用户！',
              icon: 'success'
            })
          } else {
            wx.showToast({
              title: '登录成功！',
              icon: 'success'
            })
          }

          // 加载用户数据
          this.loadTodayGoals()
        } else {
          console.error('登录失败:', res.data)
          wx.showToast({
            title: res.data.message || '登录失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('登录失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({
          isLoggingIn: false
        })
      }
    })
  },

  // 登出
  logout() {
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    
    app.globalData.token = null
    app.globalData.userInfo = null
    app.globalData.isLoggedIn = false
    
    this.setData({
      isLoggedIn: false,
      userInfo: null
    })
  },

  // 加载今日目标
  loadTodayGoals() {
    if (!this.data.isLoggedIn) return

    const token = wx.getStorageSync('token')
    console.log('🔍 加载今日目标 - Token:', token)
    console.log('🔍 请求URL:', `${app.globalData.baseUrl}/api/goals/today`)

    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/today`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        console.log('✅ 今日目标响应:', res)
        if (res.statusCode === 200 && res.data.success) {
          const goals = res.data.data || []
          const completedCount = goals.filter(g => g.completed).length
          const pendingCount = goals.filter(g => !g.completed).length
          
          this.setData({
            todayGoals: goals,
            completedGoalsCount: completedCount,
            pendingGoalsCount: pendingCount
          })
          
          console.log('✅ 今日目标加载成功:', goals.length, '个')
        } else {
          console.error('❌ 今日目标响应异常:', res.data)
        }
      },
      fail: (err) => {
        console.error('❌ 加载今日目标失败:', err)
      }
    })
  },

  // 语音交互相关方法
  startVoiceRecord() {
    if (!this.data.isLoggedIn) {
      this.showLoginModal()
      return
    }
    
    this.setData({
      isRecording: true,
      recordingText: '正在录音...',
      voiceHint: '松开结束录音'
    })
    
    // TODO: 调用微信录音API
    wx.showToast({
      title: '开始录音',
      icon: 'none'
    })
    
    // 模拟录音状态
    this.recordingTimer = setInterval(() => {
      this.setData({
        voiceHint: '正在录音...'
      })
    }, 1000)
  },

  stopVoiceRecord() {
    if (!this.data.isRecording) return
    
    clearInterval(this.recordingTimer)
    
    this.setData({
      isRecording: false,
      recordingText: '录音完成，正在识别...',
      voiceHint: '请稍候'
    })
    
    // TODO: 调用语音识别API
    wx.showToast({
      title: '录音完成，正在识别...',
      icon: 'none'
    })
    
    // 模拟语音识别过程
    setTimeout(() => {
      this.setData({
        recordingText: '按住说话',
        voiceHint: '松开结束'
      })
      
      // 显示识别结果示例
      wx.showModal({
        title: '语音识别结果',
        content: '识别到："今天跑了5公里，用时30分钟"\n是否更新运动目标？',
        confirmText: '确认更新',
        cancelText: '重新录音',
        success: (res) => {
          if (res.confirm) {
            // TODO: 调用后端API更新目标进度
            wx.showToast({
              title: '进度更新成功！',
              icon: 'success'
            })
          }
        }
      })
    }, 2000)
  },

  // 快捷操作
  onQuickAction(e) {
    const { id } = e.currentTarget.dataset
    
    switch (id) {
      case 'photo':
        this.takePhoto()
        break
      case 'create':
        this.createGoal()
        break
      case 'sync':
        this.syncData()
        break
    }
  },

  // 拍照记录
  takePhoto() {
    if (!this.data.isLoggedIn) {
      this.showLoginModal()
      return
    }

    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['camera'],
      success: (res) => {
        // TODO: 调用OCR API识别图片
        wx.showToast({
          title: '正在识别图片...',
          icon: 'none'
        })
      }
    })
  },

  // 创建目标
  createGoal() {
    // 检查用户是否已登录
    if (!app.globalData.userInfo) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    console.log('用户已登录，跳转到目标管理页面')
    // 设置全局标志，表示要显示语音创建弹窗
    app.globalData.showCreateGoalModal = true
    
    // 跳转到目标管理页面（tab页面）
    wx.switchTab({
      url: '/pages/goals/goals',
      success: () => {
        console.log('跳转成功')
      },
      fail: (err) => {
        console.error('跳转失败:', err)
        wx.showToast({
          title: '页面跳转失败',
          icon: 'none'
        })
      }
    })
  },

  // 数据同步
  syncData() {
    if (!this.data.isLoggedIn) {
      this.showLoginModal()
      return
    }

    wx.showToast({
      title: '开始同步数据...',
      icon: 'none'
    })
  },

  // 查看全部目标
  viewAllGoals() {
    wx.switchTab({
      url: '/pages/goals/goals'
    })
  },

  // 跳转到目标详情
  goToGoalDetail(e) {
    const goalId = e.currentTarget.dataset.goalId
    wx.navigateTo({
      url: `/pages/goal-detail/goal-detail?id=${goalId}`
    })
  }
})
