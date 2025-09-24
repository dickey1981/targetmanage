// API兼容性工具
// 用于处理不同版本微信小程序的API兼容性问题

/**
 * 安全调用微信API，自动处理不支持的情况
 * @param {Function} apiCall - API调用函数
 * @param {string} apiName - API名称，用于日志
 * @param {Function} fallback - 降级处理函数
 */
export function safeApiCall(apiCall, apiName, fallback) {
  try {
    // 检查API是否存在
    if (typeof apiCall === 'function') {
      apiCall()
    } else {
      console.warn(`⚠️ API ${apiName} 不支持，使用降级方案`)
      if (fallback && typeof fallback === 'function') {
        fallback()
      }
    }
  } catch (error) {
    console.error(`❌ API ${apiName} 调用失败:`, error)
    if (fallback && typeof fallback === 'function') {
      fallback()
    }
  }
}

/**
 * 检查API是否支持
 * @param {string} apiName - API名称
 * @returns {boolean}
 */
export function isApiSupported(apiName) {
  try {
    // 检查API是否存在
    const api = wx[apiName]
    return typeof api === 'function'
  } catch (error) {
    return false
  }
}

/**
 * 获取系统信息，处理兼容性
 * @returns {Object}
 */
export function getSystemInfo() {
  return new Promise((resolve, reject) => {
    if (isApiSupported('getSystemInfo')) {
      wx.getSystemInfo({
        success: resolve,
        fail: reject
      })
    } else {
      // 降级方案
      resolve({
        platform: 'unknown',
        version: 'unknown',
        SDKVersion: 'unknown'
      })
    }
  })
}

/**
 * 检查实时数据上报API支持
 * @returns {boolean}
 */
export function isRealtimeActionSupported() {
  return isApiSupported('reportRealtimeAction')
}

/**
 * 安全的上报实时数据
 * @param {Object} data - 上报数据
 */
export function safeReportRealtimeAction(data) {
  if (isRealtimeActionSupported()) {
    try {
      wx.reportRealtimeAction(data)
    } catch (error) {
      console.warn('⚠️ reportRealtimeAction 调用失败:', error)
    }
  } else {
    console.info('ℹ️ reportRealtimeAction 不支持，跳过上报')
  }
}

/**
 * 检查Worker支持
 * @returns {boolean}
 */
export function isWorkerSupported() {
  try {
    return typeof Worker !== 'undefined'
  } catch (error) {
    return false
  }
}

/**
 * 获取环境信息
 * @returns {Object}
 */
export function getEnvironmentInfo() {
  return {
    isWorkerSupported: isWorkerSupported(),
    isRealtimeActionSupported: isRealtimeActionSupported(),
    platform: wx.getSystemInfoSync().platform,
    version: wx.getSystemInfoSync().version
  }
}

module.exports = {
  safeApiCall,
  isApiSupported,
  getSystemInfo,
  isRealtimeActionSupported,
  safeReportRealtimeAction,
  isWorkerSupported,
  getEnvironmentInfo
}
