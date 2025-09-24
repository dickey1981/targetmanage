// pages/timeline/timeline.js
const app = getApp()

Page({
  data: {
    // 筛选器
    activeFilter: 'all',
    timeRangeIndex: 0,
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
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/process-records/timeline`,
      method: 'GET',
      data: {
        days: days,
        goal_id: goalId,
        record_type: activeFilter === 'all' ? null : activeFilter
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const newData = res.data || []
          
          if (page === 1) {
            // 第一页，直接设置数据
            this.setData({
              timelineData: newData,
              hasMore: newData.length >= this.data.pageSize
            })
          } else {
            // 后续页，追加数据
            this.setData({
              timelineData: [...this.data.timelineData, ...newData],
              hasMore: newData.length >= this.data.pageSize
            })
          }
        }
      },
      fail: (error) => {
        console.error('加载时间线数据失败:', error)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({
          loading: false
        })
      }
    })
  },

  // 加载统计数据
  loadStats() {
    const { timeRanges, timeRangeIndex, goalId } = this.data
    const days = timeRanges[timeRangeIndex].days
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/process-records/stats`,
      method: 'GET',
      data: {
        days: days,
        goal_id: goalId
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            stats: res.data
          })
        }
      },
      fail: (error) => {
        console.error('加载统计数据失败:', error)
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
    console.log('查看记录详情:', record)
    
    // 可以跳转到记录详情页面或显示详情弹窗
    wx.showModal({
      title: '记录详情',
      content: record.content,
      showCancel: false,
      confirmText: '确定'
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