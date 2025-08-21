# 字体规范

## 📝 字体系统概述

智能目标管理小程序的字体系统设计注重可读性、层次感和移动端适配，确保在小屏幕上提供良好的阅读体验。

## 📏 字体大小系统

### 字体尺寸层次 (rpx单位)
```scss
// 超大标题 - 用于页面主标题、重要数值
$font-size-xl: 40rpx;        // 约等于 20px

// 大标题 - 用于卡片标题、区块标题  
$font-size-lg: 36rpx;        // 约等于 18px

// 中标题 - 用于次级标题、重要信息
$font-size-md: 32rpx;        // 约等于 16px

// 正文标准 - 用于正文内容、按钮文字
$font-size-sm: 28rpx;        // 约等于 14px

// 辅助信息 - 用于说明文字、标签
$font-size-xs: 24rpx;        // 约等于 12px

// 说明文字 - 用于极小的提示信息
$font-size-xxs: 20rpx;       // 约等于 10px
```

### 使用场景映射
```scss
// 页面标题
.page-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
}

// 卡片标题
.card-title {
  font-size: $font-size-lg;
  font-weight: $font-weight-medium;
}

// 目标标题
.goal-title {
  font-size: $font-size-md;
  font-weight: $font-weight-medium;
}

// 正文内容
.body-text {
  font-size: $font-size-sm;
  font-weight: $font-weight-normal;
}

// 辅助信息
.meta-text {
  font-size: $font-size-xs;
  font-weight: $font-weight-normal;
}

// 提示文字
.hint-text {
  font-size: $font-size-xxs;
  font-weight: $font-weight-normal;
}
```

## ⚖️ 字体粗细系统

### 字重层次定义
```scss
$font-weight-bold: 600;      // 粗体 - 页面标题、重要信息
$font-weight-medium: 500;    // 中粗 - 卡片标题、按钮文字
$font-weight-normal: 400;    // 正常 - 正文内容、说明文字

// 字重使用原则
// Bold (600): 吸引注意力，建立视觉层次
// Medium (500): 重要但不突兀，平衡感强
// Normal (400): 舒适阅读，减少视觉疲劳
```

### 字重与字号搭配
```scss
// 推荐搭配组合
.title-primary {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;    // 大字号 + 粗体
}

.title-secondary {
  font-size: $font-size-lg;
  font-weight: $font-weight-medium;  // 中字号 + 中粗
}

.body-content {
  font-size: $font-size-sm;
  font-weight: $font-weight-normal;  // 小字号 + 正常
}

// 避免的搭配
.avoid-thin-small {
  font-size: $font-size-xs;
  font-weight: 300;                  // ❌ 小字号 + 细体，难以阅读
}
```

## 📐 行高系统

### 行高比例定义
```scss
$line-height-tight: 1.2;     // 紧凑行高 - 标题、数值显示
$line-height-normal: 1.4;    // 正常行高 - 正文、按钮
$line-height-loose: 1.6;     // 宽松行高 - 长段落、说明文字

// 计算示例
// font-size: 28rpx, line-height: 1.4 → 实际行高: 39.2rpx
// font-size: 32rpx, line-height: 1.2 → 实际行高: 38.4rpx
```

### 行高使用规则
```scss
// 标题类 - 使用紧凑行高
.title {
  line-height: $line-height-tight;
  // 减少标题占用空间，增强视觉冲击力
}

// 正文类 - 使用正常行高
.body {
  line-height: $line-height-normal;
  // 平衡阅读舒适度和空间利用率
}

// 说明类 - 使用宽松行高
.description {
  line-height: $line-height-loose;
  // 提高长文本的阅读体验
}
```

## 🎯 移动端适配规范

### 最小字体要求
```scss
// 可读性要求
$min-font-size: 24rpx;       // 最小字体，确保可读性
$min-touch-target: 88rpx;    // 最小点击区域

// 实施检查
@mixin font-size-check($size) {
  @if $size < $min-font-size {
    @warn "字体大小 #{$size} 小于最小要求 #{$min-font-size}";
  }
  font-size: $size;
}
```

### 屏幕尺寸适配
```scss
// 小屏设备适配 (iPhone SE等)
@media screen and (max-width: 375px) {
  .responsive-text {
    font-size: $font-size-xs;   // 适当减小字体
    line-height: 1.3;           // 调整行高
  }
}

// 大屏设备适配 (iPad等)
@media screen and (min-width: 768px) {
  .responsive-text {
    font-size: $font-size-md;   // 适当增大字体
    line-height: 1.5;           // 增加行高
  }
}
```

## 🎨 字体与色彩搭配

