# GW2 Backend Docker Compose 部署指南

**版本**: v2.0  
**更新日期**: 2026-05-05  
**适用场景**: 单实依Docker Compose 部署（阿里云 ECS / 任意支持 Docker 的系统）  
**镜像体积**: ~180MB（多阶段构建（ 
**编排文件**: `backend/docker-compose.yml`（配置全部内联，无需 `.env` 文件） 

---

## 1. 环境要求

| 项目 | 最低配置| 推荐配置 |
|------|---------|---------|
| 实例 | 2 vCPU / 4GB 内存 | 4 vCPU / 8GB 内存 |
| 系统目| 40GB SSD | 100GB SSD |
| 操作系统 | Debian 12 / Ubuntu 22.04 | Debian 12 |
| Docker | 24.0+ | 最新版 |
| Docker Compose | 2.20+ | 最新版 |

**安全组规分*（入方向）

| 端口 | 协议 | 来源 | 说明 |
|------|------|------|------|
| 22 | TCP | 你的IP/32 | SSH 管理 |
| 80 | TCP | 0.0.0.0/0 | HTTP 访问 |
| 443 | TCP | 0.0.0.0/0 | HTTPS 访问（如需）|

---

## 2. 前置准备

### 2.1 创建 ECS 实例

1. 登录云服务商控制变→ECS →创建实例
2. 选择 **Debian 12** 成**Ubuntu 22.04** 镜像
3. 安全组开放22/80/443 端口
4. 设置 root 密码或绑定密钥对

### 2.2 绑定域名（可选）

如需 HTTPS，准备域名并解析分ECS 公网 IP、
---

## 3. 安装 Docker & Docker Compose

SSH 登录服务器后执行）
```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装 Docker
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 验证
sudo docker --version
sudo docker compose version
```

---

## 4. 部署应用

### 4.1 上传代码

**方式一: Git 克隆（推荐）**

```bash
cd /opt
sudo git clone <你的仓库地址> gw2-backend
cd gw2-backend/backend
sudo git checkout master
```

**方式二 SCP 上传**

```bash
# 本地执行
scp -r ./gw2-backend root@<ECS_IP>:/opt/
```

> **注意**：`docker-compose.yml` 一`Dockerfile` 位于项目根目录下的`backend/` 文件夹中，构建上下文（`context: .`）也指向该目录、
### 4.2 配置环境变量

本项目`docker-compose.yml` 采用**全部内联配置**，无需 `.env` 文件。直接修放`docker-compose.yml` 中的 `services.app.environment` 即可）
```yaml
environment:
  # 数据库配置（使用容器内db 服务（  DB_TYPE: mysql
  MYSQL_HOST: db
  MYSQL_PORT: 3306
  MYSQL_DATABASE: gw2
  MYSQL_USER: gw2
  MYSQL_PASSWORD: gw2_pass_2026   # →生产环境必须修改

  # 应用配置
  SECRET_KEY: change-me-to-a-random-string-at-least-32-characters-long  # →必须修改
  DEBUG: "false"
  LOG_LEVEL: info
  AUTO_INIT_DB: "true"
  ADMIN_INITIAL_PASSWORD: admin123456   # →建议修改

  # Uvicorn
  UVICORN_HOST: 0.0.0.0
  UVICORN_PORT: 8000
  UVICORN_WORKERS: 2
```

> 若使用外部数据库（如阿里云RDS），删除 `db` 服务，将 `MYSQL_HOST` 改为 RDS 地址，并移除 `depends_on db`、
### 4.3 启动服务

```bash
cd /opt/gw2-backend/backend
sudo docker compose up -d
```

首次启动会：
1. 拉取/构建 Docker 镜像（约 3-5 分钟（2. 启动 MySQL 8.0 容器并初始化数据应3. 启动 FastAPI 应用容器
4. 启动 Nginx 反向代理

### 4.4 验证部署

