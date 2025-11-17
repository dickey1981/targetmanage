# 文字记录目标选择调试指南

## 🐛 问题描述
文字记录弹窗中无法选择目标。

## 🔍 调试步骤

### 第一步：检查目标列表是否加载

1. 打开微信开发者工具控制台
2. 进入"过程记录"页面
3. 点击"文字记录"按钮
4. 查看控制台输出：

**期望看到的日志：**
```
🎯 开始加载目标列表...
✅ 加载目标成功: X个      (X为目标数量)
✅ 目标加载成功
目标列表: [Array of goals]
目标数量: X
```

**如果看到错误：**
```
❌ 加载目标失败: 未登录
```
→ **解决方案**：需要先登录

```
❌ 加载目标失败: [Error]
```
→ **解决方案**：检查网络连接和后端服务

---

### 第二步：检查弹窗是否显示目标列表

弹窗打开后，查看：

1. **是否显示"选择关联目标（可选）"标题**
2. **是否显示目标列表**
3. **是否显示"不关联目标"选项**

**如果没有显示目标列表：**
- 检查控制台的"目标数量"是否为 0
- 如果为 0，说明账号下没有活跃目标，需要先创建目标

---

### 第三步：测试点击事件

点击目标列表中的任一目标，查看控制台：

**期望看到的日志：**
```
📌 selectGoal 被调用
事件对象: {Object}
dataset: {goalId: "xxx-xxx-xxx"}
提取的 goalId: xxx-xxx-xxx
✅ 选择目标完成，当前 selectedGoalId: xxx-xxx-xxx
```

**如果没有日志输出：**
→ 说明点击事件没有触发，可能是：
1. UI 层级问题（被其他元素遮挡）
2. 事件绑定错误

**如果日志中 goalId 是 undefined：**
→ `data-goal-id` 属性没有正确绑定

---

### 第四步：检查选中状态

选中目标后，该目标应该高亮显示（背景变为浅蓝色）。

**检查方式：**
1. 点击一个目标
2. 观察该目标是否有蓝色背景
3. 点击另一个目标，前一个目标的选中状态应该消失

**如果没有高亮效果：**
→ CSS 样式问题，检查 `.goal-item.selected` 样式

---

### 第五步：测试提交功能

1. 选择一个目标
2. 输入文字内容
3. 点击"提交记录"
4. 查看控制台，确认提交的数据中包含 `goal_id`

**期望的提交数据：**
```javascript
{
  content: "你输入的文字",
  record_type: "process",
  source: "manual",
  goal_id: "xxx-xxx-xxx",  // ← 应该有这个字段
  user_id: "..."
}
```

---

## 🔧 可能的问题和解决方案

### 问题1：目标列表为空

**原因**：账号下没有活跃目标

**解决方案**：
1. 切换到"目标"页面
2. 创建至少一个目标
3. 回到"过程记录"页面重试

---

### 问题2：点击目标没有反应

**原因A**：事件绑定错误

**检查 WXML**：
```xml
<view 
  wx:for="{{availableGoals}}" 
  wx:key="id"
  class="goal-item {{selectedGoalId === item.id ? 'selected' : ''}}"
  bindtap="selectGoal"           <!-- 确保有这个 -->
  data-goal-id="{{item.id}}"     <!-- 确保有这个 -->
>
```

**原因B**：CSS 层级问题

**检查样式**：
```css
.goal-item {
  z-index: 1;
  pointer-events: auto;  /* 确保可以点击 */
}
```

---

### 问题3：选中状态不显示

**原因**：CSS 样式没有生效

**检查 WXSS**：
```css
.goal-item.selected {
  background: #e3f2fd;           /* 浅蓝色背景 */
  border-color: #00B4D8;         /* 蓝色边框 */
}
```

**调试方式**：
1. 在开发者工具中选择"Wxml"面板
2. 找到被选中的 `goal-item`
3. 检查是否有 `selected` 类名
4. 检查该元素的计算样式

---

### 问题4：提交时目标ID丢失

**原因**：`this.data.selectedGoalId` 没有正确传递

**检查 submitTextRecord 方法**：
```javascript
submitTextRecord() {
  const text = this.data.textInput.trim()
  if (!text) {
    wx.showToast({ title: '请输入记录内容', icon: 'none' })
    return
  }

  console.log('📤 准备提交')
  console.log('内容:', text)
  console.log('选中的目标ID:', this.data.selectedGoalId)  // ← 添加这个日志

  this.submitRecord('text', { 
    content: text,
    goalId: this.data.selectedGoalId   // ← 确保传递了这个
  })
}
```

---

## 📝 完整的测试流程

```
1. 登录系统
   ↓
2. 创建至少一个活跃目标
   ↓
3. 进入"过程记录"页面
   ↓
4. 点击"文字记录"
   ↓
5. 等待弹窗出现
   ↓
6. 观察是否显示目标列表
   ↓
7. 点击任一目标
   ↓
8. 确认该目标被高亮显示
   ↓
9. 输入文字内容
   ↓
10. 点击"提交记录"
    ↓
11. 查看提交是否成功
    ↓
12. 检查"最近记录"列表是否更新
```

---

## 🎯 期望的完整日志输出

```
// 点击"文字记录"
🎯 开始加载目标列表...
✅ 加载目标成功: 3个
✅ 目标加载成功
目标列表: [{id: "xxx", title: "每月跑步100公里", ...}, ...]
目标数量: 3

// 点击某个目标
📌 selectGoal 被调用
事件对象: {type: "tap", timeStamp: 12345, ...}
dataset: {goalId: "abc-123-def-456"}
提取的 goalId: abc-123-def-456
✅ 选择目标完成，当前 selectedGoalId: abc-123-def-456

// 提交记录
📤 准备提交
内容: 今天完成了跑步任务
选中的目标ID: abc-123-def-456
```

---

## 🚀 现在请执行测试

1. **保存所有文件**
2. **重新编译小程序**
3. **按照上面的步骤进行测试**
4. **将控制台的完整日志截图或复制给我**

这样我就能准确定位问题所在！

