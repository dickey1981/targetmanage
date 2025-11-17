// config/env.js
// 环境配置文件

const ENV = {
  // 开发环境（开发者工具中使用）
  development: {
    baseUrl: 'http://localhost:8000',  // 本地开发环境
    apiVersion: 'v1',
    debug: true
  },
  
  // 生产环境（备案完成后使用HTTPS域名）
  production: {
    baseUrl: 'https://targetmanage.cn',
    apiVersion: 'v1',
    debug: false
  }
}

// 获取当前环境
function getCurrentEnv() {
  try {
    // 在微信开发者工具中
    if (wx.getSystemInfoSync().platform === 'devtools') {
      return 'development'
    }
    
    // 在真机环境中
    return 'production'
  } catch (error) {
    // 如果获取系统信息失败，默认使用开发环境
    console.log('获取环境信息失败，使用开发环境:', error)
    return 'development'
  }
}

// 获取当前环境配置
function getConfig() {
  const currentEnv = getCurrentEnv()
  return ENV[currentEnv]
}

// 获取API基础URL
function getBaseUrl() {
  const config = getConfig()
  return config.baseUrl
}

module.exports = {
  ENV,
  getCurrentEnv,
  getConfig,
  getBaseUrl
}