```bash
# 查看容器状性sudo docker compose ps

# 查看应用日志
sudo docker compose logs -f app

# 测试 API 健康检查（容器内）
curl http://localhost:8000/api/v1/health

# 测试 Nginx 健康检查curl http://localhost/nginx-health

# 测试公网访问（本地执行）
curl http://<ECS公网IP>/api/v1/health
```

---

## 5. 架构说明

### 5.1 三服务架构
```
┌──────────────    ┌──────────────    ┌───────────────  nginx     │────▶│     app     │────▶│     db      ──nginx:alpine─    │FastAPI/Uvicorn─   ─mysql:8.0  ── :80 :443   ─    ─ :8000       ─    ─ :3306      ─└──────────────    └──────────────    └──────────────       ─                  ─       ░                  ░  /var/www/html      /app/uploads
  /var/www/uploads   /app/logs
```

| 服务 | 镜像 | 容器名| 暴露端口 | 说明 |
|------|------|--------|---------|------|
| `app` | 本地构建（多阶段）| `gw2-backend` | `127.0.0.1:8000:8000` | FastAPI + Uvicorn |
| `db` | `mysql:8.0` | `gw2-mysql` | 无（内部网络）| 应用数据应|
| `nginx` | `nginx:alpine` | `gw2-nginx` | `80:80`、`443:443` | 反向代理 + 静态文件|

### 5.2 命名卷与网络

**命名南*（Docker 自动管理持久化））
| 卷名 | 挂载路径 | 说明 |
|------|---------|------|
| `mysql_data` | `/var/lib/mysql`（db 容器）| MySQL 数据持久化|
| `app_logs` | `/app/logs`（app 容器）| 应用日志 |
| `app_uploads` | `/app/uploads`（app 容器）| 上传文件 |

**网络**：- `gw2-network`（bridge 驱动）- 三个服务共享同一内部网络，服务名即为 DNS 主机名（`app`、`db`、`nginx` 互通）

### 5.3 Dockerfile 详解

**多阶段构建*）
| 阶段 | 基础镜像 | 说明 |
|------|---------|------|
| `builder` | `python:3.13-slim` | 安装编译依赖（gcc、g++、libffi-dev、libmariadb-dev、pkg-config），创建虚拟环境并安装依资|
| `runtime` | `python:3.13-slim` | 仅保留运行时：安装`libmariadb3` + `curl`，复制虚拟环境，创建面root 用户 `gw2` |

**关键配置**：- 面root 运行：`USER gw2`
- 暴露端口：`EXPOSE 8000`
- 健康检查：`HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 CMD curl -fs http://localhost:8000/api/v1/health || exit 1`
- 入口脚本：`ENTRYPOINT ["sh", "./entrypoint.sh"]`

### 5.4 entrypoint.sh 启动逻辑

`backend/scripts/docker/entrypoint.sh` 执行流程）
1. **等待 MySQL 就绪**（仅录`DB_TYPE=mysql` 一`MYSQL_HOST` 已配置时）：
   - 使用 Python socket 连接测试
   - 最复30 次重试，间隔 2 移   - 超时后继续启动（不阻塞）

2. **自动初始化数据库**（仅录`AUTO_INIT_DB=true` 时）（   - 执行 `app.config.database.init_db()` 自动建表
   - 失败则跳过（表已存在时安全）

3. **启动 Uvicorn**：   ```bash
   uvicorn main:app \
       --host "${UVICORN_HOST:-0.0.0.0}" \
       --port "${UVICORN_PORT:-8000}" \
       --workers "${UVICORN_WORKERS:-1}" \
       --proxy-headers \
       --forwarded-allow-ips "*" \
       --access-log \
       --log-level "${LOG_LEVEL:-info}"
   ```

### 5.5 Nginx 配置细节

`backend/scripts/docker/nginx.conf` 一*完整主配置*（非站点配置），功能包括）
- **上游定义**：`upstream app_server { server app:8000; keepalive 32; }`
- **健康检查端点*：`/nginx-health` 返回 `200 healthy`
- **后端代理路由**（按优先级排列）（  - `/api/` →`app_server`
  - `/health` →`app_server`
  - `/docs` →`app_server`
  - `/redoc` →`app_server`
  - `/openapi.json` →`app_server`
