# 组件设计规范

## 🧩 组件系统概述

智能目标管理小程序的组件系统基于原子设计理念，从基础原子组件到复杂的模板组件，确保界面的一致性和可复用性。

## 📋 组件层次结构

### 组件分级
```
1. 原子组件 (Atoms)
   - 按钮、输入框、图标等基础元素

2. 分子组件 (Molecules)  
   - 搜索框、导航项等组合元素

3. 有机体组件 (Organisms)
   - 导航栏、卡片列表等复杂组件

4. 模板组件 (Templates)
   - 页面布局、区块模板等
```

## 🎤 语音交互组件

### 主语音按钮 (Primary Voice Button)
```scss
.voice-button {
  // 基础样式
  width: 320rpx;
  height: 320rpx;
  border-radius: 50%;
  border: none;
  position: relative;
  
  // 布局
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  
  // 默认状态
  background: $primary-gradient;
  box-shadow: $shadow-button;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  // 激活状态
  &.active {
    background: $success-gradient;
    transform: scale(1.1);
    box-shadow: 0 25rpx 50rpx rgba(17, 153, 142, 0.4);
    
    .voice-icon {
      animation: pulse 1.5s infinite;
    }
  }
  
  // 禁用状态
  &.disabled {
    background: $border-medium;
    box-shadow: none;
    cursor: not-allowed;
    
    .voice-text, .voice-hint {
      color: $text-disabled;
    }
  }
  
  // 错误状态
  &.error {
    background: $error-color;
    animation: shake 0.5s ease-in-out;
  }
}

// 内部元素
.voice-icon {
  width: 80rpx;
  height: 80rpx;
  margin-bottom: 20rpx;
}

.voice-text {
  color: white;
  font-size: $font-size-md;
  font-weight: $font-weight-medium;
  margin-bottom: 10rpx;
}

.voice-hint {
  color: rgba(255, 255, 255, 0.8);
  font-size: $font-size-xs;
  text-align: center;
  line-height: 1.4;
  max-width: 240rpx;
}

// 动画定义
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10rpx); }
  75% { transform: translateX(10rpx); }
}
```

### 语音结果显示组件
```scss
.voice-result {
  background: white;
  border-radius: $border-radius-lg;
  padding: $padding-component;
  margin-top: 40rpx;
  box-shadow: $shadow-card;
  animation: slideUp 0.3s ease-out;
  
  .result-text {
    font-size: $font-size-md;
    color: $text-primary;
    line-height: $line-height-loose;
    margin-bottom: 30rpx;
    min-height: 60rpx;
  }
  
  .result-actions {
    display: flex;
    gap: 20rpx;
    
    .confirm-btn {
      flex: 1;
      @include button-style($success-color);
    }
    
    .retry-btn {
      flex: 1;
      @include button-style($border-medium, $text-primary);
    }
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

## 📊 目标卡片组件

### 标准目标卡片
```scss
.goal-card {
  @include card-style;
  margin-bottom: $margin-component;
  transition: all 0.2s ease;
  
  // 交互状态
  &:active {
    transform: scale(0.98);
    box-shadow: $shadow-card-hover;
  }
  
  // 完成状态
  &.completed {
    opacity: 0.7;
    
    .goal-title {
      text-decoration: line-through;
      color: $text-secondary;
    }
    
    .progress-bar .fill {
      background: $success-gradient;
    }
  }
  
  // 延期状态
  &.overdue {
    border-left: 4rpx solid $error-color;
    
    .goal-deadline {
      color: $error-color;
      font-weight: $font-weight-medium;
    }
  }
  
  // 即将到期状态
  &.deadline-warning {
    border-left: 4rpx solid $warning-color;
    
    .goal-deadline {
      color: $warning-color;
      font-weight: $font-weight-medium;
    }
  }
}

// 卡片内部结构
.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
  gap: 20rpx;
}

.goal-title {
  font-size: $font-size-md;
  font-weight: $font-weight-medium;
  color: $text-primary;
  line-height: $line-height-tight;
  flex: 1;
  @include text-ellipsis(2);
}

.goal-progress-text {
  font-size: $font-size-sm;
  font-weight: $font-weight-bold;
  color: $success-color;
  white-space: nowrap;
}

.goal-progress-bar {
  @include progress-bar-style;
  margin-bottom: 20rpx;
}

.goal-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: $font-size-xs;
  color: $text-secondary;
}

.goal-category {
  background: $bg-secondary;
  color: $text-secondary;
  padding: 8rpx 16rpx;
  border-radius: $border-radius-sm;
  font-size: $font-size-xxs;
  font-weight: $font-weight-medium;
}

.goal-deadline {
  font-weight: $font-weight-medium;
}
```

### 目标卡片变体
```scss
// 紧凑型卡片
.goal-card-compact {
  @include card-style;
  padding: 20rpx;
  
  .goal-header {
    margin-bottom: 10rpx;
  }
  
  .goal-title {
    font-size: $font-size-sm;
    @include text-ellipsis(1);
  }
  
  .goal-progress-bar {
    height: 6rpx;
    margin-bottom: 10rpx;
  }
}

