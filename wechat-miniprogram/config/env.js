// config/env.js
// 环境配置文件

const ENV = {
  // 开发环境
  development: {
    baseUrl: 'http://localhost:8000',
    apiVersion: 'v1',
    debug: true
  },
  
  // 生产环境
  production: {
    baseUrl: 'https://106.54.212.67:8000',
    apiVersion: 'v1',
    debug: false
  }
}

// 获取当前环境
function getCurrentEnv() {
  // 在微信开发者工具中
  if (wx.getSystemInfoSync().platform === 'devtools') {
    return 'development'
  }
  
  // 在真机环境中
  return 'production'
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
