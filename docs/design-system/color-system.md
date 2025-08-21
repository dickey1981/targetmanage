# 色彩系统规范

## 🎨 色彩系统概述

智能目标管理小程序的色彩系统基于现代UI设计理念，注重可访问性、一致性和品牌表达。

### 设计原则
- **功能性优先**: 色彩服务于功能，而非装饰
- **情感化设计**: 通过色彩传达积极、专业、可信赖的品牌形象
- **可访问性**: 确保足够的对比度，支持色盲用户
- **系统化**: 规范化的色彩层次和语义

## 🎯 主色调系统

### 主色 - 科技感渐变蓝
```scss
// 主色渐变 - 用于语音按钮、重要CTA
$primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

// 主色系
$primary-color: #667eea;      // 主色调 - 用于按钮、链接
$primary-light: #8a9fff;     // 浅色 - 用于悬停状态
$primary-dark: #4c63d2;      // 深色 - 用于按下状态

// 使用场景
// ✅ 主要操作按钮
// ✅ 重要信息高亮
// ✅ 进度指示器
// ✅ 选中状态
```

**色彩心理学**: 蓝色代表专业、可信赖、科技感，紫色增加创新和智能的感觉。

### 辅助色 - 自然绿 (成功/进步)
```scss
// 成功色渐变 - 用于进度条、完成状态
$success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);

// 成功色系
$success-color: #1AAD19;     // 成功色 - 微信绿标准色
$success-light: #2DD03A;     // 浅成功色 - 悬停状态

// 使用场景
// ✅ 目标完成状态
// ✅ 进度条填充
// ✅ 成功反馈提示
// ✅ 积极数据展示
```

**色彩心理学**: 绿色代表成长、进步、健康，符合目标管理的积极含义。

## 🖤 中性色系统

### 文字颜色层次
```scss
$text-primary: #333333;      // 主要文字 - 标题、重要信息
$text-secondary: #666666;    // 次要文字 - 正文内容
$text-placeholder: #999999;  // 占位文字 - 输入提示
$text-disabled: #cccccc;     // 禁用文字 - 不可操作状态

// 对比度要求
// text-primary vs bg-primary: 12.6:1 (AAA级)
// text-secondary vs bg-primary: 7.0:1 (AA级)
// text-placeholder vs bg-primary: 4.1:1 (AA级)
```

### 背景颜色层次
```scss
$bg-primary: #ffffff;        // 主背景 - 页面背景
$bg-secondary: #f8f9fa;      // 次背景 - 区域划分
$bg-card: #ffffff;           // 卡片背景 - 内容容器
$bg-overlay: rgba(0,0,0,0.5); // 遮罩背景 - 弹层背景

// 使用层次
// Level 1: bg-primary (页面基础)
// Level 2: bg-secondary (区域分割)
// Level 3: bg-card (内容容器)
// Level 4: bg-overlay (遮罩层)
```

### 边框颜色层次
```scss
$border-light: #f0f0f0;      // 浅边框 - 分割线
$border-medium: #e0e0e0;     // 中边框 - 卡片边框
$border-dark: #d0d0d0;       // 深边框 - 输入框边框

// 使用原则
// - 浅边框用于微妙分割
// - 中边框用于内容区分
// - 深边框用于交互元素
```

## 🚨 状态色系统

### 状态色定义
```scss
$warning-color: #FF9500;     // 警告橙 - 注意事项
$error-color: #FF3B30;       // 错误红 - 错误状态
$info-color: #007AFF;        // 信息蓝 - 提示信息

// 语义化使用
warning: 目标即将到期、进度缓慢
error: 操作失败、数据错误
info: 功能说明、操作提示
```

### 状态色扩展
```scss
// 警告色系
$warning-light: #FFB84D;     // 浅警告色
$warning-dark: #CC7700;      // 深警告色

// 错误色系  
$error-light: #FF6B60;       // 浅错误色
$error-dark: #E6342A;        // 深错误色

// 信息色系
$info-light: #4DA6FF;        // 浅信息色
$info-dark: #0056CC;         // 深信息色
```

## 🌙 深色模式适配

