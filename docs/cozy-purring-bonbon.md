# 多源搜索引擎接入 — 方案

## Context

当前 5 个搜索渠道中，4 个底层都是 DuckDuckGo HTML 搜索，仅 `ai` 是独立的 LLM 渠道。

| 渠道 | 当前实现 | 问题 |
|------|----------|------|
| `google` | DDG + 标记为 `google_search` | 不是真正的 Google 结果 |
| `linkedin` | DDG + `site:linkedin.com/company` | 同上 |
| `linkedin_people` | DDG + `site:linkedin.com/in` + 正则 | 同上 |
| `duckduckgo` | DDG HTML 搜索 | 正常，单源覆盖有限 |

目标：接入 Serper.dev（Google 搜索）和 Bing API 作为真正的独立搜索源，DDG 保留作为兜底。

---

## 方案

### 1. Google 渠道 — 接入 Serper.dev

**为什么不用 Google 官方 API**：官方 Custom Search API 必须绑定 CSE、免费仅 100 次/天、需要 Google Cloud 项目。Serper.dev 本质是"帮你爬 Google 结果并返回结构化 JSON"，极大简化。

**API**：`POST https://google.serper.dev/search`
- 免费额度：2500 次/月（注册即得）
- 请求体：`{ "q": "query", "gl": "sg", "num": 20 }`
- `gl` 参数按国家过滤（`sg` 东南亚、`us` 美国等）
- 返回 `organic` 数组：`title`、`link`、`snippet`、`position`
- 也返回 `peopleAlsoAsk`、`relatedSearches` 等附加信息

**实现**：
- 新建 `SerperSearchChannel` 类，继承 `SearchChannel`，`source_channel = "google_search"`
- `_CHANNELS_MAP` 中 `google` 键指向新类
- 未配置 `SERPER_API_KEY` 时，自动回退现有 `GoogleSearchChannel`（DDG 模式）
- 原有 `google_channel.py` 保留不动，作为回退

### 2. Bing 渠道（新增）— 接入 Bing Web Search API

**API**：`GET https://api.bing.microsoft.com/v7.0/search`
- 免费额度：1000 次/月（Azure Marketplace F0 层，无需信用卡）
- 参数：`?q=query&mkt=en-SG&count=20`
- 认证：Header `Ocp-Apim-Subscription-Key`
- 返回 `webPages.value` 数组：`name`、`url`、`snippet`

**实现**：
- 新建 `BingSearchChannel` 类
- 前端新增 `bing` 复选框，未配置 Key 时隐藏
- 未配置 `BING_API_KEY` 时该渠道不可用

### 3. LinkedIn 渠道 — 改用 Serper + site: 过滤

LinkedIn 没有公开搜索 API，用 Serper.dev 做 `site:linkedin.com` 搜索效果远好于 DDG：

| 渠道 | 新实现 | 回退 |
|------|--------|------|
| `linkedin` | Serper `site:linkedin.com/company` 搜索 | 未配 Key → DDG |
| `linkedin_people` | Serper `site:linkedin.com/in` 搜索 + 正则提取 | 未配 Key → DDG |

前端标签改为「LinkedIn 公司」「LinkedIn 人物」消除误导。

### 4. 渠道并行化（顺手优化）

Step 1 当前串行 `for channel in channels` 改为 `asyncio.gather`：

```python
# 之前：串行，总耗时 = 各渠道之和
for channel_name in channels:
    results = await channel.search(query, region)

# 之后：并行，总耗时 = 最慢渠道耗时
tasks = [_search_one(name, cls, query, region) for name in channels]
results_list = await asyncio.gather(*tasks, return_exceptions=True)
```

Step 1 从 ~60s 降到 ~15s（最慢渠道的耗时）。

---

## 配置新增

`backend/.env` 新增（均为可选，未配置则回退 DDG）：

```bash
# Serper.dev Google 搜索（2500次/月免费）https://serper.dev
SERPER_API_KEY=your_serper_api_key

# Bing Web Search（1000次/月免费）Azure Marketplace F0 层
BING_API_KEY=your_bing_api_key
```

[config.py](backend/app/config.py) 新增 2 个配置项。

---

## 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/services/search/serper_channel.py` | **新建** | Serper.dev Google 搜索渠道 |
| `backend/app/services/search/bing_channel.py` | **新建** | Bing Web Search API 渠道 |
| `backend/app/services/search/linkedin_channel.py` | 修改 | 优先 Serper + `site:linkedin.com/company`，回退 DDG |
| `backend/app/services/search/linkedin_people_channel.py` | 修改 | 优先 Serper + `site:linkedin.com/in`，回退 DDG |
| `backend/app/config.py` | 修改 | 新增 `SERPER_API_KEY`、`BING_API_KEY` |
| `backend/app/api/customers.py` | 修改 | `_CHANNELS_MAP` 注册新渠道 + Step 1 `asyncio.gather` 并行化 |
| `frontend/src/views/customer/CustomerListView.vue` | 修改 | 新增 `bing` 复选框；LinkedIn 标签更新 |

---

## 验证方式

1. 未配置任何 Key：所有渠道回退 DDG，前端只显示 `ai`/`duckduckgo`/`linkedin`/`linkedin_people`
2. 仅配置 Serper Key：`google`、`linkedin`、`linkedin_people` 走 Serper，结果质量明显提升
3. 配置 Bing Key：前端出现 `bing` 复选框，可独立搜索
4. 并行搜索：Step 1 总耗时 ≈ 最慢渠道耗时
5. `vue-tsc --noEmit` + Python 语法检查通过
