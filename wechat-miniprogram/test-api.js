// API测试脚本
// 用于测试后端API的可用性和认证

const testAPI = {
  // 测试健康检查
  testHealth() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: 'http://localhost:8000/health',
        method: 'GET',
        success: (res) => {
          console.log('✅ 健康检查成功:', res.data)
          resolve(res.data)
        },
        fail: (error) => {
          console.error('❌ 健康检查失败:', error)
          reject(error)
        }
      })
    })
  },

  // 测试认证
  testAuth(token) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: 'http://localhost:8000/api/auth/validate',
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          console.log('✅ 认证验证成功:', res.data)
          resolve(res.data)
        },
        fail: (error) => {
          console.error('❌ 认证验证失败:', error)
          reject(error)
        }
      })
    })
  },

  // 测试过程记录API
  testProcessRecords(token, goalId) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: 'http://localhost:8000/api/process-records/',
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          goal_id: goalId,
          page: 1,
          page_size: 3
        },
        success: (res) => {
          console.log('✅ 过程记录API成功:', res.data)
          resolve(res.data)
        },
        fail: (error) => {
          console.error('❌ 过程记录API失败:', error)
          reject(error)
        }
      })
    })
  },

  // 运行所有测试
  async runAllTests() {
    const app = getApp()
    const token = app.globalData.token
    const goalId = '2a11ae65-9896-4a35-a035-ce05f192d4f4'

    console.log('🧪 开始API测试...')
    console.log('Token:', token ? '已设置' : '未设置')
    console.log('目标ID:', goalId)

    try {
      // 1. 健康检查
      console.log('1️⃣ 测试健康检查...')
      await this.testHealth()

      // 2. 认证验证
      if (token) {
        console.log('2️⃣ 测试认证验证...')
        await this.testAuth(token)
      } else {
        console.log('⚠️ 跳过认证测试，Token未设置')
      }

      // 3. 过程记录API
      if (token && goalId) {
        console.log('3️⃣ 测试过程记录API...')
        await this.testProcessRecords(token, goalId)
      } else {
        console.log('⚠️ 跳过过程记录测试，Token或目标ID未设置')
      }

      console.log('✅ 所有测试完成')
    } catch (error) {
      console.error('❌ 测试过程中出现错误:', error)
    }
  }
}

// 导出测试对象
module.exports = testAPI
