# 执行记录 (Todolist)

> 按时间顺序简要记录每一次执行的任务。依据 CLAUDE.md 第十一条维护。

---

## 2026-06-25

- **项目初始化**：创建 CLAUDE.md 全局开发规范（含十大章节），添加 .gitignore，初始化 12 个标准子目录。
- **文档建设**：新增 PRD v1.0（AI 外贸助手产品需求文档，定义一期 MVP），新增开发实施规约（面向 AI vibe coding 执行手册）。

## 2026-06-26 — Phase 0

- **基础设施搭建**：FastAPI 后端骨架（数据库连接、配置、模型基类）、Vue 3 + Vite 前端骨架（路由、布局、Element Plus 集成）、Alembic 迁移初始化、用户端/管理后台双端架构设计文档。

## 2026-06-27 — Phase 1

- **双端认证系统**：用户端登录/注册、管理后台登录、JWT Token 签发与验证、租户隔离、密码哈希存储、路由守卫鉴权、注册页确认密码二次校验、登录错误提示完善、Python 3.8 兼容性修复。

## 2026-06-28 — Phase 0/1 查漏补缺

- **后端邮箱校验**：注册时校验邮箱格式唯一性。
- **前端登录态恢复**：修复 Token 过期后未清理 localStorage 的问题。
- **代码规范**：统一前后端代码风格，补充类型注解。

## 2026-06-29 ~ 2026-07-02 — Phase 2–7

- **Phase 2 — 客户画像 (ICP)**：CRUD 接口 + 列表/详情/创建页面。
- **Phase 3 — 客户管理**：客户列表、客户详情、关联 ICP。
- **Phase 4 — 邮件模板**：模板 CRUD、变量占位符、预览。
- **Phase 5 — 发送任务**：任务创建、列表、详情、SMTP 发信。
- **Phase 6 — 企业资料**：编辑页、Logo 上传、表单校验。
- **Phase 7 — 系统设置**：成员管理、角色权限、租户设置。
- **SMTP 发信修复**：修复发信连接超时问题。
- **UX 优化**：通用组件（PageHeader、EmptyState、LoadingSkeleton、StatusBadge、ConfirmDialog）、全局样式变量。

## 2026-07-15

- **修复页面刷新后会话丢失**：Vue Router 4 路由守卫竞态问题——`beforeEach` 在 `App.vue` 异步初始化完成前触发导致误判未登录，将会话恢复逻辑移入路由守卫并 await 完成。
- **修复页面刷新 500 错误**：
  - `dashboard.py`：`total_emails_replied` 变量未定义直接引用导致 `NameError`，提取为独立查询结果。
  - `auth.py`：`scalar_one()` 在租户不存在时抛出 `NoResultFound`，改为 `scalar_one_or_none()` 并增加空值检查。
- **修复双次错误提示**：axios 拦截器对所有非认证错误弹 toast，即使组件自身已处理。增加 `silent` 配置选项，非关键接口（dashboard 统计、企业状态）标记为静默。

## 2026-07-17 — v1.2 版本

- **PRD 升级**：[docs/prd.md](docs/prd.md) 升级至 v1.2，新增 §12 v1.2 变更记录。
- **企业字段扩展**（后端）：`enterprise_profile` 表新增 10 个外贸字段（成立年份、员工规模、工厂面积、年出口额、主要市场、认证资质、OEM/ODM、企业优势、工厂照片、资质照片），其中市场/认证/照片为 JSONB 类型。
- **国家默认值**：`country` 默认值设为"中国"，前端隐藏国家选择，注册时自动创建 EnterpriseProfile。
- **中国城市下拉**：新增 [frontend/src/data/cities.json](frontend/src/data/cities.json)（300+ 城市），`el-select` + `filterable` 实现模糊匹配。
- **企业图片上传**：新增 `POST /enterprise/photos?type=factory|certificate` 端点，前端双区域图片上传（工厂实景/资质证件），复用 logo 上传的文件校验/存储模式。JSONB 字段更新使用 `flag_modified()` 确保 SQLAlchemy 检测变更。
- **产品多图上传**：`product` 表新增 `images` JSONB 字段（保留原 `image_url`），新增 `POST /products/{id}/images` 端点，前端 ProductForm 集成可复用 ImageUpload 组件，ProductListView 新增缩略图列。
- **产品路由注册**：`router/index.ts` 注册 `/app/products`、`/app/products/create`、`/app/products/:id/edit` 三条路由，侧栏新增"产品管理"入口。
- **可复用组件**：新增 ImageUpload.vue（多图上传，v-model 模式，文件类型/大小客户端校验）。
- **数据库迁移**：Alembic 迁移 `779370b0cfe1` 已执行（新增 10 个企业字段 + 1 个产品字段）。
- **前端类型检查**：`vue-tsc --noEmit` 零错误通过。

## 2026-07-17 — v1.3 PRD

- **PRD 升级**：[docs/prd.md](docs/prd.md) 升级至 v1.3，新增 §13 v1.3 变更记录（客户画像模块优化：公司规模多选、产品关联产品列表、价格结构化 USD、草稿保存、列表字段扩展、二次编辑重新生成）。

## 2026-07-17 — v1.3 开发