// 大型展示卡片
.goal-card-large {
  @include card-style;
  padding: 40rpx;
  
  .goal-title {
    font-size: $font-size-lg;
    margin-bottom: 30rpx;
  }
  
  .goal-progress-bar {
    height: 12rpx;
    margin-bottom: 30rpx;
  }
  
  .goal-stats {
    display: flex;
    justify-content: space-around;
    margin-top: 30rpx;
    
    .stat-item {
      text-align: center;
      
      .stat-value {
        font-size: $font-size-lg;
        font-weight: $font-weight-bold;
        color: $primary-color;
      }
      
      .stat-label {
        font-size: $font-size-xs;
        color: $text-secondary;
        margin-top: 10rpx;
      }
    }
  }
}
```

## 🎯 快速操作组件

### 操作按钮组
```scss
.quick-actions {
  display: flex;
  gap: 20rpx;
  padding: 0 20rpx;
}

.quick-action-item {
  flex: 1;
  @include card-style;
  padding: 30rpx 20rpx;
  text-align: center;
  transition: all 0.2s ease;
  min-height: 120rpx;
  
  &:active {
    transform: scale(0.95);
    box-shadow: $shadow-card-hover;
  }
  
  .action-icon {
    width: 60rpx;
    height: 60rpx;
    margin: 0 auto 15rpx;
    display: block;
  }
  
  .action-text {
    font-size: $font-size-xs;
    color: $text-primary;
    font-weight: $font-weight-medium;
    line-height: $line-height-tight;
  }
  
  .action-description {
    font-size: $font-size-xxs;
    color: $text-secondary;
    margin-top: 8rpx;
    line-height: $line-height-normal;
  }
}
```

### 浮动操作按钮 (FAB)
```scss
.fab {
  position: fixed;
  right: 30rpx;
  bottom: 120rpx;
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: $primary-gradient;
  box-shadow: $shadow-button;
  border: none;
  z-index: 100;
  
  display: flex;
  justify-content: center;
  align-items: center;
  
  transition: all 0.3s ease;
  
  &:active {
    transform: scale(0.9);
  }
  
  .fab-icon {
    width: 48rpx;
    height: 48rpx;
    filter: brightness(0) invert(1); // 白色图标
  }
  
  // 扩展状态
  &.expanded {
    border-radius: $border-radius-lg;
    width: 200rpx;
    height: 80rpx;
    
    .fab-text {
      color: white;
      font-size: $font-size-sm;
      font-weight: $font-weight-medium;
      margin-left: 10rpx;
    }
  }
}
```

## 📅 时间线组件

### 时间线容器
```scss
.timeline {
  position: relative;
  padding-left: 60rpx;
  
  // 时间线主线
  &::before {
    content: '';
    position: absolute;
    left: 30rpx;
    top: 0;
    bottom: 0;
    width: 2rpx;
    background: $border-medium;
  }
}

.timeline-item {
  position: relative;
  margin-bottom: 40rpx;
  
  // 时间节点
  &::before {
    content: '';
    position: absolute;
    left: -45rpx;
    top: 10rpx;
    width: 20rpx;
    height: 20rpx;
    border-radius: 50%;
    background: $bg-primary;
    border: 3rpx solid $border-medium;
    z-index: 1;
  }
  
  // 不同类型的节点样式
  &.progress {
    &::before {
      border-color: $success-color;
      background: $success-color;
    }
  }
  
  &.milestone {
    &::before {
      border-color: $primary-color;
      background: $primary-color;
      width: 24rpx;
      height: 24rpx;
      left: -47rpx;
    }
  }
  
  &.difficulty {
    &::before {
      border-color: $warning-color;
      background: $warning-color;
    }
  }
  
  &.reflection {
    &::before {
      border-color: $info-color;
      background: $info-color;
    }
  }
}

.timeline-content {
  @include card-style;
  padding: 25rpx;
  
  .timeline-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15rpx;
    
    .timeline-type {
      font-size: $font-size-xs;
      color: $text-secondary;
      background: $bg-secondary;
      padding: 6rpx 12rpx;
      border-radius: $border-radius-sm;
    }
    
    .timeline-date {
      font-size: $font-size-xs;
      color: $text-placeholder;
    }
  }
  
  .timeline-text {
    font-size: $font-size-sm;
    color: $text-primary;
    line-height: $line-height-loose;
  }
  
  .timeline-data {
    margin-top: 15rpx;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    color: $success-color;
  }
}
```

## 📋 表单组件

### 输入框组件
```scss
.form-group {
  margin-bottom: 30rpx;
}

