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

### 2026-07-23 下午：列表页菜单 & 看板 UI 优化（参考设计稿）
- **依据文档**：`docs/UI/看板.png` 参考图
- **SidebarNav.vue**：整体重构
  - 背景色改为 `#0b1a2e`，Logo 区域增加 tagline 副标题
  - 菜单项激活态改为左侧 3px 蓝色指示条（`border-left-color: #3b82f6`）+ 蓝色半透明背景
  - 新增手风琴子菜单（邮件营销），点击展开/收起
  - 底部新增用户信息卡片（头像 + 姓名 + 企业名），替代纯版本号
  - 注册折叠过渡动画
- **MainLayout.vue**：调整侧边栏宽度（64/232）、阴影、内容区背景色（`#f5f7fa`）
- **HeaderBar.vue**：
  - 折叠按钮改为汉堡图标 SVG
  - 新增面包屑（当前页面标题）
  - 新增通知铃铛（`el-badge`，演示数字 3）
  - 用户下拉增加企业资料快捷入口，显示企业名
- **DashboardView.vue**：
  - 欢迎横幅增加 3 个汇总数字（获取客户/客户画像/已发邮件）
  - 统计卡片增加左侧彩色装饰条（`stat-card__accent`），四色方案：蓝/绿/琥珀/紫
  - 统一卡片圆角 14px、边框色 `#e8ecf1`、微阴影
  - 快捷入口卡片不再使用 `el-card`，改为纯 div 提升渲染性能
  - 图表区卡片统一 header 样式
- **AdminLayout.vue**：同步重构，与主布局保持一致的侧边栏/头部/导航风格（紫调主题）
- **验证**：`vue-tsc --noEmit` 零错误通过，Vite dev server 正常运行

### 2026-07-23 上午：登录页 & 注册页 UI 优化（参考设计稿）
- **依据文档**：`docs/UI/登录.png`、`docs/UI/注册.png` 参考图
- **AuthLayout.vue**：整体重构为左右分栏（split-screen）布局
  - **左栏（44%）**：深色品牌面板（`#0f172a` → `#1e293b` 渐变），含 Logo、品牌名、tagline、SVG 地球插画（含经纬线/节点/脉冲动画）、三条特性列表（AI 智能获客/全球客户开发/智能客户画像）、网格背景 + 模糊光晕装饰
  - **右栏（56%）**：浅灰背景（`#f5f7fa`）上的白色表单卡片（圆角 16px、阴影），内部 `:deep()` 样式覆盖 Element Plus 输入框/按钮/链接等
  - 卡片内的样式槽位：`.auth-tabs`（tab 切换条）、`.auth-submit-btn`（渐变蓝紫按钮）、`.auth-forgot`（忘记密码链接）、`.auth-footer`（底部注册链接）、`.auth-divider`（第三方登录分隔线）、`.auth-social`（社交登录图标行）
  - 响应式：≤768px 时上下堆叠，缩小插画和间距
- **LoginView.vue**：匹配登录参考图
  - 新增 tab 切换条（"邮箱登录" 为当前激活 tab）
  - 新增「忘记密码？」链接（暂为占位 `@click.prevent`）
  - 新增第三方登录图标行（微信/Google/Apple）
  - 输入框 placeholder 改为中文提示语
  - 所有现有逻辑（表单校验/错误处理/登录调用）保持不变
- **RegisterView.vue**：同样适配新 AuthLayout，更新 tab 条（"注册账号"）、placeholder 文案
- **AdminLoginView.vue**：同样适配新 AuthLayout，更新 tab 条（"管理员登录"）
- **验证**：`vue-tsc --noEmit` 零错误通过

### 2026-07-23 — v1.5 客户画像产品信息优化 + 产品管理合并

- **需求一 — 客户画像产品信息支持手动填写**：
  - [IcpCreate.vue](frontend/src/views/icp/IcpCreate.vue) Step 1 新增产品来源切换（`el-radio-group`：「关联已有产品」/「手动填写产品」）
  - 手动模式：动态表单支持添加/删除多个产品，字段：name、category、description、price_usd、moq、hs_code
  - `buildInputData()` 新增 `product_source` + `manual_products` 字段
  - [icp_generator.py](backend/app/services/ai/icp_generator.py) `_build_user_prompt()` 提取公共 `_format_product()` 函数，当 `product_source === "manual"` 时格式化 `manual_products`
