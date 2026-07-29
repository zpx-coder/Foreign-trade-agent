"""AI 邮件模板生成器 — Phase 6 Email Marketing

复用 IcpGenerator 的 SSE 流式输出模式：
  前端 → POST SSE → email_generator.generate() → chat_stream → yield 事件
"""

import json
import re
from typing import AsyncIterator, Dict, Any, Optional

from app.services.ai_service import AIService


def html_to_plain_text(html: str) -> str:
    """从 HTML 中提取纯文本：去除标签，合并空白，解码常见实体"""
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


EMAIL_SYSTEM_PROMPT = """你是一位资深的 B2B 外贸邮件营销专家。你的任务是根据给定的客户画像、产品信息、企业资料和营销要求，撰写一封高转化率的商务开发邮件。

## 邮件撰写原则

1. **个性化**：根据收件人的行业、职位和公司背景定制内容
2. **价值导向**：开头快速说明你能为对方带来什么价值
3. **实力背书**：充分利用我方企业资料中的具体数据（成立年份、认证资质、出口市场、员工规模、工厂面积、OEM/ODM 能力等），用事实说话，增强信任感
4. **图文并茂**：在合适位置插入图片占位符，展示产品和工厂实力
5. **简洁有力**：正文不超过 200 词，段落简短
6. **明确行动号召**：结尾给出清晰、低门槛的下一步行动
7. **专业得体**：语气正式但不生硬，展现真诚合作意愿

## 变量占位符

邮件中涉及对方公司、联系人等信息时，使用 `{{ 变量名 }}` 占位符，发送时会自动替换：

**对方信息：**
- `{{ 客户联系人 }}` — 收件人姓名
- `{{ 客户公司 }}` — 对方公司名称
- `{{ 客户行业 }}` — 对方所处行业

**我方信息：**
- `{{ 我方企业 }}` — 我方公司名称
- `{{ 我方联系人 }}` — 发件人姓名
- `{{ 我方职位 }}` — 发件人职位
- `{{ 我方邮箱 }}` — 发件人邮箱
- `{{ 我方电话 }}` — 发件人电话
- `{{ 我方网站 }}` — 公司官网

**产品信息：**
- `{{ 产品名称 }}` — 推广的产品名称
- `{{ 产品描述 }}` — 产品简介
- `{{ 产品图片 }}` — 产品照片（自动替换为 <img> 标签，请在邮件正文中合适位置使用）

**企业形象：**
- `{{ 企业Logo }}` — 公司 Logo（自动替换为 <img> 标签，建议放在邮件开头或签名区）

## 图片使用指南

- 在邮件开头用 `{{ 企业Logo }}` 展示公司品牌
- 在产品介绍段落中插入 `{{ 产品图片 }}`，让客户直观看到产品
- 图片使邮件更专业、更具说服力，但要适度（1-3 张为宜）
- 图片占位符会自动替换为实际图片 URL，你只需在合适位置插入即可

## 输出格式

请严格按照以下 JSON 格式输出。在 JSON 前后不要添加任何说明文字。

```json
{
  "subjects": [
    "主题方案1 — 突出价值",
    "主题方案2 — 提出问题",
    "主题方案3 — 简洁直接"
  ],
  "body_html": "<p>HTML 格式的邮件正文，使用 {{ 变量名 }} 占位符。在适合的位置插入 {{ 企业Logo }} 和 {{ 产品图片 }}</p>",
  "spam_score": 3,
  "read_time_seconds": 45
}
```

### body_html 要求
- 使用简单的 HTML 标签：<p>, <br>, <b>, <ul>, <li>, <img>, <table>
- 不要使用 <style>, <script>, 外部样式表
- 邮件开头可以用 <b> 加粗关键信息吸引注意
- 在合适位置插入图片占位符 {{ 企业Logo }}、{{ 产品图片 }}
- 图片可放在 <table> 中并排展示（如 2-3 张产品图）
- 邮件末尾附上签名区：发件人姓名 / 职位 / 公司 / 联系方式
- 签名区上方放 {{ 企业Logo }} 增加品牌识别度

### spam_score 评分标准（1-10 分）
- 1-3 分：内容个性化强，无垃圾关键词
- 4-6 分：有一定模板感但可接受
- 7-10 分：包含大量促销词汇，易被过滤

请客观评分，不要故意打低分。
"""

