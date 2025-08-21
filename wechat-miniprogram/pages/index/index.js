// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: {},
    greeting: '早上好',
    currentDate: '',
    weekDay: '',
    isRecording: false,
    recordingTime: 0,
    waveBars: [20, 40, 60, 40, 20, 30, 50, 30],
    todayGoals: [],
    recentRecords: [],
    recordingTimer: null
  },

  onLoad() {
    this.loadUserInfo()
    this.updateDateTime()
    this.loadTodayGoals()
    this.loadRecentRecords()
    
    // 每分钟更新一次时间
    this.timeUpdateInterval = setInterval(() => {
      this.updateDateTime()
    }, 60000)
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.loadUserInfo()
    this.loadTodayGoals()
    this.loadRecentRecords()
  },

  onUnload() {
    // 清理定时器
    if (this.timeUpdateInterval) {
      clearInterval(this.timeUpdateInterval)
    }
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
    }
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = app.getUserInfo()
    if (userInfo) {
      this.setData({ userInfo })
      this.updateGreeting()
    }
  },

  // 更新日期时间
  updateDateTime() {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth() + 1
    const date = now.getDate()
    const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const weekDay = weekDays[now.getDay()]
    
    this.setData({
      currentDate: `${year}年${month}月${date}日`,
      weekDay: weekDay
    })
  },

  // 更新问候语
  updateGreeting() {
    const hour = new Date().getHours()
    let greeting = '早上好'
    
    if (hour >= 5 && hour < 12) {
      greeting = '早上好'
    } else if (hour >= 12 && hour < 18) {
      greeting = '下午好'
    } else if (hour >= 18 && hour < 22) {
      greeting = '晚上好'
    } else {
      greeting = '夜深了'
    }
    
    this.setData({ greeting })
  },

  // 加载今日目标
  loadTodayGoals() {
    if (!app.checkIsLoggedIn()) return

    // 这里应该调用API获取今日目标
    // 目前使用模拟数据
    const mockGoals = [
      {
        id: 1,
        title: '减重目标',
        category: '健康',
        progress: 65,
        status: 'normal',
        statusText: '进行中'
      },
      {
        id: 2,
        title: '学习Python',
        category: '学习',
        progress: 30,
        status: 'urgent',
        statusText: '需加速'
      }
    ]
    
    this.setData({ todayGoals: mockGoals })
  },

  // 加载最近记录
  loadRecentRecords() {
    if (!app.checkIsLoggedIn()) return

    // 这里应该调用API获取最近记录
    // 目前使用模拟数据
    const mockRecords = [
      {
        id: 1,
        type: 'voice',
        content: '今天跑了5公里，感觉很不错',
        time: '2小时前'
      },
      {
        id: 2,
        type: 'photo',
        content: '体重秤显示70.5kg',
        time: '昨天'
      }
    ]
    
    this.setData({ recentRecords: mockRecords })
  },

  // 开始录音
  onVoiceStart() {
    this.setData({ 
      isRecording: true,
      recordingTime: 0
    })
    
    // 开始录音计时
    const timer = setInterval(() => {
      this.setData({
        recordingTime: this.data.recordingTime + 1
      })
    }, 1000)
    
    this.setData({ recordingTimer: timer })
    
    // 这里应该调用微信录音API
    console.log('开始录音')
  },

  // 结束录音
  onVoiceEnd() {
    this.setData({ isRecording: false })
    
    // 停止计时
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
      this.setData({ recordingTimer: null })
    }
    
    // 这里应该停止录音并处理录音结果
    console.log('录音结束，时长:', this.data.recordingTime, '秒')
    
    // 模拟语音识别结果
    this.processVoiceInput('今天完成了减重目标的一半')
  },

  // 取消录音
  onVoiceCancel() {
    this.setData({ isRecording: false })
    
    // 停止计时
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
      this.setData({ recordingTimer: null })
    }
    
    console.log('录音已取消')
  },

  // 处理语音输入
  processVoiceInput(text) {
    wx.showModal({
      title: '语音识别结果',
      content: `识别内容：${text}\n\n请确认是否正确？`,
      confirmText: '正确',
      cancelText: '重新录音',
      success: (res) => {
        if (res.confirm) {
          // 处理正确的语音输入
          this.handleVoiceCommand(text)
        } else {
          // 重新录音
          wx.showToast({
            title: '请重新录音',
            icon: 'none',
            duration: 2000
          })
        }
      }
    })
  },

  // 处理语音命令
  handleVoiceCommand(text) {
    // 这里应该调用后端API处理语音命令
    // 目前只是显示提示
    wx.showToast({
      title: '语音命令已处理',
      icon: 'success',
      duration: 2000
    })
    
    // 刷新数据
    setTimeout(() => {
      this.loadTodayGoals()
      this.loadRecentRecords()
    }, 1000)
  },

  // 点击目标项
  onGoalTap(e) {
    const goal = e.currentTarget.dataset.goal
    wx.navigateTo({
      url: `/pages/goal-detail/goal-detail?id=${goal.id}`
    })
  },

  // 创建目标
  onCreateGoal() {
    wx.navigateTo({
      url: '/pages/goals/create-goal'
    })
  },

  // 快速拍照
  onQuickPhoto() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        this.processPhoto(tempFilePath)
      },
      fail: (err) => {
        console.error('拍照失败:', err)
        wx.showToast({
          title: '拍照失败',
          icon: 'none',
          duration: 2000
        })
      }
    })
  },

  // 快速语音
  onQuickVoice() {
    // 直接触发语音录音
    this.onVoiceStart()
  },

  // 快速查看
  onQuickView() {
    wx.navigateTo({
      url: '/pages/timeline/timeline'
    })
  },

  // 处理拍照结果
  processPhoto(filePath) {
    // 这里应该调用后端OCR API处理图片
    // 目前只是显示提示
    wx.showToast({
      title: '图片已上传，正在识别...',
      icon: 'loading',
      duration: 2000
    })
    
    // 模拟识别过程
    setTimeout(() => {
      wx.showModal({
        title: '识别结果',
        content: '检测到数字：70.5\n\n是否更新减重目标进度？',
        confirmText: '更新',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            // 更新目标进度
            wx.showToast({
              title: '进度已更新',
              icon: 'success',
              duration: 1500
            })
            
            // 刷新数据
            setTimeout(() => {
              this.loadTodayGoals()
              this.loadRecentRecords()
            }, 1000)
          }
        }
      })
    }, 2000)
  },

  // 点击记录项
  onRecordTap(e) {
    const record = e.currentTarget.dataset.record
    wx.navigateTo({
      url: `/pages/process-record/process-record?id=${record.id}`
    })
  },

  // 页面分享
  onShareAppMessage() {
    return {
      title: '智能目标管理 - 让目标管理变得简单智能',
      path: '/pages/index/index',
      imageUrl: '/images/share-cover.png'
    }
  }
})
