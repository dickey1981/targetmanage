# 代码开发规范

## 📋 规范概述

本文档定义了智能目标管理小程序的代码开发规范，确保代码质量、可维护性和团队协作效率。

### 规范目标
- **一致性**: 统一的代码风格和结构
- **可读性**: 清晰易懂的代码组织
- **可维护性**: 便于修改和扩展的代码架构
- **性能**: 高效的代码实现

## 📂 文件和目录命名规范

### 目录命名
```
// ✅ 推荐命名 - 小写字母 + 连字符
pages/
├── create-goal/           # 创建目标页面
├── goal-detail/           # 目标详情页面
├── voice-input/           # 语音输入页面
└── timeline/              # 时间线页面

components/
├── voice-button/          # 语音按钮组件
├── goal-card/             # 目标卡片组件
├── progress-bar/          # 进度条组件
└── timeline-item/         # 时间线项目组件

// ❌ 避免的命名
CreateGoal/                # 大写开头
goal_detail/               # 下划线分隔
voiceInput/                # 驼峰命名
```

### 文件命名
```
// 页面文件
pages/index/index.js       # 页面逻辑
pages/index/index.wxml     # 页面模板
pages/index/index.wxss     # 页面样式
pages/index/index.json     # 页面配置

// 组件文件
components/voice-button/index.js    # 组件逻辑
components/voice-button/index.wxml  # 组件模板
components/voice-button/index.wxss  # 组件样式
components/voice-button/index.json  # 组件配置

// 服务文件
services/goalService.js    # 目标相关服务
services/voiceService.js   # 语音相关服务
services/apiService.js     # API 服务
```

### 样式文件命名
```
styles/
├── variables.scss         # 样式变量
├── mixins.scss           # 样式混入
├── common.scss           # 通用样式
├── reset.scss            # 重置样式
└── components.scss       # 组件样式
```

## 🎨 样式编写规范

### SCSS变量使用
```scss
// ✅ 正确 - 使用预定义变量
.button {
  background: $primary-color;
  padding: $spacing-md;
  border-radius: $border-radius-sm;
  font-size: $font-size-sm;
  color: white;
}

// ❌ 错误 - 硬编码数值
.button {
  background: #667eea;
  padding: 30rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: white;
}
```

### 混入 (Mixins) 使用
```scss
// ✅ 正确 - 使用预定义混入
.card {
  @include card-style;
  @include text-ellipsis(2);
  @include fade-in-animation;
}

// ❌ 错误 - 重复编写样式
.card {
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
```

### 样式类命名
```scss
// ✅ BEM命名规范
.goal-card {                    // 块 (Block)
  &__header {                   // 元素 (Element)
    display: flex;
  }
  
  &__title {
    @include text-ellipsis(1);
  }
  
  &--completed {                // 修饰符 (Modifier)
    opacity: 0.7;
  }
  
  &--large {
    padding: 40rpx;
  }
}

// 生成的CSS类名
.goal-card { }
.goal-card__header { }
.goal-card__title { }
.goal-card--completed { }
.goal-card--large { }
```

### 响应式设计
```scss
// ✅ 使用预定义混入
.voice-button {
  @include voice-button-style;
  
  @include small-screen {
    @include size(280rpx);
  }
  
  @include large-screen {
    @include size(360rpx);
  }
}

// 深色模式适配
.card {
  background: var(--bg-card);
  color: var(--text-primary);
  
  @include dark-mode {
    border: 1rpx solid var(--border-color);
  }
}
```

## 🧩 组件开发规范

### 组件目录结构
```
components/voice-button/
├── index.js               # 组件逻辑
├── index.wxml             # 组件模板
├── index.wxss             # 组件样式
├── index.json             # 组件配置
└── README.md              # 组件文档 (可选)
```

