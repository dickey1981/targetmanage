// 开发环境警告处理工具
// 用于处理和抑制开发环境中不影响功能的警告

/**
 * 抑制SharedArrayBuffer警告
 * 这个警告只在开发工具中出现，不影响实际功能
 */
export function suppressSharedArrayBufferWarning() {
  // 在微信小程序环境中，这个警告可以安全忽略
  try {
    if (typeof console !== 'undefined' && console.warn) {
      const originalWarn = console.warn
      console.warn = function(...args) {
        const message = args.join(' ')
        // 过滤掉SharedArrayBuffer相关的警告
        if (message.includes('SharedArrayBuffer') && message.includes('cross-origin isolation')) {
          console.info('ℹ️ 已忽略SharedArrayBuffer跨域警告（开发环境正常现象）')
          return
        }
        // 其他警告正常显示
        originalWarn.apply(console, args)
      }
    }
  } catch (error) {
    console.log('⚠️ 无法设置警告过滤，跳过')
  }
}

/**
 * 处理API不支持的错误
 * @param {string} apiName - API名称
 * @param {string} feature - 功能名称
 */
export function handleApiNotSupported(apiName, feature) {
  console.info(`ℹ️ ${apiName} 不支持，${feature} 功能将使用降级方案`)
  
  // 在开发环境中显示友好提示
  try {
    const systemInfo = wx.getSystemInfoSync()
    const isDevTools = systemInfo.platform === 'devtools'
    
    if (isDevTools) {
      console.group('🔧 开发环境提示')
      console.log(`API: ${apiName}`)
      console.log(`功能: ${feature}`)
      console.log('状态: 已使用降级方案，不影响核心功能')
      console.groupEnd()
    }
  } catch (error) {
    // 忽略错误，继续执行
  }
}

/**
 * 初始化开发环境警告处理
 */
export function initDevWarnings() {
  // 检查是否在微信小程序开发工具中
  try {
    const systemInfo = wx.getSystemInfoSync()
    const isDevTools = systemInfo.platform === 'devtools'
    
    if (isDevTools) {
      suppressSharedArrayBufferWarning()
      
      console.log('🔧 开发环境警告处理已启用')
      console.log('ℹ️ 以下警告为正常现象，不影响实际功能：')
      console.log('  - SharedArrayBuffer 跨域隔离警告')
      console.log('  - reportRealtimeAction API 不支持警告')
    }
  } catch (error) {
    console.log('⚠️ 无法检测开发环境，跳过警告处理')
  }
}

module.exports = {
  suppressSharedArrayBufferWarning,
  handleApiNotSupported,
  initDevWarnings
}