.form-label {
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
  color: $text-primary;
  margin-bottom: 15rpx;
  display: block;
  
  .required {
    color: $error-color;
    margin-left: 5rpx;
  }
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 20rpx;
  border: 2rpx solid $border-medium;
  border-radius: $border-radius-sm;
  font-size: $font-size-sm;
  color: $text-primary;
  background: $bg-primary;
  transition: all 0.2s ease;
  
  &:focus {
    border-color: $primary-color;
    box-shadow: 0 0 0 4rpx rgba(102, 126, 234, 0.1);
    outline: none;
  }
  
  &.error {
    border-color: $error-color;
    
    &:focus {
      box-shadow: 0 0 0 4rpx rgba(255, 59, 48, 0.1);
    }
  }
  
  &::placeholder {
    color: $text-placeholder;
  }
  
  &:disabled {
    background: $bg-secondary;
    color: $text-disabled;
    cursor: not-allowed;
  }
}

.form-textarea {
  @extend .form-input;
  height: 160rpx;
  padding: 20rpx;
  resize: none;
  line-height: $line-height-loose;
}

.form-help {
  font-size: $font-size-xs;
  color: $text-secondary;
  margin-top: 10rpx;
  line-height: $line-height-normal;
  
  &.error {
    color: $error-color;
  }
}
```

### 按钮组件
```scss
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx 40rpx;
  border-radius: $border-radius-xl;
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 88rpx;
  
  &:active {
    transform: scale(0.98);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    
    &:active {
      transform: none;
    }
  }
}

// 按钮变体
.btn-primary {
  @include button-style($primary-color);
  box-shadow: $shadow-button;
}

.btn-success {
  @include button-style($success-color);
  box-shadow: $shadow-button-success;
}

.btn-secondary {
  @include button-style($bg-secondary, $text-primary);
  border: 2rpx solid $border-medium;
}

.btn-outline {
  background: transparent;
  color: $primary-color;
  border: 2rpx solid $primary-color;
  
  &:active {
    background: $primary-color;
    color: white;
  }
}

.btn-text {
  background: transparent;
  color: $primary-color;
  padding: 10rpx 20rpx;
  min-height: auto;
}

// 按钮尺寸
.btn-large {
  padding: 25rpx 50rpx;
  font-size: $font-size-md;
  min-height: 100rpx;
}

.btn-small {
  padding: 15rpx 30rpx;
  font-size: $font-size-xs;
  min-height: 60rpx;
}

.btn-block {
  width: 100%;
}
```

## 📱 导航组件

### 底部导航栏
```scss
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 98rpx;
  background: $bg-primary;
  border-top: 1rpx solid $border-light;
  display: flex;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 1000;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10rpx;
  
  .tab-icon {
    width: 44rpx;
    height: 44rpx;
    margin-bottom: 6rpx;
    opacity: 0.6;
    transition: all 0.2s ease;
  }
  
  .tab-text {
    font-size: $font-size-xxs;
    color: $text-secondary;
    transition: all 0.2s ease;
  }
  
  &.active {
    .tab-icon {
      opacity: 1;
      transform: scale(1.1);
    }
    
    .tab-text {
      color: $primary-color;
      font-weight: $font-weight-medium;
    }
  }
}
```

## 💬 反馈组件

### Toast 提示
```scss
.toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 30rpx 40rpx;
  border-radius: $border-radius-lg;
  font-size: $font-size-sm;
  text-align: center;
  z-index: 2000;
  animation: fadeInOut 3s ease-in-out;
  
  &.success {
    background: $success-color;
  }
  
  &.error {
    background: $error-color;
  }
  
  &.warning {
    background: $warning-color;
  }
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  10%, 90% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}
```

### 加载状态
```scss
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx;
  
  .loading-spinner {
    width: 60rpx;
    height: 60rpx;
    border: 4rpx solid $border-light;
    border-top: 4rpx solid $primary-color;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20rpx;
  }
  
  .loading-text {
    font-size: $font-size-sm;
    color: $text-secondary;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 骨架屏
.skeleton-item {
  @include skeleton-animation;
  border-radius: $border-radius-sm;
  margin-bottom: 10rpx;
  
  &.skeleton-title {
    height: 40rpx;
    width: 60%;
  }
  
  &.skeleton-text {
    height: 28rpx;
    width: 100%;
  }
  
  &.skeleton-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
  }
}
```

## ✅ 组件使用检查清单

### 设计一致性检查
- [ ] 是否使用了预定义的组件样式？
- [ ] 交互状态是否完整（默认、悬停、激活、禁用）？
- [ ] 颜色、字体、间距是否符合规范？
- [ ] 是否考虑了不同尺寸的适配？

### 可访问性检查
- [ ] 点击区域是否≥88rpx？
- [ ] 是否有清晰的状态反馈？
- [ ] 错误状态是否有友好提示？
- [ ] 是否支持键盘导航？

### 性能检查
- [ ] 动画是否流畅且不过度？
- [ ] 是否避免了不必要的重绘？
- [ ] 组件是否可复用？

---

**组件规范更新记录**:
- v1.0 (2025-01): 建立基础组件库
- 计划更新: 根据用户测试完善交互细节
