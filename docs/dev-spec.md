# AI 外贸助手 — 开发实施规约 (Dev Spec)

> **面向对象**：AI（Vibe Coding）及开发者
> **配套文档**：[PRD](./prd.md) — 产品需求定义
> **版本**：v1.0 | **日期**：2026-06-25
>
> 本文档是 AI 编写代码的**执行手册**。每个章节回答一个实施问题：「建什么文件、写成什么样、按什么顺序做」。

---

## 目录

1. [项目初始化](#1-项目初始化)
2. [路由与页面清单](#2-路由与页面清单)
3. [UI Shell 布局](#3-ui-shell-布局)
4. [组件拆解](#4-组件拆解)
5. [Pinia 状态管理](#5-pinia-状态管理)
6. [API 端点契约](#6-api-端点契约)
7. [数据库迁移与种子数据](#7-数据库迁移与种子数据)
8. [SSE 流式输出实现](#8-sse-流式输出实现)
9. [认证与授权实现](#9-认证与授权实现)
10. [环境配置与 Docker](#10-环境配置与-docker)
11. [实现依赖图与执行顺序](#11-实现依赖图与执行顺序)
12. [交互状态矩阵](#12-交互状态矩阵)

---

## 1. 项目初始化

### 1.1 仓库结构

```
Foreign trade agent/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 应用入口
│   │   ├── config.py           # 配置管理（pydantic-settings）
│   │   ├── database.py         # SQLAlchemy async engine + session
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 请求/响应 Schema
│   │   ├── api/                # 路由模块（按资源划分）
│   │   ├── services/           # 业务逻辑层
│   │   ├── core/               # 认证、安全、中间件
│   │   └── utils/              # 工具函数
│   ├── alembic/                # 数据库迁移
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/             # Vue Router
│   │   ├── stores/             # Pinia
│   │   ├── api/                # Axios 封装 + API 调用
│   │   ├── views/              # 页面组件（对应路由）
│   │   ├── components/         # 公共组件
│   │   ├── layouts/            # 布局组件
│   │   ├── composables/        # 组合式函数
│   │   └── utils/              # 工具函数
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
└── .github/
```

### 1.2 依赖清单

#### 后端 (requirements.txt)

```
fastapi==0.115.*
uvicorn[standard]==0.34.*
sqlalchemy[asyncio]==2.0.*
asyncpg==0.30.*
alembic==1.14.*
pydantic==2.*
pydantic-settings==2.*
python-jose[cryptography]==3.3.*
passlib[bcrypt]==1.7.*
redis==5.2.*
httpx==0.28.*
openai==1.*                    # DeepSeek 兼容 OpenAI SDK
python-multipart==0.0.*
elasticsearch[async]==8.*
python-dotenv==1.0.*
celery==5.4.*                  # 异步任务（邮件发送）
pytest==8.*
pytest-asyncio==0.24.*
httpx==0.28.*
```

#### 前端 (package.json dependencies)

```json
{
  "dependencies": {
    "vue": "^3.5",
    "vue-router": "^4.5",
    "pinia": "^2.2",
    "element-plus": "^2.9",
    "@element-plus/icons-vue": "^2.3",
    "axios": "^1.7",
    "dayjs": "^1.11",
    "marked": "^14.0",
    "dompurify": "^3.2",
    "@vueuse/core": "^11.0"
  },
  "devDependencies": {
    "vite": "^6.0",
    "@vitejs/plugin-vue": "^5.2",
    "typescript": "^5.6",
    "unplugin-auto-import": "^0.18",
    "unplugin-vue-components": "^0.27",
    "sass": "^1.80",
    "vitest": "^2.1",
    "@vue/test-utils": "^2.4"
  }
}
```

### 1.3 Vite 配置要点

```ts
// vite.config.ts 核心配置
{
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',  // 代理到 FastAPI
      '/sse': {                          // SSE 不走缓存
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: { '@': '/src' }
  }
}
```

---

## 2. 路由与页面清单

### 2.1 完整路由表

> 同一 Vue 项目，按路由前缀区分用户端和管理后台。

```
【公开路由 — 无 Layout 壳】
/                            → 重定向到 /app/dashboard
/login                       → views/auth/LoginView.vue          （用户端登录）
/register                    → views/auth/RegisterView.vue       （用户端注册）
/admin/login                 → views/auth/AdminLoginView.vue     （管理后台登录）

【用户端 — /app/* — MainLayout 壳】
/app/dashboard               → views/dashboard/DashboardView.vue
/app/enterprise              → views/enterprise/EnterpriseView.vue
/app/enterprise/edit         → views/enterprise/EnterpriseEdit.vue
/app/products                → views/product/ProductListView.vue
/app/products/create         → views/product/ProductCreate.vue
/app/products/:id/edit       → views/product/ProductEdit.vue
/app/icps                    → views/icp/IcpListView.vue
/app/icps/create             → views/icp/IcpCreate.vue
/app/icps/:id                → views/icp/IcpDetail.vue
/app/customers               → views/customer/CustomerListView.vue
/app/customers/:id           → views/customer/CustomerDetail.vue
/app/email/templates         → views/email/TemplateListView.vue
/app/email/templates/create  → views/email/TemplateCreate.vue
/app/email/templates/:id/edit → views/email/TemplateEdit.vue
/app/email/campaigns         → views/email/CampaignListView.vue
/app/email/campaigns/create  → views/email/CampaignCreate.vue
/app/email/campaigns/:id     → views/email/CampaignDetail.vue
/app/settings                → views/settings/SettingsView.vue
/app/settings/members        → views/settings/MemberListView.vue （超管/管理员）

【管理后台 — /admin/* — AdminLayout 壳】
/admin/dashboard             → views/admin/DashboardView.vue     （运营仪表盘）
/admin/tenants               → views/admin/TenantListView.vue    （租户列表）
/admin/tenants/:id           → views/admin/TenantDetailView.vue  （租户详情）
/admin/settings              → views/admin/SettingsView.vue      （系统配置，二期）
```

### 2.2 路由守卫逻辑

```
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // ── 公开路由 ──
  if (to.path === '/login' || to.path === '/register') {
    if (authStore.isAuthenticated) return next('/app/dashboard')
    return next()
  }

  // 管理后台登录
  if (to.path === '/admin/login') {
    if (authStore.isAdminAuthenticated) return next('/admin/dashboard')
    return next()
  }

  // ── 管理后台鉴权 ──
  if (to.path.startsWith('/admin')) {
    if (!authStore.isAdminAuthenticated) return next('/admin/login')
    return next()
  }

  // ── 用户端鉴权 ──
  if (!authStore.isAuthenticated) return next('/login')

  // 权限路由
  if (to.path === '/app/settings/members' && !authStore.canManageMembers) {
    return next('/app/settings')
  }

  next()
})
```

---

## 3. UI Shell 布局

### 3.1 MainLayout 结构

```
┌──────────────────────────────────────────────┐
│  Sidebar（固定 220px）         │  Header（64px）│
│  ┌─────────────┐              │  ┌───────────┐ │
│  │ Logo        │              │  │面包屑 通知 用户│ │
│  │ 导航菜单     │              │  └───────────┘ │
│  │  - 工作台   │              ├─────────────────│
│  │  - 客户画像  │              │                 │
│  │  - 客户管理  │              │  <router-view>  │
│  │  - 邮件营销  │              │   页面内容区     │
│  │  - 产品管理  │              │   (min-height   │
│  │  - 企业资料  │              │    calc(...))   │
│  │  - 系统设置  │              │                 │
│  │             │              │                 │
│  │  收起/展开   │              │                 │
│  └─────────────┘              │                 │
└──────────────────────────────────────────────┘
```

### 3.2 Layout 组件文件

```
layouts/
├── MainLayout.vue          # 主壳：Sidebar + Header + Content
├── AuthLayout.vue          # 登录/注册壳：居中卡片
├── components/
│   ├── SidebarNav.vue      # 左侧导航菜单
│   ├── HeaderBar.vue       # 顶部栏
│   └── BreadcrumbNav.vue   # 面包屑
```

### 3.3 导航菜单定义

```ts
// router/navMenu.ts — 用户端菜单
export const appNavItems = [
  { path: '/app/dashboard',   title: '工作台',   icon: 'Monitor',    roles: ['*'] },
  { path: '/app/icps',         title: '客户画像', icon: 'PictureFilled', roles: ['*'] },
  { path: '/app/customers',    title: '客户管理', icon: 'UserFilled',  roles: ['*'] },
  { path: '/app/email/templates', title: '邮件营销', icon: 'Message', roles: ['*'],
    children: [
      { path: '/app/email/templates', title: '邮件模板' },
      { path: '/app/email/campaigns', title: '发送任务' },
    ]
  },
  { path: '/app/products',     title: '产品管理', icon: 'Goods',      roles: ['*'] },
  { path: '/app/enterprise',   title: '企业资料', icon: 'OfficeBuilding', roles: ['*'] },
  { path: '/app/settings',     title: '系统设置', icon: 'Setting',     roles: ['super_admin', 'admin'] },
]

// 管理后台菜单
export const adminNavItems = [
  { path: '/admin/dashboard',  title: '运营仪表盘', icon: 'DataAnalysis' },
  { path: '/admin/tenants',    title: '租户管理',   icon: 'OfficeBuilding' },
  { path: '/admin/settings',   title: '系统配置',   icon: 'Setting',   roles: ['super_admin'] },
]
```

---

## 4. 组件拆解

### 4.1 ICP 画像模块

```
views/icp/
├── IcpListView.vue            页面：画像列表
│   ├── IcpCard.vue            画像卡片（名称/日期/状态/操作按钮）
│   ├── EmptyState.vue         空状态（公共组件，无画像时展示引导）
│   └── ConfirmDialog.vue      确认删除弹窗（公共组件）

├── IcpCreate.vue              页面：新建画像（多步骤表单）
│   ├── IcpFormStep1.vue       步骤1：本企业信息（自动拉取企业资料）
│   ├── IcpFormStep2.vue       步骤2：期望客户特征
│   ├── IcpFormStep3.vue       步骤3：客户样例（可选）
│   └── IcpGeneratePanel.vue   生成面板：进度条 + 流式输出 + 结果预览

├── IcpDetail.vue              页面：画像详情
│   ├── IcpOutputCard.vue      画像输出结果卡片（渲染 AI 生成的画像内容）
│   └── IcpActionBar.vue       操作栏：修改后保存 / 重新生成 / 删除
```

#### IcpCard.vue 组件契约

```ts
// Props
interface IcpCardProps {
  icp: {
    id: string
    name: string
    status: 'draft' | 'generated' | 'archived'
    createdAt: string
    targetIndustries: string[]
    targetCountries: string[]
  }
}

// Emits
// @delete -> icpId: string
// @archive -> icpId: string
```

#### IcpGeneratePanel.vue 组件契约

```ts
// Props
interface GeneratePanelProps {
  formData: IcpCreatePayload   // 三步表单的完整数据
  visible: boolean
}

// Emits
// @generated -> IcpOutput      // 生成完成，传出结果
// @error -> string             // 生成失败
// @close                       // 关闭面板

// States: idle | streaming | completed | error
// idle: 点击「生成」前
// streaming: 流式输出中，展示实时文本 + 进度条
// completed: 全部输出完成，展示画像卡片预览
// error: 展示错误信息 + 重试按钮
```

### 4.2 客户管理模块

```
views/customer/
├── CustomerListView.vue          页面：客户列表
│   ├── CustomerFilterBar.vue     筛选栏：画像/行业/国家/评分/状态
│   ├── CustomerTable.vue         表格视图（Element Plus Table）
│   ├── CustomerCard.vue          卡片视图（网格布局，与表格切换）
│   ├── CustomerSearchPanel.vue   搜索面板：选择画像 → 勾选渠道 → 开始搜索
│   │   ├── ChannelSelector.vue   渠道选择器（Google/LinkedIn 复选框）
│   │   └── SearchProgress.vue    搜索进度：各渠道实时计数
│   ├── BatchActions.vue          批量操作栏：标记/导出/加入营销/补全信息
│   └── EnrichProgress.vue        信息补全进度弹窗

├── CustomerDetail.vue            页面：客户详情
│   ├── CustomerInfoCard.vue      企业基础信息卡片
│   ├── ContactList.vue           联系人列表
│   │   └── ContactCard.vue       联系人卡片（姓名/职位/邮箱/决策层级/有效标记）
│   └── ActivityTimeline.vue      活动时间线（搜索/补全/发送邮件等操作记录）
```

### 4.3 邮件营销模块

```
views/email/
├── TemplateListView.vue          页面：模板列表
│   └── TemplateCard.vue          模板卡片

├── TemplateCreate.vue / TemplateEdit.vue  页面：新建/编辑模板
│   ├── TemplateForm.vue          模板表单（画像选择/产品选择/语气/CTA/样例）
│   ├── TemplatePreview.vue       实时预览面板（变量高亮）
│   │   └── VariableHighlighter.vue  变量 `{{...}}` 语法高亮
│   ├── SpamScoreGauge.vue        垃圾邮件评分仪表
│   └── TestSendDialog.vue        测试发送弹窗

├── CampaignListView.vue          页面：发送任务列表
│   ├── CampaignCard.vue          任务卡片（进度环/状态/统计）
│   └── CampaignStatusBadge.vue   状态徽标

├── CampaignCreate.vue            页面：新建发送任务
│   ├── TemplateSelector.vue      模板选择器（带预览）
│   ├── CustomerSelector.vue      客户选择器（多选 + 搜索 + 筛选）
│   ├── EmailPreview.vue          最终邮件预览（变量已替换）
│   └── SchedulePicker.vue        定时发送选择器

├── CampaignDetail.vue            页面：发送任务详情
│   ├── CampaignStats.vue         统计卡片：已发送 / 成功 / 失败 / 打开 / 点击
│   ├── SendLogTable.vue          单封发送记录表格
│   └── CampaignActions.vue       操作按钮：暂停 / 继续 / 取消
```

### 4.4 公共组件清单

```
components/
├── common/
│   ├── EmptyState.vue          # 空状态占位（图标 + 文案 + 操作按钮）
│   ├── LoadingSkeleton.vue     # 骨架屏
│   ├── ConfirmDialog.vue       # 确认弹窗（标题/描述/确认/取消）
│   ├── ErrorMessage.vue        # 错误提示（可关闭 + 重试按钮）
│   ├── StatusBadge.vue         # 状态徽标（支持多种状态颜色映射）
│   ├── PageHeader.vue          # 页面标题栏（标题 + 面包屑 + 操作按钮 slot）
│   └── DataExportButton.vue    # 导出按钮（Excel/CSV 下拉选择）
├── ai/
│   ├── StreamingOutput.vue     # 流式文本输出组件（打字机效果）
│   └── AiGenerationPanel.vue   # AI 生成通用面板（输入→进度→输出）
└── email/
    ├── EmailEditor.vue         # 邮件富文本编辑器（基于 Quill/TinyMCE）
    └── VariableSelector.vue    # 变量插入选择器
```

---

## 5. Pinia 状态管理

### 5.1 Store 拆分

```
stores/
├── auth.ts          # 认证状态
├── enterprise.ts    # 企业资料
├── product.ts       # 产品管理
├── icp.ts           # 客户画像
├── customer.ts      # 客户管理 + 搜索状态 + 联系人
├── email.ts         # 邮件模板 + 发送任务
├── tenant.ts        # 租户/成员管理
└── ui.ts            # 全局 UI 状态（侧栏折叠、loading 遮罩等）
```

### 5.2 核心 Store 定义

#### auth.ts

```ts
interface AuthState {
  user: User | null           // 当前用户信息
  token: string | null        // JWT access token
  refreshToken: string | null
  tenant: Tenant | null       // 当前租户

  // Computed (getters)
  isAuthenticated: boolean
  userRole: string
  canManageMembers: boolean   // role in ['super_admin', 'admin']
  tenantId: string | null
}

// Actions
login(email: string, password: string): Promise<void>
register(data: RegisterPayload): Promise<void>
logout(): void
refreshAccessToken(): Promise<void>
fetchCurrentUser(): Promise<void>
```

#### icp.ts

```ts
interface IcpState {
  list: Icp[]                 // 画像列表
  current: Icp | null         // 当前查看/编辑的画像
  listLoading: boolean
  generateStatus: 'idle' | 'streaming' | 'completed' | 'error'
  streamContent: string       // 流式输出的当前文本
}

// Actions
fetchList(params: PaginationParams): Promise<void>
fetchById(id: string): Promise<void>
create(data: IcpCreatePayload): Promise<Icp>
generate(data: IcpCreatePayload): Promise<Icp>  // 触发 SSE 生成
update(id: string, data: Partial<Icp>): Promise<void>
remove(id: string): Promise<void>
cancelGeneration(): void
```

#### customer.ts

```ts
interface CustomerState {
  list: Customer[]
  current: Customer | null
  total: number
  filters: CustomerFilter    // 画像 / 行业 / 国家 / 评分 / 状态
  searchStatus: 'idle' | 'searching' | 'completed' | 'error'
  searchProgress: ChannelProgress[]   // 各渠道实时计数
  selectedIds: Set<string>   // 批量操作选中项
  enrichStatus: Record<string, 'pending' | 'loading' | 'done' | 'error'>
}

interface ChannelProgress {
  channel: 'google' | 'linkedin' | 'facebook' | 'amazon'
  found: number
  status: 'pending' | 'searching' | 'done' | 'error'
}

// Actions
fetchList(params: CustomerListParams): Promise<void>
fetchById(id: string): Promise<void>
searchCustomers(icpId: string, channels: string[], limit: number): Promise<void>
cancelSearch(): void
batchUpdateStatus(ids: string[], status: string): Promise<void>
enrichContacts(customerIds: string[]): Promise<void>
batchExport(ids: string[], format: 'xlsx' | 'csv'): Promise<Blob>
```

#### email.ts

```ts
interface EmailState {
  templates: EmailTemplate[]
  currentTemplate: EmailTemplate | null
  campaigns: Campaign[]
  currentCampaign: Campaign | null
  generateStatus: 'idle' | 'streaming' | 'completed' | 'error'
  streamContent: string
}

// Actions — 模板
fetchTemplates(params: PaginationParams): Promise<void>
fetchTemplateById(id: string): Promise<void>
generateTemplate(data: TemplateGeneratePayload): Promise<EmailTemplate>
updateTemplate(id: string, data: Partial<EmailTemplate>): Promise<void>
deleteTemplate(id: string): Promise<void>
testSend(templateId: string, toEmail: string): Promise<void>

// Actions — 发送任务
fetchCampaigns(params: PaginationParams): Promise<void>
fetchCampaignById(id: string): Promise<void>
createCampaign(data: CampaignCreatePayload): Promise<Campaign>
pauseCampaign(id: string): Promise<void>
resumeCampaign(id: string): Promise<void>
cancelCampaign(id: string): Promise<void>
```

---

## 6. API 端点契约

### 6.1 认证

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `POST` | `/api/v1/auth/register` | `{ email, password, name, company_name }` | `{ user, token, refresh_token, tenant }` | 注册即创建租户 |
| `POST` | `/api/v1/auth/login` | `{ email, password }` | `{ user, token, refresh_token, tenant }` | |
| `POST` | `/api/v1/auth/refresh` | `{ refresh_token }` | `{ token, refresh_token }` | |
| `GET` | `/api/v1/auth/me` | — | `{ user, tenant, permissions }` | 当前用户信息 |
| `POST` | `/api/v1/auth/logout` | — | `{ success: true }` | 废弃 refresh_token |

### 6.2 企业资料

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `GET` | `/api/v1/enterprise` | — | `EnterpriseProfile` | 当前租户的企业资料 |
| `PUT` | `/api/v1/enterprise` | `EnterpriseProfile` | `EnterpriseProfile` | 创建或更新 |
| `POST` | `/api/v1/enterprise/logo` | `multipart/form-data` | `{ url }` | 上传企业 Logo |

### 6.3 产品

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `GET` | `/api/v1/products` | `?page=&page_size=&keyword=` | `{ total, page, page_size, items: Product[] }` | |
| `POST` | `/api/v1/products` | `ProductCreate` | `Product` | |
| `GET` | `/api/v1/products/{id}` | — | `Product` | |
| `PUT` | `/api/v1/products/{id}` | `ProductUpdate` | `Product` | |
| `DELETE` | `/api/v1/products/{id}` | — | `{ success: true }` | |

### 6.4 客户画像 (ICP)

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `GET` | `/api/v1/icps` | `?page=&page_size=&status=` | `PaginatedResponse<Icp>` | |
| `POST` | `/api/v1/icps` | `IcpCreate` | `Icp` | 仅保存草稿 |
| `GET` | `/api/v1/icps/{id}` | — | `Icp` | |
| `PUT` | `/api/v1/icps/{id}` | `IcpUpdate` | `Icp` | |
| `DELETE` | `/api/v1/icps/{id}` | — | `{ success: true }` | |
| `POST` | `/api/v1/icps/{id}/generate` | — | **SSE 流** | 触发 AI 生成 |
| `POST` | `/api/v1/icps/generate` | `IcpCreate` (不存草稿直接生成) | **SSE 流** | 新建+生成一步完成 |

#### SSE 事件格式

```
event: progress
data: {"stage": "analyzing", "message": "正在分析企业信息..."}

event: chunk
data: {"field": "target_keywords", "content": "outdoor"}

event: chunk
data: {"field": "target_keywords", "content": " equipment"}

event: complete
data: {"icp_id": "uuid", "output": {...完整画像 JSON...}}

event: error
data: {"code": "GENERATION_FAILED", "message": "AI 服务暂时不可用，请重试"}
```

### 6.5 客户管理

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `GET` | `/api/v1/customers` | `?page=&page_size=&icp_id=&industry=&country=&score_min=&status=&keyword=` | `PaginatedResponse<Customer>` | |
| `GET` | `/api/v1/customers/{id}` | — | `CustomerWithContacts` | 含联系人列表 |
| `PUT` | `/api/v1/customers/{id}` | `CustomerUpdate` | `Customer` | |
| `DELETE` | `/api/v1/customers/{id}` | — | `{ success: true }` | |
| `POST` | `/api/v1/customers/batch-status` | `{ ids: [], status: "" }` | `{ updated: N }` | 批量修改状态 |
| `GET` | `/api/v1/customers/export` | `?ids=...&format=xlsx` | `Blob` (文件流) | |
| `POST` | `/api/v1/customers/search` | `{ icp_id, channels: [], limit }` | **SSE 流** | 触发多渠道搜索 |
| `POST` | `/api/v1/customers/{id}/enrich` | — | `{ job_id }` | 触发信息补全（异步） |
| `POST` | `/api/v1/customers/batch-enrich` | `{ ids: [] }` | `{ job_id }` | 批量补全 |

### 6.6 邮件模板

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `GET` | `/api/v1/email-templates` | `?page=&page_size=` | `PaginatedResponse<EmailTemplate>` | |
| `POST` | `/api/v1/email-templates` | `TemplateCreate` | `EmailTemplate` | 手动创建 |
| `GET` | `/api/v1/email-templates/{id}` | — | `EmailTemplate` | |
| `PUT` | `/api/v1/email-templates/{id}` | `TemplateUpdate` | `EmailTemplate` | |
| `DELETE` | `/api/v1/email-templates/{id}` | — | `{ success: true }` | |
| `POST` | `/api/v1/email-templates/generate` | `TemplateGeneratePayload` | **SSE 流** | AI 生成 |
| `POST` | `/api/v1/email-templates/{id}/test-send` | `{ to_email }` | `{ success: true }` | 发送测试邮件到指定邮箱 |

### 6.7 邮件发送任务

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `GET` | `/api/v1/email-campaigns` | `?page=&page_size=&status=` | `PaginatedResponse<Campaign>` | |
| `POST` | `/api/v1/email-campaigns` | `CampaignCreate` | `Campaign` | |
| `GET` | `/api/v1/email-campaigns/{id}` | — | `CampaignDetail` (含 stats + logs) | |
| `POST` | `/api/v1/email-campaigns/{id}/pause` | — | `Campaign` | |
| `POST` | `/api/v1/email-campaigns/{id}/resume` | — | `Campaign` | |
| `POST` | `/api/v1/email-campaigns/{id}/cancel` | — | `Campaign` | |
| `GET` | `/api/v1/email-campaigns/{id}/logs` | `?page=&page_size=&status=` | `PaginatedResponse<SendLog>` | |
| `POST` | `/api/v1/email-campaigns/{id}/preview` | `{ customer_ids: [] }` | `{ previews: [{customer_id, subject, body_html}] }` | 变量替换后的预览 |

### 6.8 邮箱 OAuth（Gmail）

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `GET` | `/api/v1/email-auth/gmail/url` | — | `{ auth_url }` | 返回 Google OAuth 授权 URL |
| `POST` | `/api/v1/email-auth/gmail/callback` | `{ code }` | `{ connected: true, email }` | OAuth 回调，保存 token |
| `GET` | `/api/v1/email-auth/status` | — | `{ provider, connected, email, quota_remaining }` | 邮箱连接状态 |
| `DELETE` | `/api/v1/email-auth/{provider}` | — | `{ success: true }` | 断开邮箱连接 |

### 6.9 管理后台 API

| Method | Path | Request Body | Response | 说明 |
|--------|------|-------------|----------|------|
| `POST` | `/api/v1/admin/auth/login` | `{ email, password }` | `{ admin, token }` | 平台管理员登录 |
| `POST` | `/api/v1/admin/auth/logout` | — | `{ success: true }` | 登出 |
| `GET` | `/api/v1/admin/auth/me` | — | `PlatformAdmin` | 当前管理员信息 |
| `GET` | `/api/v1/admin/tenants` | `?page=&page_size=&status=&keyword=` | `PaginatedResponse<Tenant>` | 租户列表 |
| `GET` | `/api/v1/admin/tenants/{id}` | — | `TenantDetail`（含成员数/画像数/客户数/邮件统计） | 租户详情 |
| `POST` | `/api/v1/admin/tenants/{id}/suspend` | — | `Tenant` | 停用租户 |
| `POST` | `/api/v1/admin/tenants/{id}/activate` | — | `Tenant` | 启用租户 |
| `GET` | `/api/v1/admin/dashboard` | — | `{ total_tenants, active_tenants, total_users, today_tokens, today_emails, chart_data }` | 运营仪表盘 |
| `GET` | `/api/v1/admin/logs` | `?page=&page_size=&admin_id=&action=` | `PaginatedResponse<AdminLog>` | 操作日志 |

### 6.10 统一错误码

```json
{
  "AUTH_INVALID_CREDENTIALS":  "邮箱或密码错误",
  "AUTH_TOKEN_EXPIRED":        "登录已过期，请重新登录",
  "AUTH_EMAIL_EXISTS":         "该邮箱已注册",
  "FORBIDDEN":                 "无权访问该资源",
  "TENANT_QUOTA_EXCEEDED":     "已超出当前套餐配额",
  "NOT_FOUND":                 "资源不存在",
  "VALIDATION_ERROR":          "输入校验失败",
  "AI_GENERATION_FAILED":      "AI 生成失败",
  "AI_TIMEOUT":                "AI 响应超时",
  "SEARCH_FAILED":             "搜索执行失败",
  "EMAIL_SEND_FAILED":         "邮件发送失败",
  "EMAIL_AUTH_REQUIRED":       "请先连接邮箱",
  "EMAIL_QUOTA_EXCEEDED":      "邮箱今日发送配额已用完",
  "RATE_LIMITED":              "请求过于频繁，请稍后再试",
  "INTERNAL_ERROR":            "服务器内部错误"
}
```

---

## 7. 数据库迁移与种子数据

### 7.1 Alembic 初始化

```bash
cd backend
alembic init alembic
# 修改 alembic/env.py 使用异步引擎
```

### 7.2 初始迁移（upgrade）

```sql
-- 创建 uuid-ossp 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建枚举类型
CREATE TYPE plan_type AS ENUM ('free', 'pro', 'enterprise');
CREATE TYPE tenant_status AS ENUM ('active', 'suspended', 'cancelled');
CREATE TYPE icp_status AS ENUM ('draft', 'generated', 'archived');
CREATE TYPE customer_status AS ENUM ('new', 'interested', 'not_interested', 'marketing');
CREATE TYPE email_validity AS ENUM ('valid', 'invalid', 'risky', 'unknown');
CREATE TYPE decision_level AS ENUM ('c_level', 'vp', 'director', 'manager', 'staff');
CREATE TYPE campaign_status AS ENUM ('draft', 'scheduled', 'sending', 'completed', 'paused', 'cancelled');

-- 创建所有表（基于 PRD 第6章 SQL 定义）
-- ...（详见 PRD 6.2）

-- 创建索引
CREATE INDEX idx_customer_tenant ON customer(tenant_id);
CREATE INDEX idx_customer_icp ON customer(icp_id);
CREATE INDEX idx_customer_status ON customer(status);
CREATE INDEX idx_customer_country ON customer(country);
CREATE INDEX idx_customer_match_score ON customer(match_score DESC);
CREATE INDEX idx_contact_customer ON contact(customer_id);
CREATE INDEX idx_contact_email ON contact(email);
CREATE INDEX idx_email_template_tenant ON email_template(tenant_id);
CREATE INDEX idx_email_campaign_tenant ON email_campaign(tenant_id);
CREATE INDEX idx_email_campaign_status ON email_campaign(status);
CREATE INDEX idx_email_log_campaign ON email_log(campaign_id);
CREATE INDEX idx_unsubscribe_tenant ON unsubscribe_list(tenant_id);
CREATE INDEX idx_unsubscribe_email ON unsubscribe_list(email);

-- 租户行级安全（可选，未来增强）
-- ALTER TABLE customer ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY tenant_isolation ON customer USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### 7.3 种子数据

```python
# backend/app/seed.py — 开发/测试用种子数据
# 不包含真实用户数据，仅行业枚举、国家列表等元数据

INDUSTRIES = [...]
COUNTRIES = [...]
```

---

## 8. SSE 流式输出实现

### 8.1 后端（FastAPI）

```python
# backend/app/api/icp.py
from fastapi.responses import StreamingResponse
import json

@router.post("/icps/{icp_id}/generate")
async def generate_icp(icp_id: UUID, current_user: User = Depends(get_current_user)):
    icp = await icp_service.get_by_id(icp_id, current_user.tenant_id)

    async def event_stream():
        try:
            # 阶段1：分析
            yield f"event: progress\ndata: {json.dumps({'stage': 'analyzing', 'message': '正在分析企业信息...'})}\n\n"

            # 阶段2：流式生成
            async for chunk in ai_service.generate_icp_stream(icp.input_data):
                yield f"event: chunk\ndata: {json.dumps(chunk)}\n\n"

            # 阶段3：完成
            yield f"event: complete\ndata: {json.dumps({'icp_id': str(icp_id), 'output': icp.output_data})}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'code': 'AI_GENERATION_FAILED', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",   # 禁用 Nginx 缓冲
        }
    )
```

### 8.2 前端（Vue 3 Composable）

```ts
// frontend/src/composables/useSSE.ts
export function useSSE() {
  const content = ref('')
  const stage = ref('')
  const isStreaming = ref(false)
  const error = ref<string | null>(null)
  let abortController: AbortController | null = null

  async function connect(url: string, body?: any) {
    abortController = new AbortController()
    isStreaming.value = true
    error.value = null
    content.value = ''

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: abortController.signal,
    })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()

    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // SSE 协议解析
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''     // 不完整的行留在 buffer

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7)
        } else if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          handleEvent(currentEvent, data)
        }
      }
    }
    isStreaming.value = false
  }

  function handleEvent(event: string, data: any) {
    switch (event) {
      case 'progress':
        stage.value = data.message
        break
      case 'chunk':
        content.value += data.content   // 打字机效果累积
        break
      case 'complete':
        stage.value = 'completed'
        break
      case 'error':
        error.value = data.message
        break
    }
  }

  function cancel() {
    abortController?.abort()
    isStreaming.value = false
  }

  onUnmounted(() => { abortController?.abort() })

  return { content, stage, isStreaming, error, connect, cancel }
}
```

### 8.3 StreamingOutput.vue（打字机效果组件）

```vue
<template>
  <div class="streaming-output">
    <div v-if="isStreaming" class="streaming-indicator">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>{{ stage }}</span>
    </div>
    <div class="content" v-html="renderedContent"></div>
    <el-alert v-if="error" type="error" :title="error" show-icon closable />
  </div>
</template>

<script setup lang="ts">
// 使用 marked + DOMPurify 渲染 Markdown
const renderedContent = computed(() => DOMPurify.sanitize(marked.parse(props.content)))
</script>
```

---

## 9. 认证与授权实现

### 9.1 JWT 设计

```python
# Access Token Payload
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "role": "admin",
  "exp": 1234567890,
  "iat": 1234560890,
  "type": "access"
}

# Refresh Token Payload
{
  "sub": "user_uuid",
  "exp": 1234567890,
  "type": "refresh"
}
```

- Access Token 有效期：**2 小时**
- Refresh Token 有效期：**30 天**（存储于 DB，支持吊销）
- 每次使用 Refresh Token 时轮换（Rotation），旧 Token 立即失效。

### 9.2 中间件

```python
# backend/app/core/auth.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """解析 JWT，返回当前用户。自动注入 tenant_id。"""
    payload = decode_jwt(token)
    user = await user_service.get_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="无效的用户")
    return user

def require_roles(*allowed_roles: str):
    """角色权限装饰器"""
    async def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="无权访问")
        return current_user
    return dependency
