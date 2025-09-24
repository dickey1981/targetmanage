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
    isRecording: false,
    recordingText: '按住开始录音',
    voiceHint: '松开结束录音',
    voiceButtonClass: 'voice-button',
    showVoiceHintModal: false,
    voiceHintData: {},
    // 新增功能
    isLoading: false,
    refreshing: false,
    filterStatus: 'all', // all, active, completed
    sortBy: 'deadline', // deadline, progress, created
    showFilterModal: false,
    searchText: '',
    showSearchBar: false
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
            
            // 处理日期格式
            let startDateText = '未设置'
            let endDateText = '未设置'
            
            if (goal.startDate) {
              try {
                const startDate = new Date(goal.startDate)
                if (!isNaN(startDate.getTime())) {
                  startDateText = this.formatDateText(startDate)
                }
              } catch (e) {
                console.error('开始日期解析失败:', goal.startDate, e)
              }
            }
            
            if (goal.endDate) {
              try {
                const endDate = new Date(goal.endDate)
                if (!isNaN(endDate.getTime())) {
                  endDateText = this.formatDateText(endDate)
                }
              } catch (e) {
                console.error('结束日期解析失败:', goal.endDate, e)
              }
            }
            
            return {
              ...goal,
              daysLeft: daysLeft,
              progressPercent: goal.progress || 0,
              statusText: statusText,
              categoryText: goal.category || '其他',
              startDateText: startDateText,
              endDateText: endDateText
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
      isRecording: false,
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

  // 检查录音权限
  checkRecordPermission() {
    return new Promise((resolve, reject) => {
      wx.getSetting({
        success: (res) => {
          if (res.authSetting['scope.record'] === true) {
            console.log('✅ 录音权限已授权')
            resolve(true)
          } else if (res.authSetting['scope.record'] === false) {
            console.log('❌ 录音权限被拒绝')
            reject(new Error('录音权限被拒绝'))
          } else {
            console.log('⚠️ 录音权限未设置')
            reject(new Error('录音权限未设置'))
          }
        },
        fail: (err) => {
          console.error('❌ 获取权限设置失败:', err)
          reject(err)
        }
      })
    })
  },

  // 开始语音录音
  startVoiceRecord() {
    // 先检查录音权限
    this.checkRecordPermission()
      .then(() => {
        console.log('✅ 录音权限检查通过')
        this.startRecordingWithPermission()
      })
      .catch((err) => {
        console.log('⚠️ 需要申请录音权限')
        // 申请录音权限
        wx.authorize({
          scope: 'scope.record',
          success: () => {
            console.log('✅ 录音权限已获取')
            this.startRecordingWithPermission()
          },
          fail: (authErr) => {
            console.error('❌ 录音权限获取失败:', authErr)
            wx.showModal({
              title: '需要录音权限',
              content: '为了使用语音记录功能，需要获取录音权限。请在设置中开启录音权限。',
              confirmText: '去设置',
              cancelText: '取消',
              success: (res) => {
                if (res.confirm) {
                  wx.openSetting({
                    success: (settingRes) => {
                      if (settingRes.authSetting['scope.record']) {
                        console.log('✅ 用户已授权录音权限')
                        this.startRecordingWithPermission()
                      } else {
                        wx.showToast({
                          title: '录音权限未开启',
                          icon: 'none'
                        })
                      }
                    }
                  })
                }
              }
            })
          }
        })
      })
  },

  // 有权限后开始录音
  startRecordingWithPermission() {
    this.setData({
      isRecording: true,
      recordingText: '正在录音...',
      voiceHint: '松开结束录音',
      voiceButtonClass: 'voice-button recording'
    })
    
    // 开始录音
    const recorderManager = wx.getRecorderManager()
    
    recorderManager.onStart(() => {
      console.log('录音开始')
      wx.showToast({
        title: '开始录音',
        icon: 'none'
      })
    })
    
    recorderManager.onError((err) => {
      console.error('录音错误:', err)
      
      // 根据错误类型显示不同的提示
      let errorMessage = '录音失败'
      if (err.errMsg && err.errMsg.includes('NotFoundError')) {
        errorMessage = '录音设备未找到，请检查麦克风权限'
      } else if (err.errMsg && err.errMsg.includes('NotAllowedError')) {
        errorMessage = '录音权限被拒绝，请在设置中开启'
      } else if (err.errMsg && err.errMsg.includes('NotSupportedError')) {
        errorMessage = '当前环境不支持录音功能'
      }
      
      wx.showModal({
        title: '录音失败',
        content: errorMessage,
        showCancel: false,
        confirmText: '确定'
      })
      
      this.setData({
        isRecording: false,
        recordingText: '按住开始录音',
        voiceHint: '松开结束录音',
        voiceButtonClass: 'voice-button'
      })
    })
    
    // 开始录音
    recorderManager.start({
      duration: 60000, // 最长60秒
      sampleRate: 16000, // 16k采样率
      numberOfChannels: 1, // 单声道
      encodeBitRate: 96000, // 编码码率
      format: 'mp3' // 格式
    })
    
    // 保存录音管理器引用
    this.recorderManager = recorderManager
  },

  // 停止语音录音
  stopVoiceRecord() {
    if (!this.data.isRecording) return
    
    this.setData({
      isRecording: false,
      recordingText: '录音完成，正在识别...',
      voiceHint: '请稍候',
      voiceButtonClass: 'voice-button'
    })
    
    // 停止录音
    if (this.recorderManager) {
      this.recorderManager.stop()
    }
    
    // 监听录音结束
    this.recorderManager.onStop((res) => {
      console.log('录音结束:', res)
      this.processVoiceRecord(res.tempFilePath)
    })
  },

  // 处理录音文件
  processVoiceRecord(tempFilePath) {
    console.log('处理录音文件:', tempFilePath)
    
    // 显示加载提示
    wx.showLoading({
      title: '正在识别语音...',
      mask: true
    })
    
    // 上传录音文件到后端进行识别
    wx.uploadFile({
      url: `${app.globalData.baseUrl}/api/goals/recognize-voice`,
      filePath: tempFilePath,
      name: 'audio',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      success: (res) => {
        wx.hideLoading()
        console.log('语音识别响应:', res)
        
        try {
          const data = JSON.parse(res.data)
          if (data.success) {
            const recognizedText = data.data.text
            this.handleVoiceRecognitionResult(recognizedText)
          } else {
            wx.showToast({
              title: data.message || '语音识别失败',
              icon: 'none'
            })
            this.resetVoiceButton()
          }
        } catch (e) {
          console.error('解析响应失败:', e)
          wx.showToast({
            title: '语音识别失败',
            icon: 'none'
          })
          this.resetVoiceButton()
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('语音识别请求失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
        this.resetVoiceButton()
      }
    })
  },

  // 处理语音识别结果
  handleVoiceRecognitionResult(recognizedText) {
    console.log('语音识别结果:', recognizedText)
    
    // 直接跳转到创建目标页面，传递语音识别结果
    wx.navigateTo({
      url: `/pages/create-goal/create-goal?voiceResult=${encodeURIComponent(recognizedText)}`,
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
  },

  // 解析语音并显示提示
  parseVoiceAndShowHints(voiceText) {
    wx.showLoading({
      title: '正在解析...',
      mask: true
    })

    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/test-parse-voice`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        voice_text: voiceText
      },
      success: (res) => {
        wx.hideLoading()
        console.log('语音解析响应:', res)
        
        if (res.statusCode === 200 && res.data.success) {
          const parsedData = res.data.data
          const parsingHints = res.data.parsing_hints
          const validation = res.data.validation
          
          // 显示统一的解析建议弹窗
          this.showVoiceParsingHints(voiceText, parsingHints, validation)
        } else {
          // 解析失败，显示简单的确认对话框
          this.showSimpleVoiceConfirm(voiceText)
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('语音解析请求失败:', err)
        // 网络错误，显示简单的确认对话框
        this.showSimpleVoiceConfirm(voiceText)
      }
    })
  },

  // 显示语音解析提示弹窗
  showVoiceParsingHints(voiceText, parsingHints, validation) {
    const missingElements = parsingHints.missing_elements || []
    
    // 将缺少元素转换为更友好的建议
    const improvementSuggestions = this.convertToImprovementSuggestions(missingElements)
    
    // 只显示前2个建议
    const suggestions = improvementSuggestions.slice(0, 2)
    
    // 显示自定义弹窗
    this.setData({
      showVoiceHintModal: true,
      voiceHintData: {
        title: '语音创建目标',
        voiceText: voiceText,
        suggestions: suggestions,
        cancelText: '重新录音',
        confirmText: '创建目标'
      }
    })
  },

  // 处理自定义弹窗事件
  onVoiceHintModalClose() {
    this.setData({
      showVoiceHintModal: false
    })
  },

  onVoiceHintModalCancel() {
    this.setData({
      showVoiceHintModal: false
    })
    // 用户选择重新录音，重置按钮状态
    this.resetVoiceButton()
  },

  onVoiceHintModalConfirm() {
    const voiceText = this.data.voiceHintData.voiceText
    this.setData({
      showVoiceHintModal: false
    })
    
    // 跳转到创建目标页面，传递语音识别结果
    wx.navigateTo({
      url: `/pages/create-goal/create-goal?voiceResult=${encodeURIComponent(voiceText)}`,
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
  },

  // 将缺少元素转换为改进建议
  convertToImprovementSuggestions(missingElements) {
    const suggestionMap = {
      '明确的数量指标': '增加明确量化目标',
      '明确的时间期限': '增加明确完成时间期限',
      '明确的目标类别': '明确目标类别',
      '详细的目标描述': '提供更详细的目标描述',
      '具体明确的表达': '使用更具体的表达方式'
    }
    
    return missingElements.map(element => suggestionMap[element] || element)
  },

  // 显示简单的语音确认对话框（备用方案）
  showSimpleVoiceConfirm(voiceText) {
    wx.showModal({
      title: '语音识别结果',
      content: `识别到："${voiceText}"\n\n是否创建这个目标？`,
      confirmText: '创建目标',
      cancelText: '重新录音',
      success: (res) => {
        if (res.confirm) {
          // 跳转到创建目标页面，传递语音识别结果
          wx.navigateTo({
            url: `/pages/create-goal/create-goal?voiceResult=${encodeURIComponent(voiceText)}`,
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
        } else {
          // 用户选择重新录音，重置按钮状态
          this.resetVoiceButton()
        }
      }
    })
  },

  // 重置语音按钮状态
  resetVoiceButton() {
    this.setData({
      isRecording: false,
      recordingText: '按住开始录音',
      voiceHint: '松开结束录音',
      voiceButtonClass: 'voice-button'
    })
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

  // 下拉刷新
  onPullDownRefresh() {
    this.setData({ refreshing: true })
    this.loadGoals()
    setTimeout(() => {
      this.setData({ refreshing: false })
      wx.stopPullDownRefresh()
    }, 1000)
  },

  // 搜索功能
  toggleSearchBar() {
    this.setData({
      showSearchBar: !this.data.showSearchBar,
      searchText: ''
    })
    if (!this.data.showSearchBar) {
      this.loadGoals() // 清除搜索时重新加载所有目标
    }
  },

  onSearchInput(e) {
    const searchText = e.detail.value
    this.setData({ searchText })
    this.filterAndSortGoals()
  },

  // 筛选和排序功能
  showFilterOptions() {
    this.setData({ showFilterModal: true })
  },

  hideFilterModal() {
    this.setData({ showFilterModal: false })
  },

  onFilterChange(e) {
    const filterStatus = e.currentTarget.dataset.status
    this.setData({ filterStatus })
    this.filterAndSortGoals()
    this.hideFilterModal()
  },

  onSortChange(e) {
    const sortBy = e.currentTarget.dataset.sort
    this.setData({ sortBy })
    this.filterAndSortGoals()
    this.hideFilterModal()
  },

  // 筛选和排序目标
  filterAndSortGoals() {
    let filteredGoals = [...this.data.goals]

    // 搜索筛选
    if (this.data.searchText) {
      const searchText = this.data.searchText.toLowerCase()
      filteredGoals = filteredGoals.filter(goal => 
        goal.title.toLowerCase().includes(searchText) ||
        goal.categoryText.toLowerCase().includes(searchText) ||
        goal.description?.toLowerCase().includes(searchText)
      )
    }

    // 状态筛选
    if (this.data.filterStatus !== 'all') {
      filteredGoals = filteredGoals.filter(goal => goal.status === this.data.filterStatus)
    }

    // 排序
    filteredGoals.sort((a, b) => {
      switch (this.data.sortBy) {
        case 'deadline':
          return new Date(a.endDate) - new Date(b.endDate)
        case 'progress':
          return b.progressPercent - a.progressPercent
        case 'created':
          return new Date(b.createdAt) - new Date(a.createdAt)
        default:
          return 0
      }
    })

    this.setData({ goals: filteredGoals })
  },

  // 快速操作 - 标记完成
  toggleGoalComplete(e) {
    e.stopPropagation() // 阻止冒泡到目标点击事件
    const goalId = e.currentTarget.dataset.id
    const goal = this.data.goals.find(g => g.id === goalId)
    
    if (!goal) return

    wx.showModal({
      title: goal.status === '结束' ? '恢复目标' : '完成目标',
      content: goal.status === '结束' ? '是否将此目标恢复为进行中？' : '是否标记此目标为已完成？',
      success: (res) => {
        if (res.confirm) {
          this.updateGoalStatus(goalId, goal.status === '结束' ? '进行中' : '结束')
        }
      }
    })
  },

  // 更新目标状态
  updateGoalStatus(goalId, newStatus) {
    wx.showLoading({ title: '更新中...' })

    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/${goalId}`,
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`,
        'Content-Type': 'application/json'
      },
      data: {
        status: newStatus
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data.success) {
          wx.showToast({
            title: newStatus === '结束' ? '目标已完成' : '目标已恢复',
            icon: 'success'
          })
          this.loadGoals() // 重新加载数据
        } else {
          wx.showToast({
            title: res.data.message || '更新失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('更新目标状态失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 删除目标
  deleteGoal(e) {
    e.stopPropagation()
    const goalId = e.currentTarget.dataset.id
    const goal = this.data.goals.find(g => g.id === goalId)
    
    if (!goal) return

    wx.showModal({
      title: '删除目标',
      content: `确定要删除目标"${goal.title}"吗？删除后无法恢复。`,
      confirmText: '删除',
      confirmColor: '#ff4757',
      success: (res) => {
        if (res.confirm) {
          this.performDeleteGoal(goalId)
        }
      }
    })
  },

  // 执行删除目标
  performDeleteGoal(goalId) {
    wx.showLoading({ title: '删除中...' })

    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/${goalId}`,
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data.success) {
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          })
          this.loadGoals() // 重新加载数据
        } else {
          wx.showToast({
            title: res.data.message || '删除失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('删除目标失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    })
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
  },

  // 获取状态颜色
  getStatusColor(status) {
    const colorMap = {
      '进行中': '#00B4D8',
      '结束': '#28a745',
      '暂停': '#ffc107',
      '取消': '#6c757d'
    }
    return colorMap[status] || '#6c757d'
  }
})
