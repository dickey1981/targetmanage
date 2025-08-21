# 代码规范强制执行指南

## 📋 概述

本文档说明如何在开发过程中自动强制执行我们制定的代码规范，确保代码质量和一致性。

## 🛠️ 配置说明

### 1. 已配置的工具

#### ESLint (JavaScript/TypeScript/Vue)
- **配置文件**: `.eslintrc.js`
- **作用**: 检查代码质量、命名规范、最佳实践
- **自动修复**: 支持大部分问题的自动修复

#### Prettier (代码格式化)
- **配置文件**: `.prettierrc`
- **作用**: 统一代码格式、缩进、引号等
- **自动格式化**: 保存时自动格式化

#### Stylelint (CSS/SCSS)
- **配置文件**: `.stylelintrc.js`
- **作用**: 检查样式规范、变量使用、命名规范
- **自动修复**: 支持大部分样式问题的自动修复

#### Python代码规范
- **配置文件**: `backend/pyproject.toml`
- **工具**: Black (格式化), isort (导入排序), flake8 (代码检查), pylint (代码质量)

### 2. VS Code配置

#### 工作区设置 (`.vscode/settings.json`)
- 保存时自动格式化
- 保存时自动修复ESLint和Stylelint问题
- 设置默认格式化工具
- 配置微信小程序文件关联

#### 扩展推荐 (`.vscode/extensions.json`)
- 自动推荐必要的VS Code扩展
- 支持代码规范检查
- 微信小程序开发支持

### 3. Git Hooks

#### Pre-commit钩子 (`.husky/pre-commit`)
- 提交前自动检查代码规范
- 阻止不符合规范的代码提交
- 确保代码库质量

## 🚀 使用方法

### 1. 安装依赖

```bash
# 安装Node.js依赖
npm install

# 安装Python依赖
cd backend
pip install -r requirements.txt
pip install black isort flake8 pylint
cd ..
```

### 2. 代码规范检查

```bash
# 检查所有代码规范
npm run lint:all

# 检查JavaScript/TypeScript代码
npm run lint:check

# 检查样式代码
npm run stylelint:check

# 检查代码格式
npm run format:check
```

### 3. 自动修复

```bash
# 修复所有可自动修复的问题
npm run fix:all

# 修复JavaScript/TypeScript问题
npm run lint:fix

# 修复样式问题
npm run stylelint:fix

# 格式化代码
npm run format
```

### 4. VS Code开发

1. 安装推荐的扩展
2. 打开项目文件夹
3. 代码会自动格式化和检查
4. 保存时自动修复问题

## 📱 微信小程序特殊配置

### 1. 文件关联
- `.wxml` → HTML
- `.wxss` → CSS
- `.js` → JavaScript

### 2. 规范适配
- 支持`rpx`单位
- 小程序全局变量处理
- 特殊命名规范支持

## 🐍 Python后端规范

### 1. 代码格式化
```bash
cd backend
# 格式化代码
python -m black .
# 排序导入
python -m isort .
# 检查代码质量
python -m flake8 .
python -m pylint .
```

### 2. 规范要点
- 行长度限制: 88字符
- 使用Black格式化
- 导入排序规范
- 代码质量检查

## ⚠️ 注意事项

### 1. 首次使用
- 确保安装了所有必要的VS Code扩展
- 运行`npm install`安装依赖
- 配置Git Hooks: `npm run prepare`

### 2. 团队协作
- 所有开发者都应安装相同的扩展
- 提交前必须通过规范检查
- 定期运行`npm run lint:all`检查

### 3. 自定义规则
- 修改配置文件前与团队讨论
- 保持规则的一致性和合理性
- 记录规则变更原因

## 🔧 故障排除

### 1. 常见问题

#### ESLint不工作
- 检查是否安装了`dbaeumer.vscode-eslint`扩展
- 确认`.eslintrc.js`配置正确
- 检查文件扩展名是否正确

#### Prettier不格式化
- 检查是否安装了`esbenp.prettier-vscode`扩展
- 确认`.prettierrc`配置正确
- 检查VS Code设置中的默认格式化工具

#### Stylelint不工作
- 检查是否安装了`stylelint.vscode-stylelint`扩展
- 确认`.stylelintrc.js`配置正确
- 检查文件扩展名关联

### 2. 性能优化
- 排除不必要的文件夹
- 使用`.gitignore`和`.vscode/settings.json`中的排除规则
- 定期清理缓存文件

## 📚 相关文档

- [UI/UX设计规范](../design-system/ui-ux-guidelines.md)
- [编码标准](../development/coding-standards.md)
- [颜色系统](../design-system/color-system.md)
- [组件设计规范](../design-system/components.md)
