// components/photo-result-modal/photo-result-modal.js
Component({
  properties: {
    show: {
      type: Boolean,
      value: false
    },
    photoData: {
      type: Object,
      value: null
    }
  },

  data: {
    recordTypeMap: {
      'progress': '进度更新',
      'reflection': '反思总结',
      'plan': '计划安排',
      'achievement': '成果记录',
      'challenge': '困难挑战',
      'learning': '学习笔记',
      'other': '其他'
    },
    sentimentMap: {
      'positive': '积极',
      'negative': '消极',
      'neutral': '中性'
    }
  },

  methods: {
    // 关闭弹窗
    close() {
      this.triggerEvent('close')
    },

    // 确认
    confirm() {
      this.triggerEvent('confirm', this.properties.photoData)
      this.close()
    },

    // 查看详情
    viewDetail() {
      this.triggerEvent('viewDetail', this.properties.photoData)
      this.close()
    },

    // 获取记录类型文本
    getRecordTypeText(type) {
      return this.data.recordTypeMap[type] || '其他'
    },

    // 获取情绪文本
    getSentimentText(sentiment) {
      return this.data.sentimentMap[sentiment] || '中性'
    }
  }
})