- **需求 1 — 公司规模多选**：`company_size` 从单选 `str` 改为多选 `List[str]`，后端 Schema 添加 `field_validator` 兼容旧数据，前端 `el-select` 添加 `multiple`。
- **需求 2 — 产品关联产品列表**：`IcpInputData` 新增 `product_ids`，新增 [ProductSelector.vue](frontend/src/views/icp/components/ProductSelector.vue) 可复用组件（多选+卡片展示+内联快照），AI Prompt 模板适配产品内联数据（`_products_inline`）。
- **需求 3 — 价格结构化 USD**：废弃自由文本价格字段，新增 `product_price_min/max` 和 `customer_budget_min/max`，前端 `el-input-number` + 固定 "USD" 标签，后端 prompt 构建时格式化显示。
- **需求 4 — 保存草稿**：[IcpCreate.vue](frontend/src/views/icp/IcpCreate.vue) Step 2 新增「保存草稿」按钮，调用 `createDraft()` 后跳转列表页。
- **需求 5 — 列表新增 4 字段**：`IcpListItem` Schema 新增 `target_region`/`target_industry`/`company_size`/`customer_budget`，API 列表端点从 `input_data` 提取填充，前端表格新增 4 列。
- **需求 6 — 二次编辑重新生成**：[IcpDetail.vue](frontend/src/views/icp/IcpDetail.vue) 新增「编辑输入信息」按钮（内联编辑模式）、`completed` 状态重新生成（含覆盖确认弹窗）、Store 新增 `update()` action。
- **验证**：TypeScript `vue-tsc --noEmit` 零错误，Python 3 文件语法检查通过。

## 2026-07-22 — v1.4 客户搜索联系人发现率优化

- **问题分析**：客户搜索模块联系人发现率低——AI prompt 过于保守、搜索渠道仅限公司名、网站抓取覆盖面窄（4页/8秒）、无邮箱推断。
- **Contact 模型扩展**：新增 `contact_type`（scraped/inferred/ai_suggested）和 `confidence`（high/medium/low）字段，Alembic 迁移 `8a1c3d5e7f92` 已执行。
- **新增 LinkedIn 人物搜索渠道**：[linkedin_people_channel.py](backend/app/services/search/linkedin_people_channel.py) — 搜索 `site:linkedin.com/in` + 行业/职位关键词，从搜索结果摘要提取人名+职位。
- **增强 Contact Scraper**：页面路径 4→13 个（新增 our-team/people/management/leadership），最大页数 4→8，超时 8→12s，新增 `mailto:` 链接提取、Schema.org Person/Organization JSON-LD 结构化数据提取、`<meta>` 标签提取。
- **新增 Email Inferrer**：[email_inferrer.py](backend/app/services/enrichment/email_inferrer.py) — 从人名+域名推断企业邮箱（6 种常见模式），通过已知邮箱反推公司命名规则。
- **新增 AI 定向联系人搜索**：[contact_search.py](backend/app/services/search/contact_search.py) — 对每家公司生成 5 类精确搜索查询（邮箱、采购经理、LinkedIn、联系方式页），从搜索结果提取联系人线索。
- **优化 AI Prompt**：AI 搜索 prompt 从"不要编造邮箱"改为"合理推测时可填写，标记 confidence: inferred"，支持区分 verified/inferred 置信度。
- **搜索端点重构**（customers.py）：原 4 步流程 → 6 步（新增 Step 4 定向联系人搜索 + Step 6 邮箱模式推断），所有联系人保存携带 contact_type/confidence。
- **前端适配**：CustomerListView 搜索对话框新增"LinkedIn 人物搜索"复选框，StreamingOutput 进度步骤新增"定向联系人搜索"和"邮箱模式推断"两步，完成面板显示各渠道联系人增量统计。
- **客户详情 AI 搜联系人**：新增 `POST /customers/{id}/ai-search-contacts` SSE 端点（4步：LinkedIn人物搜索→定向搜索→网站抓取→邮箱推断），CustomerDetail 联系人卡片头部新增"AI 搜联系人"按钮，联系人卡片显示来源标签（AI发现/推测/待验证）。
- **修复 ICP 编辑保存 500 错误**：`update_icp` 端点中 `data.model_dump()` 递归将嵌套 `IcpInputData` 转为 dict 后，代码对 dict 调用 `.model_dump()` 导致 `AttributeError`。改为直接从原始 Pydantic 模型 `data.input_data.model_dump()` 取值。

## 2026-07-22 — v1.4 客户搜索后台执行

- **背景**：客户搜索整个过程耗时较长，用户必须在弹窗中等待不能关闭。
- **后端 — 任务管理器**：新增 [task_manager.py](backend/app/services/search/task_manager.py) 内存任务管理器，支持 create/get/list/update/remove + 自动清理过期任务（2h TTL）。
- **后端 — 搜索逻辑重构**：提取 `_execute_search()` 独立异步函数，通过 `on_progress` 回调报告进度，SSE 端点和后台端点共用同一逻辑。`POST /customers/search` 改用 `asyncio.Queue` + `asyncio.create_task` 模式。
- **后端 — 新增端点**：
  - `POST /customers/search/background`：接收搜索参数，创建后台任务（`asyncio.create_task`），立即返回 `task_id`。
  - `GET /customers/search/tasks`：返回当前租户最近 20 个搜索任务（含进度、结果、状态）。
- **前端 — 搜索弹窗**：footer 新增「后台执行」按钮，点击后关闭弹窗并提交后台任务。
- **前端 — 任务进度面板**：客户列表页顶部（筛选栏上方）新增可折叠的后台任务面板，显示运行中/已完成/失败任务，运行中任务展示进度条和当前步骤，每 3 秒轮询刷新，无活跃任务时自动停止轮询。
- **验证**：TypeScript `vue-tsc --noEmit` 零错误，Vite build 成功，Python 路由注册验证通过。