- **上传文件直接访问**：`/uploads/` →`/var/www/uploads/`，缓存7 复- **前端 SPA 静态文件服功*（  - `root /var/www/html`
  - `try_files $uri $uri/ @spa`
  - `location @spa` 回写分`index.html`
- **长期缓存**（带 hash 的资源）：`~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|otf)$`
  - `expires 1y`
  - `Cache-Control: public, immutable`
  - 关闭 access_log
- **Gzip 压缩**：等级6，覆目text/css、application/json、image/svg+xml 等- **上传大小限制**：`client_max_body_size 100M`
- **HTTPS server 块*（注释状态，需自行配置 SSL 证书）
---

## 6. 日常运维

### 6.1 查看日志

```bash
# 应用日志
sudo docker compose logs -f app --tail 100

# Nginx 访问日志
sudo docker compose logs -f nginx --tail 100

# MySQL 日志
sudo docker compose logs -f db --tail 100

# 所有服务日志sudo docker compose logs -f
```

### 6.2 重启服务

```bash
# 重启单个服务
sudo docker compose restart app

# 重启所有服功sudo docker compose restart

# 重新构建并启动（代码更新后）
sudo docker compose up -d --build
```

### 6.3 更新应用

```bash
cd /opt/gw2-backend/backend
sudo git pull origin master

# 如果 requirements.txt 有变化，需要重新构建sudo docker compose up -d --build app

# 仅代码更新（无需重建（sudo docker compose restart app
```

### 6.4 备份数据

**数据库备件*）
```bash
# 备份 MySQL
sudo docker compose exec db mysqldump -u root -p"root_pass_2026" gw2 > /opt/backups/gw2_$(date +%Y%m%d).sql

# 定时备份（加充crontab（0 3 * * * cd /opt/gw2-backend/backend && docker compose exec -T db mysqldump -u root -p"root_pass_2026" gw2 > /opt/backups/gw2_$(date +%Y%m%d).sql
```

**上传文件备份**：
```bash
sudo tar czvf /opt/backups/uploads_$(date +%Y%m%d).tar.gz /opt/gw2-backend/backend/uploads/
```

---

## 7. 生产环境优化（使用外部RDS）
### 7.1 使用阿里云RDS MySQL

1. 创建 RDS MySQL 8.0 实例
2. 创建数据库账变`gw2`，授权读内3. 添加白名单：ECS 公网/内网 IP
4. 记录连接地址

### 7.2 修改 docker-compose.yml

删除 `db` 服务，修放`app` 服务）
```yaml
services:
  app:
    # ...
    environment:
      DB_TYPE: mysql
      MYSQL_HOST: rm-xxxxxxxx.mysql.rds.aliyuncs.com
      MYSQL_PORT: 3306
      MYSQL_DATABASE: gw2
      MYSQL_USER: gw2
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      # 移除 MYSQL_ROOT_PASSWORD
      AUTO_INIT_DB: "false"   # RDS 建议手动初始化    # 移除 depends_on db

  # 删除整个 db 服务块
  nginx:
    # ...（保持不变）
```

同时删除底部 `volumes` 中的 `mysql_data`、
---

## 8. HTTPS 配置

### 8.1 使用 Let's Encrypt（免费证书）

```bash
# 安装 Certbot
sudo apt-get install -y certbot

# 申请证书
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书到项目目录sudo mkdir -p /opt/gw2-backend/backend/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/gw2-backend/backend/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/gw2-backend/backend/ssl/key.pem
```

取消 `docker-compose.yml` 一nginx 服务的SSL 挂载注释）
```yaml
volumes:
  # - ./ssl/cert.pem:/etc/nginx/ssl/cert.pem:ro
  # - ./ssl/key.pem:/etc/nginx/ssl/key.pem:ro
```

并编辑`scripts/docker/nginx.conf` 启用 HTTPS server 块、
### 8.2 自动续期

