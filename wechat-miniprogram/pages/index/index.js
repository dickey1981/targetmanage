// pages/index/index.js
const app = getApp()

Page({
  data: {
    isLoggedIn: false,
    userInfo: null,
    showLoginModal: false,
    isLoggingIn: false,
    userPhoneNumber: '',
    todayGoals: [],
    completedGoalsCount: 0,
    pendingGoalsCount: 0,
    // 语音交互相关
    isRecording: false,
    recordingText: '按住说话',
    voiceHint: '松开结束',
    // 创建目标弹窗
    showCreateGoalModal: false,
    // 语音识别结果弹窗
    showVoiceResultModal: false,
    voiceRecognizedText: '',
    voiceInstructionType: '',
    voiceConfidence: 0,
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
    
    // 添加测试数据
    this.setData({
      todayGoals: [
        { id: 1, title: '学习新技能', progress: 44, completed: false },
        { id: 2, title: '健身锻炼', progress: 25, completed: false },
        { id: 3, title: '阅读书籍', progress: 80, completed: false },
        { id: 4, title: '项目开发', progress: 60, completed: false }
      ],
      completedGoalsCount: 2,
      pendingGoalsCount: 2
    })
    
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
        userInfo: null,
        showLoginModal: true  // 未登录时直接显示授权弹窗
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
  // 授权按钮点击调试
  onAuthButtonTap(e) {
    console.log('🔘 授权按钮被点击:', e)
    console.log('按钮类型:', e.currentTarget.dataset)
    
    // 检查微信环境
    const systemInfo = wx.getSystemInfoSync()
    console.log('系统信息:', systemInfo)
    
    // 检查是否支持手机号授权
    if (wx.getPhoneNumber) {
      console.log('✅ 支持 getPhoneNumber API')
    } else {
      console.log('❌ 不支持 getPhoneNumber API')
      wx.showModal({
        title: '提示',
        content: '当前环境不支持手机号授权，请在微信中打开',
        showCancel: false
      })
    }
  },

  // 获取手机号授权
  onGetPhoneNumber(e) {
    console.log('📱 手机号授权结果:', e.detail)
    console.log('授权事件详情:', JSON.stringify(e.detail, null, 2))
    
    // 检查是否有错误信息
    if (e.detail.errMsg) {
      console.log('授权错误信息:', e.detail.errMsg)
      
      if (e.detail.errMsg.includes('deny') || e.detail.errMsg.includes('cancel')) {
        // 用户拒绝授权
        console.log('用户拒绝手机号授权')
        wx.showToast({
          title: '需要手机号授权才能使用完整功能',
          icon: 'none',
          duration: 3000
        })
        return
      } else if (e.detail.errMsg.includes('fail')) {
        // 授权失败
        console.log('手机号授权失败')
        wx.showToast({
          title: '授权失败，请重试',
          icon: 'none'
        })
        return
      }
    }
    
    if (e.detail.code) {
      console.log('✅ 获取到手机号授权码:', e.detail.code)
      
      // 显示授权成功提示
      wx.showLoading({
        title: '正在登录...'
      })
      
      this.setData({
        isLoggingIn: true
      })
      
      // 调用登录接口
      this.loginWithWeChat(e.detail.code)
    } else {
      console.log('❌ 未获取到授权码')
      wx.showToast({
        title: '授权失败，请重试',
        icon: 'none'
      })
    }
  },

  // 拒绝授权
  denyAuth() {
    console.log('用户选择暂不授权')
    
    wx.showModal({
      title: '授权提示',
      content: '授权手机号可以获得更好的使用体验，包括目标同步、数据备份等功能。',
      confirmText: '重新授权',
      cancelText: '暂不使用',
      success: (res) => {
        if (res.confirm) {
          // 用户选择重新授权，保持弹窗显示
          console.log('用户选择重新授权')
        } else {
          // 用户选择暂不使用，关闭弹窗
          this.setData({
            showLoginModal: false
          })
          wx.showToast({
            title: '部分功能将受限',
            icon: 'none'
          })
        }
      }
    })
  },

  // 获取用户信息授权（主要方案）
  onGetUserInfo(e) {
    console.log('👤 用户信息授权结果:', e.detail)
    console.log('授权详情:', JSON.stringify(e.detail, null, 2))
    
    if (e.detail.userInfo) {
      console.log('✅ 获取到用户信息:', e.detail.userInfo)
      
      // 显示授权成功提示
      wx.showLoading({
        title: '正在登录...'
      })
      
      this.setData({
        isLoggingIn: true
      })
      
      // 使用用户信息进行登录（不需要手机号）
      this.loginWithWeChat(null, e.detail.userInfo)
    } else {
      console.log('❌ 用户拒绝授权')
      console.log('错误信息:', e.detail.errMsg)
      
      // 检查是否是因为用户拒绝
      if (e.detail.errMsg && e.detail.errMsg.includes('deny')) {
        wx.showModal({
          title: '授权提示',
          content: '需要获取您的微信信息才能使用小程序，是否重新授权？',
          confirmText: '重新授权',
          cancelText: '取消',
          success: (res) => {
            if (res.cancel) {
              this.setData({
                showLoginModal: false
              })
              wx.showToast({
                title: '已取消授权',
                icon: 'none'
              })
            }
          }
        })
      } else {
        wx.showToast({
          title: '授权失败，请重试',
          icon: 'none'
        })
      }
    }
  },

  // 使用其他方式登录
  useOtherPhone() {
    wx.showModal({
      title: '其他登录方式',
      content: '目前支持微信授权登录，请选择上方的授权方式完成登录。',
      confirmText: '去授权',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          // 用户选择去授权，保持弹窗显示
          console.log('引导用户进行授权')
        }
      }
    })
  },

  // 使用微信信息登录/注册
  loginWithWeChat(phoneCode, userInfo) {
    console.log('🔐 开始登录流程，手机号授权码:', phoneCode, '用户信息:', userInfo)
    
    this.setData({
      isLoggingIn: true
    })

    // 先获取微信登录code
    wx.login({
      success: (loginRes) => {
        if (loginRes.code) {
          console.log('✅ 获取微信登录code成功:', loginRes.code)
          // 获取到code后，发送给后端
          this.sendLoginRequest(loginRes.code, phoneCode, userInfo)
        } else {
          console.error('❌ 获取微信登录code失败')
          wx.hideLoading()
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
        console.error('❌ wx.login失败:', err)
        wx.hideLoading()
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
  sendLoginRequest(code, phoneCode, userInfo) {
    // 调试信息
    const apiUrl = `${app.globalData.baseUrl}/api/auth/wechat-login`
    console.log('📡 发送登录请求到:', apiUrl)
    console.log('微信code:', code)
    console.log('手机号授权码:', phoneCode)
    console.log('用户信息:', userInfo)

    // 构建请求数据
    const requestData = {
      code: code
    }
    
    // 如果有手机号授权码，添加到请求中
    if (phoneCode) {
      requestData.phoneCode = phoneCode
    }
    
    // 如果有用户信息，添加到请求中
    if (userInfo) {
      requestData.userInfo = userInfo
    }

    wx.request({
      url: apiUrl,
      method: 'POST',
      data: requestData,
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
          
          // 隐藏加载状态
          wx.hideLoading()
          
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
    
    // 如果已经在录音，先停止
    if (this.data.isRecording && this.recorderManager) {
      console.log('⚠️ 录音器已在录音，先停止')
      try {
        this.recorderManager.stop()
      } catch (e) {
        console.log('停止录音异常:', e)
      }
    }
    
    // 检查录音权限
    this.checkRecordPermission().then(() => {
      this.setData({
        isRecording: true,
        recordingText: '正在录音...',
        voiceHint: '松开结束录音'
      })
      
      // 获取或创建录音管理器（使用单例）
      if (!this.recorderManager) {
        this.recorderManager = wx.getRecorderManager()
        
        // 只绑定一次事件监听
        this.recorderManager.onStart(() => {
          console.log('录音开始')
        })
        
        this.recorderManager.onError((err) => {
          console.error('录音错误:', err)
          this.handleRecordError(err)
        })
        
        this.recorderManager.onStop((res) => {
          console.log('录音结束:', res)
          if (this.onStopCallback) {
            this.onStopCallback(res)
          }
        })
      }
      
      // 开始录音
      try {
        this.recorderManager.start({
          duration: 60000, // 最长60秒
          sampleRate: 16000, // 16k采样率
          numberOfChannels: 1, // 单声道
          encodeBitRate: 96000, // 编码码率
          format: 'mp3' // 格式
        })
      } catch (e) {
        console.error('启动录音失败:', e)
        this.handleRecordError(e)
      }
    }).catch((error) => {
      console.error('录音权限检查失败:', error)
      wx.showToast({
        title: '录音权限不足',
        icon: 'none'
      })
    })
  },

  // 检查录音权限
  checkRecordPermission() {
    return new Promise((resolve, reject) => {
      wx.getSetting({
        success: (res) => {
          if (res.authSetting['scope.record'] === false) {
            // 用户拒绝了录音权限，引导用户手动开启
            wx.showModal({
              title: '需要录音权限',
              content: '语音功能需要录音权限，请在设置中开启',
              confirmText: '去设置',
              cancelText: '取消',
              success: (modalRes) => {
                if (modalRes.confirm) {
                  wx.openSetting({
                    success: (settingRes) => {
                      if (settingRes.authSetting['scope.record']) {
                        resolve()
                      } else {
                        reject(new Error('用户拒绝授权录音权限'))
                      }
                    },
                    fail: () => {
                      reject(new Error('打开设置失败'))
                    }
                  })
                } else {
                  reject(new Error('用户取消授权'))
                }
              }
            })
          } else if (res.authSetting['scope.record'] === undefined) {
            // 首次使用，请求权限
            wx.authorize({
              scope: 'scope.record',
              success: () => {
                resolve()
              },
              fail: () => {
                reject(new Error('用户拒绝授权录音权限'))
              }
            })
          } else {
            // 已授权
            resolve()
          }
        },
        fail: () => {
          reject(new Error('获取设置失败'))
        }
      })
    })
  },

  // 处理录音错误
  handleRecordError(err) {
    let errorMessage = '录音失败'
    
    if (err.errMsg.includes('NotFoundError')) {
      errorMessage = '录音功能不可用，请检查设备'
    } else if (err.errMsg.includes('NotAllowedError')) {
      errorMessage = '录音权限被拒绝，请在设置中开启'
    } else if (err.errMsg.includes('NotSupportedError')) {
      errorMessage = '设备不支持录音功能'
    } else if (err.errMsg.includes('AbortError')) {
      errorMessage = '录音被中断'
    }
    
    wx.showToast({
      title: errorMessage,
      icon: 'none',
      duration: 3000
    })
    
    this.setData({
      isRecording: false,
      recordingText: '按住说话',
      voiceHint: '松开结束'
    })
  },

  stopVoiceRecord() {
    if (!this.data.isRecording) {
      console.log('⚠️ 当前没有在录音')
      return
    }
    
    this.setData({
      isRecording: false,
      recordingText: '录音完成，正在识别...',
      voiceHint: '请稍候'
    })
    
    // 停止录音
    if (this.recorderManager) {
      try {
        // 设置回调函数
        this.onStopCallback = (res) => {
          console.log('录音结束，文件路径:', res.tempFilePath)
          this.processVoiceRecord(res.tempFilePath)
          this.onStopCallback = null // 清除回调
        }
        
        this.recorderManager.stop()
      } catch (e) {
        console.error('停止录音失败:', e)
        this.setData({
          isRecording: false,
          recordingText: '按住说话',
          voiceHint: '松开结束'
        })
      }
    }
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
          }
        } catch (e) {
          console.error('解析响应失败:', e)
          wx.showToast({
            title: '语音识别失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('语音识别请求失败:', err)
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({
          recordingText: '按住说话',
          voiceHint: '松开结束'
        })
      }
    })
  },

  // 处理语音识别结果
  handleVoiceRecognitionResult(recognizedText) {
    console.log('语音识别结果:', recognizedText)
    
    // 智能判断语音指令类型
    const instructionType = this.analyzeVoiceInstruction(recognizedText)
    console.log('语音指令类型:', instructionType)
    
    // 显示语音识别结果弹窗
    this.showVoiceResultModal(recognizedText, instructionType)
  },

  // 显示语音识别结果弹窗
  showVoiceResultModal(recognizedText, instructionType) {
    this.setData({
      showVoiceResultModal: true,
      voiceRecognizedText: recognizedText,
      voiceInstructionType: instructionType.type,
      voiceConfidence: instructionType.confidence
    })
  },

  // 隐藏语音识别结果弹窗
  hideVoiceResultModal() {
    this.setData({
      showVoiceResultModal: false,
      voiceRecognizedText: '',
      voiceInstructionType: '',
      voiceConfidence: 0
    })
  },

  // 分析语音指令类型
  analyzeVoiceInstruction(text) {
    const createKeywords = ['我要', '我想', '计划', '目标', '创建', '设定', '开始']
    const updateKeywords = ['完成', '跑了', '读了', '做了', '达到', '实现', '今天']
    const recordKeywords = ['感觉', '发现', '遇到', '困难', '方法', '收获', '总结']
    const queryKeywords = ['情况', '进展', '如何', '怎样', '状态', '进度']
    
    if (createKeywords.some(keyword => text.includes(keyword))) {
      return { type: 'create_goal', confidence: 0.8 }
    } else if (updateKeywords.some(keyword => text.includes(keyword))) {
      return { type: 'update_progress', confidence: 0.7 }
    } else if (recordKeywords.some(keyword => text.includes(keyword))) {
      return { type: 'process_record', confidence: 0.6 }
    } else if (queryKeywords.some(keyword => text.includes(keyword))) {
      return { type: 'query_status', confidence: 0.5 }
    } else {
      return { type: 'unknown', confidence: 0.3 }
    }
  },

  // 创建目标按钮点击
  createGoalFromVoice() {
    const voiceText = this.data.voiceRecognizedText
    
    // 隐藏语音识别结果弹窗
    this.hideVoiceResultModal()
    
    // 跳转到目标创建确认页
    wx.navigateTo({
      url: `/pages/create-goal/create-goal?voiceResult=${encodeURIComponent(voiceText)}`,
      success: () => {
        console.log('跳转到目标创建页面成功')
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

  // 创建记录按钮点击
  createRecordFromVoice() {
    const voiceText = this.data.voiceRecognizedText
    
    // 隐藏语音识别结果弹窗
    this.hideVoiceResultModal()
    
    // 跳转到记录创建确认页
    wx.navigateTo({
      url: `/pages/process-record/process-record?voiceText=${encodeURIComponent(voiceText)}`,
      success: () => {
        console.log('跳转到记录创建页面成功')
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

  // 处理进度更新
  handleProgressUpdate(voiceText) {
    wx.showModal({
      title: '更新进度',
      content: `识别到："${voiceText}"\n是否更新目标进度？`,
      confirmText: '更新进度',
      cancelText: '重新录音',
      success: (res) => {
        if (res.confirm) {
          this.updateGoalProgress(voiceText)
        } else {
          // 用户选择重新录音，重新显示语音创建弹窗
          this.setData({
            recordingText: '按住说话',
            voiceHint: '松开结束'
          })
          // 重新显示语音创建弹窗
          this.showCreateGoalModal()
        }
      }
    })
  },

  // 处理过程记录
  handleProcessRecord(voiceText) {
    wx.showModal({
      title: '记录过程',
      content: `识别到："${voiceText}"\n是否记录为过程内容？`,
      confirmText: '记录过程',
      cancelText: '重新录音',
      success: (res) => {
        if (res.confirm) {
          this.recordProcess(voiceText)
        } else {
          // 用户选择重新录音，重新显示语音创建弹窗
          this.setData({
            recordingText: '按住说话',
            voiceHint: '松开结束'
          })
          // 重新显示语音创建弹窗
          this.showCreateGoalModal()
        }
      }
    })
  },

  // 处理状态查询
  handleStatusQuery(voiceText) {
    // 跳转到目标管理页面
    wx.switchTab({
      url: '/pages/goals/goals',
      success: () => {
        wx.showToast({
          title: '已跳转到目标管理',
          icon: 'none'
        })
      }
    })
  },

  // 处理未知指令
  handleUnknownInstruction(voiceText) {
    wx.showModal({
      title: '语音识别',
      content: `识别到："${voiceText}"\n请选择操作类型：`,
      confirmText: '创建目标',
      cancelText: '重新录音',
      success: (res) => {
        if (res.confirm) {
          this.handleGoalCreation(voiceText)
        } else {
          // 用户选择重新录音，重新显示语音创建弹窗
          this.setData({
            recordingText: '按住说话',
            voiceHint: '松开结束'
          })
          // 重新显示语音创建弹窗
          this.showCreateGoalModal()
        }
      }
    })
  },

  // 更新目标进度
  updateGoalProgress(voiceText) {
    // TODO: 实现进度更新逻辑
    wx.showToast({
      title: '进度更新功能开发中',
      icon: 'none'
    })
  },

  // 记录过程
  recordProcess(voiceText) {
    // TODO: 实现过程记录逻辑
    wx.showToast({
      title: '过程记录功能开发中',
      icon: 'none'
    })
  },

  // 判断是否为目标创建
  isGoalCreation(text) {
    const creationKeywords = ['我要', '我想', '计划', '目标', '创建', '设定']
    return creationKeywords.some(keyword => text.includes(keyword))
  },

  // 处理目标创建
  handleGoalCreation(voiceText) {
    wx.showModal({
      title: '创建新目标',
      content: `识别到："${voiceText}"\n是否创建新目标？`,
      confirmText: '创建目标',
      cancelText: '重新录音',
      success: (res) => {
        if (res.confirm) {
          this.createGoalFromVoice(voiceText)
        } else {
          // 用户选择重新录音，重新显示语音创建弹窗
          this.setData({
            recordingText: '按住说话',
            voiceHint: '松开结束'
          })
          // 重新显示语音创建弹窗
          this.showCreateGoalModal()
        }
      }
    })
  },

  // 处理进度更新
  handleProgressUpdate(voiceText) {
    wx.showModal({
      title: '更新目标进度',
      content: `识别到："${voiceText}"\n是否更新目标进度？`,
      confirmText: '确认更新',
      cancelText: '重新录音',
      success: (res) => {
        if (res.confirm) {
          this.updateGoalProgress(voiceText)
        } else {
          // 用户选择重新录音，重新显示语音创建弹窗
          this.setData({
            recordingText: '按住说话',
            voiceHint: '松开结束'
          })
          // 重新显示语音创建弹窗
          this.showCreateGoalModal()
        }
      }
    })
  },



  // 更新目标进度
  updateGoalProgress(voiceText) {
    // TODO: 实现进度更新逻辑
    wx.showToast({
      title: '进度更新功能开发中',
      icon: 'none'
    })
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
    if (!this.data.isLoggedIn) {
      this.showLoginModal()
      return
    }

    console.log('用户已登录，显示语音创建弹窗')
    this.setData({
      showCreateGoalModal: true
    })
  },

  // 显示创建目标弹窗
  showCreateGoalModal() {
    // 检查用户是否已登录
    if (!this.data.isLoggedIn) {
      this.showLoginModal()
      return
    }

    console.log('显示语音创建目标弹窗')
    this.setData({
      showCreateGoalModal: true
    })
  },

  // 隐藏创建目标弹窗
  hideCreateGoalModal() {
    this.setData({
      showCreateGoalModal: false
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
  },

  // 图片加载成功
  onImageLoad(e) {
    console.log('图片加载成功:', e)
  },

  // 图片加载失败
  onImageError(e) {
    console.log('图片加载失败:', e)
    wx.showToast({
      title: '图片加载失败',
      icon: 'none'
    })
  }
})