### 文字颜色层次
```scss
// 主要信息 - 深色字体
.text-primary {
  color: $text-primary;         // #333333
  font-weight: $font-weight-medium;
}

// 次要信息 - 中等深度
.text-secondary {
  color: $text-secondary;       // #666666
  font-weight: $font-weight-normal;
}

// 辅助信息 - 浅色字体
.text-tertiary {
  color: $text-placeholder;     // #999999
  font-weight: $font-weight-normal;
}

// 禁用状态 - 最浅色
.text-disabled {
  color: $text-disabled;        // #cccccc
  font-weight: $font-weight-normal;
}
```

### 特殊用途字体
```scss
// 数值显示 - 突出重要数据
.number-display {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: $primary-color;
  font-feature-settings: "tnum"; // 等宽数字
}

// 成功状态 - 积极信息
.success-text {
  color: $success-color;
  font-weight: $font-weight-medium;
}

// 警告信息 - 引起注意
.warning-text {
  color: $warning-color;
  font-weight: $font-weight-medium;
}

// 错误信息 - 强调问题
.error-text {
  color: $error-color;
  font-weight: $font-weight-medium;
}
```

## 📱 微信小程序字体特殊考虑

### 系统字体设置
```scss
// 微信小程序推荐字体栈
body {
  font-family: 
    -apple-system,              // iOS系统字体
    BlinkMacSystemFont,         // macOS系统字体
    "Helvetica Neue",           // iOS备选字体
    Helvetica,                  // 通用无衬线字体
    "PingFang SC",              // 中文字体 (简体)
    "Hiragino Sans GB",         // 中文字体备选
    "Microsoft YaHei",          // Windows中文字体
    Arial,                      // 通用字体
    sans-serif;                 // 系统默认
}
```

### 文字渲染优化
```scss
// 文字渲染优化
.text-optimize {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

// 禁用文字选择 (按钮等元素)
.no-select {
  -webkit-user-select: none;
  user-select: none;
}
```

## 🎯 组件级字体规范

### 语音按钮文字
```scss
.voice-button-text {
  font-size: $font-size-md;     // 32rpx
  font-weight: $font-weight-medium;
  line-height: $line-height-tight;
  color: #ffffff;
  text-align: center;
}

.voice-hint-text {
  font-size: $font-size-xs;     // 24rpx
  font-weight: $font-weight-normal;
  line-height: $line-height-normal;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}
```

### 目标卡片文字
```scss
.goal-card {
  .title {
    font-size: $font-size-md;   // 32rpx
    font-weight: $font-weight-medium;
    line-height: $line-height-tight;
    color: $text-primary;
    @include text-ellipsis(1);  // 单行省略
  }
  
  .progress {
    font-size: $font-size-sm;   // 28rpx
    font-weight: $font-weight-bold;
    color: $success-color;
  }
  
  .meta {
    font-size: $font-size-xs;   // 24rpx
    font-weight: $font-weight-normal;
    color: $text-secondary;
  }
}
```

### 表单文字
```scss
.form-label {
  font-size: $font-size-sm;     // 28rpx
  font-weight: $font-weight-medium;
  color: $text-primary;
  margin-bottom: 10rpx;
}

.form-input {
  font-size: $font-size-sm;     // 28rpx
  font-weight: $font-weight-normal;
  color: $text-primary;
  
  &::placeholder {
    color: $text-placeholder;
    font-weight: $font-weight-normal;
  }
}

.form-help {
  font-size: $font-size-xs;     // 24rpx
  font-weight: $font-weight-normal;
  color: $text-secondary;
  line-height: $line-height-loose;
}
```

## ✅ 字体使用检查清单

### 设计检查
- [ ] 字体大小是否在预定义范围内？
- [ ] 最小字体是否≥24rpx？
- [ ] 字重搭配是否合理？
- [ ] 行高是否适合阅读？
- [ ] 文字颜色对比度是否足够？

### 技术检查
- [ ] 是否使用了字体变量？
- [ ] 是否考虑了不同屏幕适配？
- [ ] 长文本是否有省略处理？
- [ ] 是否优化了文字渲染？

### 用户体验检查
- [ ] 在小屏设备上是否清晰可读？
- [ ] 信息层次是否清晰？
- [ ] 阅读负担是否最小化？

## 🔧 实用工具类

### 文字工具类
```scss
// 文字对齐
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

// 文字省略
.text-ellipsis-1 { @include text-ellipsis(1); }
.text-ellipsis-2 { @include text-ellipsis(2); }
.text-ellipsis-3 { @include text-ellipsis(3); }

// 文字换行
.text-break {
  word-wrap: break-word;
  word-break: break-all;
}

.text-nowrap {
  white-space: nowrap;
}

// 文字变换
.text-uppercase { text-transform: uppercase; }
.text-lowercase { text-transform: lowercase; }
.text-capitalize { text-transform: capitalize; }
```

---

**字体规范更新记录**:
- v1.0 (2025-01): 建立基础字体系统
- 计划更新: 根据可读性测试优化字体搭配