- **需求二 — 产品管理合并至企业资料**：
  - **新建** [EnterpriseProducts.vue](frontend/src/views/enterprise/components/EnterpriseProducts.vue)：自包含产品管理面板（表格列表 + 创建/编辑弹窗（复用 ProductForm）+ 删除确认），数据自行加载
  - [EnterpriseEdit.vue](frontend/src/views/enterprise/EnterpriseEdit.vue)：新增「产品管理」卡片（在「资质证件」后），嵌入 EnterpriseProducts 组件
  - [SidebarNav.vue](frontend/src/layouts/components/SidebarNav.vue)：移除「产品管理」导航项
  - [router/index.ts](frontend/src/router/index.ts)：3 条产品路由改为重定向至 `/app/enterprise`
  - 后端无需修改，产品 API 保持不变
- **验证**：TypeScript `vue-tsc --noEmit` 零错误，Python 语法检查通过

## 2026-07-24 — Hunter.io 邮箱发现集成 + Serper.dev 搜索渠道

- **Hunter.io API 配置**：`.env` 新增 `HUNTER_API_KEY`，`config.py` 已有对应字段。免费套餐：50 次域名搜索 + 100 次邮箱验证/月。API key 验证通过。
- **新增 Serper.dev Google 搜索渠道**：[serper_channel.py](backend/app/services/search/serper_channel.py) — 替代 SerpAPI（屏蔽中国手机号），免费额度 2500 次/月，返回结构化 JSON。支持区域映射（`_region_to_gl`）、公司名清洗、非商业域名黑名单过滤。
- **渠道注册**：[customers.py](backend/app/api/customers.py) `_CHANNELS_MAP` 新增 `"serper": SerperSearchChannel`，`config.py` 新增 `SERPER_API_KEY` 配置项，`.env.example` 同步更新。Serper API key 已配置并验证通过。
- **侧栏子菜单 UI 优化**：[SidebarNav.vue](frontend/src/layouts/components/SidebarNav.vue) 二级菜单（邮件营销）去掉右对齐——箭头移入 `__inner` 紧跟文字，子菜单项去除圆点标记改用 `padding-left: 52px` 对齐父级文字，hover/激活态仅通过颜色变化反馈，整体更简洁统一。
- **IMAP 轮询邮件回复追踪**：实现完整的邮件回复检测链路。
  - **Model**：[send_log.py](backend/app/models/send_log.py) 新增 `message_id`（SMTP Message-ID）和 `replied_at`（检测到回复的时间）；[email_campaign.py](backend/app/models/email_campaign.py) 新增 `replied_count`。Alembic 迁移 `4191c6f1fa78` 已执行。
  - **发件**：[email_sender.py](backend/app/services/email_sender.py) 新增 `build_message_id()`，发件时生成 `Message-ID` header 并返回；[email_campaigns.py](backend/app/api/email_campaigns.py) 两处发件完成后将 `message_id` 写入 SendLog。
  - **IMAP 追踪服务**：[reply_tracker.py](backend/app/services/email/reply_tracker.py) — 使用 stdlib `imaplib`+`email` 零外部依赖。搜索 INBOX 中 UNSEEN 邮件，通过 `In-Reply-To`/`References` 头匹配已发 Message-ID，匹配成功则更新 SendLog 状态为 replied。
  - **自动推导 IMAP 配置**：支持 Gmail/Outlook/QQ/163/126/Zoho 等 10 种常见邮箱的 SMTP→IMAP 自动映射，用户无需额外配置。
  - **配置与 API**：`config.py` 新增 `IMAP_POLL_INTERVAL_MINUTES`（默认 5 分钟）；`GET/PUT /settings/imap` 端点管理 IMAP 配置（密文存储，复用 Fernet 加密）。
  - **后台轮询**：[main.py](backend/app/main.py) lifespan 中启动 `_imap_poll_loop()` asyncio 任务，每 5 分钟全租户检查；`POST /email/check-replies` 支持手动即时触发。
