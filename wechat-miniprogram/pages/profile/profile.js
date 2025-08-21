// pages/profile/profile.js
const app = getApp()

Page({
  data: {
    userInfo: {},
    maskedPhoneNumber: '',
    stats: {
      totalGoals: 0,
      activeGoals: 0,
      completedGoals: 0,
      completionRate: 0
    },
    notificationStatus: '已开启',
    lastSyncTime: '刚刚',
    appVersion: '1.0.0'
  },

  onLoad() {
    this.loadUserInfo()
    this.loadUserStats()
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.loadUserInfo()
    this.loadUserStats()
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = app.getUserInfo()
    if (userInfo) {
      this.setData({
        userInfo: userInfo,
        maskedPhoneNumber: this.maskPhoneNumber(userInfo.phoneNumber)
      })
    } else {
      // 未登录，跳转到登录页
      wx.redirectTo({
        url: '/pages/login/login'
      })
    }
  },

  // 加载用户统计数据
  loadUserStats() {
    if (!app.checkIsLoggedIn()) return

    wx.request({
      url: `${app.globalData.baseUrl}/api/user/stats`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const stats = res.data.data
          this.setData({
            stats: {
              totalGoals: stats.totalGoals || 0,
              activeGoals: stats.activeGoals || 0,
              completedGoals: stats.completedGoals || 0,
              completionRate: stats.completionRate || 0
            }
          })
        }
      },
      fail: (err) => {
        console.error('获取统计数据失败:', err)
        // 使用默认数据
        this.setData({
          stats: {
            totalGoals: 0,
            activeGoals: 0,
            completedGoals: 0,
            completionRate: 0
          }
        })
      }
    })
  },

  // 手机号脱敏处理
  maskPhoneNumber(phone) {
    if (!phone || phone === '未授权') return phone
    if (phone.length !== 11) return phone
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
  },

  // 编辑个人资料
  onEditProfile() {
    wx.showModal({
      title: '编辑个人资料',
      content: '此功能正在开发中，敬请期待！',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 查看我的目标
  onViewGoals() {
    wx.switchTab({
      url: '/pages/goals/goals'
    })
  },

  // 查看成长时间线
  onViewTimeline() {
    wx.navigateTo({
      url: '/pages/timeline/timeline'
    })
  },

  // 查看数据分析
  onViewAnalytics() {
    wx.showModal({
      title: '数据分析',
      content: '此功能正在开发中，敬请期待！',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 通知设置
  onNotificationSettings() {
    wx.showActionSheet({
      itemList: ['开启通知', '关闭通知', '自定义设置'],
      success: (res) => {
        const actions = ['开启通知', '关闭通知', '自定义设置']
        const selected = actions[res.tapIndex]
        
        if (selected === '开启通知') {
          this.setData({ notificationStatus: '已开启' })
          this.updateNotificationSettings(true)
        } else if (selected === '关闭通知') {
          this.setData({ notificationStatus: '已关闭' })
          this.updateNotificationSettings(false)
        } else {
          this.showCustomNotificationSettings()
        }
      }
    })
  },

  // 更新通知设置
  updateNotificationSettings(enabled) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/user/notification-settings`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      data: {
        enabled: enabled
      },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({
            title: enabled ? '通知已开启' : '通知已关闭',
            icon: 'success',
            duration: 1500
          })
        }
      },
      fail: (err) => {
        console.error('更新通知设置失败:', err)
        wx.showToast({
          title: '设置失败，请重试',
          icon: 'none',
          duration: 2000
        })
      }
    })
  },

  // 显示自定义通知设置
  showCustomNotificationSettings() {
    wx.showModal({
      title: '自定义通知设置',
      content: '此功能正在开发中，敬请期待！',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 隐私设置
  onPrivacySettings() {
    wx.showModal({
      title: '隐私设置',
      content: '此功能正在开发中，敬请期待！',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 数据同步
  onDataSync() {
    this.setData({
      lastSyncTime: '同步中...'
    })

    wx.request({
      url: `${app.globalData.baseUrl}/api/user/sync-data`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            lastSyncTime: '刚刚'
          })
          wx.showToast({
            title: '数据同步成功',
            icon: 'success',
            duration: 1500
          })
        } else {
          this.setData({
            lastSyncTime: '同步失败'
          })
        }
      },
      fail: (err) => {
        console.error('数据同步失败:', err)
        this.setData({
          lastSyncTime: '同步失败'
        })
        wx.showToast({
          title: '同步失败，请重试',
          icon: 'none',
          duration: 2000
        })
      }
    })
  },

  // 使用帮助
  onHelp() {
    wx.showModal({
      title: '使用帮助',
      content: '1. 语音创建目标：点击语音按钮，说出您的目标\n2. 拍照更新进度：拍摄相关照片，系统自动识别\n3. 查看时间线：记录您的成长历程\n4. 更多功能请访问帮助中心',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  // 意见反馈
  onFeedback() {
    wx.showModal({
      title: '意见反馈',
      content: '感谢您的反馈！请发送邮件至：feedback@targetmanage.com',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 关于我们
  onAbout() {
    wx.showModal({
      title: '关于我们',
      content: '智能目标管理系统 v1.0.0\n\n我们致力于让目标管理变得简单智能，通过AI技术帮助用户更好地实现目标。\n\n如有问题，请联系客服。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 退出登录
  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '退出登录后需要重新授权，是否确认退出？',
      confirmText: '退出',
      cancelText: '取消',
      confirmColor: '#ff4757',
      success: (res) => {
        if (res.confirm) {
          app.logout()
        }
      }
    })
  },

  // 页面分享
  onShareAppMessage() {
    return {
      title: '智能目标管理 - 让目标管理变得简单智能',
      path: '/pages/profile/profile',
      imageUrl: '/images/share-cover.png'
    }
  }
})