### 组件属性定义
```javascript
// ✅ 完整的属性定义
Component({
  properties: {
    // 基础属性
    placeholder: {
      type: String,
      value: '点击说话',
      observer: function(newVal, oldVal) {
        // 属性变化监听
      }
    },
    
    // 枚举属性
    size: {
      type: String,
      value: 'normal',
      validator: function(value) {
        return ['small', 'normal', 'large'].includes(value);
      }
    },
    
    // 布尔属性
    disabled: {
      type: Boolean,
      value: false
    },
    
    // 数字属性
    duration: {
      type: Number,
      value: 3000,
      validator: function(value) {
        return value > 0;
      }
    },
    
    // 对象属性
    config: {
      type: Object,
      value: function() {
        return {
          autoStart: false,
          maxDuration: 60000
        };
      }
    }
  },
  
  // 组件数据
  data: {
    isRecording: false,
    recordingText: ''
  },
  
  // 生命周期
  lifetimes: {
    attached() {
      // 组件初始化
      this.initComponent();
    },
    
    detached() {
      // 组件销毁
      this.cleanup();
    }
  },
  
  // 组件方法
  methods: {
    // 初始化组件
    initComponent() {
      console.log('VoiceButton component initialized');
    },
    
    // 清理资源
    cleanup() {
      if (this.recordingTimer) {
        clearTimeout(this.recordingTimer);
      }
    },
    
    // 开始录音
    startRecording() {
      if (this.data.disabled) return;
      
      this.setData({
        isRecording: true,
        recordingText: '正在录音...'
      });
      
      // 触发事件
      this.triggerEvent('recordstart', {
        timestamp: Date.now()
      });
    }
  }
});
```

### 组件样式规范
```scss
// components/voice-button/index.wxss
@import '../../styles/variables.scss';
@import '../../styles/mixins.scss';

.voice-button {
  @include voice-button-style;
  
  // 组件特有样式
  position: relative;
  
  &--small {
    @include voice-button-style($voice-button-size-small);
  }
  
  &--disabled {
    @include disabled-state;
  }
  
  &__icon {
    @include size($voice-icon-size);
    margin-bottom: $spacing-sm;
  }
  
  &__text {
    color: white;
    font-size: $font-size-md;
    font-weight: $font-weight-medium;
  }
  
  &__hint {
    color: rgba(255, 255, 255, 0.8);
    font-size: $font-size-xs;
    margin-top: $spacing-xs;
    text-align: center;
  }
}
```

## 📱 页面开发规范

### 页面生命周期
```javascript
// pages/index/index.js
Page({
  // 页面数据
  data: {
    userInfo: {},
    goals: [],
    loading: false,
    error: null
  },
  
  // 页面加载
  onLoad(options) {
    console.log('Page loaded with options:', options);
    this.initPage(options);
  },
  
  // 页面显示
  onShow() {
    console.log('Page shown');
    this.refreshData();
  },
  
  // 页面隐藏
  onHide() {
    console.log('Page hidden');
    this.pauseAutoRefresh();
  },
  
  // 页面卸载
  onUnload() {
    console.log('Page unloaded');
    this.cleanup();
  },
  
  // 下拉刷新
  onPullDownRefresh() {
    this.refreshData().finally(() => {
      wx.stopPullDownRefresh();
    });
  },
  
  // 上拉加载
  onReachBottom() {
    this.loadMoreData();
  },
  
  // 页面方法
  initPage(options) {
    this.setData({ loading: true });
    
    Promise.all([
      this.loadUserInfo(),
      this.loadGoals()
    ])
    .then(() => {
      this.setData({ loading: false });
    })
    .catch(error => {
      this.handleError(error);
    });
  },
  
  // 刷新数据
  async refreshData() {
    try {
      const goals = await this.loadGoals();
      this.setData({ goals });
    } catch (error) {
      this.handleError(error);
    }
  },
  
  // 清理资源
  cleanup() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  }
});
```

