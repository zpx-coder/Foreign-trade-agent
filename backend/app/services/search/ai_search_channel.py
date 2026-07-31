"""AI 搜索渠道 — 基于 LLM 知识生成潜在客户列表 + 二次精筛补全"""

import json
import logging
from typing import List, Optional

from app.services.search.base import SearchChannel, SearchResult
from app.services.ai_service import AIServiceError, get_ai_service

logger = logging.getLogger(__name__)

AI_SEARCH_SYSTEM_PROMPT = """你是一个 B2B 外贸客户开发专家。根据用户提供的客户画像条件和我方企业背景，列出真实存在的潜在客户公司及其关键联系人。

## 核心原则
- 如果提供了"我方企业背景"，请充分利用其中的信息（行业、产能、认证、出口市场等）来匹配最有可能采购我方产品的客户
- 优先推荐与我方规模和能力匹配的客户（如我方有 ISO 认证，优先匹配重视质量的采购商；我方支持 OEM，优先匹配品牌商/进口商）
- 推荐的客户应该是我方产品的潜在买家/进口商/分销商，而非同行竞争对手

## 要求
1. 返回真实存在的公司（基于你的训练数据）
2. 公司名称必须是正式注册名称
3. 网站域名尽可能准确
4. 每条记录包含：company_name（必填）、website、industry、country、city、company_size、description
5. 尽可能提供该公司的关键联系人（采购、销售或管理层），格式为 contacts 数组
6. 联系人信息按 confidence 区分：verified（网页确认过的）> inferred（根据命名规则推测的）> null（完全不确定则不填）
7. 邮箱地址在合理推测时可填写（如根据该公司命名规则推测 firstname.lastname@company.com），标记 confidence 为 "inferred"
8. 返回至少 10 条，最多 20 条结果
9. 仅返回 JSON 数组，不要包含任何其他文字

输出格式示例：
[
  {
    "company_name": "Siemens AG",
    "website": "https://www.siemens.com",
    "industry": "Industrial Automation",
    "country": "Germany",
    "city": "Munich",
    "company_size": "1000+",
    "description": "Global industrial manufacturing conglomerate",
    "contacts": [
      {
        "name": "Roland Busch",
        "title": "CEO",
        "email": "roland.busch@siemens.com",
        "phone": null,
        "linkedin_url": "https://www.linkedin.com/in/roland-busch",
        "confidence": "inferred"
      }
    ]
  }
]
"""

# ── AI 二次精筛 System Prompt ──

AI_CURATION_SYSTEM_PROMPT = """你是一个 B2B 外贸客户精筛专家。你的任务是根据完整的客户画像（ICP）条件，对搜索引擎返回的原始客户列表进行二次筛选、评分、补全。

## 工作流程
1. **识别非公司结果**：先快速扫描，将以下类型的结果直接丢弃（不评分、不输出）：
   - 行业报告/市场分析文章（标题含"报告"、"分析"、"趋势"、"Market Report"等）
   - 新闻/资讯文章（非公司实体）
   - 博客/论坛帖子
   - 海关数据条目/贸易统计（非具体公司）
2. **逐条评估**：对照 ICP 条件，逐一评估每条搜索结果的匹配度
3. **过滤不相关**：剔除明显不匹配的结果（行业不对口、规模差距过大、非目标区域等）
4. **评分排序**：按匹配度从高到低排序，1=完全不匹配，10=完美匹配
5. **补全信息**：对于匹配度 ≥ 6 的结果，利用你的知识补全缺失的字段（industry、company_size、description 等）
6. **增补推荐**：如果你知道其他完美匹配 ICP 但不在列表中的公司，可以最多添加 5 家（匹配度标记为 10）

## 评分标准
- 行业匹配度（最重要）：目标行业一致得高分，相关行业得中分，不相关得 0-2 分
- 地区匹配：在目标区域内的加分
- 公司规模匹配：在目标规模范围内的加分
- 预算匹配：公司采购能力与预算范围匹配的加分
- 买家类型匹配：类型一致的加分

## 输出要求
- 仅返回 JSON 数组，不要包含任何其他文字
- 每条记录必须包含原始字段 + relevance_score（整数 1-10）+ curation_notes（简要说明评分理由，20 字以内）
- 保留原始数据中的 contacts（如有）；如果新增公司，按 AI 搜索格式提供 contacts
- contacts 中的 confidence 字段：verified > inferred > null

输出格式示例：
[
  {
    "company_name": "TechStyle Inc.",
    "website": "https://www.techstyle.com",
    "industry": "Consumer Electronics",
    "country": "United States",
    "city": "Los Angeles",
    "company_size": "200-500",
    "description": "Leading consumer electronics distributor in North America",
    "contacts": [],
    "relevance_score": 9,
    "curation_notes": "行业精准匹配，北美目标区域，中型企业规模契合"
  }
]"""


