"""ORM 模型包 — Alembic 通过 Base.metadata 自动发现所有模型"""

from app.database import Base

# Phase 1
from app.models.tenant import Tenant
from app.models.user import User
from app.models.platform_admin import PlatformAdmin

# Phase 2+
# from app.models.enterprise import EnterpriseProfile
# from app.models.product import Product
# from app.models.icp import Icp
# from app.models.customer import Customer
# from app.models.contact import Contact
# from app.models.email_template import EmailTemplate
# from app.models.email_campaign import EmailCampaign
# from app.models.send_log import SendLog
# from app.models.unsubscribe import Unsubscribe

__all__ = ["Base"]