```

### 9.3 前端 Axios 拦截器

```ts
// frontend/src/api/client.ts
const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use(config => {
  const token = useAuthStore().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      try {
        await authStore.refreshAccessToken()
        // 重试原请求
        return api(error.config)
      } catch {
        authStore.logout()
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)
```

---

## 10. 环境配置与 Docker

### 10.1 docker-compose.yml

```yaml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg16   # 含 pgvector 扩展的 PG，未来可用于 AI embedding
    environment:
      POSTGRES_DB: foreign_trade
      POSTGRES_USER: ft_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  elasticsearch:
    image: elasticsearch:8.15.0
    environment:
      discovery.type: single-node
      xpack.security.enabled: false
    ports: ["9200:9200"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db, redis, elasticsearch]
    env_file: ./backend/.env
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
    volumes:
      - ./frontend:/app

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    depends_on: [backend, frontend]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

volumes:
  pgdata:
```

### 10.2 环境变量清单

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://ft_user:password@db:5432/foreign_trade
REDIS_URL=redis://redis:6379/0
ELASTICSEARCH_URL=http://elasticsearch:9200

# AI
DEEPSEEK_API_KEY=sk-xxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
AI_MAX_TOKENS=4096
AI_TEMPERATURE=0.3
AI_TIMEOUT=60

# Auth
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=30

# Gmail OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/email-auth/gmail/callback

# App
APP_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=AI 外贸助手
```

---

## 11. 实现依赖图与执行顺序

```
Phase 0: 基础设施（必须最先完成）
  ├── docker-compose.yml + PG/Redis/ES 容器
  ├── backend: 项目骨架 + config + database.py
  ├── backend: Alembic 初始化 + 初始迁移
  ├── frontend: Vite 创建项目 + Element Plus 引入
  └── nginx.conf 基础配置
        ↓
Phase 1: 认证系统（所有功能的前置依赖）
  ├── backend: User + Tenant 模型 + JWT 中间件
  ├── backend: /auth/register, /auth/login, /auth/me
  └── frontend: LoginView, RegisterView, AuthLayout, auth store
        ↓
Phase 2: 基础 CRUD（无 AI 依赖）
  ├── backend: EnterpriseProfile, Product 模型 + CRUD API
  ├── frontend: EnterpriseView, ProductListView, MainLayout
  └── frontend: 公共组件（EmptyState, LoadingSkeleton, ConfirmDialog, PageHeader）
        ↓
Phase 3: 客户画像（核心 AI 模块）
  ├── backend: Icp 模型 + CRUD API + AI generate SSE
  ├── backend: Prompt 模板 + DeepSeek 调用封装
  ├── frontend: IcpListView, IcpCreate, IcpDetail
  ├── frontend: IcpGeneratePanel + StreamingOutput
  └── frontend: icp store
        ↓
Phase 4: 客户获取（依赖 Phase 3 画像）
  ├── backend: Customer + Contact 模型 + CRUD API
  ├── backend: 搜索渠道抽象 (Google + LinkedIn)
  ├── backend: SSE 搜索接口 + 结果去重/清洗/AI结构化
  ├── frontend: CustomerListView, CustomerDetail
  ├── frontend: CustomerSearchPanel, SearchProgress
  └── frontend: customer store
        ↓
Phase 5: 信息补全（依赖 Phase 4 客户）
  ├── backend: 数据补全适配器 + enrich API（公开数据版）
  ├── frontend: EnrichProgress, ContactList
  └── frontend: enrich 状态集成到 customer store
        ↓
Phase 6: 邮件营销（依赖 Phase 3/4/5）
  ├── backend: EmailTemplate + Campaign + SendLog 模型 + CRUD API
  ├── backend: Gmail OAuth 流程 + Celery 发送任务
  ├── backend: AI 模板生成 SSE + 变量替换
  ├── frontend: TemplateListView, TemplateCreate, TemplateEdit
  ├── frontend: CampaignListView, CampaignCreate, CampaignDetail
  ├── frontend: EmailEditor, VariableSelector, SpamScoreGauge
  └── frontend: email store
        ↓
Phase 7: 系统设置 + 收尾
  ├── backend: 成员管理 API
  ├── frontend: SettingsView, MemberListView
  └── 整体 polish: 错误处理、加载态、边界情况
```

**可并行**：Phase 2 中的 Enterprise 和 Product 可并行开发。Phase 6 中的模板和发送任务可并行。

---

## 12. 交互状态矩阵

每个页面必须覆盖至少以下 4 种状态：

| 状态 | 触发条件 | UI 表现 |
|------|----------|---------|
| **Loading** | 首次进入页面，数据请求中 | 骨架屏 (`LoadingSkeleton`) 或 `el-skeleton` |
| **Empty** | 请求成功但列表为空 | `EmptyState` 组件：图标 + 引导文案 + 新建按钮 |
| **Error** | 请求失败（网络/服务/权限） | `ErrorMessage` 组件：错误描述 + 重试按钮 |
| **Content** | 请求成功，有数据 | 正常内容渲染 |

### 12.1 各页面额外状态

| 页面 | 额外状态 | 说明 |
|------|----------|------|
| **IcpCreate** | `streaming` — 流式生成中 | 禁用表单编辑，展示 StreamingOutput |
| | `generated` — 生成完成但未保存 | 展示结果预览 + 「保存」「重新生成」按钮 |
| | `validating` — 表单校验中 | 提交按钮 loading |
| **CustomerListView** | `searching` — 正在搜索客户 | SearchProgress 面板，禁用搜索按钮 |
| | `partial` — 部分渠道失败 | 成功的渠道展示结果，失败的展示重试按钮 |
| | `selecting` — 批量选择模式 | 列表出现复选框，底部浮现 BatchActions |
| **TemplateCreate** | `streaming` — AI 生成中 | 同 IcpCreate |
| | `previewing` — 预览模式 | 展示变量替换后的最终邮件 |
| **CampaignCreate** | `previewing` — 预览邮件 | 选择客户后展示变量替换效果 |
| | `scheduling` — 选择定时 | 日期时间选择器展开 |
| **CampaignDetail** | `sending` — 正在发送 | 进度环实时更新，显示已发送/总数 |
| | `paused` — 已暂停 | 展示继续/取消按钮 |

### 12.2 全局 Loading 遮罩

以下操作使用全屏 Loading（`el-loading` 服务）：

- 客户搜索（`/customers/search`）
- 批量信息补全（`/customers/batch-enrich`）
- 邮件批量发送确认（`/email-campaigns/{id}/start`）

---

## 附录 A：文件命名约定

| 类型 | 格式 | 示例 |
|------|------|------|
| Vue 页面 | PascalCase + `View` 后缀 | `IcpListView.vue` |
| Vue 组件 | PascalCase | `IcpCard.vue`, `EmptyState.vue` |
| Pinia Store | kebab-case | `icp.ts`, `auth.ts` |
| API 模块 | kebab-case | `client.ts`, `icps.ts`, `customers.ts` |
| Composable | `use` 前缀 + PascalCase | `useSSE.ts`, `usePagination.ts` |
| Python 模型 | snake_case | `icp.py`, `email_template.py` |
| Python 路由 | snake_case 复数 | `icps.py`, `customers.py` |

---

## 附录 B：关键组件库版本锁定

| 包 | 版本 | 用途 |
|----|------|------|
| element-plus | ^2.9 | 主 UI 库 |
| @element-plus/icons-vue | ^2.3 | 图标 |
| dayjs | ^1.11 | 日期格式化 |
| marked | ^14.0 | Markdown 渲染（AI 输出） |
| dompurify | ^3.2 | XSS 过滤 |

---

> **最后更新**：2026-06-25
> **关联文档**：[CLAUDE.md](../CLAUDE.md) · [PRD](./prd.md)