def _format_icp_criteria(icp_data: dict) -> str:
    """将 ICP input_data 格式化为 AI prompt 可用的筛选条件文本"""
    lines: list[str] = []

    def _add(label: str, value):
        if value is None or value == "" or value == []:
            return
        if isinstance(value, list):
            value = "、".join(str(v) for v in value)
        lines.append(f"- {label}：{value}")

    _add("目标行业", icp_data.get("target_industry"))
    _add("目标地区", icp_data.get("target_region"))
    _add("目标公司规模", icp_data.get("company_size"))
    _add("买家类型", icp_data.get("buyer_type"))
    _add("采购频次", icp_data.get("procurement_frequency"))
    _add("单批次采购预算", _format_budget(icp_data))
    _add("目标采购单价", _format_price_range(icp_data))
    _add("采购渠道偏好", icp_data.get("sourcing_channels"))
    _add("关键决策因素", icp_data.get("key_decision_factors"))
    _add("决策者角色", icp_data.get("decision_makers"))
    _add("客户痛点", icp_data.get("pain_points"))
    _add("补充说明", icp_data.get("additional_notes"))

    # 提取产品信息
    product_category = _extract_product_category(icp_data)
    if product_category:
        lines.insert(0, f"- 产品品类：{product_category}")

    if not lines:
        return ""

    return "\n".join(lines)


def _format_budget(icp_data: dict) -> Optional[str]:
    """格式化预算区间"""
    lo = icp_data.get("customer_budget_min")
    hi = icp_data.get("customer_budget_max")
    if lo is not None and hi is not None:
        return f"${lo:,.0f} — ${hi:,.0f} USD"
    if lo is not None:
        return f"≥ ${lo:,.0f} USD"
    if hi is not None:
        return f"≤ ${hi:,.0f} USD"
    return None


def _format_price_range(icp_data: dict) -> Optional[str]:
    """格式化单价区间"""
    lo = icp_data.get("product_price_min")
    hi = icp_data.get("product_price_max")
    if lo is not None and hi is not None:
        return f"${lo:,.2f} — ${hi:,.2f} USD"
    if lo is not None:
        return f"≥ ${lo:,.2f} USD"
    if hi is not None:
        return f"≤ ${hi:,.2f} USD"
    return None


def _extract_product_category(icp_data: dict) -> str:
    """从 ICP 数据中提取产品品类文本"""
    # 优先从关联产品中提取 category
    products = icp_data.get("_products_inline") or []
    if products:
        cats = list({p.get("category", "") for p in products if isinstance(p, dict) and p.get("category")})
        if cats:
            return "、".join(cats)
    # 手动产品
    manuals = icp_data.get("manual_products") or []
    if manuals:
        cats = list({m.get("category", "") for m in manuals if isinstance(m, dict) and m.get("category")})
        if cats:
            return "、".join(cats)
    # legacy 字段
    legacy = icp_data.get("product_category")
    if legacy:
        return str(legacy)
    return ""


def _serialize_results_for_curation(results: List[SearchResult]) -> str:
    """将搜索结果序列化为精筛 prompt 使用的紧凑 JSON。

    只保留 AI 评估需要的核心字段，去掉 contacts 等大字段以节省 token。
    """
    compact = []
    for r in results:
        item: dict = {
            "company_name": r.company_name,
            "website": r.website or "",
        }
        if r.industry:
            item["industry"] = r.industry
        if r.country:
            item["country"] = r.country
        if r.description:
            item["description"] = r.description[:200] if r.description else ""
        item["source_channel"] = r.source_channel
        compact.append(item)
    return json.dumps(compact, ensure_ascii=False)


