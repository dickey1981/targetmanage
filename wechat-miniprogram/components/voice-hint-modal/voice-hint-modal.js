// 语音提示弹窗组件
Component({
  properties: {
    show: {
      type: Boolean,
      value: false
    },
    title: {
      type: String,
      value: '语音创建目标'
    },
    voiceText: {
      type: String,
      value: ''
    },
    suggestions: {
      type: Array,
      value: []
    },
    cancelText: {
      type: String,
      value: '重新录音'
    },
    confirmText: {
      type: String,
      value: '创建目标'
    }
  },

  methods: {
    onMaskTap() {
      // 点击遮罩层不关闭弹窗
    },

    onContainerTap() {
      // 点击容器不关闭弹窗
    },

    onClose() {
      this.triggerEvent('close')
    },

    onCancel() {
      this.triggerEvent('cancel')
    },

    onConfirm() {
      this.triggerEvent('confirm')
    }
  }
})
