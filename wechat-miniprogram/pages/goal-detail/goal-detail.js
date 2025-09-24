// pages/goal-detail/goal-detail.js
Page({
  data: {
    goalId: '',
    goalData: {},
    isEditing: false,
    categories: [
      { name: '学习', value: '学习' },
      { name: '工作', value: '工作' },
      { name: '健康', value: '健康' },
      { name: '财务', value: '财务' },
      { name: '人际关系', value: '人际关系' },
      { name: '个人发展', value: '个人发展' },
      { name: '兴趣爱好', value: '兴趣爱好' },
      { name: '其他', value: '其他' }
    ],
    categoryIndex: 0,
    progressPercentage: 0,
    statusClass: 'status-active',
    remainingDaysClass: '',
    recentRecords: [],
    // 新增功能
    showVoiceModal: false,
    isRecording: false,
    recordingText: '按住开始录音',
    voiceHint: '松开结束录音',
    voiceButtonClass: 'voice-button',
    showProgressModal: false,
    progressValue: '',
    progressNote: '',
    chartData: [],
    showChart: false,
    selectedTab: 'overview' // overview, records, analytics
  },

  onLoad(options) {
    if (options.id) {
      this.setData({
        goalId: options.id
      });
      this.loadGoalDetail();
      this.loadRecentRecords();
      
      // 添加API测试（开发环境）
      if (wx.getSystemInfoSync().platform === 'devtools') {
        this.debugAuthStatus();
        this.runAPITests();
      }
    }
  },

  // 加载目标详情
  loadGoalDetail() {
    const app = getApp();
    const token = app.globalData.token;
    const baseUrl = app.globalData.baseUrl;
    
    console.log('调试信息:', {
      token: token ? '已设置' : '未设置',
      baseUrl: baseUrl,
      goalId: this.data.goalId
    });
    
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }

    if (!baseUrl) {
      wx.showToast({
        title: 'API地址未配置',
        icon: 'none'
      });
      console.error('API基础URL未配置:', app.globalData);
      return;
    }

    wx.showLoading({
      title: '加载中...'
    });

    const apiUrl = `${baseUrl}/api/goals/${this.data.goalId}`;
    console.log('请求URL:', apiUrl);

    wx.request({
      url: apiUrl,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        wx.hideLoading();
        console.log('API响应:', res);
        if (res.statusCode === 200) {
          const goalData = res.data;
          
          // 处理日期格式，将ISO格式转换为YYYY-MM-DD格式
          if (goalData.startDate) {
            goalData.startDate = this.formatDateForPicker(goalData.startDate);
          }
          if (goalData.endDate) {
            goalData.endDate = this.formatDateForPicker(goalData.endDate);
          }
          
          this.setData({
            goalData: goalData,
            categoryIndex: this.findCategoryIndex(goalData.category)
          });
          this.calculateProgress();
          this.updateStatusClass(); // 调用更新状态CSS类名的函数
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        wx.hideLoading();
        console.error('加载目标详情失败:', error);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 查找分类索引
  findCategoryIndex(category) {
    const index = this.data.categories.findIndex(item => item.value === category);
    return index >= 0 ? index : 0;
  },

  // 计算进度百分比
  calculateProgress() {
    const { targetValue, currentValue } = this.data.goalData;
    if (targetValue && currentValue) {
      const target = parseFloat(targetValue);
      const current = parseFloat(currentValue);
      if (target > 0) {
        const percentage = Math.min(Math.round((current / target) * 100), 100);
        this.setData({
          progressPercentage: percentage
        });
      }
    }
  },

  // 更新状态CSS类名
  updateStatusClass() {
    const { goalData } = this.data;
    let statusClass = 'status-active';
    let remainingDaysClass = '';

    // 根据状态设置CSS类名
    if (goalData.status) {
      switch (goalData.status) {
        case '进行中':
          statusClass = 'status-active';
          break;
        case '未开始':
          statusClass = 'status-pending';
          break;
        case '延期':
          statusClass = 'status-overdue';
          break;
        case '结束':
          statusClass = 'status-completed';
          break;
        default:
          statusClass = 'status-active';
      }
    }

    // 根据剩余天数设置CSS类名
    if (goalData.remaining_days !== undefined) {
      if (goalData.remaining_days <= 0) {
        remainingDaysClass = 'status-overdue-text';
      }
    }

    this.setData({
      statusClass,
      remainingDaysClass
    });
  },

  // 切换编辑模式
  toggleEditMode() {
    if (this.data.isEditing) {
      // 当前是编辑模式，点击"完成"按钮，先保存再退出编辑模式
      this.saveChanges();
    } else {
      // 当前是查看模式，点击"编辑"按钮，进入编辑模式
      this.setData({
        isEditing: true
      });
    }
  },

  // 标题输入
  onTitleChange(e) {
    this.setData({
      'goalData.title': e.detail.value
    });
  },

  // 分类选择
  onCategoryChange(e) {
    const index = e.detail.value;
    this.setData({
      categoryIndex: index,
      'goalData.category': this.data.categories[index].value
    });
  },

  // 描述输入
  onDescriptionChange(e) {
    this.setData({
      'goalData.description': e.detail.value
    });
  },

  // 开始时间选择
  onStartDateChange(e) {
    this.setData({
      'goalData.startDate': e.detail.value
    });
  },

  // 结束时间选择
  onEndDateChange(e) {
    this.setData({
      'goalData.endDate': e.detail.value
    });
  },

  // 目标值输入
  onTargetValueChange(e) {
    this.setData({
      'goalData.targetValue': e.detail.value
    });
  },

  // 当前值输入
  onCurrentValueChange(e) {
    this.setData({
      'goalData.currentValue': e.detail.value
    });
  },

  // 单位输入
  onUnitChange(e) {
    this.setData({
      'goalData.unit': e.detail.value
    });
  },

  // 优先级选择
  selectPriority(e) {
    const priority = e.currentTarget.dataset.priority;
    this.setData({
      'goalData.priority': priority
    });
  },

  // 每日提醒开关
  onDailyReminderChange(e) {
    console.log('每日提醒开关变化:', e.detail.value);
    this.setData({
      'goalData.dailyReminder': e.detail.value
    });
    console.log('更新后的每日提醒状态:', this.data.goalData.dailyReminder);
  },

  // 截止提醒开关
  onDeadlineReminderChange(e) {
    console.log('截止提醒开关变化:', e.detail.value);
    this.setData({
      'goalData.deadlineReminder': e.detail.value
    });
    console.log('更新后的截止提醒状态:', this.data.goalData.deadlineReminder);
  },

  // 保存修改
  saveChanges() {
    const app = getApp();
    const token = app.globalData.token;
    const baseUrl = app.globalData.baseUrl;
    
    console.log('保存调试信息:', {
      token: token ? '已设置' : '未设置',
      baseUrl: baseUrl,
      goalId: this.data.goalId
    });
    
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }

    if (!baseUrl) {
      wx.showToast({
        title: 'API地址未配置',
        icon: 'none'
      });
      console.error('API基础URL未配置:', app.globalData);
      return;
    }

    // 验证必填字段
    if (!this.data.goalData.title || !this.data.goalData.title.trim()) {
      wx.showToast({
        title: '请输入目标标题',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '保存中...'
    });

    // 准备要发送的数据
    const goalDataToSend = {
      title: this.data.goalData.title,
      category: this.data.goalData.category,
      description: this.data.goalData.description,
      startDate: this.data.goalData.startDate,
      endDate: this.data.goalData.endDate,
      targetValue: this.data.goalData.targetValue,
      currentValue: this.data.goalData.currentValue,
      unit: this.data.goalData.unit,
      priority: this.data.goalData.priority,
      dailyReminder: this.data.goalData.dailyReminder,
      deadlineReminder: this.data.goalData.deadlineReminder
    };

    console.log('准备发送的目标数据:', goalDataToSend);
    console.log('提醒设置详情:', {
      dailyReminder: goalDataToSend.dailyReminder,
      deadlineReminder: goalDataToSend.deadlineReminder,
      dailyReminderType: typeof goalDataToSend.dailyReminder,
      deadlineReminderType: typeof goalDataToSend.deadlineReminder
    });

    const apiUrl = `${baseUrl}/api/goals/${this.data.goalId}`;
    console.log('保存请求URL:', apiUrl);
    console.log('保存数据:', goalDataToSend);

    wx.request({
      url: apiUrl,
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: goalDataToSend,
      success: (res) => {
        wx.hideLoading();
        console.log('保存API响应:', res);
        if (res.statusCode === 200) {
          wx.showToast({
            title: '保存成功',
            icon: 'success'
          });
          
          // 更新本地数据
          this.setData({
            goalData: { ...this.data.goalData, ...goalDataToSend },
            isEditing: false
          });
          
          // 重新计算进度
          this.calculateProgress();
          this.updateStatusClass(); // 调用更新状态CSS类名的函数
          
          // 通知上一页刷新
          const pages = getCurrentPages();
          if (pages.length > 1) {
            const prevPage = pages[pages.length - 2];
            if (prevPage && prevPage.refreshGoals) {
              prevPage.refreshGoals();
            }
          }
        } else {
          wx.showToast({
            title: '保存失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        wx.hideLoading();
        console.error('保存目标失败:', error);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 返回上一页
  goBack() {
    wx.navigateBack();
  },

  // 格式化日期为picker组件需要的格式
  formatDateForPicker(dateString) {
    if (!dateString) return '';
    
    try {
      // 处理ISO格式的日期字符串
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    } catch (e) {
      console.error('日期格式化失败:', e);
      return '';
    }
  },

  // 跳转到过程记录页面
  goToProcessRecord() {
    wx.navigateTo({
      url: `/pages/process-record/process-record?goalId=${this.data.goalId}`
    })
  },

  // 跳转到时间线页面
  goToTimeline() {
    wx.navigateTo({
      url: `/pages/timeline/timeline?goalId=${this.data.goalId}`
    })
  },

  // 更新进度
  updateProgress() {
    wx.showModal({
      title: '更新进度',
      content: '请选择更新方式',
      showCancel: true,
      cancelText: '语音更新',
      confirmText: '手动更新',
      success: (res) => {
        if (res.confirm) {
          // 手动更新进度
          this.showProgressInput()
        } else if (res.cancel) {
          // 语音更新进度
          this.goToProcessRecord()
        }
      }
    })
  },

  // 显示进度输入框
  showProgressInput() {
    wx.showModal({
      title: '更新进度',
      editable: true,
      placeholderText: '请输入当前进度值',
      success: (res) => {
        if (res.confirm && res.content) {
          this.updateGoalProgress(res.content)
        }
      }
    })
  },

  // 更新目标进度
  updateGoalProgress(progressValue) {
    const app = getApp()
    wx.showLoading({
      title: '更新中...'
    })

    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/${this.data.goalId}/progress`,
      method: 'PUT',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        current_value: parseFloat(progressValue)
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200) {
          wx.showToast({
            title: '更新成功',
            icon: 'success'
          })
          // 重新加载目标详情
          this.loadGoalDetail()
        } else {
          wx.showToast({
            title: '更新失败',
            icon: 'none'
          })
        }
      },
      fail: (error) => {
        wx.hideLoading()
        console.error('更新进度失败:', error)
        wx.showToast({
          title: '更新失败',
          icon: 'none'
        })
      }
    })
  },

  // 加载最近过程记录
  loadRecentRecords() {
    const app = getApp()
    const token = app.globalData.token
    
    // 检查是否已登录
    if (!token) {
      console.log('用户未登录，跳过加载过程记录')
      return
    }
    
    console.log('📋 加载过程记录，目标ID:', this.data.goalId)
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/process-records/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        goal_id: this.data.goalId,
        page: 1,
        page_size: 3
      },
      success: (res) => {
        console.log('📋 过程记录响应:', res)
        if (res.statusCode === 200) {
          this.setData({
            recentRecords: res.data.records || []
          })
          console.log('✅ 成功加载过程记录:', res.data.records?.length || 0, '条')
        } else {
          console.error('❌ 加载过程记录失败，状态码:', res.statusCode)
          console.error('响应数据:', res.data)
        }
      },
      fail: (error) => {
        console.error('❌ 加载最近记录失败:', error)
        // 使用模拟数据作为降级方案
        this.setMockRecords()
      }
    })
  },

  // 认证状态调试
  debugAuthStatus() {
    console.log('🔍 认证状态调试...')
    const app = getApp()
    
    // 检查全局状态
    console.log('全局状态:')
    console.log('  Token:', app.globalData.token ? '已设置' : '未设置')
    console.log('  用户信息:', app.globalData.userInfo ? '已设置' : '未设置')
    console.log('  登录状态:', app.globalData.isLoggedIn ? '已登录' : '未登录')
    
    // 检查存储状态
    const storedToken = wx.getStorageSync('token')
    const storedUserInfo = wx.getStorageSync('userInfo')
    
    console.log('存储状态:')
    console.log('  存储的Token:', storedToken ? '已设置' : '未设置')
    console.log('  存储的用户信息:', storedUserInfo ? '已设置' : '未设置')
    
    // 同步状态
    if (storedToken && storedUserInfo && !app.globalData.token) {
      console.log('🔄 同步存储的认证信息...')
      app.globalData.token = storedToken
      app.globalData.userInfo = storedUserInfo
      app.globalData.isLoggedIn = true
    }
    
    // 测试token有效性
    if (app.globalData.token) {
      console.log('🧪 测试token有效性...')
      wx.request({
        url: `${app.globalData.baseUrl}/api/auth/validate`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${app.globalData.token}`
        },
        success: (res) => {
          console.log('✅ Token有效:', res.data)
        },
        fail: (error) => {
          console.error('❌ Token无效:', error)
          console.error('状态码:', error.statusCode)
          console.error('错误信息:', error.errMsg)
        }
      })
    }
  },

  // API测试方法（开发环境）
  runAPITests() {
    console.log('🧪 开始API测试...')
    const app = getApp()
    const token = app.globalData.token
    const goalId = this.data.goalId

    // 测试健康检查
    wx.request({
      url: `${app.globalData.baseUrl}/health`,
      method: 'GET',
      success: (res) => {
        console.log('✅ 健康检查成功:', res.data)
      },
      fail: (error) => {
        console.error('❌ 健康检查失败:', error)
      }
    })

    // 测试认证
    if (token) {
      wx.request({
        url: `${app.globalData.baseUrl}/api/auth/validate`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          console.log('✅ 认证验证成功:', res.data)
        },
        fail: (error) => {
          console.error('❌ 认证验证失败:', error)
        }
      })
    }

    // 测试过程记录API
    if (token && goalId) {
      wx.request({
        url: `${app.globalData.baseUrl}/api/process-records/`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          goal_id: goalId,
          page: 1,
          page_size: 3
        },
        success: (res) => {
          console.log('✅ 过程记录API成功:', res.data)
        },
        fail: (error) => {
          console.error('❌ 过程记录API失败:', error)
          console.error('错误详情:', error)
        }
      })
    }
  },

  // 设置模拟记录数据（降级方案）
  setMockRecords() {
    console.log('📋 使用模拟过程记录数据')
    const mockRecords = [
      {
        id: '1',
        content: '今天完成了Python基础语法学习，感觉很有成就感！',
        type: 'progress',
        created_at: new Date().toISOString(),
        goal_id: this.data.goalId
      },
      {
        id: '2',
        content: '遇到了递归算法的问题，需要多练习理解',
        type: 'difficulty',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        goal_id: this.data.goalId
      },
      {
        id: '3',
        content: '完成了第一个小程序项目，学到了很多新知识',
        type: 'achievement',
        created_at: new Date(Date.now() - 172800000).toISOString(),
        goal_id: this.data.goalId
      }
    ]
    
    this.setData({
      recentRecords: mockRecords
    })
  },

  // 查看记录详情
  viewRecordDetail(e) {
    const record = e.currentTarget.dataset.record
    wx.showModal({
      title: '记录详情',
      content: record.content,
      showCancel: false,
      confirmText: '确定'
    })
  },

  // 获取类型图标
  getTypeIcon(type) {
    const icons = {
      'progress': '📈',
      'process': '📝',
      'milestone': '🏆',
      'difficulty': '😰',
      'method': '💡',
      'reflection': '🤔',
      'adjustment': '⚙️',
      'achievement': '🎉',
      'insight': '🔍',
      'other': '📋'
    }
    return icons[type] || '📋'
  },

  // 获取类型名称
  getTypeName(type) {
    const names = {
      'progress': '进度',
      'process': '过程',
      'milestone': '里程碑',
      'difficulty': '困难',
      'method': '方法',
      'reflection': '反思',
      'adjustment': '调整',
      'achievement': '成就',
      'insight': '洞察',
      'other': '其他'
    }
    return names[type] || '其他'
  },

  // 格式化时间
  formatTime(timeStr) {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now - date
    
    // 小于1分钟
    if (diff < 60000) {
      return '刚刚'
    }
    
    // 小于1小时
    if (diff < 3600000) {
      return Math.floor(diff / 60000) + '分钟前'
    }
    
    // 小于1天
    if (diff < 86400000) {
      return Math.floor(diff / 3600000) + '小时前'
    }
    
    // 小于7天
    if (diff < 604800000) {
      return Math.floor(diff / 86400000) + '天前'
    }
    
    // 超过7天，显示具体日期
    return date.toLocaleDateString()
  },

  // 切换标签页
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ selectedTab: tab })
    
    if (tab === 'analytics') {
      this.loadChartData()
    }
  },

  // 显示语音记录弹窗
  showVoiceRecordModal() {
    this.setData({
      showVoiceModal: true,
      isRecording: false,
      recordingText: '按住开始录音',
      voiceHint: '松开结束录音',
      voiceButtonClass: 'voice-button'
    })
  },

  // 隐藏语音记录弹窗
  hideVoiceRecordModal() {
    this.setData({
      showVoiceModal: false
    })
  },

  // 显示进度更新弹窗
  showProgressUpdateModal() {
    this.setData({
      showProgressModal: true,
      progressValue: this.data.goalData.currentValue || '',
      progressNote: ''
    })
  },

  // 隐藏进度更新弹窗
  hideProgressUpdateModal() {
    this.setData({
      showProgressModal: false
    })
  },

  // 开始语音录音
  startVoiceRecord() {
    this.setData({
      isRecording: true,
      recordingText: '正在录音...',
      voiceHint: '松开结束录音',
      voiceButtonClass: 'voice-button recording'
    })
    
    const recorderManager = wx.getRecorderManager()
    
    recorderManager.onStart(() => {
      console.log('录音开始')
    })
    
    recorderManager.onError((err) => {
      console.error('录音错误:', err)
      wx.showToast({
        title: '录音失败',
        icon: 'none'
      })
      this.resetVoiceButton()
    })
    
    recorderManager.start({
      duration: 60000,
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 96000,
      format: 'mp3'
    })
    
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
    
    if (this.recorderManager) {
      this.recorderManager.stop()
    }
    
    this.recorderManager.onStop((res) => {
      console.log('录音结束:', res)
      this.processVoiceRecord(res.tempFilePath)
    })
  },

  // 处理录音文件
  processVoiceRecord(tempFilePath) {
    console.log('处理录音文件:', tempFilePath)
    
    wx.showLoading({
      title: '正在识别语音...',
      mask: true
    })
    
    const app = getApp()
    wx.uploadFile({
      url: `${app.globalData.baseUrl}/api/goals/${this.data.goalId}/add-record`,
      filePath: tempFilePath,
      name: 'audio',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        wx.hideLoading()
        console.log('语音记录响应:', res)
        
        try {
          const data = JSON.parse(res.data)
          if (data.success) {
            wx.showToast({
              title: '记录添加成功',
              icon: 'success'
            })
            this.hideVoiceRecordModal()
            this.loadGoalDetail()
            this.loadRecentRecords()
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

  // 重置语音按钮状态
  resetVoiceButton() {
    this.setData({
      isRecording: false,
      recordingText: '按住开始录音',
      voiceHint: '松开结束录音',
      voiceButtonClass: 'voice-button'
    })
  },

  // 进度值输入
  onProgressValueChange(e) {
    this.setData({
      progressValue: e.detail.value
    })
  },

  // 进度备注输入
  onProgressNoteChange(e) {
    this.setData({
      progressNote: e.detail.value
    })
  },

  // 提交进度更新
  submitProgressUpdate() {
    const { progressValue, progressNote } = this.data
    
    if (!progressValue) {
      wx.showToast({
        title: '请输入进度值',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '更新中...'
    })

    const app = getApp()
    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/${this.data.goalId}/update-progress`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`,
        'Content-Type': 'application/json'
      },
      data: {
        current_value: parseFloat(progressValue),
        note: progressNote
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data.success) {
          wx.showToast({
            title: '进度更新成功',
            icon: 'success'
          })
          this.hideProgressUpdateModal()
          this.loadGoalDetail()
          this.loadRecentRecords()
        } else {
          wx.showToast({
            title: res.data.message || '更新失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('更新进度失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 加载图表数据
  loadChartData() {
    const app = getApp()
    const token = app.globalData.token
    const baseUrl = app.globalData.baseUrl
    
    if (!token || !baseUrl) {
      return
    }

    wx.request({
      url: `${baseUrl}/api/goals/${this.data.goalId}/analytics`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const analyticsData = res.data.data || {}
          this.setData({
            chartData: analyticsData.chart_data || [],
            showChart: true
          })
        }
      },
      fail: (error) => {
        console.error('加载分析数据失败:', error)
      }
    })
  },

  // 删除目标
  deleteGoal() {
    const app = getApp()
    const token = app.globalData.token
    const baseUrl = app.globalData.baseUrl
    
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    if (!baseUrl) {
      wx.showToast({
        title: 'API地址未配置',
        icon: 'none'
      })
      return
    }

    // 二次确认弹窗
    wx.showModal({
      title: '确认删除',
      content: `确定要删除目标"${this.data.goalData.title}"吗？\n\n删除后无法恢复，包括所有相关的进度记录。`,
      confirmText: '确认删除',
      cancelText: '取消',
      confirmColor: '#ff4757',
      success: (res) => {
        if (res.confirm) {
          this.performDeleteGoal()
        }
      }
    })
  },

  // 执行删除操作
  performDeleteGoal() {
    const app = getApp()
    
    wx.showLoading({
      title: '删除中...',
      mask: true
    })

    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/${this.data.goalId}`,
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        wx.hideLoading()
        console.log('删除目标响应:', res)
        
        if (res.statusCode === 200) {
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          })
          
          // 延迟返回上一页，让用户看到成功提示
          setTimeout(() => {
            // 通知上一页刷新
            const pages = getCurrentPages()
            if (pages.length > 1) {
              const prevPage = pages[pages.length - 2]
              if (prevPage && prevPage.refreshGoals) {
                prevPage.refreshGoals()
              }
            }
            
            // 返回上一页
            wx.navigateBack()
          }, 1500)
        } else {
          wx.showToast({
            title: res.data.message || '删除失败',
            icon: 'none'
          })
        }
      },
      fail: (error) => {
        wx.hideLoading()
        console.error('删除目标失败:', error)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    })
  }
});