```bash
sudo crontab -e

# 添加续期任务
0 2 * * 1 certbot renew --quiet && docker compose -f /opt/gw2-backend/backend/docker-compose.yml restart nginx
```

---

## 9. 监控与告警
### 9.1 容器资源监控

```bash
# 实时查看容器资源使用
sudo docker stats
```

### 9.2 日志轮转

容器日志用Docker 自带 `json-file` 驱动管理，可通过 `/etc/docker/daemon.json` 配置）
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## 10. 常见问题

### Q: 容器启动失败，日志显示"Connection refused" to db

**A**: MySQL 容器启动需要时间，应用容器的`depends_on` 已配置`condition: service_healthy` 等待。如仍失败：

```bash
sudo docker compose restart app
```

### Q: 上传大文件（>10MB）失责
**A**: Nginx 已配置`client_max_body_size 100M`，如还需更大，修放`scripts/docker/nginx.conf` 后重名nginx、
### Q: 如何查看容器内的 Python 错误堆栈

**A**:

```bash
sudo docker compose logs app | grep ERROR
sudo docker compose exec app cat /app/logs/app.log
```

### Q: 如何进入容器调试

**A**:

```bash
sudo docker compose exec app sh
# 容器内执行Python
python -c "from app.core.config import get_settings; print(get_settings().APP_NAME)"
```

### Q: 数据库密码泄露后如何重置

**A**:

```bash
# 1. 修改 docker-compose.yml 中的密码
sudo nano /opt/gw2-backend/backend/docker-compose.yml

# 2. 如果是容器内 MySQL，进充db 容器修改
sudo docker compose exec db mysql -u root -p
# SQL: ALTER USER 'gw2'@'%' IDENTIFIED BY 'new_password';

# 3. 重启应用
sudo docker compose up -d
```

---

## 11. 目录结构说明

```
/opt/gw2-backend/backend/
├── docker-compose.yml          # 编排文件（配置全部内联）
├── Dockerfile                  # 多阶段镜像构建├── .env.example                # 环境变量模板（裸机部署参考）
├── app/                        # 应用代码
─  └── core/
─      └── config.py           # 统一配置（58 行）
├── main.py                     # FastAPI 入口
├── requirements.txt            # Python 依赖
├── uploads/                    # 上传文件（volume 持久化）
├── logs/                       # 日志（volume 持久化）
├── database/                   # SQLite 数据（如使用（├── scripts/
─  └── docker/
─      ├── entrypoint.sh       # 容器启动脚本
─      └── nginx.conf          # Nginx 主配置├── dist/                       # 前端 SPA 构建产物（挂载到 nginx（└── docs/
    └── 06-deployment/
        └── deploy-docker-ecs.md  # 本文档```

---

## 12. 一键部署脚本（可选）

创建 `/opt/deploy.sh`:

```bash
#!/bin/bash
set -e

PROJECT_DIR="/opt/gw2-backend/backend"
BACKUP_DIR="/opt/backups"

# 备份
echo "备份当前数据..."
mkdir -p $BACKUP_DIR
cd $PROJECT_DIR
docker compose exec -T db mysqldump -u root -p"root_pass_2026" gw2 > "$BACKUP_DIR/gw2_pre_deploy_$(date +%Y%m%d_%H%M%S).sql" 2>/dev/null || true

# 更新代码
echo "拉取最新代码.."
cd $PROJECT_DIR
git pull origin master

# 重建并启功echo "构建并启动服功.."
docker compose up -d --build

# 清理旧镜像echo "清理旧镜像.."
docker image prune -f

echo "部署完成!"
docker compose ps
```

赋予执行权限:

```bash
chmod +x /opt/deploy.sh
```

---

**部署完成（* 🎉  
访问 `http://<ECS公网IP>/api/v1/health` 验证服务是否正常运行、
---

*部署文档版本: v2.0 | 更新日期: 2026-05-05 | 适用项目版本: >= 1.0.0*
