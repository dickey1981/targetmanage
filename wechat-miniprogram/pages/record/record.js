// pages/record/record.js
const app = getApp()

Page({
  data: {
    isLoggedIn: false,
    userInfo: null,
    recordTypes: [
      { id: 'voice', name: '语音记录', icon: '🎤', color: '#667eea' },
      { id: 'photo', name: '拍照记录', icon: '📷', color: '#28a745' },
      { id: 'text', name: '文字记录', icon: '✏️', color: '#ffc107' },
      { id: 'manual', name: '手动录入', icon: '📝', color: '#dc3545' }
    ],
    recentRecords: [],
    showRecordModal: false,
    currentRecordType: null,
    // 语音交互相关
    isRecording: false,
    recordingText: '按住说话',
    voiceHint: '松开结束'
  },

  onLoad() {
    this.checkLoginStatus()
  },

  onShow() {
    this.checkLoginStatus()
    if (this.data.isLoggedIn) {
      this.loadRecentRecords()
    }
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
    } else {
      this.setData({
        isLoggedIn: false,
        userInfo: null
      })
    }
  },

  // 加载最近记录
  loadRecentRecords() {
    wx.request({
      url: `${app.globalData.baseUrl}/api/records/recent`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          this.setData({
            recentRecords: res.data.data || []
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
    this.setData({
      isRecording: true,
      recordingText: '正在录音...'
    })
    
    // TODO: 调用微信录音API
    wx.showToast({
      title: '开始录音',
      icon: 'none'
    })
  },

  stopVoiceRecord() {
    this.setData({
      isRecording: false,
      recordingText: '按住说话',
      voiceHint: '松开结束'
    })
    
    // TODO: 调用语音识别API
    wx.showToast({
      title: '录音完成，正在识别...',
      icon: 'none'
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

  // 文字记录
  onTextInput(e) {
    const text = e.detail.value
    if (text.trim()) {
      this.submitRecord('text', { content: text })
    }
  },

  // 提交记录
  submitRecord(type, data) {
    wx.request({
      url: `${app.globalData.baseUrl}/api/records/create`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data: {
        type: type,
        content: data.content || '',
        goal_id: data.goalId || null
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          wx.showToast({
            title: '记录成功',
            icon: 'success'
          })
          this.closeRecordModal()
          this.loadRecentRecords()
        } else {
          wx.showToast({
            title: res.data.message || '记录失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
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
      url: `/pages/process-record/process-record?id=${recordId}`
    })
  }
})