### 错误处理规范
```javascript
// 统一的错误处理
const errorHandler = {
  // 处理网络错误
  handleNetworkError(error) {
    console.error('Network error:', error);
    wx.showToast({
      title: '网络连接失败',
      icon: 'error',
      duration: 2000
    });
  },
  
  // 处理业务错误
  handleBusinessError(error) {
    console.error('Business error:', error);
    wx.showToast({
      title: error.message || '操作失败',
      icon: 'error',
      duration: 2000
    });
  },
  
  // 处理权限错误
  handleAuthError(error) {
    console.error('Auth error:', error);
    wx.showModal({
      title: '权限不足',
      content: '请重新登录后再试',
      showCancel: false,
      success: () => {
        wx.navigateTo({
          url: '/pages/login/index'
        });
      }
    });
  }
};

// 在页面中使用
async loadData() {
  try {
    wx.showLoading({ title: '加载中...' });
    const result = await api.getData();
    this.setData({ data: result });
  } catch (error) {
    if (error.code === 'NETWORK_ERROR') {
      errorHandler.handleNetworkError(error);
    } else if (error.code === 'AUTH_ERROR') {
      errorHandler.handleAuthError(error);
    } else {
      errorHandler.handleBusinessError(error);
    }
  } finally {
    wx.hideLoading();
  }
}
```

## 🔧 服务层开发规范

### API服务规范
```javascript
// services/apiService.js
class ApiService {
  constructor() {
    this.baseURL = 'https://api.targetmanage.com';
    this.timeout = 10000;
  }
  
  // 通用请求方法
  async request(options) {
    const {
      url,
      method = 'GET',
      data = {},
      header = {}
    } = options;
    
    // 添加认证头
    const token = wx.getStorageSync('token');
    if (token) {
      header.Authorization = `Bearer ${token}`;
    }
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.baseURL}${url}`,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          ...header
        },
        timeout: this.timeout,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${res.data.message}`));
          }
        },
        fail: (error) => {
          reject(new Error('网络请求失败'));
        }
      });
    });
  }
  
  // GET 请求
  get(url, params = {}) {
    const queryString = Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
    
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    
    return this.request({
      url: fullUrl,
      method: 'GET'
    });
  }
  
  // POST 请求
  post(url, data = {}) {
    return this.request({
      url,
      method: 'POST',
      data
    });
  }
  
  // PUT 请求
  put(url, data = {}) {
    return this.request({
      url,
      method: 'PUT',
      data
    });
  }
  
  // DELETE 请求
  delete(url) {
    return this.request({
      url,
      method: 'DELETE'
    });
  }
}

// 导出单例
export default new ApiService();
```

### 业务服务规范
```javascript
// services/goalService.js
import apiService from './apiService.js';

class GoalService {
  // 获取目标列表
  async getGoals(params = {}) {
    try {
      const response = await apiService.get('/api/v1/goals', params);
      return response.data;
    } catch (error) {
      console.error('获取目标列表失败:', error);
      throw error;
    }
  }
  
  // 创建目标
  async createGoal(goalData) {
    // 数据验证
    this.validateGoalData(goalData);
    
    try {
      const response = await apiService.post('/api/v1/goals', goalData);
      return response.data;
    } catch (error) {
      console.error('创建目标失败:', error);
      throw error;
    }
  }
  
  // 更新目标进度
  async updateProgress(goalId, progressData) {
    try {
      const response = await apiService.post(`/api/v1/goals/${goalId}/progress`, progressData);
      return response.data;
    } catch (error) {
      console.error('更新进度失败:', error);
      throw error;
    }
  }
  
  // 数据验证
  validateGoalData(data) {
    const required = ['title', 'targetValue', 'startDate', 'endDate'];
    
    for (const field of required) {
      if (!data[field]) {
        throw new Error(`缺少必填字段: ${field}`);
      }
    }
    
    if (new Date(data.endDate) <= new Date(data.startDate)) {
      throw new Error('结束日期必须晚于开始日期');
    }
    
    if (data.targetValue <= 0) {
      throw new Error('目标值必须大于0');
    }
  }
  
  // 本地缓存相关
  getCachedGoals() {
    try {
      const cached = wx.getStorageSync('cached_goals');
      return cached || [];
    } catch (error) {
      console.error('读取缓存失败:', error);
      return [];
    }
  }
  
  setCachedGoals(goals) {
    try {
      wx.setStorageSync('cached_goals', goals);
    } catch (error) {
      console.error('设置缓存失败:', error);
    }
  }
}

export default new GoalService();
```

## 📊 数据管理规范

