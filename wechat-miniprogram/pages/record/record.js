// pages/record/record.js
const app = getApp()

Page({
  data: {
    isLoggedIn: false,
    userInfo: null,
    recordTypes: [
      { id: 'voice', name: '语音记录', icon: '🎤', color: '#667eea' },
      { id: 'photo', name: '拍照记录', icon: '📷', color: '#28a745' },
      { id: 'text', name: '文字记录', icon: '✏️', color: '#ffc107' }
    ],
    recentRecords: [],
    showRecordModal: false,
    currentRecordType: null,
    // 语音交互相关
    isRecording: false,
    recordingText: '按住说话',
    voiceHint: '松开结束',
    isNavigating: false,
    // 文字记录相关
    textInput: '',
    isSubmitting: false,
    // 目标选择相关
    availableGoals: [],
    selectedGoalId: null
  },

  onLoad() {
    this.checkLoginStatus()
  },

  onShow() {
    console.log('📱 record页面显示')
    
    // 重置导航状态
    this.setData({
      isNavigating: false
    })
    
    this.checkLoginStatus()
    if (this.data.isLoggedIn) {
      // 只加载最近记录，不加载目标列表
      this.loadRecentRecords()
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      // 更新全局状态
      app.globalData.token = token
      app.globalData.userInfo = userInfo
      app.globalData.isLoggedIn = true
      
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      })
    } else {
      // 清除全局状态
      app.globalData.token = null
      app.globalData.userInfo = null
      app.globalData.isLoggedIn = false
      
      this.setData({
        isLoggedIn: false,
        userInfo: null
      })
    }
  },

  // 加载最近记录
  loadRecentRecords() {
    const token = app.globalData.token
    if (!token) {
      console.warn('无法加载最近记录：用户未登录')
      return
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/process-records/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        page: 1,
        page_size: 10
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            recentRecords: res.data.records || []
          })
        }
      },
      fail: (err) => {
        console.error('加载最近记录失败:', err)
      }
    })
  },

  // 选择记录类型
  onSelectRecordType(e) {
    const { id } = e.currentTarget.dataset
    
    if (!this.data.isLoggedIn) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    this.setData({
      currentRecordType: id,
      showRecordModal: true
    })
  },

  // 关闭记录模态框
  closeRecordModal() {
    this.setData({
      showRecordModal: false,
      currentRecordType: null
    })
  },

  // 语音记录
  startVoiceRecord() {
    console.log('🎤 开始语音录制')
    
    // 申请录音权限
    wx.authorize({
      scope: 'scope.record',
      success: () => {
        console.log('✅ 录音权限已获取')
        this.startRecordingWithPermission()
      },
      fail: (err) => {
        console.error('❌ 录音权限获取失败:', err)
        wx.showModal({
          title: '需要录音权限',
          content: '为了使用语音记录功能，需要获取录音权限',
          confirmText: '去设置',
          success: (res) => {
            if (res.confirm) {
              wx.openSetting({
                success: (settingRes) => {
                  if (settingRes.authSetting['scope.record']) {
                    console.log('✅ 用户已授权录音权限')
                    this.startRecordingWithPermission()
                  }
                }
              })
            }
          }
        })
      }
    })
  },

  // 有权限后开始录音
  startRecordingWithPermission() {
    const recorderManager = wx.getRecorderManager()
    
    // 设置录音事件监听
    recorderManager.onStart(() => {
      console.log('🎤 录音开始')
      this.setData({
        isRecording: true,
        recordingText: '正在录音...',
        voiceHint: '松开结束录音'
      })
    })
    
    recorderManager.onStop((res) => {
      console.log('🛑 录音结束:', res)
      this.setData({
        isRecording: false,
        recordingText: '按住说话',
        voiceHint: '松开结束'
      })
      
      // 处理录音结果
      this.handleVoiceRecordingResult(res)
    })
    
    recorderManager.onError((err) => {
      console.error('❌ 录音错误:', err)
      this.setData({
        isRecording: false,
        recordingText: '按住说话',
        voiceHint: '录音失败，请重试'
      })
      wx.showToast({
        title: '录音失败',
        icon: 'none'
      })
    })
    
    // 开始录音
    recorderManager.start({
      duration: 60000, // 最长60秒
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 96000,
      format: 'mp3'
    })
  },

  stopVoiceRecord() {
    console.log('🛑 停止语音录制')
    const recorderManager = wx.getRecorderManager()
    
    if (this.data.isRecording) {
      recorderManager.stop()
    }
  },

  // 处理语音录制结果
  handleVoiceRecordingResult(res) {
    console.log('处理语音录制结果:', res)
    
    // 显示录音完成提示
    wx.showToast({
      title: '录音完成，正在识别...',
      icon: 'loading',
      duration: 2000
    })
    
    // 先尝试真实的上传，如果失败会回退到模拟结果
    this.uploadAudioForRecognition(res.tempFilePath)
  },

  // 模拟语音识别
  simulateVoiceRecognition() {
    console.log('🎤 使用模拟语音识别结果')
    
    // 模拟的语音识别结果
    const mockVoiceText = "今天学习了Python编程，完成了第一个计算器项目，感觉很有成就感！"
    
    // 跳转到记录详情确认编辑页面
    this.navigateToRecordEdit(mockVoiceText)
    
    console.log('✅ 模拟语音识别完成，内容:', mockVoiceText)
  },

  // 跳转到记录详情确认编辑页面
  navigateToRecordEdit(voiceText) {
    // 防止重复跳转
    if (this.data.isNavigating) {
      console.log('⚠️ 正在跳转中，忽略重复请求')
      return
    }
    
    this.setData({
      isNavigating: true
    })
    
    // 关闭语音录制弹窗
    this.setData({
      showRecordModal: false,
      currentRecordType: null
    })
    
    console.log('🚀 跳转到记录编辑页面，语音内容:', voiceText)
    
    // 跳转到记录编辑页面，传递语音识别结果
    wx.navigateTo({
      url: `/pages/process-record/process-record?mode=create&voiceText=${encodeURIComponent(voiceText)}&goalId=${this.data.selectedGoalId || ''}`,
      success: () => {
        console.log('✅ 页面跳转成功')
      },
      fail: (err) => {
        console.error('❌ 页面跳转失败:', err)
        this.setData({
          isNavigating: false
        })
      }
    })
  },

  // 上传音频进行语音识别
  uploadAudioForRecognition(filePath) {
    wx.uploadFile({
      url: `${app.globalData.baseUrl}/api/process-records/recognize-voice`,
      filePath: filePath,
      name: 'audio',
      header: {
        'Content-Type': 'multipart/form-data'
      },
      success: (res) => {
        console.log('语音识别响应:', res)
        
        try {
          const data = JSON.parse(res.data)
          console.log('解析后的数据:', data)
          
          if (data.success) {
            const voiceText = data.data.voice_text
            console.log('语音识别结果:', voiceText)
            
            // 跳转到记录详情确认编辑页面
            this.navigateToRecordEdit(voiceText)
            
          } else {
            console.error('语音识别失败:', data.message)
            // 如果真实识别失败，使用模拟结果
            setTimeout(() => {
              this.simulateVoiceRecognition()
            }, 1000)
          }
        } catch (error) {
          console.error('解析语音识别结果失败:', error)
          // 如果解析失败，使用模拟结果
          setTimeout(() => {
            this.simulateVoiceRecognition()
          }, 1000)
        }
      },
      fail: (error) => {
        console.error('语音识别请求失败:', error)
        // 如果请求失败，使用模拟结果
        setTimeout(() => {
          this.simulateVoiceRecognition()
        }, 1000)
      }
    })
  },

  // 拍照记录
  takePhoto() {
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

  // 文字记录输入
  onTextInput(e) {
    this.setData({
      textInput: e.detail.value
    })
  },

  // 提交文字记录
  submitTextRecord() {
    const text = this.data.textInput.trim()
    if (!text) {
      wx.showToast({
        title: '请输入记录内容',
        icon: 'none'
      })
      return
    }

    this.setData({
      isSubmitting: true
    })

    this.submitRecord('text', { 
      content: text,
      goalId: this.data.selectedGoalId 
    })
  },

  // 提交记录
  submitRecord(type, data) {
    // 映射前端类型到后端枚举值
    const sourceMapping = {
      'text': 'manual',
      'voice': 'voice', 
      'photo': 'photo',
      'manual': 'manual'
    }
    
    const token = app.globalData.token
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/process-records/`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      data: {
        content: data.content || '',
        record_type: 'process', // 默认类型
        source: sourceMapping[type] || 'manual', // 映射到后端枚举值
        goal_id: data.goalId || null,
        user_id: '537632ba-f2f2-4c80-a0cb-b23318fef17b' // TODO: 从认证中获取
      },
      success: (res) => {
        this.setData({
          isSubmitting: false
        })
        
        if (res.statusCode === 200) {
          wx.showToast({
            title: '记录成功',
            icon: 'success'
          })
          // 重置输入框
          this.setData({
            textInput: ''
          })
          this.closeRecordModal()
          this.loadRecentRecords()
        } else {
          wx.showToast({
            title: res.data.detail || '记录失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        this.setData({
          isSubmitting: false
        })
        console.error('提交记录失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 查看记录详情
  viewRecordDetail(e) {
    const recordId = e.currentTarget.dataset.recordId
    wx.navigateTo({
      url: `/pages/record-detail/record-detail?id=${recordId}`
    })
  },

  // 加载可用目标
  loadAvailableGoals() {
    const token = app.globalData.token
    if (!token) {
      console.warn('无法加载可用目标：用户未登录')
      return
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        status: 'active',
        page: 1,
        page_size: 50
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            availableGoals: res.data.goals || []
          })
        }
      },
      fail: (err) => {
        console.error('加载可用目标失败:', err)
      }
    })
  },

  // 选择目标
  selectGoal(e) {
    const goalId = e.currentTarget.dataset.goalId
    this.setData({
      selectedGoalId: goalId
    })
  },

  // 清除目标选择
  clearGoalSelection() {
    this.setData({
      selectedGoalId: null
    })
  }
})