- **工作台数据看板验证与修复**：
  - **Bug 修复**：月度邮件统计查询缺少 `replied` 字段，前端"已回复"曲线恒为 0。在 `monthly_q` 中新增 `func.sum(case(...))` 统计 `status == 'replied'` 的邮件数。
  - **聚合器去重增强**：[aggregator.py](backend/app/services/search/aggregator.py) `_merge()` 改为先按 `, ` 拆分已有 source_channel 再合并去重，解决 7 条客户来源显示为 `'ai_search, ai_search'` 的重复拼接问题。已修复历史脏数据。
  - **数据验证结果**：ICP 7（完成5/失败2）、产品 1、企业资料 ✓、客户 201（全部 `new` 状态 → 触达率 0% 属正常）、邮件 1（发1/开1/回0）。各项统计逻辑正确。
- **邮件任务"创建并发送"一键直达**：[CampaignListView.vue](frontend/src/views/email/CampaignListView.vue) `handleCreate()` 改为创建成功后立即调用 `store.sendCampaign(campaign.id)`，无需跳转到列表页再手动点发送。创建→发送流程无缝衔接。
- **客户列表 page_size 上限放宽**：[customers.py](backend/app/api/customers.py) `page_size` 从 `le=100` → `le=2000`，解决邮件任务选择客户时因分页限制（100条/页）导致统计数与实际不符的问题。

### 2026-07-24 下午：双语邮件模板 + 邮件发送语言版本修复

- **双语邮件模板（分开存储+重新翻译）**：
  - Model：`email_template` 表新增 `language`、`body_html_foreign`、`body_text_foreign` 三列，Alembic 迁移已执行。
  - AI Generator：[email_generator.py](backend/app/services/ai/email_generator.py) 新增 `translate()` 方法，独立翻译 prompt 保留 HTML 标签和变量占位符。
  - API：Generate 端点生成中文版后自动翻译为目标语言版本；新增 `POST /{id}/translate` SSE 端点支持修改中文后重新翻译。
  - 前端：新建模板时可选语言（英文/西语/俄语），生成结果分 Tab 预览双语版本，支持点击「重新翻译」按钮。
- **AI 生成简化**：移除 body_text 输出要求，新增 `html_to_plain_text()` 从 HTML 自动提取纯文本；翻译同理，纯文本从翻译后的 HTML 自动生成。
- **邮件主题翻译**：翻译阶段同步翻译 subjects 列表，首个翻译主题自动设为模板 subject，前端主题选择器优先显示外语主题并附中文原文。
- **编辑模板 Tab 菜单顺序调整**：重新排序为 邮件原文预览 → 中文版本预览 → HTML源码 → 中文纯文本 → 外语纯文本，移除冗余的"外语 HTML"Tab。
- **发送邮件优先使用外语版本**：修复 4 处（preview/send/resume/test-send）始终取 `body_html` 的问题，当模板设置了 language 且有 body_html_foreign 时优先使用外语版本。
- **主题选择双语分两行展示**：外语主题在上，中文原文灰色小字在下，避免超长文本溢出弹窗。

### 2026-07-24 下午：发送任务体验优化

- **修复卡在"发送中"的任务**：后台任务崩溃导致状态卡在 sending，手动修复已有僵尸任务。`list_campaigns` 新增自动检测：已发完但状态卡 sending 的自动标记为 completed。
- **发送任务列表自动轮询进度**：[CampaignListView.vue](frontend/src/views/email/CampaignListView.vue) 检测到有 sending 状态任务时自动每 3 秒刷新列表，全部完成后停止轮询，页面离开时清理定时器。
- **任务名称区分**：名称格式从 `发送任务 2026/7/24` 改为 `{模板名称} — 2026/7/24 16:30`，已批量更新全部历史任务名称。

## 2026-07-27

- **ICP 目标行业优化**：`target_industry` 从纯文本输入框改为可搜索下拉框（`el-select` + `filterable` + `allow-create`），提供 20 个外贸 B2B 常见行业快捷选项（消费电子、家居用品、服装纺织等），同时支持自由输入自定义行业。新建 [industries.ts](frontend/src/constants/industries.ts) 公共常量，[IcpCreate.vue](frontend/src/views/icp/IcpCreate.vue) 和 [IcpDetail.vue](frontend/src/views/icp/IcpDetail.vue) 同步更新。