### 状态管理
```javascript
// utils/store.js - 简单的状态管理
class Store {
  constructor() {
    this.state = {};
    this.listeners = {};
  }
  
  // 设置状态
  setState(key, value) {
    const oldValue = this.state[key];
    this.state[key] = value;
    
    // 通知监听器
    if (this.listeners[key]) {
      this.listeners[key].forEach(callback => {
        callback(value, oldValue);
      });
    }
  }
  
  // 获取状态
  getState(key) {
    return this.state[key];
  }
  
  // 监听状态变化
  subscribe(key, callback) {
    if (!this.listeners[key]) {
      this.listeners[key] = [];
    }
    this.listeners[key].push(callback);
    
    // 返回取消监听函数
    return () => {
      const index = this.listeners[key].indexOf(callback);
      if (index > -1) {
        this.listeners[key].splice(index, 1);
      }
    };
  }
}

export default new Store();
```

### 本地存储规范
```javascript
// utils/storage.js
class StorageManager {
  // 设置数据
  static set(key, data, expiry = null) {
    try {
      const item = {
        data,
        timestamp: Date.now(),
        expiry
      };
      wx.setStorageSync(key, JSON.stringify(item));
      return true;
    } catch (error) {
      console.error('存储数据失败:', error);
      return false;
    }
  }
  
  // 获取数据
  static get(key, defaultValue = null) {
    try {
      const stored = wx.getStorageSync(key);
      if (!stored) return defaultValue;
      
      const item = JSON.parse(stored);
      
      // 检查是否过期
      if (item.expiry && Date.now() > item.expiry) {
        this.remove(key);
        return defaultValue;
      }
      
      return item.data;
    } catch (error) {
      console.error('读取数据失败:', error);
      return defaultValue;
    }
  }
  
  // 删除数据
  static remove(key) {
    try {
      wx.removeStorageSync(key);
      return true;
    } catch (error) {
      console.error('删除数据失败:', error);
      return false;
    }
  }
  
  // 清空所有数据
  static clear() {
    try {
      wx.clearStorageSync();
      return true;
    } catch (error) {
      console.error('清空数据失败:', error);
      return false;
    }
  }
}

export default StorageManager;
```

## ✅ 代码质量检查清单

### 提交前检查
- [ ] **样式规范**
  - [ ] 是否使用了预定义的样式变量？
  - [ ] 是否使用了样式混入而非重复代码？
  - [ ] CSS类命名是否遵循BEM规范？
  - [ ] 是否考虑了深色模式适配？

- [ ] **组件规范**
  - [ ] 组件属性是否有完整的类型定义？
  - [ ] 是否有适当的默认值和验证？
  - [ ] 生命周期方法是否正确使用？
  - [ ] 是否有必要的错误处理？

- [ ] **性能优化**
  - [ ] 是否避免了不必要的setData调用？
  - [ ] 大列表是否使用了虚拟滚动？
  - [ ] 图片是否启用了懒加载？
  - [ ] 是否及时清理了定时器和监听器？

- [ ] **可访问性**
  - [ ] 点击区域是否≥88rpx？
  - [ ] 是否有清晰的状态反馈？
  - [ ] 色彩对比度是否符合标准？
  - [ ] 是否支持屏幕阅读器？

### 代码审查要点
- [ ] 代码逻辑是否清晰易懂？
- [ ] 是否有适当的注释说明？
- [ ] 错误处理是否完善？
- [ ] 是否遵循了命名规范？
- [ ] 是否有潜在的性能问题？

## 🔧 开发工具配置

### VS Code 推荐插件
```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "stylelint.vscode-stylelint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-json"
  ]
}
```

### Prettier 配置
```json
// .prettierrc
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "quoteProps": "as-needed",
  "trailingComma": "es5",
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

### Stylelint 配置
```json
// .stylelintrc.json
{
  "extends": [
    "stylelint-config-standard-scss",
    "stylelint-config-prettier"
  ],
  "rules": {
    "scss/at-rule-no-unknown": [
      true,
      {
        "ignoreAtRules": ["include", "mixin", "extend"]
      }
    ]
  }
}
```

---

**更新记录**:
- v1.0 (2025-01): 建立基础开发规范
- 计划更新: 根据团队实践优化规范细节
