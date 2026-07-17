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