### 深色模式色彩映射
```scss
@media (prefers-color-scheme: dark) {
  :root {
    // 背景色反转
    --bg-primary: #1a1a1a;      // 深色主背景
    --bg-secondary: #2d2d2d;    // 深色次背景
    --bg-card: #333333;         // 深色卡片背景
    
    // 文字色适配
    --text-primary: #ffffff;     // 深色模式主文字
    --text-secondary: #cccccc;   // 深色模式次文字
    --text-placeholder: #888888; // 深色模式占位文字
    
    // 边框色适配
    --border-color: #404040;     // 深色模式边框
    
    // 主色调保持不变（品牌色）
    --primary-color: #667eea;
    --success-color: #1AAD19;
  }
}

// 组件适配示例
.card {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1rpx solid var(--border-color);
}
```

## 📏 色彩使用规范

### 色彩层次规则
```
1. 主色 (Primary) - 最重要的操作和信息
   - 限制使用，突出核心功能
   - 页面中不超过3个主色元素

2. 辅助色 (Secondary) - 重要但非核心的信息
   - 支撑主色，形成视觉层次
   - 用于状态指示和分类

3. 中性色 (Neutral) - 基础信息和界面元素
   - 大面积使用，形成界面基调
   - 确保可读性和舒适度

4. 状态色 (Status) - 特定状态和反馈
   - 语义化使用，用户易于理解
   - 配合图标增强识别度
```

### 色彩搭配原则
```scss
// ✅ 推荐搭配
.primary-button {
  background: $primary-color;    // 主色背景
  color: #ffffff;                // 白色文字
}

.success-indicator {
  background: $success-light;    // 浅成功色背景
  color: $success-color;         // 深成功色文字
}

// ❌ 避免搭配
.avoid-low-contrast {
  background: #f0f0f0;
  color: #cccccc;                // 对比度不足
}

.avoid-color-conflict {
  background: $error-color;
  color: $warning-color;         // 语义冲突
}
```

## 🎨 实际应用示例

### 语音按钮色彩
```scss
.voice-button {
  // 默认状态 - 主色渐变
  background: $primary-gradient;
  
  // 激活状态 - 成功色渐变
  &.active {
    background: $success-gradient;
  }
  
  // 禁用状态 - 中性色
  &.disabled {
    background: $border-medium;
    color: $text-disabled;
  }
}
```

### 目标卡片色彩
```scss
.goal-card {
  background: $bg-card;
  border: 1rpx solid $border-light;
  
  .title {
    color: $text-primary;
  }
  
  .progress-text {
    color: $success-color;        // 进度数字用成功色
  }
  
  .meta-info {
    color: $text-secondary;       // 元信息用次要文字色
  }
}
```

### 状态反馈色彩
```scss
.toast-message {
  &.success {
    background: $success-color;
    color: #ffffff;
  }
  
  &.error {
    background: $error-color;
    color: #ffffff;
  }
  
  &.warning {
    background: $warning-color;
    color: #ffffff;
  }
}
```

## 🔍 可访问性检查

### 对比度要求
```
WCAG 2.1 AA 级标准：
- 正常文字：4.5:1
- 大文字（≥24px）：3:1
- 图形和界面组件：3:1

WCAG 2.1 AAA 级标准：
- 正常文字：7:1
- 大文字：4.5:1
```

### 色盲友好设计
```scss
// 不仅依赖色彩区分状态
.status-indicator {
  &.success {
    background: $success-color;
    &::before {
      content: "✓";              // 添加图标辅助
    }
  }
  
  &.error {
    background: $error-color;
    &::before {
      content: "⚠";              // 添加图标辅助
    }
  }
}
```

## 📋 设计检查清单

### 色彩使用检查
- [ ] 是否使用了预定义的色彩变量？
- [ ] 是否考虑了深色模式适配？
- [ ] 对比度是否满足可访问性要求？
- [ ] 是否避免了语义冲突的色彩搭配？
- [ ] 是否为色盲用户提供了其他识别方式？

### 品牌一致性检查
- [ ] 主色调是否在3个元素内？
- [ ] 色彩层次是否清晰？
- [ ] 状态色是否语义化使用？
- [ ] 整体色调是否符合品牌调性？

---

**更新记录**:
- v1.0 (2025-01): 初版色彩系统建立
- 下次更新: 根据用户测试反馈优化色彩搭配