class AISearchChannel(SearchChannel):
    """AI 驱动搜索 — 使用 LLM 基于 ICP 画像生成潜在客户列表"""

    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
        enterprise_context: str = "",
    ) -> List[SearchResult]:
        ai_service = get_ai_service()

        user_prompt = f"目标行业/产品：{query}"
        if region:
            user_prompt += f"\n目标区域：{region}"
        if enterprise_context:
            user_prompt += f"\n\n## 我方企业背景（请根据我方实力匹配最合适的采购商）\n{enterprise_context}"
        user_prompt += f"\n请列出 {max_results} 个潜在客户公司。"

        messages = [
            {"role": "system", "content": AI_SEARCH_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        results: List[SearchResult] = []

        try:
            response = await ai_service.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                timeout=self.timeout,
            )

            content = response.choices[0].message.content
            companies = self._parse_response(content)

            for c in companies:
                name = c.get("company_name", "").strip()
                if not name:
                    continue
                # 处理联系人，保留 confidence 字段
                raw_contacts = c.get("contacts") or []
                contacts = []
                for rc in raw_contacts:
                    contact = {
                        "name": rc.get("name"),
                        "title": rc.get("title"),
                        "email": rc.get("email"),
                        "phone": rc.get("phone"),
                        "linkedin_url": rc.get("linkedin_url"),
                        "confidence": rc.get("confidence", "inferred"),
                    }
                    if contact["name"]:
                        contacts.append(contact)
                results.append(
                    SearchResult(
                        company_name=name,
                        website=c.get("website"),
                        industry=c.get("industry"),
                        country=c.get("country"),
                        city=c.get("city"),
                        company_size=c.get("company_size"),
                        description=c.get("description"),
                        contacts=contacts,
                        source_url=c.get("website"),
                        source_channel="ai_search",
                        skip_extraction=True,
                    )
                )

            logger.info(f"AI search '{query}': found {len(results)} results")

        except AIServiceError as e:
            logger.error(f"AI search error: {e}")
        except Exception as e:
            logger.error(f"AI search unexpected error: {e}")

        return results[:max_results]

    def _parse_response(self, content: str) -> list:
        """解析 LLM 返回的 JSON，兼容多种格式"""
        if not content:
            return []

        content = content.strip()

        # 策略 1：直接 JSON 数组
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "companies" in data:
                return data["companies"]
        except json.JSONDecodeError:
            pass

        # 策略 2：提取 ```json ... ``` 代码块
        if "```json" in content:
            block = content.split("```json")[1].split("```")[0].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                pass
        elif "```" in content:
            block = content.split("```")[1].split("```")[0].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                pass

        # 策略 3：尝试从第一个 [ 到最后一个 ] 提取
        try:
            start = content.index("[")
            end = content.rindex("]") + 1
            return json.loads(content[start:end])
        except (ValueError, json.JSONDecodeError):
            pass

        logger.warning(f"Failed to parse AI search response: {content[:200]}")
        return []

    async def curate_results(
        self,
        results: List[SearchResult],
        icp_data: dict,
        query: str,
        region: str = "",
        enterprise_context: str = "",
        max_results: int = 20,
    ) -> List[SearchResult]:
        """对非 AI 渠道的搜索结果进行二次筛选、评分、补全。

        将全部 ICP 条件 + 聚合去重后的结果传给 LLM，由 LLM：
        1. 过滤不相关的结果
        2. 按匹配度评分排序
        3. 补全缺失字段
        4. 可选增补 AI 知晓的匹配公司
        """
        if not results:
            return []

        ai_service = get_ai_service()

        # 构建 ICP 筛选条件文本
        icp_criteria = _format_icp_criteria(icp_data)

        # 将搜索结果序列化为紧凑 JSON（只保留核心字段，减少 token）
        results_json = _serialize_results_for_curation(results)

        user_prompt = f"""## 搜索条件
目标行业/产品：{query}
{("目标区域：" + region) if region else ""}

## 客户画像（ICP）完整条件
{icp_criteria or "（未提供详细 ICP 条件）"}"""

        if enterprise_context:
            user_prompt += f"""

## 我方企业背景
{enterprise_context}"""

        user_prompt += f"""

## 搜索引擎原始结果（共 {len(results)} 条，已去重）
```json
{results_json}
```

## 任务
请对照 ICP 条件逐条评估上述 {len(results)} 条结果：
- 过滤掉明显不匹配的（行业不对口、地区错误、规模差距过大等）
- 按匹配度从高到低排序
- 补全缺失字段（利用你的知识）
- 如你知道其他完美匹配但不在列表中的公司，最多增补 5 家（relevance_score 标记为 10）
- 最多返回 {max_results} 条结果

仅返回 JSON 数组，不要包含其他文字。"""

        messages = [
            {"role": "system", "content": AI_CURATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        curated: List[SearchResult] = []

        try:
            response = await ai_service.chat_completion(
                messages=messages,
                temperature=0.4,
                max_tokens=4096,
                timeout=self.timeout,
            )

            content = response.choices[0].message.content
            companies = self._parse_response(content)

            for c in companies:
                name = c.get("company_name", "").strip()
                if not name:
                    continue
                score = c.get("relevance_score")
                # 处理联系人
                raw_contacts = c.get("contacts") or []
                contacts = []
                for rc in raw_contacts:
                    contact = {
                        "name": rc.get("name"),
                        "title": rc.get("title"),
                        "email": rc.get("email"),
                        "phone": rc.get("phone"),
                        "linkedin_url": rc.get("linkedin_url"),
                        "confidence": rc.get("confidence", "inferred"),
                    }
                    if contact["name"]:
                        contacts.append(contact)

                # 保留原始 source_channel（如果来自搜索引擎），AI 增补的标记为 ai_curated
                source = c.get("source_channel") or "ai_curated"

                curated.append(
                    SearchResult(
                        company_name=name,
                        website=c.get("website"),
                        industry=c.get("industry"),
                        country=c.get("country"),
                        city=c.get("city"),
                        company_size=c.get("company_size"),
                        description=c.get("description"),
                        contacts=contacts,
                        source_url=c.get("website") or c.get("source_url"),
                        source_channel=source,
                        skip_extraction=True,  # AI 已补全，跳过网页抓取
                        relevance_score=score,
                    )
                )

            logger.info(
                f"AI curation: {len(results)} raw → {len(curated)} curated "
                f"(query='{query[:50]}')"
            )

        except AIServiceError as e:
            logger.error(f"AI curation error: {e}")
            # 降级：返回原始结果（不过滤），标记为未精筛
            return results[:max_results]
        except Exception as e:
            logger.error(f"AI curation unexpected error: {e}")
            return results[:max_results]

        return curated[:max_results]
