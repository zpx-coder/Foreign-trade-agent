"""ORM 模型包 — Alembic 通过 Base.metadata 自动发现所有模型"""

from app.database import Base

# 模型文件在此导入后，Alembic 即可自动检测
# from app.models.tenant import Tenant       # Phase 1
# from app.models.user import User           # Phase 1
# from app.models.enterprise import EnterpriseProfile  # Phase 2
# from app.models.product import Product     # Phase 2
# from app.models.icp import Icp             # Phase 3
# from app.models.customer import Customer   # Phase 4
# from app.models.contact import Contact     # Phase 4
# from app.models.email_template import EmailTemplate     # Phase 6
# from app.models.email_campaign import EmailCampaign     # Phase 6
# from app.models.send_log import SendLog                 # Phase 6
# from app.models.unsubscribe import Unsubscribe          # Phase 6

__all__ = ["Base"]
