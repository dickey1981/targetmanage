// pages/timeline/timeline.js
const app = getApp()

Page({
  data: {
    // 筛选器
    activeFilter: 'all',
    timeRangeIndex: 3,  // 默认选择"全部"
    timeRanges: [
      { name: '最近7天', days: 7 },
      { name: '最近30天', days: 30 },
      { name: '最近90天', days: 90 },
      { name: '全部', days: 365 }
    ],
    
    // 时间线数据
    timelineData: [],
    stats: null,
    
    // 分页
    page: 1,
    pageSize: 20,
    hasMore: true,
    loading: false,
    
    // 目标ID（如果从目标详情页进入）
    goalId: null
  },

  onLoad(options) {
    // 获取传入的目标ID
    if (options.goalId) {
      this.setData({
        goalId: options.goalId
      })
    }
    
    // 加载时间线数据
    this.loadTimelineData()
    this.loadStats()
  },

  onShow() {
    // 页面显示时刷新数据
    this.refreshData()
  },

  // 设置筛选器
  setFilter(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({
      activeFilter: filter
    })
    this.refreshData()
  },

  // 时间范围变化
  onTimeRangeChange(e) {
    const index = e.detail.value
    this.setData({
      timeRangeIndex: index
    })
    this.refreshData()
  },

  // 刷新数据
  refreshData() {
    this.setData({
      page: 1,
      hasMore: true,
      timelineData: []
    })
    this.loadTimelineData()
    this.loadStats()
  },

  // 加载时间线数据
  loadTimelineData() {
    if (this.data.loading) return
    
    this.setData({
      loading: true
    })
    
    const { timeRanges, timeRangeIndex, activeFilter, page, goalId } = this.data
    const days = timeRanges[timeRangeIndex].days
    const token = wx.getStorageSync('token') || app.globalData.token
    
    console.log('📊 加载时间线数据:', { days, activeFilter, goalId })
    
    // 构建请求参数，排除 null 值
    const params = { days: days }
    if (goalId) params.goal_id = goalId
    if (activeFilter !== 'all') params.record_type = activeFilter
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/process-records/timeline`,
      method: 'GET',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      data: params,
      success: (res) => {
        console.log('✅ 时间线数据响应:', res)
        if (res.statusCode === 200) {
          const newData = res.data || []
          
          // 处理数据，添加辅助方法
          const processedData = newData.map(item => {
            return {
              ...item,
              records: item.records.map(record => ({
                ...record,
                typeIcon: this.getTypeIcon(record.record_type),
                typeName: this.getTypeName(record.record_type),
                sentimentIcon: this.getSentimentIcon(record.sentiment),
                sentimentText: this.getSentimentText(record.sentiment),
                formattedTime: this.formatTime(record.recorded_at)
              }))
            }
          })
          
          if (page === 1) {
            // 第一页，直接设置数据
            this.setData({
              timelineData: processedData,
              hasMore: newData.length >= this.data.pageSize
            })
          } else {
            // 后续页，追加数据
            this.setData({
              timelineData: [...this.data.timelineData, ...processedData],
              hasMore: newData.length >= this.data.pageSize
            })
          }
          
          console.log('✅ 时间线数据加载成功:', processedData.length, '天')
        } else {
          console.error('❌ 时间线数据加载失败:', res)
          wx.showToast({
            title: res.data?.message || '加载失败',
            icon: 'none'
          })
        }
      },
      fail: (error) => {
        console.error('❌ 加载时间线数据失败:', error)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({
          loading: false
        })
        wx.stopPullDownRefresh()
      }
    })
  },

  // 加载统计数据
  loadStats() {
    const { timeRanges, timeRangeIndex, goalId } = this.data
    const days = timeRanges[timeRangeIndex].days
    const token = wx.getStorageSync('token') || app.globalData.token
    
    console.log('📈 加载统计数据:', { days, goalId })
    
    // 构建请求参数，排除 null 值
    const params = { days: days }
    if (goalId) params.goal_id = goalId
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/process-records/stats`,
      method: 'GET',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      data: params,
      success: (res) => {
        console.log('✅ 统计数据响应:', res)
        if (res.statusCode === 200) {
          this.setData({
            stats: res.data
          })
          console.log('✅ 统计数据加载成功')
        }
      },
      fail: (error) => {
        console.error('❌ 加载统计数据失败:', error)
      }
    })
  },

  // 加载更多
  loadMore() {
    if (!this.data.hasMore || this.data.loading) return
    
    this.setData({
      page: this.data.page + 1
    })
    this.loadTimelineData()
  },

  // 查看记录详情
  viewRecordDetail(e) {
    const record = e.currentTarget.dataset.record
    console.log('📝 查看记录详情:', record)
    
    // 跳转到记录详情页面
    wx.navigateTo({
      url: `/pages/record-detail/record-detail?id=${record.id}`,
      success: () => {
        console.log('✅ 跳转到记录详情页成功')
      },
      fail: (err) => {
        console.error('❌ 跳转失败:', err)
        // 降级方案：显示简单弹窗
        wx.showModal({
          title: '记录详情',
          content: record.content,
          showCancel: false,
          confirmText: '确定'
        })
      }
    })
  },

  // 去记录页面
  goToRecord() {
    wx.navigateTo({
      url: '/pages/process-record/process-record'
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

  // 获取情感图标
  getSentimentIcon(sentiment) {
    const icons = {
      'positive': '😊',
      'negative': '😔',
      'neutral': '😐'
    }
    return icons[sentiment] || '😐'
  },

  // 获取情感文本
  getSentimentText(sentiment) {
    const texts = {
      'positive': '积极',
      'negative': '消极',
      'neutral': '中性'
    }
    return texts[sentiment] || '中性'
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

  // 下拉刷新
  onPullDownRefresh() {
    this.refreshData()
    wx.stopPullDownRefresh()
  },

  // 上拉加载更多
  onReachBottom() {
    this.loadMore()
  }
})