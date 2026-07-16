"""SMTP 邮件发送服务 — Phase 6 Email Marketing

使用 stdlib smtplib + email.mime，异步包装避免阻塞事件循环。
"""

import asyncio
import hashlib
import hmac
import logging
import smtplib
import uuid
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any

from app.config import settings
from app.core.security import decrypt_smtp_password

logger = logging.getLogger(__name__)

# 1x1 透明 PNG（追踪像素）
_TRACKING_PIXEL = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

# 标准邮件签名/退订模板
FOOTER_TEMPLATE = """
<br><br>
---
<br><small>
此邮件由 {from_name} ({from_email}) 通过 AI 外贸助手自动发送。<br>
如果您不希望再收到此类邮件，请<a href="{unsubscribe_url}">点击此处退订</a>。
</small>
"""


def render_template(
    template: str,
    variables: Dict[str, str],
) -> str:
    """替换模板中的 {{ 变量 }} 占位符

    特殊处理图片变量：{{ 企业Logo }}、{{ 产品图片 }} — 替换为 <img> 标签
    """
    result = template
    for key, value in variables.items():
        placeholder = "{{ " + key + " }}"
        if key in ("企业Logo", "产品图片") and value:
            # 替换为带样式的 img 标签
            max_width = "200" if key == "企业Logo" else "100%"
            style = f"max-width:{max_width}px;height:auto;display:block;"
            replacement = f'<img src="{value}" alt="{key}" style="{style}" />'
            result = result.replace(placeholder, replacement)
        else:
            result = result.replace(placeholder, str(value or ""))
    return result


def _build_message(
    smtp_config: dict,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str = "",
    tracking_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> MIMEMultipart:
    """构建 MIME 邮件"""
    msg = MIMEMultipart("alternative")
    # 发件邮箱即为认证邮箱，from_email 为空时回退到 username
    sender_email = smtp_config.get("from_email") or smtp_config.get("username", "")
    msg["From"] = f"{smtp_config.get('from_name', '')} <{sender_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    # 退订链接（含 HMAC token + tenant_id 防伪造，按租户隔离退订）
    payload = f"{to_email}:{tenant_id}" if tenant_id else to_email
    token = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        "sha256",
    ).hexdigest()
    tenant_param = f"&tenant_id={tenant_id}" if tenant_id else ""
    base = settings.APP_BASE_URL or "http://localhost:8000"
    unsubscribe_url = (
        f"{base}/api/v1/email/unsubscribe?email={to_email}&token={token}{tenant_param}"
    )

    # 邮件尾部
    footer = FOOTER_TEMPLATE.format(
        from_name=smtp_config.get("from_name", ""),
        from_email=sender_email,
        unsubscribe_url=unsubscribe_url,
    )

    # 追踪像素
    tracking_img = ""
    if tracking_id:
        tracking_url = f"{settings.APP_BASE_URL or 'http://localhost:8000'}/api/v1/email/tracking/{tracking_id}.png"
        tracking_img = f'<img src="{tracking_url}" width="1" height="1" style="display:none" alt="" />'

    full_html = html_body + footer + tracking_img

    msg.attach(MIMEText(text_body or "请使用支持 HTML 的邮件客户端查看", "plain", "utf-8"))
    msg.attach(MIMEText(full_html, "html", "utf-8"))

    return msg


async def send_email(
    smtp_config: dict,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str = "",
    tracking_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """异步发送单封邮件（在 executor 中运行同步 SMTP）"""
    loop = asyncio.get_event_loop()

    def _send():
        msg = _build_message(
            smtp_config, to_email, subject, html_body, text_body,
            tracking_id, tenant_id,
        )
        host = smtp_config["host"]
        port = smtp_config.get("port", 465)

        try:
            # local_hostname 设为 localhost，避免本机内网 IP（如 192.168.x.x）
            # 被 SMTP 服务器当成垃圾邮件源而断开连接
            if port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=30, local_hostname="localhost")
            else:
                server = smtplib.SMTP(host, port, timeout=30, local_hostname="localhost")
                server.starttls()

            smtp_password = decrypt_smtp_password(smtp_config.get("password", ""))
            server.login(smtp_config["username"], smtp_password)
            server.send_message(msg)
            server.quit()
            return {"success": True}
        except smtplib.SMTPAuthenticationError as e:
            return {"success": False, "error": f"SMTP 认证失败: {e.smtp_error}"}
        except smtplib.SMTPException as e:
            return {"success": False, "error": f"SMTP 错误: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    return await loop.run_in_executor(None, _send)
