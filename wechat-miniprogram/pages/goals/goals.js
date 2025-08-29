// pages/goals/goals.js
const app = getApp()

Page({
  data: {
    goals: [],
    totalGoals: 0,
    activeGoals: 0,
    completedGoals: 0,
    completionRate: 0,
    showCreateModal: false,
    recordingText: '按住开始录音',
    voiceHint: '松开结束录音',
    voiceButtonClass: 'voice-button'
  },

  onLoad() {
    this.loadGoals()
  },

  onShow() {
    // 每次显示页面时都重新加载目标数据
    this.loadGoals()
    
    // 检查是否需要显示创建目标弹窗
    if (app.globalData.showCreateGoalModal) {
      this.showCreateModal()
      app.globalData.showCreateGoalModal = false
    }
  },

  // 加载目标数据
  loadGoals() {
    // 显示加载提示
    wx.showLoading({
      title: '加载中...'
    })

    // 获取API基础URL
    const baseUrl = app.globalData.baseUrl;
    if (!baseUrl) {
      wx.hideLoading();
      wx.showToast({
        title: 'API地址未配置',
        icon: 'none'
      });
      return;
    }

    // 调用后端API获取目标数据
    wx.request({
      url: `${baseUrl}/api/goals/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        wx.hideLoading()
        console.log('获取目标数据成功:', res)
        
        if (res.statusCode === 200 && res.data.success) {
          const goals = res.data.data || []
          
          // 处理每个目标数据，添加显示所需的字段
          const processedGoals = goals.map(goal => {
            // 使用后端计算的状态和剩余天数
            const statusText = goal.status || '进行中'
            const daysLeft = goal.remaining_days || 0
            
            return {
              ...goal,
              daysLeft: daysLeft,
              progressPercent: goal.progress || 0,
              statusText: statusText,
              categoryText: goal.category || '其他',
              startDateText: goal.startDate ? this.formatDateText(new Date(goal.startDate)) : '未设置',
              endDateText: goal.endDate ? this.formatDateText(new Date(goal.endDate)) : '未设置'
            }
          })
          
          // 计算统计数据 - 使用新的状态字段
          const totalGoals = processedGoals.length
          const activeGoals = processedGoals.filter(item => item.status === '进行中').length
          const completedGoals = processedGoals.filter(item => item.status === '结束').length
          const completionRate = totalGoals > 0 ? Math.round((completedGoals / totalGoals) * 100) : 0
          
          this.setData({
            goals: processedGoals,
            totalGoals: totalGoals,
            activeGoals: activeGoals,
            completedGoals: completedGoals,
            completionRate: completionRate
          })
        } else {
          console.error('获取目标数据失败:', res.data.message)
          wx.showToast({
            title: res.data.message || '获取目标失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('获取目标数据失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 显示创建目标弹窗
  showCreateModal() {
    this.setData({
      showCreateModal: true,
      recordingText: '按住开始录音',
      voiceHint: '松开结束录音',
      voiceButtonClass: 'voice-button'
    })
  },

  // 隐藏创建目标弹窗
  hideCreateModal() {
    this.setData({
      showCreateModal: false
    })
  },

  // 开始语音录音
  startVoiceRecord() {
    this.setData({
      recordingText: '正在录音...',
      voiceHint: '松开结束录音',
      voiceButtonClass: 'voice-button recording'
    })
    
    // 模拟录音开始
    console.log('开始录音')
  },

  // 停止语音录音
  stopVoiceRecord() {
    this.setData({
      recordingText: '录音完成',
      voiceHint: '正在识别...',
      voiceButtonClass: 'voice-button'
    })
    
    // 模拟语音识别
    setTimeout(() => {
      // 模拟语音识别结果
      const mockResult = '我要在3个月内完成Python学习，目标是掌握FastAPI框架，每周学习10小时，最终能够独立开发Web应用'
      
      // 录音完成后直接跳转到创建目标页面，传递语音识别结果
      wx.navigateTo({
        url: `/pages/create-goal/create-goal?voiceResult=${encodeURIComponent(mockResult)}`,
        success: () => {
          console.log('跳转到创建目标页面成功')
          // 隐藏弹窗
          this.hideCreateModal()
        },
        fail: (err) => {
          console.error('跳转失败:', err)
          wx.showToast({
            title: '页面跳转失败',
            icon: 'none'
          })
        }
      })
    }, 1500)
  },

  // 跳转到目标详情
  goToGoalDetail(e) {
    const goalId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/goal-detail/goal-detail?id=${goalId}`
    })
  },

  // 点击目标项
  onGoalTap(e) {
    const goalId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/goal-detail/goal-detail?id=${goalId}`
    });
  },

  // 刷新目标列表
  refreshGoals() {
    this.loadGoals();
  },

  // 工具方法
  formatDate(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  formatDateText(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}年${month}月${day}日`
  }
})
