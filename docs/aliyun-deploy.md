# 阿里云部署方案

> 预算：最低 ~¥90-120/月（不含域名，直接用 IP 访问）  
> 目标：单机部署全部服务，适合项目起步阶段

---

## 一、资源规划

### 推荐方案：轻量应用服务器

| 配置项 | 规格 | 月费 |
|--------|------|------|
| 轻量应用服务器 | 2 vCPU / 4 GB 内存 / 60 GB SSD | ~¥90-120 |
| 带宽 | 5 Mbps 固定 | 含在套餐内 |
| 流量包 | 1 TB/月 | 含在套餐内 |
| **合计** | | **~¥90-120/月** |

> 备注：阿里云轻量应用服务器自带固定带宽和流量包，相比同等配置的 ECS（~¥170/月）便宜约 40%。新用户首年通常有折扣，最低至 ¥60/月。  
> **不需要域名**，部署完成后直接通过 `http://<公网IP>` 访问。

### 为什么不用 Elasticsearch？

项目代码中 Elasticsearch **从未被实际使用**（`ELASTICSEARCH_URL` 仅在 `config.py` 定义了变量，无任何业务代码引用）。去掉后 4 GB 内存完全够用。

### 资源预算分配

| 服务 | 预估内存 | 说明 |
|------|----------|------|
| OS（Alibaba Cloud Linux 4） | ~500 MB | 系统基础开销 |
| PostgreSQL 16 + pgvector | ~300 MB | 数据库 + 向量扩展 |
| Redis 7 | ~80 MB | 缓存 / 会话 |
| Backend（uvicorn 2 workers） | ~400 MB | Python FastAPI |
| Nginx | ~50 MB | 前端静态文件 + API 代理 |
| Docker 守护进程 | ~100 MB | 容器运行时 |
| **已用合计** | **~1.4 GB** | |
| **剩余可用** | **~2.6 GB** | 留有充足余量 |

### 升级路径

| 阶段 | 方案 | 月费 |
|------|------|------|
| 起步（当前） | 轻量服务器 2c4g，单机全服务 | ~¥90-120 |
| 数据增长 | 轻量服务器 4c8g + 100 GB SSD | ~¥200 |
| 正式运营 | ECS 2c4g + ApsaraDB RDS PG + Redis 云服务 | ~¥450 |
| 规模扩展 | ECS 多台 + SLB + RDS 高可用 + CDN | ¥1000+ |

---

## 二、服务器初始化

### 2.1 创建服务器