EMAIL_USER_PROMPT_TEMPLATE = """## 客户画像
{icp_summary}

## 推广产品
{product_info}

## 我方企业资料（用于邮件中展示实力和优势）
{company_profile}

## 邮件要求
- 语气：{tone}
- 行动号召：{cta}
- 关键卖点：{key_points}

{reference_section}

请基于以上信息撰写一封商务开发邮件。请充分利用我方企业资料中的具体数据（成立年份、认证、出口市场、OEM能力等），让邮件更具说服力和专业性。"""

TONE_LABELS = {
    "formal": "正式商务",
    "friendly": "商务友好",
    "concise": "简洁直接",
}

CTA_LABELS = {
    "reply": "回复邮件了解更多",
    "meeting": "预约一次简短通话/会议",
    "website": "访问我方网站了解详情",
    "catalog": "索取产品目录/样品",
}


# ── 语言标签 ──

LANGUAGE_LABELS = {
    "en": "英文 (English)",
    "es": "西班牙语 (Español)",
    "ru": "俄语 (Русский)",
}

TRANSLATE_SYSTEM_PROMPT = """你是一位专业的外贸邮件翻译专家。你的任务是将中文商务开发邮件**精确翻译**为{target_language}。

## 翻译要求

1. **保留 HTML 标签**：所有 HTML 标签（<p>, <b>, <ul>, <li>, <table>, <img> 等）必须原样保留，只翻译标签内的文本内容
2. **保留变量占位符**：所有 `{{{{ 变量名 }}}}` 格式的占位符必须原样保留，不要翻译或修改
3. **保留图片占位符**：`{{{{ 企业Logo }}}}`、`{{{{ 产品图片 }}}}` 原样保留
4. **专业术语准确**：外贸行业术语（FOB, MOQ, OEM, ISO 等）使用国际通用表达
5. **语气一致**：保持与原文相同的商务正式程度
6. **输出格式**：先输出翻译后的主题（每行一个，以 `## 主题` 开头），再输出翻译后的 HTML（以 `## HTML` 开头）

请严格按照格式输出，不要用代码块包裹。"""

TRANSLATE_USER_PROMPT = """请将以下中文邮件内容翻译为{target_language}。

## 主题

{subjects}

## HTML

{body_html}"""


