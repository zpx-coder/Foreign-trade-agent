# AI 外贸助手 — 产品需求文档 (PRD)

> **版本**：v1.3 | **日期**：2026-07-17 | **状态**：一期迭代 — 客户画像模块优化
>
> 本文档定义 AI 外贸助手的产品需求，作为设计、开发、测试的基准文档。
> 需求变更须通过 PR 评审，重大变更按 CLAUDE.md 第一章确认机制执行。
>
> **v1.3 说明**：本文档在 v1.2 基础上，根据 v1.3 需求列表进行了客户画像（ICP）模块优化。
> 新增与变更详见 [§13 v1.3 变更记录](#13-v13-变更记录)。

---

## 目录

1. [产品概述](#1-产品概述)
2. [产品形态与角色体系](#2-产品形态与角色体系)
3. [功能需求](#3-功能需求)
   - [3.1 企业客户画像生成](#31-企业客户画像生成)
   - [3.2 全网客户获取](#32-全网客户获取)
   - [3.3 客户信息补全](#33-客户信息补全)
   - [3.4 邮件营销模块](#34-邮件营销模块)
   - [3.5 WhatsApp 营销模块（二期）](#35-whatsapp-营销模块二期)
   - [3.6 管理后台（平台级）](#36-管理后台平台级)
4. [非功能需求](#4-非功能需求)
5. [技术架构决策](#5-技术架构决策)
6. [数据模型概要](#6-数据模型概要)
7. [API 设计原则](#7-api-设计原则)
8. [分期规划](#8-分期规划)
9. [风险与假设](#9-风险与假设)
10. [附录](#10-附录)
11. [v1.1 变更记录](#11-v11-变更记录)
12. [v1.2 变更记录](#12-v12-变更记录)
13. [v1.3 变更记录](#13-v13-变更记录)

---

## 1. 产品概述

### 1.1 产品定位

AI 外贸助手是一款**企业级 AI Agent 产品**，替代传统外贸业务中的业务员部分工作。通过大语言模型（LLM）驱动的智能代理能力，自动化完成客户画像构建、潜客搜寻、信息补全、营销触达等外贸核心链路，助力外贸企业降本增效。

### 1.2 目标用户

| 用户类型 | 特征 | 核心诉求 |
|----------|------|----------|
| 外贸企业老板 | 管理者视角，关注 ROI 与客户增长 | 快速获客、跟踪转化效果 |
| 外贸业务员 | 日常操作者，执行开发与营销任务 | 减少重复劳动、提高触达效率 |
| 运营管理员 | 企业账户管理者 | 模板管理、权限控制、数据查看 |

### 1.3 产品价值主张

> **让 AI 替业务员跑完"找客户 → 补信息 → 发邮件"的全链路，人只做决策与跟进。**

---

## 2. 产品形态与角色体系

### 2.1 产品形态

本产品包含两个 Web 前端（均为 PC 端浏览器网页，同一 Vue 项目内按路由区分）：

| 端 | 路由前缀 | 用户群体 | 说明 |
|---|----------|----------|------|
| **用户端** | `/app/*` | 外贸企业用户 | SaaS 平台主体，企业注册后使用客户开发与营销功能 |
| **管理后台** | `/admin/*` | 平台运营方 | 平台级管理：租户管理、计费、系统监控、运营数据 |

### 2.2 用户端角色（租户级）

| 角色 | 权限范围 | 说明 |
|------|----------|------|
| **超级管理员** | 企业全部数据 + 成员管理 + 计费 | 通常为企业老板，一个企业仅 1 人 |
| **管理员** | 企业全部数据 + 模板管理 | 可管理营销模板和客户数据 |
| **业务员** | 本人创建的客户数据 + 本人发送的营销记录 | 日常操作用户 |
| **只读用户** | 查看授权范围内的数据 | 报表查看、管理层 |

### 2.3 管理后台角色（平台级）

| 角色 | 权限范围 | 说明 |
|------|----------|------|
| **平台超级管理员** | 全部租户 + 全部功能 | 平台最高权限，可管理所有租户和系统配置 |
| **平台运营** | 租户查看 + 运营数据 + 客服工具 | 日常运营：查看租户状态、处理工单、查看数据报表 |
| **平台财务** | 计费管理 + 账单 + 发票 | 仅访问计费与财务模块 |

### 2.4 多租户隔离

- 每个注册企业为一个**独立租户**，数据完全隔离。
- 租户内成员按角色划分权限，RBAC 模型控制。
- 数据库层使用 `tenant_id` 实现行级隔离。
- 平台管理员通过独立的 `platform_admin` 表管理，不受租户隔离限制。

---

## 3. 功能需求

### 3.1 企业客户画像生成

#### 3.1.1 功能描述

企业填写自身信息和期望客户特征后，由 AI 模型综合分析并生成结构化的**企业客户画像**（ICP, Ideal Customer Profile），作为后续客户搜索的输入依据。

#### 3.1.2 输入字段

**A. 本企业信息**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 企业名称 | 文本 | 是 | |
| 企业官网 | URL | 否 | 用于 AI 自动提取企业信息 |
| 所属行业 | 枚举 + 自定义 | 是 | 一级行业 / 二级行业 |
| 产品名称 | 文本 | 是 | 支持添加多个产品（SKU 级别） |
| 产品描述 | 富文本 | 是 | 每个产品的规格、用途、卖点 |
| 产品图片 | 图片（≤10 张） | 否 | 辅助 AI 理解产品特征 |
| 目标市场 | 多选（国家 / 地区） | 是 | 如北美、欧盟、东南亚 |
| 企业优势 | 文本 | 否 | 产能、认证、价格优势等 |
| 合作案例 | 文本 | 否 | 已有客户行业 / 品牌案例 |

**B. 期望客户特征**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 客户行业 | 多选 + 自定义 | 是 | 期望客户所在行业 |
| 客户类型 | 枚举 | 是 | 品牌商 / 进口商 / 批发商 / 零售商 / 电商卖家 |
| 客户规模 | 枚举 | 否 | 小（<50人）/ 中（50-500）/ 大（>500） |
| 年采购量估算 | 文本 | 否 | 如"年进口额 > 500 万美元" |
| 客户所在地区 | 多选（国家 / 城市） | 是 | |
| 客户痛点描述 | 文本 | 否 | 你的产品能为客户解决什么问题 |
| 排除客户类型 | 文本 | 否 | 如"已有稳定中国供应商超过 5 年的企业" |

**C. 客户样例（可选但推荐）**

| 字段 | 类型 | 说明 |
|------|------|------|
| 样例客户名称 | 文本 | 已知的理想客户 |
| 样例客户网址 | URL | |
| 样例客户说明 | 文本 | 为什么这是理想客户 |

#### 3.1.3 AI 处理逻辑

```
输入 → [本企业信息] + [期望客户特征] + [客户样例]
      ↓
Prompt 引擎 → 构建结构化提示词（含角色设定、输出格式约束）
      ↓
LLM 调用 → DeepSeek 等国产模型，温度 ≈ 0.3，max_tokens 4096
      ↓
输出解析 → JSON Schema 校验，确保字段完整性与格式合规
      ↓
输出 → 结构化企业客户画像（以下输出字段）
```

#### 3.1.4 输出字段（企业客户画像）

| 字段 | 类型 | 说明 |
|------|------|------|
| 画像名称 | 文本 | 由 AI 自动生成标题，如"北美户外用品进口商画像" |
| 目标客户行业关键词 | 数组 | 用于搜索的行业关键词（中/英/西语） |
| 目标客户产品关键词 | 数组 | 产品相关搜索关键词（多语言） |
| 客户企业规模范围 | 文本 | |
| 客户地理分布 | 数组 | 国家→州/省→城市层级 |
| 客户采购决策链 | 文本 | 关键决策人角色（如 Purchasing Manager, CEO） |
| 客户痛点与需求 | 文本 | |
| 推荐搜索渠道 | 数组 | Google / LinkedIn / Facebook / Amazon 等及其权重 |
| 搜索语法建议 | 文本 | Google 高级搜索语法、LinkedIn 筛选建议 |
| 竞品客户分析 | 文本 | 可能从哪些竞品手中切入 |
| 沟通策略建议 | 文本 | 针对该画像客户的最佳沟通角度 |

#### 3.1.5 交互流程

```
1. 用户进入「客户画像」页面
2. 点击「新建画像」，进入表单
3. 填写本企业信息（支持从企业资料库一键填充）
4. 填写期望客户特征
5. （可选）添加客户样例
6. 点击「生成画像」
7. 系统显示生成进度（流式输出）
8. 生成完成 → 展示完整画像卡片
9. 用户可：确认保存 / 修改后保存 / 重新生成 / 删除
10. 保存后，该画像可用于「客户获取」模块
```

---

### 3.2 全网客户获取

#### 3.2.1 功能描述

基于已生成的客户画像，通过多渠道路由自动搜索匹配的潜在客户企业，将非结构化数据转化为结构化客户记录。

#### 3.2.2 渠道定义

| 渠道 | 搜索方式 | 返回内容 | 优先级 |
|------|----------|----------|--------|
| **Google Search** | 关键词搜索 + 高级语法 | 企业官网、新闻报道、行业目录 | P0（一期） |
| **LinkedIn** | Company Search API / 公开页面 | 企业主页、员工规模、行业标签 | P0（一期） |
| **Facebook** | 公共页面搜索 | 企业主页、品牌信息 | P1（一期后半程） |
| **Amazon** | 卖家店铺搜索 | 品牌卖家信息、产品线 | P1（一期后半程） |
| **独立站** | 电商平台扫描（Shopify 等） | 独立品牌 DTC 商家信息 | P2（二期） |

#### 3.2.3 搜索执行流程

```
用户选择画像 → 勾选搜索渠道 → 设置搜索数量上限（默认 50）
      ↓
渠道路由器 → 根据画像中"推荐搜索渠道"的权重分配搜索任务
      ↓
并行搜索 → 各渠道独立执行搜索并返回原始结果集
      ↓
结果聚合 → 去重（按域名 / 企业名模糊匹配）
      ↓
结果清洗 → AI 过滤无关结果（非企业 / 已倒闭 / 非目标行业）
      ↓
结构化提取 → LLM 将非结构化结果转为结构化客户记录
      ↓
输出 → 「潜在客户列表」+ 匹配度评分（0-100）
```

#### 3.2.4 客户记录结构

| 字段 | 类型 | 来源 |
|------|------|------|
| 客户企业名称 | 文本 | 搜索提取 |
| 企业官网 | URL | 搜索提取 |
| 所属行业 | 枚举 | AI 分类 |
| 企业规模 | 枚举 | 搜索 + AI 推断 |
| 所在国家 / 地区 | 文本 | 搜索提取 |
| 主营产品 / 品类 | 数组 | AI 提取 |
| 社交主页链接 | 数组 | LinkedIn / Facebook |
| 电商店铺链接 | URL | Amazon / 独立站 |
| 匹配度评分 | 0-100 | AI 评估 |
| 匹配原因 | 文本 | AI 简述匹配依据 |
| 数据来源 | 枚举 | 标识搜索渠道 |
| 获取时间 | 时间戳 | 系统生成 |

#### 3.2.5 交互流程

```
1. 用户在「客户画像」列表中选择一个已生成的画像
2. 点击「查找客户」
3. 勾选搜索渠道（支持多选，默认全选）
4. 设置搜索数量上限（10 / 30 / 50 / 100）
5. 点击「开始搜索」
6. 实时展示搜索进度（每个渠道的搜索结果计数）
7. 搜索完成 → 展示客户列表（表格 + 卡片视图切换）
8. 用户可：
   - 查看客户详情
   - 标记「有意向 / 无意向 / 待评估」
   - 单个删除 / 批量删除
   - 导出为 Excel / CSV
   - 加入「营销列表」
```

---

### 3.3 客户信息补全

#### 3.3.1 功能描述

针对已获取的客户企业记录，通过第三方数据接口补全该企业的关键联系人信息（姓名、职位、邮箱、电话），将"企业级"记录升级为"联系人级"记录，为后续营销触达做准备。

#### 3.3.2 补全字段

| 字段 | 必达 | 数据来源 |
|------|------|----------|
| 联系人姓名 | 是 | 第三方数据接口 / LinkedIn 公开信息 |
| 职位 (Job Title) | 是 | 同上 |
| 工作邮箱 | 是（核心） | 第三方数据接口（邮箱验证服务校验） |
| 直拨电话 | 否 | 第三方数据接口 |
| LinkedIn 个人主页 | 否 | LinkedIn |
| 决策层级 | AI 推断 | LLM 根据职位判断（C-Level / VP / Director / Manager） |
| 邮箱有效性 | 是 | 邮箱验证服务返回（valid / invalid / risky / unknown） |

#### 3.3.3 接口适配器模式

由于第三方数据商未最终锁定，采用**适配器模式**设计数据补全层：

```
┌──────────────────────────────────────┐
│        数据补全服务 (Service)          │
│   定义统一接口：enrich(company) → contacts │
└──────────────────────────────────────┘
              ▲
              │ 实现
    ┌─────────┼─────────┬──────────┐
    │         │         │          │
┌───────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│Clearbit│ │Apollo│ │Lusha │ │公开数据   │
│Adapter │ │Adapter│ │Adapter│ │爬取Adapter│
└───────┘ └──────┘ └──────┘ └──────────┘
```

- 初期默认使用**公开数据爬取 + LLM 提取**（零外部依赖）。
- 后续接入商业数据接口时，只需新增 Adapter 实现，业务代码无感知。

#### 3.3.4 交互流程

```
1. 用户在客户列表中选择待补全的客户（支持多选）
2. 点击「补全信息」
3. 系统逐条或批量请求数据补全服务
4. 展示补全进度（成功 / 失败 / 无结果）
5. 补全完成 → 客户记录关联联系人信息
6. 用户可查看 / 编辑 / 删除联系人
```

---

### 3.4 邮件营销模块

#### 3.4.1 功能描述

根据企业信息、产品信息及参考邮件样例，通过 AI 生成个性化营销邮件模板；用户可勾选目标客户批量发送，邮件通过用户自有邮箱发出。

#### 3.4.2 邮件模板生成

**输入：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 关联画像 | 引用 | 是 | 选择已生成的客户画像，AI 根据画像调整邮件话术 |
| 关联产品 | 引用 | 是 | 选择推广的产品 |
| 邮件主题 | 文本 | 否 | 用户自定义主题，留空则 AI 自动生成 |
| 邮件语气 | 枚举 | 是 | 正式 / 商务友好 / 简洁直接 |
| 关键卖点 | 文本 | 否 | 本次营销的重点卖点 |
| 行动号召 (CTA) | 枚举 | 否 | 回复邮件 / 预约会议 / 访问网站 / 查看目录 |
| 参考邮件样例 | 富文本 | 否 | 用户提供的优秀邮件范例，AI 参照其风格与结构 |
| 公司签名信息 | 文本 | 自动填充 | 发件人姓名 / 职位 / 公司 / 联系方式 |

**AI 生成输出：**

| 字段 | 说明 |
|------|------|
| 邮件主题 | 生成 3 个备选主题 |
| 邮件正文 | HTML 格式，含变量占位符（`{{客户联系人}}`, `{{客户公司}}` 等） |
| 预计阅读时间 | AI 估算 |
| 垃圾邮件风险评分 | AI 自检（关键词密度、敏感词检测） |

#### 3.4.3 邮件变量系统

邮件模板支持以下变量，发送时自动替换：

| 变量名 | 来源 | 示例 |
|--------|------|------|
| `{{客户联系人}}` | 客户信息补全 | "John Smith" |
| `{{客户公司}}` | 客户记录 | "ABC Imports Inc." |
| `{{客户行业}}` | 客户记录 | "Home Decor" |
| `{{我方企业}}` | 企业资料 | "Guangdong XYZ Ltd." |
| `{{我方联系人}}` | 用户账户 | "张三" |
| `{{产品名称}}` | 产品信息 | "Ceramic Vase Series A" |

#### 3.4.4 邮件发送

**发送方式**：通过用户自有邮箱发送（Gmail API / Outlook API）。

| 特性 | 说明 |
|------|------|
| 发送通道 | Gmail API / Microsoft Graph API |
| 日发送限制 | Gmail 免费版 500 封/天，Workspace 2000 封/天；系统内置速率控制 |
| 发送间隔 | 可配置（默认 30-60 秒/封），模拟人工发送节奏 |
| 退订链接 | 每封邮件底部强制附带退订链接 |
| 发送状态 | 实时追踪：已发送 / 已送达 / 已打开 / 已点击 / 已回复 / 退信 |
| 追踪像素 | 可选开启（1x1 透明像素追踪打开） |

#### 3.4.5 邮件合规

- 每封营销邮件底部强制包含：
  - 发件人企业信息与联系方式
  - 退订链接（一键退订，即时生效）
- 退订用户自动加入「免打扰列表」，后续发送自动过滤。
- 系统内置 CAN-SPAM / GDPR 合规检查提示（非强制拦截，提醒用户自查）。

#### 3.4.6 交互流程（邮件模板生成）

```
1. 进入「邮件营销」→「模板管理」
2. 点击「新建模板」
3. 填写生成表单：
   - 选择关联画像
   - 选择关联产品
   - 设置邮件语气 / CTA / 卖点
   - （可选）粘贴参考邮件样例
4. 点击「生成模板」
5. AI 流式输出，用户实时预览
6. 生成完成，用户可：
   - 在线编辑修改邮件内容
   - 测试发送（发送到本人邮箱预览效果）
   - 保存模板
```

#### 3.4.7 交互流程（邮件发送）

```
1. 进入「邮件营销」→「发送任务」
2. 点击「新建发送任务」
3. 选择邮件模板
4. 选择目标客户（从客户列表中勾选，需已完成信息补全的客户）
5. 预览邮件（展示变量替换后的实际效果）
6. 选择发送策略：立即发送 / 定时发送
7. 确认发送 → 显示发送任务卡片
8. 任务卡片实时更新进度：已发送 X/总数，成功 Y，失败 Z
9. 发送完成 → 查看发送报告
```

---

### 3.5 WhatsApp 营销模块（二期）

> **本节为二期规划，MVP 不实现，但架构上预留扩展点。**

#### 3.5.1 功能概述

与邮件模块对称设计：根据企业信息 + 产品信息 + 样例生成 WhatsApp 消息模板，通过 WhatsApp Cloud API（Meta 官方）批量发送营销消息。

#### 3.5.2 核心差异点

| 维度 | 邮件模块 | WhatsApp 模块 |
|------|----------|---------------|
| 发送通道 | Gmail / Outlook API | WhatsApp Cloud API (Meta) |
| 内容格式 | HTML 富文本 | 纯文本 + 媒体（图片/PDF） |
| 模板审批 | 无需 | Meta 模板审批机制（24h 窗口） |
| 发送限制 | 邮箱服务商限制 | Meta 消息配额 + 定价等级 |
| 合规要求 | CAN-SPAM / GDPR | WhatsApp Business 政策 + 用户 opt-in |
| 交互模式 | 单向推送为主 | 支持客户回复 → AI 自动应答 |

#### 3.5.3 架构预留

- 邮件模块与 WhatsApp 模块统一抽象 `MessageChannel` 接口。
- 模板管理、发送任务、发送报告等模块复用相同的 UI 组件和数据结构。
- WhatsApp 特有的模板审批流程仅影响 `WhatsAppChannel` 实现，不冲击架构。

---

### 3.6 管理后台（平台级）

> 管理后台面向平台运营方，与用户端共享同一套后端服务，通过独立路由 `/admin/*` 访问。
> 平台管理员账号通过独立认证体系登录，与租户用户体系隔离。

#### 3.6.1 功能模块总览

| 模块 | 说明 | 优先级 |
|------|------|:--:|
| 管理后台登录 | 平台管理员独立登录（不与租户用户混用） | P0 |
| 租户管理 | 查看/搜索/筛选全部租户，支持启用/停用/删除 | P0 |
| 租户详情 | 查看租户基本信息、成员数、画像数、客户数、邮件发送统计 | P0 |
| 计费管理 | 套餐管理、租户套餐分配、账单记录查看 | P1 |
| 运营仪表盘 | 平台核心指标：总租户数、日活、AI Token 用量、邮件发送总量 | P1 |
| 系统配置 | 全局参数配置：AI 模型选择、邮件配额默认值、注册开关 | P1 |
| 操作日志 | 平台管理员操作审计日志 | P2 |

#### 3.6.2 租户管理

**租户列表字段：**

| 字段 | 说明 |
|------|------|
| 企业名称 | 注册时填写 |
| 套餐类型 | free / pro / enterprise |
| 状态 | active / suspended / cancelled |
| 成员数 | 当前租户内用户数 |
| 画像数 | 已生成的客户画像数 |
| 客户数 | 已获取的客户数 |
| 注册时间 | 租户创建时间 |
| 最近活跃 | 最后一次操作时间 |

**操作：** 查看详情 / 启用 / 停用 / 变更套餐

#### 3.6.3 运营仪表盘

**概览卡片（顶部）：**
- 总租户数 | 活跃租户数（7 日）| 今日新增注册
- 总用户数 | 日活用户数（7 日）
- AI Token 消耗（今日 / 本月）
- 邮件发送总量（今日 / 本月）

**图表（下方）：**
- 注册趋势折线图（7 日 / 30 日）
- AI Token 消耗趋势
- 邮件发送量趋势
- 套餐分布饼图

#### 3.6.4 与用户端的交互边界

```
管理后台 /admin/*          用户端 /app/*
┌──────────────┐          ┌──────────────┐
│ 平台管理员    │          │ 租户用户      │
│              │          │              │
│ 租户管理      │  ←查看→  │ 企业资料      │
│ 计费管理      │  ←关联→  │ 套餐信息      │
│ 运营仪表盘    │  ←聚合→  │ 各业务模块    │
│ 系统配置      │  ←影响→  │ 功能可用性    │
└──────────────┘          └──────────────┘
       │                        │
       └────────┬───────────────┘
                │
         ┌──────▼──────┐
         │  同一后端 API │
         │  /api/v1/    │
         └─────────────┘
```

---

## 4. 非功能需求

### 4.1 性能

| 指标 | 目标值 |
|------|--------|
| 页面首屏加载 | ≤ 2s（P95） |
| API 响应时间（非 AI） | ≤ 200ms（P95） |
| AI 画像生成时间 | ≤ 30s（流式输出首字 ≤ 3s） |
| 客户搜索任务（50 条） | ≤ 120s |
| 邮件发送吞吐 | ≥ 200 封/小时/用户 |
| 并发用户数（一期） | 50 企业，500 用户 |

### 4.2 安全

- **认证**：JWT + Refresh Token 机制，Token 有效期 2h。
- **授权**：RBAC，每个 API 端点校验用户角色与租户归属。
- **邮箱授权**：OAuth 2.0 授权码流程，不存储用户邮箱密码；Token 加密存储。
- **传输**：全站 HTTPS + API 层强制 TLS 1.2+。
- **数据**：敏感字段（邮箱、电话）AES-256 加密存储。
- **输入**：所有用户输入后端二次校验，防 XSS / SQL 注入。
- **AI 输入**：用户提供的文件/图片内容经安全预处理后再传入 LLM。

### 4.3 可用性

- 核心服务可用性 ≥ 99.5%（不含第三方依赖）。
- AI 模型调用失败自动重试（最多 3 次，指数退避）。
- 关键操作（发送、生成）失败时提供明确错误提示和重试入口。
- 优雅降级：第三方数据接口不可用时，不影响其他功能使用。

### 4.4 可扩展性

- 模块间通过 API 通信，预留微服务拆分可能。
- 第三方数据接口适配器模式，新增数据源只需实现 Adapter。
- 渠道搜索插件化设计，新增搜索渠道只需实现 Channel 接口。
- AI 模型网关支持多模型路由，可随时切换或混用。

### 4.5 可观测性

- 全链路请求日志（trace id）。
- AI 调用 Token 用量、延迟、成功率监控。
- 邮件发送状态全追踪。
- 关键业务指标仪表盘（可选，运营后台功能）。

---

## 5. 技术架构决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 前端 | Vue 3 + Element Plus | 成熟的企业级 UI 库，中文生态好 |
| 后端 | Python FastAPI | 异步支持好，AI/ML 生态丰富，适合 LLM 调用密集型应用 |
| 主数据库 | PostgreSQL 16 | 成熟的事务支持，JSONB 灵活存储 AI 输出，多租户行级安全 |
| 缓存/队列 | Redis | 缓存 + 消息队列（Bull / RQ），邮件发送任务队列 |
| 搜索引擎 | Elasticsearch | 客户全文搜索、画像匹配度评分、日志检索 |
| AI 模型 | DeepSeek + 可选模型 | 国产模型低延迟，架构上预留多模型路由能力 |
| 文件存储 | MinIO / S3 兼容 | 产品图片、邮件附件存储 |
| 容器化 | Docker + Docker Compose | MVP 阶段简化部署，二期上 K8s |
| CI/CD | GitHub Actions | 与 GitHub 仓库深度集成 |

### 5.1 系统架构概要（一期）

```
┌──────────────────────────────────────────────────────────┐
│                    Vue 3 前端（同项目分路由）               │
│        /app/* 用户端          │      /admin/* 管理后台     │
│      Nginx (静态资源 + API 反向代理)                       │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼─────────────────────────────────┐
│                      API Gateway                          │
│         FastAPI (统一认证 / 租户隔离 / 平台鉴权 / 限流)      │
└───┬──────────┬──────────┬──────────┬──────────┬──────────┘
    │          │          │          │          │
┌───▼──┐ ┌────▼────┐ ┌───▼───┐ ┌───▼──────┐ ┌──▼──────┐
│ 画像  │ │客户获取 │ │信息补全│ │ 邮件发送  │ │管理后台 │
│ 服务  │ │  服务   │ │  服务  │ │   服务    │ │  服务   │
└──┬───┘ └───┬─────┘ └──┬───┬┘ └──┬───────┘ └──┬──────┘
   │         │          │   │      │            │
   └─────────┴──────────┴───┴──────┴────────────┘
              │
    ┌─────────┼──────────┬────────────┐
┌───▼──┐ ┌───▼───┐ ┌───▼───┐ ┌─────▼────┐
│DeepSeek│ │Redis  │ │  PG   │ │ Elasticsearch│
│  LLM  │ │Cache/MQ│ │  DB   │ │   Search   │
└───────┘ └───────┘ └───────┘ └──────────┘
```

---

## 6. 数据模型概要

### 6.1 核心实体

```
【租户域】
tenant (租户)
  ├── user (用户) [1:N]
  ├── enterprise_profile (企业资料) [1:1]
  ├── product (产品) [1:N]
  ├── icp (客户画像) [1:N]
  ├── customer (客户) [1:N]
  │     └── contact (联系人) [1:N]
  ├── email_template (邮件模板) [1:N]
  ├── email_campaign (发送任务) [1:N]
  │     └── email_log (发送记录) [1:N]
  └── unsubscribe_list (免打扰列表) [1:N]

【平台域】（无租户隔离）
platform_admin (平台管理员)
  └── admin_operation_log (管理员操作日志)
```

### 6.2 关键表结构（概要）

#### tenant (租户)
```sql
id UUID PK
name VARCHAR(255)
plan_type VARCHAR(50)       -- free / pro / enterprise
status VARCHAR(20)          -- active / suspended / cancelled
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

#### icp (客户画像)
```sql
id UUID PK
tenant_id UUID FK → tenant
name VARCHAR(255)
input_data JSONB            -- 用户填写的原始信息
output_data JSONB           -- AI 生成的完整画像
status VARCHAR(20)          -- draft / generated / archived
created_at TIMESTAMPTZ
```

#### customer (客户)
```sql
id UUID PK
tenant_id UUID FK → tenant
icp_id UUID FK → icp
company_name VARCHAR(500)
website VARCHAR(500)
industry VARCHAR(200)
scale VARCHAR(50)
country VARCHAR(100)
region VARCHAR(200)
main_products JSONB
social_links JSONB
source_channel VARCHAR(50)  -- google / linkedin / facebook / amazon
match_score INT             -- 0-100
match_reason TEXT
status VARCHAR(20)          -- new / interested / not_interested / marketing
created_at TIMESTAMPTZ
```

#### contact (联系人)
```sql
id UUID PK
customer_id UUID FK → customer
full_name VARCHAR(255)
job_title VARCHAR(255)
email VARCHAR(255)
phone VARCHAR(50)
linkedin_url VARCHAR(500)
decision_level VARCHAR(50)  -- c_level / vp / director / manager / staff
email_validity VARCHAR(20)  -- valid / invalid / risky / unknown
data_source VARCHAR(50)     -- api_provider / public / manual
created_at TIMESTAMPTZ
```

#### email_template (邮件模板)
```sql
id UUID PK
tenant_id UUID FK → tenant
icp_id UUID FK → icp
product_id UUID FK → product
subject VARCHAR(500)
body_html TEXT
tone VARCHAR(50)
cta_type VARCHAR(50)
variables JSONB             -- 模板中使用的变量列表
created_at TIMESTAMPTZ
```

#### email_campaign (发送任务)
```sql
id UUID PK
tenant_id UUID FK → tenant
template_id UUID FK → email_template
user_id UUID FK → user
status VARCHAR(30)          -- draft / scheduled / sending / completed / paused
total_count INT
sent_count INT
success_count INT
failed_count INT
scheduled_at TIMESTAMPTZ
started_at TIMESTAMPTZ
finished_at TIMESTAMPTZ
```

#### platform_admin (平台管理员)

```sql
id UUID PK
email VARCHAR(255) UNIQUE
password_hash VARCHAR(255)
name VARCHAR(100)
role VARCHAR(30)             -- super_admin / operator / finance
is_active BOOLEAN DEFAULT TRUE
created_at TIMESTAMPTZ
last_login_at TIMESTAMPTZ
```

#### admin_operation_log (操作日志)

```sql
id UUID PK
admin_id UUID FK → platform_admin
action VARCHAR(100)          -- tenant_suspend / plan_change / config_update
target_type VARCHAR(50)      -- tenant / billing / system_config
target_id UUID
detail JSONB
ip_address VARCHAR(45)
created_at TIMESTAMPTZ
```

---

## 7. API 设计原则

- RESTful 风格，资源命名使用复数形式（`/api/v1/icps`, `/api/v1/customers`）。
- 请求 / 响应统一 JSON 格式。
- 统一错误响应格式：
  ```json
  {
    "error": {
      "code": "INVALID_INPUT",
      "message": "客户画像名称不能为空",
      "details": [...]
    }
  }
  ```
- 分页统一使用 `page` / `page_size` 参数，响应含 `total`, `page`, `page_size`, `items`。
- 所有 API 通过 `Authorization: Bearer <jwt>` 认证。
- AI 生成类接口使用 Server-Sent Events (SSE) 实现流式输出。

---

## 8. 分期规划

### 一期 — MVP（当前版本）

| 模块 | 范围 |
|------|------|
| 企业客户画像生成 | 完整功能 |
| 全网客户获取 | Google + LinkedIn 渠道，50 条/次上限 |
| 客户信息补全 | 公开数据 + LLM 提取（商业接口预留适配器） |
| 邮件模板生成 | 完整功能 |
| 邮件发送 | Gmail API 通道，支持批量发送 |
| 用户端认证与布局 | 注册 / 登录 / 角色权限 / 多租户 / MainLayout |
| 企业资料管理 | 基础 CRUD |
| **管理后台** | **平台管理员登录 + 租户管理（列表/详情/启停）+ 运营仪表盘** |

### 二期规划

| 模块 | 范围 |
|------|------|
| WhatsApp 营销 | 模板生成 + Cloud API 发送 |
| 客户获取渠道扩展 | Facebook + Amazon + 独立站 |
| 商业数据接口接入 | Clearbit / Apollo 等适配器 |
| AI 自动回复 | 客户回复邮件 → AI 分类 → 自动或建议回复 |
| 数据分析仪表盘 | 客户增长趋势、营销转化漏斗、AI Token 用量 |

### 三期规划

| 模块 | 范围 |
|------|------|
| AI Agent 全自动模式 | 设定策略后 AI 自主完成"找客户 → 写邮件 → 发邮件 → 跟进回复"闭环 |
| 多语言国际化 | 系统界面 i18n，邮件模板多语言 |
| 开放 API | 对外提供 API，允许企业自有系统集成 |
| 多渠道营销 | Telegram、WeChat、Line 等消息渠道 |

---

## 9. 风险与假设

### 9.1 技术风险

| 风险 | 等级 | 缓解策略 |
|------|------|----------|
| AI 输出质量不稳定 | 高 | Prompt 工程迭代 + JSON Schema 强校验 + 人工审核入口 |
| LLM 服务可用性 | 中 | 多模型 fallback，本地缓存常用生成结果 |
| 邮件送达率低 | 中 | 预热发送量 + 垃圾词检测 + 退订合规 |
| 公开数据爬取合规 | 高 | 仅爬公开可访问页面 + 遵守 robots.txt + 法律审查 |
| 第三方数据接口不确定性 | 低 | 适配器模式解耦，初始版本不依赖任何商业接口 |

### 9.2 产品假设

| 假设 | 验证方式 |
|------|----------|
| 外贸企业愿意使用 AI 生成客户画像 | MVP 用户访谈 + 画像保存率 |
| AI 搜索的客户质量不低于人工搜索 | 匹配度评分 vs 用户标记"有意向"比例 |
| 用户接受通过自有邮箱发送营销邮件 | 邮箱授权完成率 + 用户反馈 |
| Gmail API 日限额能满足中小企业需求 | 监控实际发送量 vs 配额 |

---

## 10. 附录

### 10.1 术语表

| 术语 | 全称 / 说明 |
|------|-------------|
| ICP | Ideal Customer Profile，理想客户画像 |
| LLM | Large Language Model，大语言模型 |
| SSE | Server-Sent Events，服务端推送事件 |
| RBAC | Role-Based Access Control，基于角色的访问控制 |
| CAN-SPAM | 美国反垃圾邮件法案 |
| BSP | Business Solution Provider，WhatsApp 商业解决方案提供商 |

### 10.2 术语表（续）

| 术语 | 全称 / 说明 |
|------|-------------|
| HS Code | 海关编码（Harmonized System Code），国际贸易商品分类标准 |
| MOQ | Minimum Order Quantity，最小起订量 |
| SMTP | Simple Mail Transfer Protocol，邮件发送协议 |

---

## 11. v1.1 变更记录

> 本章记录从 PRD v1.0（2026-06-25）到 v1.1（2026-07-16）期间，经 Phase 0–7 实际开发后，
> 与初始规划产生的所有偏差。变更按影响范围从大到小排列。

### 11.1 架构级变更

#### 11.1.1 邮件发送通道：Gmail OAuth → 通用 SMTP

| 维度 | v1.0 规划 | v1.1 实际 |
|------|-----------|-----------|
| 发送方式 | Gmail API / Microsoft Graph API（OAuth 2.0） | **通用 SMTP 协议** |
| 认证方式 | OAuth 授权码流程，Token 加密存储 | SMTP 用户名密码，AES-256 加密存储 |
| 配置粒度 | 全局邮箱连接 | **租户级 SMTP 配置**（每租户可配独立发件服务器） |
| 发送任务 | 关联已连接邮箱 | 发送任务创建时指定 SMTP 配置（`smtp_config` JSONB） |

**变更理由**：
- Gmail OAuth 需要 Google Cloud Console 审核，上线周期长
- SMTP 方案覆盖更多邮箱服务商（腾讯企业邮、网易、阿里云等），更符合国内外贸企业实际使用场景
- 租户级配置灵活性更高，企业可用自己的邮件服务器发送

**相关表变更**：
- `email_campaigns` 新增 `smtp_config JSONB` 字段
- `tenant` 新增 `settings JSONB` 字段（存储租户级 SMTP 默认配置）
- 新增 API：`GET/PUT /api/v1/settings/smtp`（租户级 SMTP 配置管理）

#### 11.1.2 客户搜索策略简化

| 维度 | v1.0 规划 | v1.1 实际 |
|------|-----------|-----------|
| 搜索渠道 | Google + LinkedIn + Facebook + Amazon 多渠道并行 | **单一路由**（POST `/api/v1/customers/search`） |
| 实时反馈 | SSE 流式推送各渠道进度 | SSE 保留但各渠道搜索聚合为统一接口 |
| 渠道适配器 | Channel 接口 + 多实现 | 暂未实现独立的渠道适配器层 |
| 结果去重 | 域名/企业名模糊去重 | 基础去重 |

**变更理由**：MVP 阶段优先验证核心流程，多渠道并行搜索和渠道适配器模式留待二期实现。

#### 11.1.3 部署架构简化

| 维度 | v1.0/dev-spec 规划 | v1.1 实际 |
|------|---------------------|-----------|
| Nginx 容器 | docker-compose 含 nginx 服务 | **不含 nginx 容器**（`nginx.conf` 文件保留备用） |
| 服务发现 | 容器间通过服务名通信（`db:5432`） | **localhost 直连**（开发环境） |

**变更理由**：开发阶段直接用 Vite 代理到 FastAPI，生产部署时再加 Nginx。

### 11.2 数据模型变更

#### 11.2.1 产品表（product）— 外贸属性增强

v1.0 规划的产品字段与通用 CMS 类似，v1.1 增加了外贸行业特有字段：

| 字段 | 类型 | v1.0 | v1.1 | 说明 |
|------|------|:----:|:----:|------|
| `name` | VARCHAR(255) | ✓ | ✓ | |
| `description` | TEXT | ✓ | ✓ | |
| `category` | VARCHAR(100) | ✓ | ✓ | |
| `hs_code` | VARCHAR(20) | ✗ | **新增** | 海关 HS 编码，出口报关必需 |
| `price_usd` | NUMERIC(12,2) | ✗ | **新增** | 美元单价 |
| `moq` | INTEGER | ✗ | **新增** | 最小起订量（Minimum Order Quantity） |
| `image_url` | VARCHAR(512) | ≤10 张 | **1 张** | 简化为单图，多图后续支持 |
| `is_active` | BOOLEAN | ✗ | **新增** | 软删除/下架标记 |

#### 11.2.2 客户表（customers）— 结构重构

| 维度 | v1.0 规划 | v1.1 实际 |
|------|-----------|-----------|
| 企业名称 | `company_name` | `name`（简化） |
| 企业规模 | `scale`（枚举：小/中/大） | `company_size`（自由文本，更灵活） |
| 区域 | `region`（省/州） | `city`（城市级精度） |
| 主营产品 | `main_products JSONB` | **移除**（信息转到 `source_data` 和 `ai_summary`） |
| 社交链接 | `social_links JSONB` | **移除** |
| 匹配度评分 | `match_score` INT (0-100) | **移除**（MVP 未实现评分算法） |
| 匹配原因 | `match_reason` TEXT | **移除** |
| 来源渠道 | `source_channel`（枚举） | `source`（自由文本，更灵活） |
| 来源 URL | — | **新增** `source_url` |
| 原始数据 | — | **新增** `source_data JSONB`（保留搜索原始返回） |
| AI 摘要 | — | **新增** `ai_summary TEXT` |
| 备注 | — | **新增** `notes TEXT` |
| 补全状态 | — | **新增** `enrichment_status` / `last_enriched_at` / `enrichment_count` |
| 创建人 | — | **新增** `created_by` FK → user |

#### 11.2.3 联系人表（contacts）— 精简

与 v1.0 规划的 `contact` 表相比：

| 移除字段 | 原因 |
|----------|------|
| `decision_level`（决策层级） | MVP 未实现 AI 职位推断 |
| `email_validity`（邮箱有效性） | MVP 未接入邮箱验证服务 |
| `data_source`（数据来源） | 简化为统一入口 |

| 新增字段 | 说明 |
|----------|------|
| `is_primary` BOOLEAN | 标记首要联系人 |
| `notes` TEXT | 用户自定义备注 |
| `tenant_id` FK | 直接关联租户（加速查询，跳过 customer join） |

命名调整：`full_name` → `name`，`job_title` → `title`。

#### 11.2.4 邮件模板表（email_templates）— 扩展

与 v1.0 相比新增字段：

| 新增字段 | 类型 | 说明 |
|----------|------|------|
| `name` | VARCHAR(255) | 模板名称（用户自定义） |
| `body_text` | TEXT | 纯文本版邮件（兼容纯文本客户端） |
| `key_points` | TEXT | 关键卖点文本 |
| `spam_score` | INTEGER | AI 垃圾邮件风险评分（0-100） |
| `read_time_seconds` | INTEGER | AI 估算阅读时间 |
| `input_data` | JSONB | 生成时的输入参数快照 |
| `output_data` | JSONB | AI 生成的完整输出 |
| `status` | VARCHAR | 模板状态（draft / active / archived） |
| `created_by` | UUID FK | 创建人 |

移除字段：`variables` JSONB（变量从模板内容中动态解析）。

#### 11.2.5 邮件发送任务表（email_campaigns）— 追踪增强

| 维度 | v1.0 | v1.1 |
|------|------|------|
| 统计维度 | sent / success / failed | **sent / delivered / opened / bounced** |
| 定时发送 | `scheduled_at` | `schedule_at`（命名调整） |
| 完成时间 | `finished_at` | `completed_at`（命名调整） |
| SMTP 配置 | 全局 | **`smtp_config JSONB`**（任务级） |
| 客户列表 | 关联表 | **`customer_ids JSONB`**（快照式存储） |

#### 11.2.6 发送日志表（send_logs）— 新增追踪像素

v1.0 规划中未包含追踪像素实现细节，v1.1 新增：

| 新增字段 | 说明 |
|----------|------|
| `tracking_id` UUID | 唯一追踪标识，用于 1×1 透明像素 URL |
| `opened_at` TIMESTAMPTZ | 邮件打开时间 |
| `error_message` TEXT | 发送失败原因 |

追踪端点：`GET /api/v1/tracking/{tracking_id}.png` 返回透明像素并记录打开事件。

#### 11.2.7 租户表（tenant）— 新增配置存储

v1.1 新增 `settings JSONB` 字段，存储租户级配置（当前含默认 SMTP 配置），无需新建配置表。

#### 11.2.8 表命名变更

| v1.0 规划 | v1.1 实际 | 说明 |
|-----------|-----------|------|
| `icp` | `icps` | 统一复数命名 |
| `contact` | `contacts` | 统一复数命名 |
| `email_log` | `send_logs` | 更准确反映发送日志语义 |
| `unsubscribe_list` | `unsubscribes` | 简化名称 |

### 11.3 API 变更

#### 11.3.1 新增 API

| 端点 | 说明 | 来源 |
|------|------|------|
| `POST /api/v1/auth/change-password` | 用户修改密码 | Phase 1 补充 |
| `GET /api/v1/customers/import-template` | 下载客户导入模板 | Phase 4 补充 |
| `POST /api/v1/customers/import` | 批量导入客户（Excel/CSV） | Phase 4 补充 |
| `GET /api/v1/customers/{id}/contacts` | 客户下联系人列表 | Phase 4 补充 |
| `POST /api/v1/customers/{id}/contacts` | 为客户添加联系人 | Phase 4 补充 |
| `PUT /api/v1/customers/{id}/contacts/{cid}` | 编辑联系人 | Phase 4 补充 |
| `DELETE /api/v1/customers/{id}/contacts/{cid}` | 删除联系人 | Phase 4 补充 |
| `GET /api/v1/members` | 成员列表 | Phase 7 新增 |
| `POST /api/v1/members/invite` | 邀请成员 | Phase 7 新增 |
| `PUT /api/v1/members/{id}` | 编辑成员信息 | Phase 7 新增 |
| `DELETE /api/v1/members/{id}` | 移除成员 | Phase 7 新增 |
| `GET /api/v1/settings/smtp` | 获取租户 SMTP 配置 | Phase 7 新增 |
| `PUT /api/v1/settings/smtp` | 更新租户 SMTP 配置 | Phase 7 新增 |
| `GET /api/v1/tracking/{tracking_id}.png` | 邮件追踪像素 | Phase 6 新增 |
| `GET /api/v1/unsubscribe` | 退订确认页 | Phase 6 新增 |
| `POST /api/v1/unsubscribe` | 执行退订 | Phase 6 新增 |

#### 11.3.2 API 调整

| 端点 | v1.0 | v1.1 |
|------|------|------|
| 管理后台登录 | `POST /api/v1/admin/auth/login` | `POST /api/v1/auth/admin/login`（归入 auth 路由） |
| 管理后台登出 | `POST /api/v1/admin/auth/logout` | **未实现** |
| 管理后台获取当前管理员 | `GET /api/v1/admin/auth/me` | `GET /api/v1/auth/me`（与用户共用，token 中区分） |
| 租户停用/启用 | `POST /admin/tenants/{id}/suspend` / `activate` | `PUT /api/v1/admin/tenants/{id}`（status 字段更新） |
| 管理后台操作日志 | `GET /api/v1/admin/logs` | **未实现**（二期） |
| 邮件预览 | `POST /campaigns/{id}/preview` | `POST /api/v1/email-campaigns/{id}/preview`（功能一致） |
| 客户搜索 SSE | `POST /api/v1/customers/search` → SSE 流 | 接口保留但 SSE 实现简化 |
| 邮件模板生成 | `POST /api/v1/email-templates/generate` | `POST /api/v1/email-templates/{id}/generate`（需先创建再生成） |
| ICP 生成 | `POST /api/v1/icps/generate`（直接生成） | `POST /api/v1/icps/{id}/generate`（需先创建再生成） |

#### 11.3.3 未实现的 API（延期至二期）

| v1.0 规划的端点 | 说明 |
|-----------------|------|
| `GET /api/v1/email-auth/gmail/url` | Gmail OAuth URL → 改为 SMTP |
| `POST /api/v1/email-auth/gmail/callback` | Gmail OAuth 回调 → 改为 SMTP |
| `GET /api/v1/email-auth/status` | 邮箱连接状态 → 改为 SMTP 配置 |
| `DELETE /api/v1/email-auth/{provider}` | 断开邮箱连接 → 改为 SMTP |
| `POST /api/v1/email-campaigns/{id}/cancel` | 取消发送任务 |
| `GET /api/v1/email-campaigns/{id}/logs` | 发送日志分页查询 |
| `GET /api/v1/admin/logs` | 管理后台操作日志 |
| `GET /api/v1/admin/dashboard` | 运营仪表盘（统计聚合到 `/stats`） |

### 11.4 前端路由变更

| 页面 | v1.0/dev-spec 规划 | v1.1 实际 |
|------|---------------------|-----------|
| 产品管理 | `/app/products` + `/create` + `/:id/edit` 三条路由 | **无独立路由**（功能集到列表页弹窗操作） |
| 企业资料 | `/app/enterprise`（查看）+ `/edit`（编辑） | **`/app/enterprise` 直接进入编辑页** |
| 邮件模板创建 | `/app/email/templates/create` | **重定向到列表页**（弹窗式创建） |
| 邮件模板编辑 | `/app/email/templates/:id/edit` | **重定向到列表页** |
| 发送任务创建 | `/app/email/campaigns/create` | **重定向到列表页** |
| 管理后台系统配置 | `/admin/settings` | **未实现** |
| 404 页面 | 未规划 | **已实现** `NotFound.vue` |

### 11.5 功能模块实现度总览

| 模块 | v1.0 规划 | v1.1 实际 | 差异 |
|------|:--------:|:--------:|------|
| **认证系统** | 注册/登录/Token 刷新/角色权限/管理后台登录 | 完整实现 + 新增修改密码 | ✓ 超出 |
| **企业资料** | 基础 CRUD + Logo 上传 | 完整实现 | ✓ |
| **产品管理** | CRUD + 多图上传 | CRUD + HS 编码/单价/MOQ 外贸字段 | 字段调整 |
| **ICP 客户画像** | 多步表单 + AI 流式生成 | 完整实现 | ✓ |
| **客户获取** | Google/LinkedIn 多渠道 SSE 搜索 | 基础搜索 + 批量导入 Excel/CSV | 渠道简化 |
| **信息补全** | 适配器模式 + 公开数据 + 商业接口 | 基础补全 + 联系人 CRUD | 简化 |
| **邮件模板** | AI 生成 + 变量系统 + 垃圾评分 | 完整实现 + spam_score + 阅读时间 | ✓ 超出 |
| **邮件发送** | Gmail API + 定时 + 追踪 | **SMTP** + 定时 + 追踪像素 + 退订 | 通道更灵活 |
| **成员管理** | 角色分配 | 完整 CRUD + 邀请机制 | ✓ |
| **租户设置** | 未规划 | SMTP 配置管理 | **新增** |
| **管理后台** | 租户管理 + 运营仪表盘 + 操作日志 | 租户管理 + 统计概览（日志延期） | 略微简化 |
| **WhatsApp** | 二期 | 未开发 | 按计划 |

### 11.6 未实现项（已知差距，留待后续版本）

| 功能 | v1.0 优先级 | 当前状态 | 计划 |
|------|:---------:|:--------:|------|
| 多渠道客户搜索（Google/LinkedIn 适配器） | P0 | 接口存在，渠道未独立 | v1.2 |
| 客户匹配度评分系统 | P0 | 未实现 | v1.2 |
| Gmail/Outlook OAuth 邮箱连接 | P0 | 改为 SMTP | 评估中 |
| 邮箱有效性校验服务 | P1 | 未接入 | v1.2 |
| 联系人决策层级 AI 推断 | P1 | 未实现 | v1.2 |
| 平台操作审计日志 | P2 | 未实现 | v1.3 |
| 管理后台系统配置页 | P1 | 未实现 | v1.2 |
| 邮件任务取消功能 | — | 未实现 | v1.2 |
| 发送日志独立查询接口 | — | 未实现 | v1.2 |
| 产品多图上传 | P0 | 单图 | v1.2 |
| 产品管理独立路由页 | P0 | 视图文件存在但路由未注册 | v1.2 |
| 前端企业资料/产品/租户/UI 独立 Store | P1 | 仅 4/8 个 Store 实现 | v1.2 |

### 11.7 其他技术偏差

#### 11.7.1 异步任务方案：Celery → asyncio.create_task

Dev Spec 规划使用 Celery + Redis 作为消息队列执行邮件发送等耗时任务，实际实现使用 Python 原生的 `asyncio.create_task()` 在 FastAPI 事件循环中执行后台发送。

**影响**：服务重启时未完成的发送任务会丢失，不适合高并发场景，但 MVP 阶段足够。

#### 11.7.2 基础设施使用状态

| 服务 | docker-compose 配置 | 应用代码实际使用 |
|------|:------------------:|:----------------:|
| PostgreSQL (pgvector) | ✓ | ✓ 全部数据存储 |
| Redis | ✓ | **未使用**（容器运行但无缓存/队列逻辑） |
| Elasticsearch | ✓ | **未使用**（容器运行但无索引/搜索逻辑） |

Redis 和 ES 已提前部署为后续功能准备（ES 用于客户全文搜索、Redis 用于 Token 黑名单/缓存）。

#### 11.7.3 SSE 实现格式差异

Dev Spec 定义了标准 SSE 事件格式（`event: progress\ndata: {...}\n\n`），实际实现使用**扁平 JSON 格式**（`data: {json}\n\n`），事件类型内嵌在 JSON payload 中（`{type: 'progress', ...}`）。功能等价，但格式不兼容 Dev Spec 定义。

#### 11.7.4 新增搜索渠道

除 PRD 规划的 Google/LinkedIn 外，代码中额外实现了：
- **DuckDuckGo 搜索**（`backend/app/services/search/duckduckgo_channel.py`）
- **AI 搜索通道**（`backend/app/services/search/ai_search_channel.py`）

这两个渠道在 v1.0 PRD 中未规划。

#### 11.7.5 前端状态管理简化

Dev Spec 规划了 8 个 Pinia Store（auth / enterprise / product / icp / customer / email / tenant / ui），实际只实现了 4 个核心 Store：
- `auth.ts`（认证状态）
- `icp.ts`（客户画像）
- `customer.ts`（客户管理）
- `email.ts`（邮件模板+发送任务）

其余模块的状态在组件内通过组合式 API 管理，未抽取独立 Store。

#### 11.7.6 产品管理路由未注册

`frontend/src/views/product/` 目录下存在 `ProductListView.vue`、`ProductCreate.vue`、`ProductEdit.vue`、`ProductForm.vue` 等完整组件，但路由配置（[frontend/src/router/index.ts](frontend/src/router/index.ts)）中**未注册产品相关路由**。产品功能可能通过侧边栏直接加载或集成在其他页面中。

#### 11.7.7 客户数据导出

新增 Excel 导出功能（[backend/app/api/customers.py](backend/app/api/customers.py)），支持按筛选条件或指定 ID 列表导出客户数据为 `.xlsx` 文件，v1.0 PRD 中未明确规划此功能。

---

### 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-06-25 | 初始版本，一期 MVP 需求 | zhaopuxuan |
| v1.1 | 2026-07-16 | Phase 0-7 实施后全面修订：SMTP 替代 Gmail OAuth、数据模型精简/扩展、API 调整、实现度总览 | zhaopuxuan |
| v1.2 | 2026-07-17 | 企业资料模块增强：外贸字段扩展、城市下拉选择、多图上传、产品图片、注册企业名自动带入 | zhaopuxuan |
| v1.3 | 2026-07-17 | 客户画像模块优化：公司规模多选、产品关联、价格结构化、草稿保存、列表字段扩展、二次编辑再生 | zhaopuxuan |
---

## 12. v1.2 变更记录

> 本章记录从 PRD v1.1（2026-07-16）到 v1.2（2026-07-17）期间的企业资料模块增强。

### 12.1 企业资料增强

#### 12.1.1 国家字段处理

| 维度 | v1.1 | v1.2 |
|------|------|------|
| 国家字段 | 前端自由文本输入 | **默认"中国"，前端隐藏**（目标用户均为中国国内外贸企业） |
| country 列 | 保留 | 保留，Schema 默认值 `"中国"` |

**变更理由**：产品定位面向中国国内外贸企业，国家信息无差异化价值，简化表单。

#### 12.1.2 城市字段改为下拉选择

| 维度 | v1.1 | v1.2 |
|------|------|------|
| 输入方式 | 自由文本 `<el-input>` | **下拉选择 `el-select` + filterable 模糊匹配** |
| 数据源 | 无 | 前端静态中国城市列表（`cities.json`，约 300+ 城市） |

#### 12.1.3 企业信息扩展（外贸采购商关注字段）

v1.1 企业资料仅包含基础联系信息，v1.2 新增以下外贸行业字段：

| 新增字段 | 类型 | 说明 |
|----------|------|------|
| `year_established` | INTEGER | 成立年份，体现企业经营历史 |
| `employee_count` | VARCHAR(50) | 员工规模，如 "50-100人" |
| `factory_area` | VARCHAR(100) | 工厂/厂房面积，如 "5000平方米" |
| `annual_export_volume` | VARCHAR(100) | 年度出口额，如 "500万美元" |
| `main_markets` | JSONB | 主要出口市场，如 `["北美","欧盟","东南亚"]` |
| `certifications` | JSONB | 认证资质，如 `["ISO 9001","CE","FDA"]` |
| `oem_odm` | VARCHAR(255) | OEM/ODM 代工能力描述 |
| `company_advantages` | TEXT | 企业特色/核心竞争力 |

**设计决策**：
- `main_markets`、`certifications` 使用 JSONB 数组，支持多选标签，无需额外关联表
- `employee_count`、`factory_area`、`annual_export_volume` 使用文本类型而非数值，适应"5000-10000平方米"等区间表述
- 字段全部可选（nullable），不影响现有租户

#### 12.1.4 企业图片上传

v1.1 仅有 logo 上传后端端点（前端未接入），v1.2 新增：

| 图片类型 | 存储字段 | 说明 |
|----------|----------|------|
| 企业 Logo | `logo_url` (VARCHAR) | 已有，本次接入前端 UI |
| 工厂实景 | `factory_photos` (JSONB) | 多图上传，展示生产环境 |
| 资质证件 | `certificate_photos` (JSONB) | 多图上传，展示认证证书 |

- 新增 `POST /api/v1/enterprise/photos?type=factory|certificate` 多图上传端点
- 复用现有 `uploads/` 文件存储 + `/uploads/` 静态服务
- 前端统一使用 `el-upload` 组件，支持拖拽、预览、删除

#### 12.1.5 注册企业名自动带入

| 维度 | v1.1 | v1.2 |
|------|------|------|
| 企业资料创建 | 用户手动填写 | **注册时自动创建 EnterpriseProfile，company_name 取自注册表单** |
| 已有租户兼容 | — | 首次访问企业资料页且无记录时，自动用 Tenant.name 创建 |

### 12.2 产品图片增强

#### 12.2.1 产品图片多图上传

| 维度 | v1.1 | v1.2 |
|------|------|------|
| 产品图片 | `image_url` VARCHAR(512) 单图文本 URL | **`images` JSONB 多图 URL 数组** |
| 上传方式 | 手动粘贴 URL | **新增 `POST /products/{id}/images` 上传端点** |

- 新增可复用 `ImageUpload.vue` 组件（多图上传 + 预览 + 拖拽排序）
- 迁移脚本：`image_url` 非空值转为 `images` 数组首元素

### 12.3 附带修复

- **产品路由注册**：`frontend/src/views/product/` 下完整页面文件存在但路由未注册，v1.2 在 `router/index.ts` 中注册 `/app/products`、`/app/products/create`、`/app/products/:id/edit` 三条路由

### 12.4 数据模型变更汇总

#### enterprise_profile 表新增字段

```sql
ALTER TABLE enterprise_profile
  ADD COLUMN year_established INTEGER,
  ADD COLUMN employee_count VARCHAR(50),
  ADD COLUMN factory_area VARCHAR(100),
  ADD COLUMN annual_export_volume VARCHAR(100),
  ADD COLUMN main_markets JSONB,
  ADD COLUMN certifications JSONB,
  ADD COLUMN oem_odm VARCHAR(255),
  ADD COLUMN company_advantages TEXT,
  ADD COLUMN factory_photos JSONB,
  ADD COLUMN certificate_photos JSONB;
```

#### product 表变更

```sql
ALTER TABLE product
  ADD COLUMN images JSONB;
-- 迁移: UPDATE product SET images = jsonb_build_array(image_url) WHERE image_url IS NOT NULL;
-- 后续: ALTER TABLE product DROP COLUMN image_url;
```

### 12.5 新增 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/enterprise/photos` | POST | 上传企业图片（type=factory|certificate），返回 URL |
| `/api/v1/products/{id}/images` | POST | 上传产品图片，返回 URL 数组 |

> **审批状态**：已实施
> **下一步**：v1.3 客户画像模块优化（详见 §13）

---

## 13. v1.3 变更记录

> 本章记录从 PRD v1.2（2026-07-17）到 v1.3（2026-07-17）期间的客户画像（ICP）模块优化。
> 变更范围：ICP 表单交互优化、产品关联、列表字段扩展、草稿与编辑功能完善。

### 13.1 需求概述

v1.3 聚焦于**客户画像（ICP）模块**的 6 项优化需求：

| # | 需求 | 类别 |
|---|------|------|
| 1 | 公司规模支持多选 | 表单优化 |
| 2 | 产品信息关联产品管理列表 | 架构变更 |
| 3 | 价格输入货币单位固定为美元 | 表单优化 |
| 4 | 新增保存草稿功能 | 功能完善 |
| 5 | 列表增加目标地区/行业/规模/预算字段 | 列表增强 |
| 6 | 已完成画像支持二次编辑并重新 AI 生成 | 功能完善 |

**关键设计决策：**

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 产品关联方式 | **完全替换为产品选择器** | 用户已确认——不再手动填写产品信息，直接从产品管理列表勾选 |
| 价格输入格式 | **最小/最大两个数字框 + 固定 USD 标签** | 结构化输入，避免自由文本格式不一致 |
| 重新生成策略 | **直接覆盖旧 output_data** | MVP 阶段不留版本历史，保持简洁 |
| 编辑入口 | **详情页内联编辑** | 无需额外跳转页面，改动最小 |

### 13.2 公司规模多选

#### 13.2.1 现状

ICP 创建表单 Step 0「目标市场」中 `company_size` 为单选下拉框，选项为：

- 小型企业（1-50人）
- 中型企业（50-200人）
- 大型企业（200-1000人）
- 超大型企业（1000人+）

但在实际外贸场景中，企业可能同时面向多种规模的客户（如既想找中型进口商，也愿意合作大型零售商）。

#### 13.2.2 变更

| 维度 | v1.2 | v1.3 |
|------|------|------|
| 前端控件 | `el-select` 单选 | `el-select` + `multiple` 多选 |
| Schema 类型 | `Optional[str]` | `Optional[List[str]]` |
| 已存储旧数据 | `"中型企业（50-200人）"` | 读取时自动包装为 `["中型企业（50-200人）"]` |
| AI Prompt | 直接传入字符串 | 以顿号连接后传入（如"小型企业（1-50人）、中型企业（50-200人）"） |

#### 13.2.3 兼容性

- 后端 `IcpInputData.company_size` 字段接受 `str | List[str]`，读取时统一转为 `List[str]`
- 已有 ICP 记录的 `input_data.company_size` 若为字符串，读取时自动包装为单元素列表
- 详情页显示时，数组以顿号连接展示

### 13.3 产品信息关联产品管理列表

#### 13.3.1 现状

ICP 创建表单 Step 1「产品信息」包含三个自由文本字段：

| 字段 | 说明 |
|------|------|
| `product_category` | 产品品类，如"蓝牙耳机、智能穿戴" |
| `product_price_range` | 价格区间，如"$15-50 / 件" |
| `product_features` | 产品特点/优势，如"ANC降噪、IPX5防水" |

用户需手动输入产品信息，可能与企业资料中已维护的产品数据不一致。

#### 13.3.2 变更

| 维度 | v1.2 | v1.3 |
|------|------|------|
| 产品输入方式 | 三个自由文本字段 | **从产品管理列表多选产品** |
| 数据存储 | 文本字段存入 `input_data` | 新增 `product_ids: List[str]` 存入 `input_data` |
| AI Prompt | 使用用户手填的文本 | 使用选中产品的完整信息（名称、描述、价格、MOQ、HS 编码等） |

#### 13.3.3 前端交互

新建/编辑 ICP 表单 Step 1 重构为：

1. **产品多选器**（`el-select` + `multiple` + `filterable`）：
   - 从 `GET /api/v1/products` 获取当前租户的产品列表
   - 支持输入过滤，显示产品名称、分类、单价
2. **已选产品展示**：每个选中产品显示摘要卡片（缩略图、名称、分类、价格），可删除
3. **上限**：最多选择 10 个产品
4. **自动填充**：选中产品后，均价区间自动计算（取自产品 `price_usd`），用户仍可手动覆盖

#### 13.3.4 AI Prompt 适配

AI 生成时，`IcpGenerator._build_user_prompt()` 处理逻辑：

```
if product_ids 非空:
    → 使用产品关联信息（名称、描述、价格、MOQ 等完整数据）填入 prompt 模板
elif 旧文本字段非空（已有 ICP）:
    → 回退到现有模板
else:
    → 标记为"未指定"
```

产品信息采用**快照方式**传入：前端在调用 generate 前将 `product_ids` 对应的产品完整数据嵌入 `input_data`，避免 SSE 流中持有数据库 session。

#### 13.3.5 字段废弃策略

| 字段 | 策略 | 说明 |
|------|------|------|
| `product_category` | **保留，废弃** | 旧 ICP 仍可读取，新创建 ICP 不再写入 |
| `product_price_range` | **保留，废弃** | 被 `product_price_min`/`product_price_max` 替代 |
| `product_features` | **保留，废弃** | 旧 ICP 仍可读取，新创建 ICP 不再写入 |
| `product_ids` | **新增** | 存储已选产品 UUID 列表 |

### 13.4 价格货币固定为美元

#### 13.4.1 现状

| 字段 | 当前格式 | 问题 |
|------|----------|------|
| `product_price_range` | 自由文本，如 "$15-50 / 件" | 格式不统一，AI 难以精确解析 |
| `customer_budget` | 自由文本，如 "$5,000-50,000 / 批" | 同上 |

#### 13.4.2 变更

| 维度 | v1.2 | v1.3 |
|------|------|------|
| `product_price_range` | 单个自由文本 | 拆分为 `product_price_min: float` + `product_price_max: float`（USD） |
| `customer_budget` | 单个自由文本 | 拆分为 `customer_budget_min: float` + `customer_budget_max: float`（USD） |
| 前端控件 | `<el-input>` 文本 | 两个 `<el-input-number>` + 固定 "USD" 标签 |
| 货币单位 | 用户自行输入 | **系统固定为美元（$ USD）** |

**前端表单示例**：

```
价格区间:  [$ 15.00]  —  [$ 200.00]  USD
客户预算:  [$ 5000]   —  [$ 50000]   USD
```

#### 13.4.3 与产品关联的联动

需求 13.3（产品关联）实施后，选中产品后可自动根据产品 `price_usd` 计算价格区间：
- `product_price_min` = 选中产品中的最低单价
- `product_price_max` = 选中产品中的最高单价
- 用户可手动修改覆盖

#### 13.4.4 兼容性

- AI Prompt 构建时优先使用新的结构化价格字段
- 若新字段为空但旧文本字段（`product_price_range`、`customer_budget`）有值，回退使用旧字段
- 旧字段保留在 Schema 中，不删除

### 13.5 保存草稿功能

#### 13.5.1 现状

| 维度 | 说明 |
|------|------|
| 数据库 | ICP 创建时 `status` 默认为 `"draft"` ✓ |
| 列表页 | 草稿统计卡片、草稿状态筛选 ✓ |
| 创建页 | **仅有"保存并生成画像"按钮**，无单独保存草稿入口 |
| 实际草稿 | 不存在——用户要么一次性完成创建+生成，要么放弃 |

#### 13.5.2 变更

| 维度 | 说明 |
|------|------|
| 创建页新增按钮 | Step 2 增加「保存草稿」按钮（secondary 样式） |
| 保存逻辑 | 调用 `POST /api/v1/icps`（与现有逻辑相同），**不触发 SSE 生成**，跳转至列表页 |
| 列表草稿入口 | 用户可在列表中筛选「草稿」状态，点击查看详情后编辑并生成 |

#### 13.5.3 交互流程

```
新建 ICP → 填写 3 步表单 → 点击「保存草稿」
→ POST /icps (status="draft") → 跳转至 ICP 列表页
→ 草稿统计 +1，列表中出现新记录（状态=草稿）
→ 点击查看详情 → 详情页显示「编辑」「重新生成」按钮
→ 编辑完善后点击「保存并重新生成」→ 生成画像
```

### 13.6 列表新增字段

#### 13.6.1 现状

ICP 列表仅显示四列：

| 列 | 宽度 |
|------|------|
| 画像名称 | 240px (min) |
| 状态 | 120px |
| 创建时间 | 180px |
| 操作（查看/删除） | 140px |

用户无法在列表中快速了解画像的核心参数（目标地区、行业、规模、预算）。

#### 13.6.2 变更

**新增列：**

| 新增列 | 数据来源 | 宽度 | 空值显示 |
|--------|----------|------|----------|
| 目标地区 | `input_data.target_region` | 120px | `—` |
| 目标行业 | `input_data.target_industry` | 120px | `—` |
| 公司规模 | `input_data.company_size` | 140px | `—` |
| 预算 | `input_data.customer_budget_min` + `_max` | 140px | `—` |

**后端适配：**

`IcpListItem` Schema 新增 `target_region`、`target_industry`、`company_size`、`customer_budget` 字段，从 `input_data` JSONB 中提取。由于 `input_data` 已在 ORM 对象中，无需额外的数据库查询：

```python
# Schema 层增加 computed 字段或手动填充
class IcpListItem(BaseModel):
    ...
    target_region: Optional[str] = None
    target_industry: Optional[str] = None
    company_size: Optional[List[str]] = None
    customer_budget: Optional[str] = None
```

列表 API 返回时从 `icp.input_data` 中提取对应键值。

**显示格式：**
- `company_size`：数组以顿号连接显示，如"小型企业、中型企业"
- `customer_budget`：格式化为 "$min — $max USD"，如 "$5,000 — $50,000 USD"

### 13.7 已完成画像支持二次编辑并重新生成

#### 13.7.1 现状

| 维度 | v1.2 |
|------|------|
| 「重新生成」按钮可见条件 | 仅 `status === 'draft' || status === 'failed'` |
| 编辑输入数据 | 无前端入口（`PUT /{icp_id}` 后端接口存在但前端未调用） |
| Store action | 无 `update` action |
| `completed` 状态 | **只读**，不可修改 |

#### 13.7.2 变更

| 维度 | v1.2 | v1.3 |
|------|------|------|
| 「重新生成」按钮 | 仅 draft/failed | **扩展至 completed** |
| 编辑入口 | 无 | **详情页「编辑输入信息」按钮** |
| 编辑方式 | — | **详情页内联编辑**（左侧输入摘要变为可编辑表单） |
| 保存 | — | `PUT /{icp_id}` 更新 → `POST /{icp_id}/generate` 重新生成 |
| Store | `create`、`remove` | **新增 `update(id, data)` action** |
| 覆盖确认 | 无 | `ElMessageBox.confirm`："重新生成将覆盖现有画像结果，是否继续？" |

#### 13.7.3 编辑交互流程

```
详情页（completed）→ 点击「编辑输入信息」
→ 左侧「输入信息」从 el-descriptions 切换为可编辑表单
→ 表单复用 Create 页的字段结构（含产品选择器、价格结构化输入等）
→ 点击「保存并重新生成」
→ ElMessageBox.confirm 二次确认
→ PUT /{icp_id} 更新 input_data
→ 详情页显示 SSE 流式生成进度
→ 生成完成 → 刷新详情页，显示新 output_data
```

#### 13.7.4 状态流转

```
draft     → [生成] → generating → completed ✓
completed → [编辑并重新生成] → generating → completed（覆盖）
failed    → [重新生成] → generating → completed
```

### 13.8 数据模型变更汇总

#### Schema 变更（IcpInputData）

| 字段 | 操作 | 旧类型 | 新类型 |
|------|------|--------|--------|
| `company_size` | 类型变更 | `Optional[str]` | `Optional[List[str]]` |
| `product_ids` | **新增** | — | `Optional[List[str]]` |
| `product_price_min` | **新增** | — | `Optional[float]` |
| `product_price_max` | **新增** | — | `Optional[float]` |
| `customer_budget_min` | **新增** | — | `Optional[float]` |
| `customer_budget_max` | **新增** | — | `Optional[float]` |
| `product_category` | 废弃（保留） | `Optional[str]` | 不变 |
| `product_price_range` | 废弃（保留） | `Optional[str]` | 不变 |
| `product_features` | 废弃（保留） | `Optional[str]` | 不变 |
| `customer_budget` | 废弃（保留） | `Optional[str]` | 不变 |

#### Schema 变更（IcpListItem）

| 字段 | 操作 | 来源 |
|------|------|------|
| `target_region` | **新增** | `input_data.target_region` |
| `target_industry` | **新增** | `input_data.target_industry` |
| `company_size` | **新增** | `input_data.company_size` |
| `customer_budget` | **新增** | `input_data.customer_budget_min` + `_max` 格式化 |

### 13.9 无数据库迁移

本次变更**无需 Alembic 迁移**：

- ICP 的 `input_data` 和 `output_data` 均使用 JSONB 存储，Schema 变更仅影响 Pydantic 校验层
- 新增字段（`product_ids`、价格 min/max）是 JSONB 内的键，新旧数据在同一 JSONB 列中共存
- `company_size` 类型变更：旧字符串值在读取时自动包装为单元素列表，无需数据库层面修改
- 废弃字段保留在 Schema 中，已有数据不受影响

### 13.10 风险与注意事项

| 风险 | 等级 | 缓解策略 |
|------|------|----------|
| AI Prompt 质量波动 | 中 | 产品关联改为实际产品数据后 prompt 内容更丰富，需关注生成效果；必要时微调 prompt 模板 |
| 向后兼容性 | 低 | 废弃字段保留在 Schema 中，读取优先新字段、回退旧字段 |
| Prompt 长度 | 低 | 前端限制最多选择 10 个产品，避免 prompt 超出 token 限制 |
| 旧数据 company_size 迁移 | 低 | 读取时自动检测并包装为列表，无需 ETL |

### 13.11 改动文件清单

#### 后端

| 文件 | 改动 |
|------|------|
| [backend/app/schemas/icp.py](../backend/app/schemas/icp.py) | `IcpInputData` 新增/废弃字段，`company_size` 类型变更；`IcpListItem` 新增 4 个显示字段 |
| [backend/app/api/icps.py](../backend/app/api/icps.py) | 列表查询提取 `input_data` 子字段填充 `IcpListItem`；generate 端点支持产品信息快照 |
| [backend/app/services/ai/icp_generator.py](../backend/app/services/ai/icp_generator.py) | Prompt 模板适配 `product_ids` + 结构化价格 + 公司规模数组 |

#### 前端

| 文件 | 改动 |
|------|------|
| [frontend/src/stores/icp.ts](../frontend/src/stores/icp.ts) | `IcpInputData`/`IcpItem` 接口更新，新增 `update()` action |
| [frontend/src/views/icp/IcpCreate.vue](../frontend/src/views/icp/IcpCreate.vue) | Step 0 公司规模多选；Step 1 完全重构为产品选择器；Step 2 价格结构化 + 草稿按钮 |
| [frontend/src/views/icp/IcpListView.vue](../frontend/src/views/icp/IcpListView.vue) | 表格新增 4 列 |
| [frontend/src/views/icp/IcpDetail.vue](../frontend/src/views/icp/IcpDetail.vue) | 编辑模式、重新生成扩展到 completed、覆盖确认 |
| [frontend/src/views/icp/components/ProductSelector.vue](../frontend/src/views/icp/components/ProductSelector.vue) | **新增** — 可复用产品多选组件 |

#### 文档

| 文件 | 改动 |
|------|------|
| [docs/prd.md](../docs/prd.md) | 新增 §13 v1.3 变更记录 |

### 13.12 验证方式

| # | 验证项 | 验证步骤 |
|---|--------|----------|
| 1 | 公司规模多选 | 创建 ICP 时多选 2+ 个规模 → 检查详情页/列表正确显示 |
| 2 | 产品关联 | 新建 ICP 时从产品列表选择产品 → 验证 AI 生成 prompt 包含完整产品信息 |
| 3 | 价格结构化 | 输入 min/max 价格 → 检查列表预算列格式化正确 → AI 输出使用 USD 单位 |
| 4 | 草稿保存 | 保存草稿 → 列表「草稿」统计 +1 → 详情页可重新生成 |
| 5 | 列表新字段 | 检查列表 4 个新增列正确显示，空值显示 `—` |
| 6 | 二次编辑 | 编辑已完成 ICP → 修改输入 → 重新生成 → 验证 output_data 更新且无重复 |
