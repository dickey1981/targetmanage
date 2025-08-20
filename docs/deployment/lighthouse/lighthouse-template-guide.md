# 腾讯云 Lighthouse 应用模板选择指南

## 🎯 推荐模板选择

### 第一选择：Docker CE 模板（强烈推荐）

```
应用模板: Docker CE
操作系统: Ubuntu 20.04 LTS
套餐配置: 2核4GB 80GB SSD
```

**选择理由**：
- ✅ 预装 Docker 和 Docker Compose
- ✅ 环境配置最简单
- ✅ 与我们的部署脚本完全兼容
- ✅ 节省初始化时间
- ✅ 官方维护，稳定可靠

### 第二选择：Ubuntu 20.04 LTS 纯净系统

```
应用模板: Ubuntu 20.04 LTS (纯净系统)
套餐配置: 2核4GB 80GB SSD
```

**选择理由**：
- ✅ 系统纯净，无多余软件
- ✅ 完全可控的环境配置
- ✅ 适合有Linux经验的开发者
- ✅ 我们的初始化脚本会自动安装所需软件

## 📋 详细对比分析

### Docker CE 模板 vs 纯净系统

| 对比项 | Docker CE 模板 | Ubuntu 纯净系统 |
|--------|----------------|------------------|
| 初始化时间 | 5分钟 | 10分钟 |
| Docker版本 | 预装最新版 | 需要安装 |
| 系统纯净度 | 中等 | 最高 |
| 部署难度 | 极简单 | 简单 |
| 推荐指数 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🚫 不推荐的模板

### 避免选择这些模板：

1. **宝塔面板模板**
   - ❌ 资源占用过多
   - ❌ 与Docker部署冲突
   - ❌ 不适合容器化应用

2. **LAMP/LNMP 模板**
   - ❌ 预装Apache/Nginx会端口冲突
   - ❌ 预装PHP/MySQL不需要
   - ❌ 增加系统复杂度

3. **WordPress等CMS模板**
   - ❌ 完全不相关的应用
   - ❌ 浪费资源

4. **Node.js模板**
   - ❌ 版本可能不匹配
   - ❌ 预装环境可能冲突

## 🛒 购买步骤指南

### 步骤1：选择地域
```
推荐地域: 
- 北京（华北）- ap-beijing
- 上海（华东）- ap-shanghai  
- 广州（华南）- ap-guangzhou

选择原则：选择离你的用户最近的地域
```

### 步骤2：选择套餐配置

```
推荐配置：
┌─────────────────┬──────────────────────┐
│ CPU/内存        │ 2核4GB               │
│ 系统盘          │ 80GB SSD             │
│ 峰值带宽        │ 4Mbps                │
│ 每月流量包      │ 300GB                │
│ 价格            │ ¥45/月 (年付¥24/月) │
└─────────────────┴──────────────────────┘
```

**配置说明**：
- **2核4GB**: 足够运行完整系统（数据库+后端+前端）
- **80GB SSD**: 存储系统、应用、数据库和日志文件
- **4Mbps带宽**: 支持同时在线用户访问
- **300GB流量**: 足够小规模业务使用

### 步骤3：选择应用模板

**首选方案**：
```
应用镜像: Docker CE 20.10
系统版本: Ubuntu 20.04 LTS 64位
```

**备选方案**：
```
应用镜像: Ubuntu 20.04 LTS
系统版本: 纯净系统
```

### 步骤4：基础配置

```
实例名称: targetmanage-lighthouse
登录方式: 设置密码 (建议后续配置SSH密钥)
安全组: 默认安全组 (后续可调整)
```

### 步骤5：购买时长选择

```
推荐选择: 1年 (享受5折优惠)
月付价格: ¥45/月
年付价格: ¥24/月 (节省47%)
```

## 🔧 购买后的初始配置

### Docker CE 模板初始化

如果选择了Docker CE模板，连接服务器后运行：

```bash
# 检查Docker状态
docker --version
docker-compose --version

# 如果Docker Compose未安装，运行：
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 直接运行我们的一键部署脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/one-click-deploy.sh | bash
```

### Ubuntu 纯净系统初始化

如果选择了纯净系统，连接服务器后运行：

```bash
# 运行完整的初始化脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/setup-lighthouse.sh | bash

# 重新登录后运行部署脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/one-click-deploy.sh | bash
```

## 🔍 购买前检查清单

在购买前确认以下事项：

- [ ] 已完成腾讯云账号实名认证
- [ ] 账户余额充足（建议预存¥100以上）
- [ ] 确认选择的地域（后续不可更改）
- [ ] 确认套餐配置满足需求
- [ ] 选择了正确的应用模板
- [ ] 设置了安全的登录密码

## 🎯 模板选择决策树

```
开始购买 Lighthouse
    │
    ├─ 你熟悉Docker吗？
    │   ├─ 是 → 选择 Docker CE 模板 ✅
    │   └─ 否 → 继续下一个问题
    │
    ├─ 你有Linux运维经验吗？
    │   ├─ 是 → 选择 Ubuntu 纯净系统 ✅
    │   └─ 否 → 选择 Docker CE 模板 ✅
    │
    └─ 建议：Docker CE 模板最适合新手 🎯
```

## 💡 购买小贴士

1. **时间选择**：
   - 工作日购买，技术支持响应更快
   - 避开促销高峰期，创建更稳定

2. **支付方式**：
   - 选择年付享受最大折扣
   - 可以使用代金券进一步降低成本

3. **后续优化**：
   - 购买后立即配置SSH密钥登录
   - 及时更新系统和软件包
   - 配置自动备份策略

## 📞 购买后支持

如果在购买或配置过程中遇到问题：

1. **查看官方文档**：[轻量应用服务器文档](https://cloud.tencent.com/document/product/1207)
2. **联系技术支持**：腾讯云控制台提交工单
3. **社区支持**：腾讯云开发者社区
4. **项目支持**：在我们的GitHub项目中提Issue

---

**总结推荐**：选择 **Docker CE 模板 + 2核4GB + 年付** 方案，这是最适合目标管理系统部署的配置，既经济又高效！
