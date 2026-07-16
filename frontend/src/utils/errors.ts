/**
 * Pydantic 校验错误翻译工具
 *
 * 将 FastAPI/Pydantic 返回的 422 错误详情数组转为清晰的中文提示。
 * 原始格式：[{loc: ["body","smtp_config","host"], msg: "field required", type: "value_error.missing"}]
 */

interface PydanticError {
  loc: string[];
  msg: string;
  type: string;
}

/** 字段路径 → 中文名称映射 */
const FIELD_NAME_MAP: Record<string, string> = {
  // Campaign 创建请求
  name: "任务名称",
  template_id: "模板",
  customer_ids: "客户列表",
  // SMTP 配置
  host: "SMTP 服务器地址",
  port: "端口号",
  username: "发件邮箱地址",
  password: "邮箱授权码",
  from_name: "发件人名称",
  from_email: "发件人邮箱（显示）",
  smtp_config: "SMTP 配置",
  // 通用
  email: "邮箱地址",
  subject: "邮件主题",
  body_html: "邮件正文",
  status: "状态",
  title: "标题",
};

/** Pydantic 错误类型 → 中文描述 */
function translatePydanticMessage(msg: string): string {
  const patterns: [RegExp | string, string][] = [
    ["field required", "此字段为必填项，请填写"],
    ["value is not a valid integer", "请输入有效的整数"],
    ["value is not a valid uuid", "ID 格式无效"],
    ["value is not a valid email address", "请输入有效的邮箱地址"],
    [/ensure this value has at least (\d+) characters?/, "至少需要 $1 个字符"],
    [/ensure this value has at most (\d+) characters?/, "不能超过 $1 个字符"],
    [/ensure this value has at least (\d+) items?/, "至少需要选择 $1 项"],
    [/ensure this value has at most (\d+) items?/, "最多可选择 $1 项"],
    [/value is not a valid enumeration; permitted: (.+)/, "无效的选项，允许：$1"],
    [/string does not match regex "(.+)"/, "格式不符合要求"],
    ["value could not be parsed to a boolean", "请输入有效的布尔值"],
    ["value is not a valid dict", "数据格式无效"],
    ["value is not a valid list", "数据格式无效"],
  ];

  for (const [pattern, replacement] of patterns) {
    if (typeof pattern === "string") {
      if (msg === pattern) return replacement;
    } else {
      const match = msg.match(pattern);
      if (match) {
        return msg.replace(pattern, replacement);
      }
    }
  }
  return msg;
}

/** 从错误 loc 路径提取最后一个有中文映射的字段名 */
function extractFieldName(loc: string[]): string {
  // 跳过 body 等前缀，从后往前找有中文映射的字段
  for (let i = loc.length - 1; i >= 0; i--) {
    const name = FIELD_NAME_MAP[loc[i]];
    if (name) return name;
  }
  // 兜底：返回最后一个路径段
  return loc[loc.length - 1] || "未知字段";
}

/**
 * 将 Pydantic 422 错误详情数组转为一行中文提示
 * @param detail FastAPI 返回的 detail 数组
 * @returns 中文错误提示字符串
 */
export function formatPydanticErrors(detail: PydanticError[]): string {
  if (!Array.isArray(detail) || detail.length === 0) return "";

  const messages = detail.map((err) => {
    const fieldName = extractFieldName(err.loc);
    const desc = translatePydanticMessage(err.msg);
    return `「${fieldName}」${desc}`;
  });

  return messages.join("；");
}

/**
 * 从 HTTP 错误响应中提取可读的中文错误提示
 * 优先处理 Pydantic 422 数组格式，否则返回 detail 字符串或兜底文案
 */
export function getErrorMessage(err: any, fallback = "操作失败"): string {
  const detail = err?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return formatPydanticErrors(detail) || fallback;
  }

  if (typeof detail === "string" && detail.length > 0) {
    return detail;
  }

  return err?.message || fallback;
}
