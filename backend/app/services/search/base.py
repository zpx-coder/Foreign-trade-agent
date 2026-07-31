"""搜索渠道抽象接口 — Phase 4"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# ── 非公司结果过滤 ──

# URL 域名黑名单：命中任一关键词则丢弃
NON_COMPANY_DOMAIN_KEYWORDS = [
    # 内容平台 / 博客
    "zhihu.com", "medium.com", "blog.", "blogs.",
    # 百科 / 知识库
    "wikipedia.org", "baike.baidu.com", "wiki.",
    # 新闻 / 媒体
    "news.", "forbes.com", "36kr.com", "sohu.com",
    "ifeng.com", "163.com", "qq.com", "sina.com.cn",
    "bbc.com", "cnn.com", "reuters.com", "bloomberg.com",
    "finance.yahoo.com", "marketwatch.com",
    # 行业报告 / 市场研究
    "grandviewresearch.com", "mordorintelligence.com", "marketsandmarkets.com",
    "statista.com", "ibisworld.com", "euromonitor.com",
    "reportlinker.com", "researchandmarkets.com", "marketresearch.com",
    "frost.com", "gartner.com", "forrester.com", "idc.com",
    "technavio.com", "alliedmarketresearch.com", "transparencymarketresearch.com",
    "futuremarketinsights.com", "factmr.com", "thebusinessresearchcompany.com",
    "360marketupdates.com", "absolutereports.com", "marketstudyreport.com",
    "dataintelo.com", "databridgemarketresearch.com", "cognitive-marketresearch.com",
    "questale.com", "marketresearchengine.com", "planetmarketreports.com",
    "globalmarketmonitor.com", "globalmarketvision.com",
    "verifiedmarketresearch.com", "exactitudeconsultancy.com",
    "contify.com", "dataintelligence.com", "marketintelligencedata.com",
    # 中文行业报告站
    "iresearch", "analysys.cn", "bigdata-research.cn", "askci.com",
    "chyxx.com", "qianzhan.com", "forwardthe.com", "reportcn.com",
    # 海关数据 / 贸易平台（非公司结果）
    "panjiva.com", "importgenius.com", "trademap.org",
    # 跨境导航 / 贸易资讯（文章聚合，非公司）
    "amz123.com", "hktdc.com", "dny123.com",
    # 行业报告 / 研究机构文章
    "baijiahao.baidu.com", "ethicalsupplychain.org",
    "scribd.com", "mag.ctoy.com.cn",
    # 名录 / 目录聚合站
    "beiei.com", "mingluji.com", "esources.co.uk",
    "globalimporter.net", "foreign.emagecompany.com",
    "africa-businesspages.com", "africantradeplatform.com",
    "globaltoysandgames.com", "csi-factory-china.com",
    "leadxpress.com", "tragoa.com",
    # 企业信息查询 / 黄页
    "qizhidao.com", "shenzhen.11467.com",
    # 服务公司文章页面
    "zhongmaoda.net", "sh-zhongshen.com", "mugroup.com",
    # 问答 / 论坛
    "quora.com", "reddit.com", "stackexchange.com",
    "stackoverflow.com", "zhidao.baidu.com",
    # 视频 / 社交
    "youtube.com", "youtu.be", "bilibili.com",
    "facebook.com", "twitter.com", "instagram.com",
    "tiktok.com", "weibo.com",
    # 招聘
    "linkedin.com/jobs", "indeed.com", "glassdoor.com",
    "zhaopin.com", "51job.com",
    # 电商
    "amazon.com", "ebay.com", "alibaba.com/products",
]

# 标题关键词：命中则判定为文章/报告而非公司
_ARTICLE_TITLE_PATTERNS_CN = [
    # 报告/研究类
    r"报告",           # 市场报告、行业报告、分析报告
    r"研报",           # 研究报告
    r"白皮书",
    r"蓝皮书",
    r"调研",           # 市场调研
    r"统计",           # 行业统计
    # 分析/趋势类
    r"分析[^师]",      # 市场分析、数据分析（排除"分析师"）
    r"趋势",           # 市场趋势
    r"洞察",           # 行业洞察
    r"走势",           # 价格走势
    r"前景",           # 市场前景
    r"预测",           # 行业预测
    r"概览",           # 市场概览
    r"扫描",           # 市场格局扫描
    r"深度",           # 深度分析/深度解读
    r"解读",           # 政策解读
    r"机遇",           # 市场机遇
    # 榜单/排名类
    r"盘点",           # 十大品牌盘点
    r"排名",           # 公司排名
    r"榜单",           # 排行榜
    # 名录/目录类
    r"[名目][录錄]",   # 进口商名录、企业名录（含繁简体）
    r"进口商",         # 进口商名录
    r"采购商",         # 采购商名录
    r"企业[名目]",     # 企业名录
    # 攻略/指南类
    r"攻略",           # 采购攻略
    r"指南",           # 出口指南（去掉$锚定，匹配更多模式）
    r"详解",           # 全流程详解
    r"解析",           # 全流程解析
    r"全流程",         # 全流程详解/解析
    r"一篇搞定",       # 一篇搞定
    r"怎么.*[？?]",    # 怎么进入？
    r"如何.*[？?]",    # 如何出海？
    # 文章特征
    r"万字长文",       # 万字长文
    r"认证标准",       # 准入与认证标准
    r"准入与认证",     # 市场准入与认证
    r"进口代理",       # 进口玩具代理加工
    r"年.*展望",       # 2024年展望
    r"投资",           # 投资分析
    # 贸易研究/市场渠道文章
    r"打通.*市場",     # 打通東盟消費市場
    r"網上銷售渠道",   # 網上銷售渠道
    r"销售渠道",       # 销售渠道（线上/线下）
    # 系列标记
    r"[（(][上下中]篇[）)]",   # （上篇）（下篇）
    r"[（(][一二三四五六七八九十\d]+[）)]\s*$",  # （四）
    # PDF/文档
    r"\|\s*PDF",       # | PDF
]

_ARTICLE_TITLE_PATTERNS_EN = [
    # Market/industry reports
    r"\bmarket\s+(report|analysis|research|overview|outlook|size|share|trend|forecast|insight)\b",
    r"\bindustry\s+(report|analysis|trend|overview|insight)\b",
    r"\b(report|analysis)\s+(on|of)\s+the\b",
    # Rankings/lists
    r"\btop\s+\d{1,2}\b",          # Top 10, Top 25
    r"\bbest\s+\d{1,2}\b",          # Best 5
    r"\b\d{1,2}\s+(largest|biggest|leading)\b",  # 10 largest
    # Directories/lists
    r"\b(buyers?|importers?|purchasers?|suppliers?)\s+(list|directory|database)\b",
    r"\b(factory|third.party)\s+list\b",
    r"\b(wholesale|retail)\s+(buyers?|importers?|suppliers?)\b",
    # How-to guides
    r"\bhow\s+to\b",                # How to find/import
    r"\b(guide|tutorial)\s+(to|for)\b",
    r"\bstep.by.step\b",
    # Market data
    r"\bgrowth\s+rate\b",
    r"\bcagr\b",                    # Compound Annual Growth Rate
    r"\bmarket\s+segmentation\b",
    r"\bswot\s+analysis\b",
    r"\bindustry\s+\d{4}\b",        # Industry 2024
    r"\boutlook\s+\d{4}\b",         # Outlook 2025
    # Platform/marketplace
    r"\b(b2b|b2c)\s+(marketplace|platform|portal)\b",
    r"\b(ecommerce|e-commerce)\s+platform\b",
    r"\btrade\s+platform\b",
    # Generic non-company
    r"^\d{4}[\.\s].*(list|directory|database)",  # 2024.xxx List
]

# 编译正则（忽略大小写）
_ARTICLE_RE_CN = re.compile("|".join(_ARTICLE_TITLE_PATTERNS_CN))
_ARTICLE_RE_EN = re.compile("|".join(_ARTICLE_TITLE_PATTERNS_EN), re.IGNORECASE)


def is_non_company_url(url: Optional[str]) -> bool:
    """检查 URL 是否命中非公司网站黑名单"""
    if not url:
        return False
    url_lower = url.lower()
    for keyword in NON_COMPANY_DOMAIN_KEYWORDS:
        if keyword in url_lower:
            return True
    return False


def looks_like_article_title(title: str) -> bool:
    """检查搜索结果标题是否像文章/报告而非公司名。

    用保守的正则匹配，只排除明显是文章标题的结果。
    公司名中不太可能出现"市场报告"、"industry report"这类短语。
    """
    if not title or not title.strip():
        return False
    if _ARTICLE_RE_CN.search(title):
        return True
    if _ARTICLE_RE_EN.search(title):
        return True
    return False


# ── 更宽泛的非公司结果检测（供 post-curation 使用）──

# 明显不是公司名的页面标题
_NON_COMPANY_EXACT_NAMES = {
    "关于我们", "联系我们", "首页", "Buyer Enquiry", "Contact Us",
    "Home Page", "Other Toys", "International Distributors",
    "International Buyers", "Global Importers",
}

# 泛泛的描述性名称模式
_GENERIC_NAME_PATTERNS = [
    r"^(Toys|Toy|Games|Electronics|Products)\s+(buyer|importer|supplier|distributor)",
    r"^Wholesale\s+\w+\s+Supplier\s+for",
]


def is_clearly_not_company(name: str, website: Optional[str] = None) -> bool:
    """更宽泛的非公司结果检测，用于 post-curation 过滤。

    与 looks_like_article_title 互补：前者在搜索渠道解析时使用（保守），
    本函数在 AI curation 之后使用（更激进），两者共同构成三层防线。
    """
    if not name or not name.strip():
        return True

    # 1. URL 作为名称
    if name.startswith("https://") or name.startswith("http://"):
        return True

    # 2. 精确匹配的页面标题
    if name.strip() in _NON_COMPANY_EXACT_NAMES:
        return True

    # 3. 垃圾数据
    if name.strip() == "LinkedIn | LinkedIn":
        return True

    # 4. 泛泛描述
    for pat in _GENERIC_NAME_PATTERNS:
        if re.search(pat, name, re.IGNORECASE):
            return True

    # 5. 复用文章标题检测
    if looks_like_article_title(name):
        return True

    return False


@dataclass
class SearchResult:
    """搜索结果 — 渠道无关的标准化结构"""
    company_name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    contacts: List[Dict[str, Any]] = field(default_factory=list)
    source_url: Optional[str] = None
    source_channel: str = ""
    # 如果为 True，跳过 LLM 提取步骤直接保存（AI 渠道已返回结构化数据）
    skip_extraction: bool = False
    # AI 精筛匹配度评分（1-10），仅 AI curation 设置
    relevance_score: Optional[int] = None

    @property
    def domain(self) -> str:
        """提取域名用于去重"""
        if not self.website:
            return self.company_name.lower().strip()
        from urllib.parse import urlparse
        parsed = urlparse(self.website if "://" in self.website else f"https://{self.website}")
        return parsed.netloc or self.website.lower().strip()


class SearchChannel(ABC):
    """搜索渠道抽象基类"""

    @abstractmethod
    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
    ) -> List[SearchResult]:
        """执行搜索，返回标准化结果列表"""
        ...
