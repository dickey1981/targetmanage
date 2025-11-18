// pages/create-goal/create-goal.js
const app = getApp()

Page({
  data: {
    voiceResult: '',
    isEditing: false, // 新增：编辑模式状态
    categories: [
      { id: '学习', name: '学习', icon: '📚' },
      { id: '工作', name: '工作', icon: '💼' },
      { id: '健康', name: '健康', icon: '🏃' },
      { id: '阅读', name: '阅读', icon: '📖' },
      { id: '旅行', name: '旅行', icon: '✈️' },
      { id: '财务', name: '财务', icon: '💰' },
      { id: '人际关系', name: '人际关系', icon: '🤝' },
      { id: '个人发展', name: '个人发展', icon: '🌟' },
      { id: '兴趣爱好', name: '兴趣爱好', icon: '🎨' },
      { id: '其他', name: '其他', icon: '🎯' }
    ],
    categoryIndex: 0, // 新增：分类选择器索引
    goalData: {
      title: '',
      category: '学习',
      description: '',
      startDate: '',
      endDate: '',
      startDateText: '请选择开始时间',
      endDateText: '请选择结束时间',
      targetValue: '',
      currentValue: '0',
      unit: '',
      priority: 'medium',
      dailyReminder: true,
      deadlineReminder: true
    },
    
    // 验证和提示
    validationErrors: [],
    suggestions: [],
    
    // 自定义弹窗数据
    showParsingModal: false,
    parsingModalData: {
      voiceResult: '',
      suggestions: []
    }
  },

  onLoad(options) {
    console.log('创建目标页面加载，参数:', options)
    
    // 检查是否来自语音创建
    if (options.fromVoice === 'true') {
      console.log('来自语音创建流程')
      this.handleVoiceParsedGoal()
    } else if (options.voiceResult) {
      // 检查是否有语音识别结果
      const voiceResult = decodeURIComponent(options.voiceResult)
      console.log('收到语音识别结果:', voiceResult)
      
      // 保存语音识别结果
      this.setData({
        voiceResult: voiceResult
      })
      
      // 自动解析语音内容并回填表单
      this.parseVoiceResult(voiceResult)
    } else if (options.goalData) {
      // 如果有目标数据，直接填充
      try {
        const goalData = JSON.parse(decodeURIComponent(options.goalData))
        this.setData({
          goalData: { ...this.data.goalData, ...goalData }
        })
      } catch (e) {
        console.error('解析目标数据失败:', e)
      }
    }
    
    // 设置分类选择器索引
    this.setCategoryIndex()
  },

  // 处理语音解析的目标数据
  handleVoiceParsedGoal() {
    const voiceParsedGoal = app.globalData.voiceParsedGoal
    if (voiceParsedGoal) {
      console.log('处理语音解析的目标数据:', voiceParsedGoal)
      
      // 转换日期格式
      const goalData = {
        title: voiceParsedGoal.title || '',
        category: voiceParsedGoal.category || '学习',
        description: voiceParsedGoal.description || '',
        startDate: voiceParsedGoal.startDate || '',
        endDate: voiceParsedGoal.endDate || '',
        startDateText: voiceParsedGoal.startDate ? this.formatDateText(new Date(voiceParsedGoal.startDate)) : '请选择开始时间',
        endDateText: voiceParsedGoal.endDate ? this.formatDateText(new Date(voiceParsedGoal.endDate)) : '请选择结束时间',
        targetValue: voiceParsedGoal.targetValue || '',
        currentValue: voiceParsedGoal.currentValue || '0',
        unit: voiceParsedGoal.unit || '',
        priority: voiceParsedGoal.priority || 'medium',
        dailyReminder: voiceParsedGoal.dailyReminder !== undefined ? voiceParsedGoal.dailyReminder : true,
        deadlineReminder: voiceParsedGoal.deadlineReminder !== undefined ? voiceParsedGoal.deadlineReminder : true
      }
      
      // 更新表单数据
      this.setData({
        goalData: goalData,
        voiceResult: voiceParsedGoal.title || ''
      })
      
      // 更新分类选择器索引
      this.setCategoryIndex()
      
      // 清除全局数据
      app.globalData.voiceParsedGoal = null
      
      console.log('语音解析数据已填充到表单')
    } else {
      console.log('没有找到语音解析的目标数据')
    }
  },

  // 返回上一页
  goBack() {
    wx.navigateBack()
  },

  // 保存目标
  saveGoal() {
    console.log('点击保存按钮')
    this.createGoal()
  },

  // 切换编辑模式
  toggleEditMode() {
    const isEditing = !this.data.isEditing
    this.setData({ isEditing })
    
    if (!isEditing) {
      // 退出编辑模式时，重新解析语音内容
      if (this.data.voiceResult && this.data.voiceResult.trim()) {
        this.parseVoiceResult(this.data.voiceResult)
      }
    }
  },

  // 语音识别结果编辑
  onVoiceResultEdit(e) {
    const value = e.detail.value || ''
    this.setData({
      voiceResult: value
    })
  },

  // 设置分类选择器索引
  setCategoryIndex() {
    const currentCategory = this.data.goalData.category
    const index = this.data.categories.findIndex(item => item.id === currentCategory)
    this.setData({
      categoryIndex: index >= 0 ? index : 0
    })
  },

  // 分类选择器变化
  onCategoryChange(e) {
    const index = e.detail.value
    const category = this.data.categories[index]
    console.log('选择分类:', category)
    
    this.setData({
      'goalData.category': category.id,
      categoryIndex: index
    })
  },

  // 解析语音识别结果
  parseVoiceResult(voiceText) {
    console.log('开始解析语音内容:', voiceText)
    
    // 显示加载提示
    wx.showLoading({
      title: '正在解析语音...',
      mask: true
    })
    
    // 调用后端语音解析API
    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/parse-voice`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data: {
        voice_text: voiceText
      },
      success: (res) => {
        wx.hideLoading()
        console.log('语音解析响应:', res)
        
        if (res.statusCode === 200 && res.data.success) {
          const parsedGoal = res.data.data
          const validation = res.data.validation
          
          console.log('后端解析结果:', parsedGoal)
          console.log('验证结果:', validation)
          
          // 转换日期格式
          const parsedData = {
            title: parsedGoal.title || '',
            category: parsedGoal.category || '学习',
            description: parsedGoal.description || voiceText,
            startDate: parsedGoal.startDate ? this.formatDateForPicker(parsedGoal.startDate) : '',
            endDate: parsedGoal.endDate ? this.formatDateForPicker(parsedGoal.endDate) : '',
            startDateText: parsedGoal.startDate ? this.formatDateText(new Date(parsedGoal.startDate)) : '请选择开始时间',
            endDateText: parsedGoal.endDate ? this.formatDateText(new Date(parsedGoal.endDate)) : '请选择结束时间',
            targetValue: parsedGoal.targetValue || '',
            currentValue: parsedGoal.currentValue || '0',
            unit: parsedGoal.unit || '',
            priority: parsedGoal.priority || 'medium',
            dailyReminder: parsedGoal.dailyReminder !== undefined ? parsedGoal.dailyReminder : true,
            deadlineReminder: parsedGoal.deadlineReminder !== undefined ? parsedGoal.deadlineReminder : true
          }
          
          // 更新表单数据
          this.setData({
            goalData: { ...this.data.goalData, ...parsedData }
          })
          
          // 更新分类选择器索引
          this.setCategoryIndex()
          
          // 显示解析成功提示
          let message = '语音内容已智能解析'
          if (validation && validation.score < 80) {
            message = `解析完成 (评分: ${validation.score}/100)`
          }
          
          wx.showToast({
            title: message,
            icon: 'success'
          })
          
          // 处理解析提示信息
          const parsingHints = res.data.parsing_hints
          if (parsingHints) {
            this.handleParsingHints(parsingHints, validation)
          } else if (validation && validation.warnings && validation.warnings.length > 0) {
            // 兼容旧的验证警告显示
            setTimeout(() => {
              wx.showModal({
                title: '解析建议',
                content: validation.warnings[0],
                showCancel: false,
                confirmText: '知道了'
              })
            }, 1000)
          }
          
        } else {
          console.error('语音解析失败:', res.data)
          wx.showToast({
            title: res.data.message || '语音解析失败',
            icon: 'none'
          })
          
          // 降级到简单解析
          this.fallbackParseVoiceResult(voiceText)
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('语音解析请求失败:', err)
        wx.showToast({
          title: '网络错误，使用简单解析',
          icon: 'none'
        })
        
        // 降级到简单解析
        this.fallbackParseVoiceResult(voiceText)
      }
    })
  },

  // 降级解析方法（当后端解析失败时使用）
  fallbackParseVoiceResult(voiceText) {
    console.log('使用降级解析:', voiceText)
    
    // 简单的正则表达式解析
    const parsedData = {
      title: '',
      category: '学习',
      description: voiceText,
      startDate: '',
      endDate: '',
      targetValue: '',
      currentValue: '0',
      unit: '',
      priority: 'medium',
      dailyReminder: true,
      deadlineReminder: true
    }
    
    // 提取时间信息
    const timeMatch = voiceText.match(/(\d+)\s*个?月|(\d+)\s*个?周|(\d+)\s*天/)
    if (timeMatch) {
      const months = timeMatch[1] || 0
      const weeks = timeMatch[2] || 0
      const days = timeMatch[3] || 0
      
      // 设置开始时间为今天
      const startDate = new Date()
      parsedData.startDate = this.formatDate(startDate)
      parsedData.startDateText = this.formatDateText(startDate)
      
      // 计算结束时间
      const endDate = new Date(startDate)
      endDate.setMonth(endDate.getMonth() + parseInt(months))
      endDate.setDate(endDate.getDate() + parseInt(weeks) * 7 + parseInt(days))
      parsedData.endDate = this.formatDate(endDate)
      parsedData.endDateText = this.formatDateText(endDate)
    }
    
    // 提取目标值
    const valueMatch = voiceText.match(/(\d+)\s*(小时|次|页|天|个|斤|公里|本书)/)
    if (valueMatch) {
      parsedData.targetValue = valueMatch[1]
      parsedData.unit = valueMatch[2]
    }
    
    // 提取标题（取前20个字符作为标题）
    parsedData.title = voiceText.substring(0, 20) + (voiceText.length > 20 ? '...' : '')
    
    // 智能分类
    if (voiceText.includes('学习') || voiceText.includes('掌握') || voiceText.includes('Python') || voiceText.includes('框架')) {
      parsedData.category = '学习'
    } else if (voiceText.includes('健身') || voiceText.includes('运动') || voiceText.includes('健康') || voiceText.includes('减重')) {
      parsedData.category = '健康'
    } else if (voiceText.includes('工作') || voiceText.includes('项目') || voiceText.includes('文档')) {
      parsedData.category = '工作'
    } else if (voiceText.includes('阅读') || voiceText.includes('书') || voiceText.includes('页')) {
      parsedData.category = '阅读'
    }
    
    console.log('降级解析结果:', parsedData)
    
    // 更新表单数据
    this.setData({
      goalData: { ...this.data.goalData, ...parsedData }
    })
    
    // 更新分类选择器索引
    this.setCategoryIndex()
  },

  // 标题输入
  onTitleInput(e) {
    this.setData({
      'goalData.title': e.detail.value
    })
  },

  // 描述输入
  onDescriptionInput(e) {
    this.setData({
      'goalData.description': e.detail.value
    })
  },

  // 开始时间变化
  onStartDateChange(e) {
    const date = e.detail.value
    console.log('开始时间:', date)
    
    this.setData({
      'goalData.startDate': date,
      'goalData.startDateText': this.formatDateText(new Date(date))
    })
  },

  // 结束时间变化
  onEndDateChange(e) {
    const date = e.detail.value
    console.log('结束时间:', date)
    
    this.setData({
      'goalData.endDate': date,
      'goalData.endDateText': this.formatDateText(new Date(date))
    })
  },

  // 目标值输入
  onTargetValueInput(e) {
    this.setData({
      'goalData.targetValue': e.detail.value
    })
  },

  // 当前值输入
  onCurrentValueInput(e) {
    this.setData({
      'goalData.currentValue': e.detail.value
    })
  },

  // 单位输入
  onUnitInput(e) {
    this.setData({
      'goalData.unit': e.detail.value
    })
  },

  // 优先级选择
  selectPriority(e) {
    const priority = e.currentTarget.dataset.priority
    this.setData({
      'goalData.priority': priority
    })
  },

  // 每日提醒开关
  onDailyReminderChange(e) {
    console.log('每日提醒开关变化:', e.detail.value)
    this.setData({
      'goalData.dailyReminder': e.detail.value
    })
    console.log('更新后的每日提醒状态:', this.data.goalData.dailyReminder)
  },

  // 截止提醒开关
  onDeadlineReminderChange(e) {
    console.log('截止提醒开关变化:', e.detail.value)
    this.setData({
      'goalData.deadlineReminder': e.detail.value
    })
    console.log('更新后的截止提醒状态:', this.data.goalData.deadlineReminder)
  },

  // 验证目标数据
  validateGoal(goalData) {
    const errors = []
    
    // 检查必填字段
    if (!goalData.title || goalData.title.trim() === '') {
      errors.push('请输入目标标题')
    }
    
    if (!goalData.description || goalData.description.trim() === '') {
      errors.push('请输入目标描述')
    }
    
    if (!goalData.startDate) {
      errors.push('请选择开始时间')
    }
    
    if (!goalData.endDate) {
      errors.push('请选择结束时间')
    }
    
    // 检查时间逻辑
    if (goalData.startDate && goalData.endDate) {
      const startDate = new Date(goalData.startDate)
      const endDate = new Date(goalData.endDate)
      if (startDate >= endDate) {
        errors.push('结束时间必须晚于开始时间')
      }
    }
    
    // 检查量化指标
    if (goalData.targetValue && goalData.unit) {
      if (isNaN(goalData.targetValue) || parseFloat(goalData.targetValue) <= 0) {
        errors.push('目标值必须是正数')
      }
    }
    
    console.log('验证结果:', { isValid: errors.length === 0, errors: errors })
    return { isValid: errors.length === 0, errors: errors }
  },

  // 创建目标
  createGoal() {
    console.log('开始创建目标')
    
    // 验证表单
    const validationResult = this.validateGoal(this.data.goalData)
    if (!validationResult.isValid) {
      wx.showToast({
        title: validationResult.errors[0],
        icon: 'none'
      })
      return
    }

    // 显示加载提示
    wx.showLoading({
      title: '创建中...'
    })

    // 准备发送到后端的数据，确保包含所有字段
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
    }

    console.log('准备发送的目标数据:', goalDataToSend)
    console.log('提醒设置详情:', {
      dailyReminder: goalDataToSend.dailyReminder,
      deadlineReminder: goalDataToSend.deadlineReminder,
      dailyReminderType: typeof goalDataToSend.dailyReminder,
      deadlineReminderType: typeof goalDataToSend.deadlineReminder
    })

    // 调用后端API
    wx.request({
      url: `${app.globalData.baseUrl}/api/goals/`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${app.globalData.token}`
      },
      data: goalDataToSend,
      success: (res) => {
        wx.hideLoading()
        console.log('创建目标成功:', res)
        
        if (res.statusCode === 200 && res.data.success) {
          wx.showToast({
            title: '目标创建成功',
            icon: 'success'
          })
          
          // 延迟跳转到目标管理页面
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/goals/goals',
              success: () => {
                console.log('成功跳转到目标管理页面')
              },
              fail: (err) => {
                console.error('跳转到目标管理页面失败:', err)
                // 如果跳转失败，回退到返回上一页
                wx.navigateBack()
              }
            })
          }, 1500)
        } else {
          wx.showToast({
            title: res.data.message || '创建失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('创建目标失败:', err)
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

  // 处理解析提示信息
  handleParsingHints(parsingHints, validation) {
    const quality = parsingHints.parsing_quality
    const missingElements = parsingHints.missing_elements || []
    const suggestions = parsingHints.suggestions || []
    const improvementTips = parsingHints.improvement_tips || []
    
    // 根据解析质量决定显示方式
    if (quality === 'excellent') {
      // 优秀：只显示成功提示
      return
    } else {
      // 其他情况：显示统一的解析建议弹窗
      this.showUnifiedParsingHints(parsingHints, validation)
    }
  },

  // 显示统一的解析提示弹窗
  showUnifiedParsingHints(parsingHints, validation) {
    const quality = parsingHints.parsing_quality
    const missingElements = parsingHints.missing_elements || []
    
    // 准备弹窗数据
    const voiceResult = this.data.voiceResult || '未识别到目标内容'
    const improvementSuggestions = this.convertToImprovementSuggestions(missingElements)
    
    // 只有在有建议时才显示弹窗
    if (improvementSuggestions.length === 0) {
      console.log('✅ 目标解析完美，无需显示建议弹窗')
      return
    }
    
    // 设置弹窗数据
    this.setData({
      showParsingModal: true,
      parsingModalData: {
        voiceResult: voiceResult,
        suggestions: improvementSuggestions.slice(0, 2) // 只显示前2个建议
      }
    })
  },

  // 隐藏自定义弹窗
  hideParsingModal() {
    this.setData({
      showParsingModal: false
    })
  },

  // 重新录音
  onReRecord() {
    this.hideParsingModal()
    // 返回目标管理页面
    wx.navigateBack({
      success: () => {
        // 延迟一下确保页面切换完成
        setTimeout(() => {
          const pages = getCurrentPages()
          const prevPage = pages[pages.length - 1]
          if (prevPage && prevPage.route === 'pages/goals/goals') {
            if (typeof prevPage.showCreateModal === 'function') {
              prevPage.showCreateModal()
            }
          } else {
            // 如果无法获取到目标管理页面，使用switchTab作为备选方案
            wx.switchTab({
              url: '/pages/goals/goals',
              success: () => {
                setTimeout(() => {
                  const currentPages = getCurrentPages()
                  const currentPage = currentPages[currentPages.length - 1]
                  if (currentPage && typeof currentPage.showCreateModal === 'function') {
                    currentPage.showCreateModal()
                  }
                }, 300)
              }
            })
          }
        }, 100)
      }
    })
  },

  // 创建目标
  onCreateGoal() {
    this.hideParsingModal()
    // 保持在当前页面继续编辑
    console.log('用户选择创建目标，继续编辑')
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
  }
})