1. 登录 [阿里云轻量应用服务器控制台](https://swas.console.aliyun.com/)
2. 选择「创建服务器」
3. 地域：选择目标客户所在区域（外贸建议 **中国香港** 或 **华东 1（杭州）**）
4. 镜像类型：**系统镜像 → Alibaba Cloud Linux 4**
5. 套餐：**2 vCPU / 4 GB 内存 / 60 GB SSD**
6. 设置 root 密码或 SSH 密钥
7. 创建完成后，在防火墙规则中放行端口：**22、80、8000**

### 2.2 基础环境

> Alibaba Cloud Linux 4 基于 CentOS Stream 9/RHEL 9，内核针对阿里云优化，兼容性好。

```bash
# SSH 登录（或用阿里云控制台自带的「远程连接」）
ssh root@<服务器公网IP>

# 安装 Docker（使用阿里云镜像源，下载更快）
dnf install -y dnf-plugins-core
dnf config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker --now

# 验证
docker --version
docker compose version
```

---

## 三、项目部署

### 3.1 上传代码

```bash
# 在服务器上
mkdir -p /opt/freight-agent
cd /opt/freight-agent

# 从本地推送代码（在本地执行，替换 <IP> 为服务器公网 IP）
# rsync -avz --exclude '.venv' --exclude 'node_modules' --exclude '.git' \
#   ./backend ./frontend ./shared ./docker-compose.yml \
#   root@<IP>:/opt/freight-agent/
```

或使用 Git：
```bash
cd /opt/freight-agent
git clone <仓库地址> .
```

### 3.2 精简 docker-compose.yml

服务器部署不需要 Elasticsearch 和前端开发容器，使用以下 `docker-compose.yml`：

```yaml
version: "3.8"

services:
  db:
    image: pgvector/pgvector:pg16
    container_name: ft_db
    environment:
      POSTGRES_DB: foreign_trade
      POSTGRES_USER: ft_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-ft_dev_password}
    ports:
      - "127.0.0.1:5432:5432"  # 仅本地监听
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: ft_redis
    ports:
      - "127.0.0.1:6379:6379"  # 仅本地监听
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: ft_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
    ports:
      - "127.0.0.1:8000:8000"  # 仅本地监听，由 Nginx 反代
    depends_on:
      - db
      - redis
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
      - ./shared:/shared:ro
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: ft_nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  pgdata:
```

> 和开发环境区别：① 去掉了 Elasticsearch；② 去掉了前端 dev server（改用 Nginx 直接托管静态文件）；③ 数据库/Redis/后端端口仅监听 127.0.0.1，不对外暴露；④ 删除了 443 端口（无 HTTPS）。

### 3.3 前端构建

在本地构建前端，然后上传 `dist/` 到服务器：

```bash
# 本地执行
cd frontend
npm ci
npm run build
# 产出在 frontend/dist/

# 上传到服务器（替换 <IP>）
rsync -avz ./dist/ root@<IP>:/opt/freight-agent/frontend/dist/
```

> 不在服务器上构建：避免 npm install 消耗大量内存导致 OOM。

### 3.4 Nginx 配置

创建 `nginx.conf`：

```nginx
events {}

http {
    include /etc/nginx/mime.types;
    server_tokens off;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name _;

        # 前端静态文件
        root /usr/share/nginx/html;
        index index.html;

        # API 反向代理
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 60s;
        }

        # Vue Router history 模式
        location / {
            try_files $uri $uri/ /index.html;
        }

        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 3.5 环境变量

编辑 `backend/.env`，确保生产配置正确：

```ini
# 数据库 — 连接同一 docker-compose 内的 db 服务
DATABASE_URL=postgresql+asyncpg://ft_user:ft_dev_password@db:5432/foreign_trade

# Redis
REDIS_URL=redis://redis:6379/0

# JWT — 务必换为随机字符串
JWT_SECRET_KEY=<生成一个 64 位随机字符串>

# AI — 填写实际 API Key
AI_API_URL=https://api.openai.com/v1
AI_API_KEY=sk-xxxxxxxx
AI_MODEL=gpt-4o-mini

# SMTP — 用于发送营销邮件
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-password
```

### 3.6 启动服务

```bash
cd /opt/freight-agent

# 拉取基础镜像
docker compose pull db redis nginx

# 构建并启动全部服务
docker compose up -d --build

# 查看运行状态
docker compose ps
docker compose logs -f --tail=100 backend
```

### 3.7 验证部署

```bash
# 在服务器上测试
curl http://localhost
curl http://localhost/api/v1/dashboard/stats

# 浏览器访问
# http://<服务器公网IP>
```

---

## 四、日常维护

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f --tail=200 backend

# 重启单个服务
docker compose restart backend

# 数据库备份
docker compose exec db pg_dump -U ft_user foreign_trade > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker compose exec -T db psql -U ft_user foreign_trade < backup_20240729.sql

# 升级所有镜像
docker compose pull
docker compose up -d --build
```

### 建议添加定时备份

```bash
# crontab -e
0 3 * * * cd /opt/freight-agent && docker compose exec -T db pg_dump -U ft_user foreign_trade > /opt/backups/db_$(date +\%Y\%m\%d).sql
```

---

## 五、后期可选：加域名 + HTTPS

当需要对外正式使用时，再购买域名（~¥50/年），然后用 Let's Encrypt 免费证书配置 HTTPS：

```bash
# 安装 certbot
dnf install -y certbot

# 申请证书
certbot certonly --webroot -w /usr/share/nginx/html -d your-domain.com

# 在 nginx.conf 中添加 443 端口 SSL 配置
# docker compose exec nginx nginx -s reload
```

---

## 六、成本对照表

| 项目 | 轻量服务器（推荐） | 传统 ECS |
|------|-------------------|----------|
| 计算 | 2c4g 含内 | 2c4g ~¥170 |
| 带宽 | 5 Mbps 固定 | 按量 ~¥0.8/GB |
| 磁盘 | 60 GB SSD | 40 GB ~¥20 |
| **月费** | **~¥90-120** | **~¥190+** |
| 适合 | 起步/小型项目 | 弹性扩展需求 |

> 结论：项目初期用轻量应用服务器，一年费用约 ¥1000-1400，直接用 IP 访问零额外成本。后续有需要再加域名和 HTTPS。