class EmailGenerator:
    """AI 邮件模板流式生成器"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self._accumulated_text = ""
        self._output: Optional[Dict[str, Any]] = None

    def _build_user_prompt(self, input_data: dict) -> str:
        """构建生成 prompt"""
        data = {
            "icp_summary": "未指定客户画像",
            "product_info": "未指定产品",
            "company_profile": "（企业资料未完善，请基于产品和市场信息撰写邮件）",
            "tone": "商务友好",
            "cta": "回复邮件了解更多",
            "key_points": "高质量产品、有竞争力的价格、可靠的交货期",
            "reference_section": "",
            **input_data,
        }

        # 翻译枚举值
        data["tone"] = TONE_LABELS.get(data["tone"], data["tone"])
        data["cta"] = CTA_LABELS.get(data["cta"], data["cta"])

        # 参考邮件
        if data.get("reference_email"):
            data["reference_section"] = f"## 参考邮件样例\n请参照以下邮件的风格和结构：\n\n{data['reference_email']}"

        # 安全替换：转义花括号防止 format 报错
        safe_data = {}
        for k, v in data.items():
            if isinstance(v, str):
                safe_data[k] = v.replace("{", "{{").replace("}", "}}")
            else:
                safe_data[k] = str(v)

        return EMAIL_USER_PROMPT_TEMPLATE.format(**safe_data)

    def _parse_output(self, text: str) -> Optional[Dict[str, Any]]:
        """从 LLM 响应中解析 JSON"""
        if not text:
            return None
        # 策略 1: ```json ... ```
        match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 策略 2: 直接 JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # 策略 3: { ... }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None

    async def generate(
        self, input_data: dict
    ) -> AsyncIterator[Dict[str, Any]]:
        """流式生成邮件模板，逐 chunk yield SSE 事件"""
        user_prompt = self._build_user_prompt(input_data)
        messages = [
            {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        self._accumulated_text = ""

        async for token in self.ai_service.chat_stream(
            messages, temperature=0.8, max_tokens=4096
        ):
            self._accumulated_text += token
            yield {"type": "text", "content": token}

        # 解析最终输出
        self._output = self._parse_output(self._accumulated_text)

        if self._output is None:
            self._output = {
                "raw_text": self._accumulated_text,
                "parse_error": True,
            }

        yield {"type": "done"}

    async def translate(
        self, body_html: str, language: str, subjects: list = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """将中文模板翻译为目标语言，保留 HTML 标签和变量占位符。
        如果提供了 subjects，同时翻译邮件主题列表。"""
        subjects = subjects or []
        lang_label = LANGUAGE_LABELS.get(language, language)
        system_prompt = TRANSLATE_SYSTEM_PROMPT.format(target_language=lang_label)
        subjects_text = "\n".join(subjects) if subjects else "（无）"
        user_prompt = TRANSLATE_USER_PROMPT.format(
            target_language=lang_label,
            subjects=subjects_text,
            body_html=body_html or "",
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        self._translate_accumulated = ""
        async for token in self.ai_service.chat_stream(
            messages, temperature=0.3, max_tokens=4096
        ):
            self._translate_accumulated += token
            yield {"type": "translate_text", "content": token}

        # 解析翻译结果：提取主题和 HTML
        foreign_subjects, foreign_html = self._parse_translation(
            self._translate_accumulated
        )
        foreign_text = html_to_plain_text(foreign_html)
        yield {
            "type": "translated",
            "subjects_foreign": foreign_subjects,
            "body_html_foreign": foreign_html,
            "body_text_foreign": foreign_text,
        }

    def _parse_translation(self, text: str) -> tuple:
        """从翻译结果中提取主题列表和 HTML"""
        subjects_foreign = []
        body_html_foreign = ""

        # 匹配 "## 主题" 段落
        subj_match = re.search(
            r"##\s*主题\s*\n(.*?)(?=##\s*HTML|\Z)",
            text, re.DOTALL | re.IGNORECASE
        )
        if subj_match:
            subj_block = subj_match.group(1).strip()
            # 按行提取，去掉序号和前缀
            for line in subj_block.split("\n"):
                line = re.sub(r"^[\d\-\.•]+\s*", "", line).strip()
                if line:
                    subjects_foreign.append(line)

        # 匹配 "## HTML" 段落
        html_match = re.search(
            r"##\s*HTML\s*\n(.*?)$",
            text, re.DOTALL | re.IGNORECASE
        )
        if html_match:
            body_html_foreign = html_match.group(1).strip()
        else:
            # 如果没有分段标记，整个文本作为 HTML
            body_html_foreign = text.strip()

        # 去掉可能的代码块包裹
        body_html_foreign = re.sub(r"^```(?:html)?\s*", "", body_html_foreign)
        body_html_foreign = re.sub(r"\s*```$", "", body_html_foreign)
        body_text_foreign = html_to_plain_text(body_html_foreign)
        return subjects_foreign, body_html_foreign

    def get_translate_output(self) -> Optional[Dict[str, Any]]:
        """获取翻译后的完整输出"""
        if hasattr(self, "_translate_accumulated"):
            subjects, html_body = self._parse_translation(self._translate_accumulated)
            return {
                "subjects_foreign": subjects,
                "body_html_foreign": html_body,
                "body_text_foreign": html_to_plain_text(html_body),
            }
        return None

    def get_output(self) -> Optional[Dict[str, Any]]:
        """获取解析后的完整输出"""
        return self._output
