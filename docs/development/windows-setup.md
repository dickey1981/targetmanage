# Windows环境配置指南

## 🪟 系统要求

- Windows 10/11 (64位)
- Python 3.8+
- 推荐: Node.js 18+ (可选)

## 🚀 快速开始

### 方法1：完整配置（推荐）

#### 1. 安装Node.js
1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载LTS版本（推荐18.x或20.x）
3. 运行安装程序，选择默认设置
4. 重启PowerShell或命令提示符

#### 2. 验证安装
```powershell
node --version
npm --version
```

#### 3. 安装项目依赖
```powershell
npm install
```

#### 4. 配置Git Hooks
```powershell
npm run prepare
```

### 方法2：仅Python配置（轻量级）

如果您暂时不想安装Node.js，可以先配置Python后端的代码规范：

#### 1. 安装Python代码规范工具
```powershell
cd backend
pip install black isort flake8 pylint
cd ..
```

#### 2. 使用Python脚本检查代码
```powershell
# 检查代码规范
python scripts/check-python-code.py

# 自动修复问题
python scripts/check-python-code.py --fix

# 或使用批处理文件
scripts\check-code.bat
scripts\check-code.bat --fix
```

## 🛠️ 开发工具配置

### VS Code扩展安装

1. 打开VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 安装以下推荐扩展：
   - **代码规范检查**: ESLint, Prettier, Stylelint
   - **微信小程序**: minapp-vscode
   - **Python开发**: Python, Black Formatter, isort, flake8, pylint
   - **Vue开发**: Volar

### 工作区设置

VS Code会自动读取项目中的 `.vscode/settings.json` 配置：
- 保存时自动格式化
- 保存时自动修复ESLint和Stylelint问题
- 微信小程序文件关联

## 📱 微信小程序开发

### 1. 安装微信开发者工具
1. 访问 [微信开发者工具官网](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 下载并安装最新版本
3. 使用微信扫码登录

### 2. 项目导入
1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择项目中的 `wechat-miniprogram` 目录
4. 填写AppID（测试时可使用测试号）

## 🐍 Python后端开发

### 1. 虚拟环境（推荐）
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r backend/requirements.txt
pip install black isort flake8 pylint

# 退出虚拟环境
deactivate
```

### 2. 代码规范检查
```powershell
cd backend

# 格式化代码
python -m black .
python -m isort .

# 检查代码质量
python -m flake8 .
python -m pylint .
```

## 🔧 常见问题解决

### 1. npm命令未找到
**问题**: `npm : 无法将"npm"项识别为 cmdlet、函数、脚本文件或可运行程序的名称`

**解决方案**:
1. 安装Node.js
2. 重启PowerShell/命令提示符
3. 检查环境变量PATH是否包含Node.js路径

### 2. Python命令未找到
**问题**: `python : 无法将"python"项识别为 cmdlet、函数、脚本文件或可运行程序的名称`

**解决方案**:
1. 安装Python
2. 勾选"Add Python to PATH"选项
3. 重启PowerShell/命令提示符

### 3. 权限问题
**问题**: 运行脚本时出现权限错误

**解决方案**:
1. 以管理员身份运行PowerShell
2. 或修改PowerShell执行策略：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. 编码问题
**问题**: 中文显示乱码

**解决方案**:
1. 确保PowerShell使用UTF-8编码
2. 在脚本开头添加：`chcp 65001`

## 📚 相关文档

- [代码规范强制执行指南](code-standards-enforcement.md)
- [编码标准](coding-standards.md)
- [UI/UX设计规范](../design-system/ui-ux-guidelines.md)

## 💡 开发建议

1. **使用虚拟环境**: 避免Python包冲突
2. **定期更新工具**: 保持开发工具最新版本
3. **备份配置**: 重要配置变更前先备份
4. **团队协作**: 确保所有开发者使用相同的工具版本
