# GW2 WvW 日志系统 - Debian 12 裸机部署指南

**版本**: v2.0  
**更新日期**: 2026-05-05  
**适用系统**: Debian 12 (bookworm)  
**部署方式**: 裸机部署 (Systemd + Uvicorn + 可选 Nginx)  
**Python 版本**: 3.13.3（从源码编译）  
**数据库**: SQLite / MySQL 8.0 / PostgreSQL（通过 `DB_TYPE` 切换，不区分大小写）  

---

## 一、部署前准备

### 1.1 服务器要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核 |
| 内存 | 2GB（编译 Python 3.13 需要） | 4GB |
| 磁盘 | 20GB SSD（至少 10GB 空闲） | 50GB SSD |
| 网络 | 1Mbps | 5Mbps+ |

### 1.2 需要准备的材料

1. **项目源码** — 打包上传到服务器（或 git clone）
2. **SSH 访问** — root 权限
3. **域名**（可选）— 用于 HTTPS 和 Nginx 配置

---

## 二、快速部署（一键脚本）

### 2.1 上传代码到服务器

```bash
# 本地打包
zip -r gw2-backend.zip gw2-backend/ -x "*.git*" -x "*.venv*" -x "*__pycache__*"

# 上传到服务器
scp gw2-backend.zip root@your-server-ip:/root/

# 服务器上解压
ssh root@your-server-ip "cd /root && unzip -q gw2-backend.zip"
```

### 2.2 运行部署脚本

```bash
ssh root@your-server-ip
cd /root/gw2-backend
chmod +x scripts/deploy/install.sh
sudo ./scripts/deploy/install.sh
```

脚本会交互式询问：
- 数据库类型（`mysql` / `sqlite`，默认 `mysql`）
- MySQL root 密码和应用密码（如果选择 MySQL）
- 是否安装 Nginx 反向代理（默认 `N`）
- 项目源码路径（默认当前目录）

### 2.3 脚本自动完成的工作（共 462 行，9 大步骤）

| 步骤 | 函数名 | 说明 |
|------|--------|------|
| 1 | `check_root` + `check_os` | 检查 root 权限与 Debian 版本 |
| 2 | `interactive_config` | 交互式选择数据库类型、Nginx、源码路径 |
| 3 | `install_system_deps` | `apt update && apt upgrade`，安装编译依赖（build-essential、libssl-dev、libmysqlclient-dev 等） |
| 4 | `install_python` | 从 `https://www.python.org/ftp/python/3.13.3/` 下载源码，编译安装到 `/usr/local` |
| 5 | `install_mysql` | 安装 `default-mysql-server`，创建数据库 `gw2_log_system`，用户 `gw2` |
| 6 | `setup_project_user` + `deploy_code` | 创建系统用户 `gw2`（无登录权限），rsync 代码到 `/opt/gw2-backend` |
| 7 | `setup_venv` | `python3.13 -m venv venv` 并安装 `requirements.txt` |
| 8 | `setup_systemd` | 复制 `gw2-backend.service`，替换密码与随机 `SECRET_KEY`，注册开机自启 |
| 9 | `setup_nginx` + `setup_logrotate` + `setup_firewall` | 可选安装 Nginx、配置 logrotate（保留 30 天）、UFW 防火墙 |
| 10 | `start_service` + `print_summary` | 启动服务并输出部署摘要 |

---

## 三、手动部署（如果你想自己控制每一步）

### 3.1 安装系统依赖

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev \
    libffi-dev liblzma-dev python3-openssl git \
    pkg-config libmysqlclient-dev libpq-dev
```

### 3.2 编译安装 Python 3.13.3

Debian 12 默认 Python 是 3.11，脚本会从源码编译 3.13.3：

```bash
cd /tmp
wget -q https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tgz
tar -xzf Python-3.13.3.tgz
cd Python-3.13.3

./configure \
    --prefix=/usr/local \
    --enable-optimizations \
    --enable-shared \
    --with-ensurepip=install \
    LDFLAGS="-Wl,-rpath /usr/local/lib"

make -j$(nproc)
sudo make altinstall
sudo ldconfig

python3.13 --version
```

编译完成后清理临时文件：`rm -rf /tmp/Python-3.13.3 /tmp/Python-3.13.3.tgz`

### 3.3 安装并配置 MySQL（可选，SQLite / PostgreSQL 可跳过）

```bash
sudo apt install -y default-mysql-server
sudo systemctl enable --now mysql

# 安全配置
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的root密码';"
sudo mysql -e "DELETE FROM mysql.user WHERE User='';"
sudo mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
sudo mysql -e "DROP DATABASE IF EXISTS test;"
sudo mysql -e "FLUSH PRIVILEGES;"

# 创建应用数据库和用户
sudo mysql -uroot -p"你的root密码" -e "CREATE DATABASE IF NOT EXISTS gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -uroot -p"你的root密码" -e "CREATE USER IF NOT EXISTS 'gw2'@'localhost' IDENTIFIED BY '你的应用密码';"
sudo mysql -uroot -p"你的root密码" -e "GRANT ALL PRIVILEGES ON gw2_log_system.* TO 'gw2'@'localhost';"
sudo mysql -uroot -p"你的root密码" -e "FLUSH PRIVILEGES;"
```

### 3.4 创建项目目录和用户

```bash
sudo useradd -r -s /bin/false -d /opt/gw2-backend -m gw2

sudo mkdir -p /opt/gw2-backend/{logs,uploads,database}
sudo chmod 755 /opt/gw2-backend
sudo chmod 750 /opt/gw2-backend/logs
sudo chmod 755 /opt/gw2-backend/uploads
sudo chmod 755 /opt/gw2-backend/database
sudo chown -R gw2:gw2 /opt/gw2-backend
```

### 3.5 部署代码

```bash
# 从本地上传
sudo rsync -av --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
    ./ /opt/gw2-backend/

sudo chown -R gw2:gw2 /opt/gw2-backend
```

### 3.6 创建虚拟环境并安装依赖

```bash
cd /opt/gw2-backend
sudo python3.13 -m venv venv
sudo ./venv/bin/pip install --upgrade pip setuptools wheel
sudo ./venv/bin/pip install -r requirements.txt
sudo chown -R gw2:gw2 venv
```

**核心依赖要求（Python >= 3.12，推荐 3.13）**：
- `fastapi>=0.115.0`
- `uvicorn[standard]>=0.34.0`
- `sqlalchemy>=2.0.0`
- `pymysql>=1.1.0`
- `pyjwt>=2.10.0`
- `passlib[bcrypt]>=1.7.4`
- `openai>=1.60.0`

### 3.7 配置 Systemd 服务

```bash
sudo cp scripts/deploy/gw2-backend.service /etc/systemd/system/gw2-backend.service

# 编辑配置（必须修改密码和密钥！）
sudo nano /etc/systemd/system/gw2-backend.service

# 修改后重载
sudo systemctl daemon-reload
sudo systemctl enable gw2-backend
sudo systemctl start gw2-backend
```

### 3.8 安装 Nginx（可选）

```bash
sudo apt install -y nginx
sudo cp scripts/deploy/nginx-gw2.conf /etc/nginx/sites-available/gw2-backend

# 编辑域名（如有需要）
sudo nano /etc/nginx/sites-available/gw2-backend

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/gw2-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 四、生产环境配置检查清单

### 4.1 配置文件说明

实际配置已集中到 `app/core/config.py`（558 行），`app/config/` 下各文件均为向后兼容入口。

### 4.2 Systemd 环境变量清单（30+ 变量，6 大类）

```bash
sudo nano /etc/systemd/system/gw2-backend.service
```

**1) 应用基础配置**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` | `GW2 WvW日志系统` | 应用名称 |
| `APP_VERSION` | `1.0.0` | 应用版本 |
| `DEBUG` | `False` | 调试模式（生产必须 `False`） |
| `API_PREFIX` | `/api/v1` | API 路由前缀 |
| `SECRET_KEY` | `CHANGE_ME...` | ✅ **必须修改** — JWT/Session 签名密钥 |
| `BACKEND_CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | 允许的跨域来源 |

**2) 日志配置**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FILE` | `/opt/gw2-backend/logs/app.log` | 日志文件路径 |

**3) 文件上传配置**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `UPLOAD_DIR` | `/opt/gw2-backend/uploads` | 上传目录 |
| `MAX_UPLOAD_SIZE` | `104857600` | 最大上传大小（100MB） |

**4) 存储管理配置**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `FILE_RETENTION_DAYS` | `30` | 文件保留天数 |
| `MAX_STORAGE_SIZE` | `10737418240` | 最大存储容量（10GB） |
| `STORAGE_WARNING_THRESHOLD` | `80.0` | 存储警告阈值（%） |
| `AUTO_CLEANUP_ENABLED` | `True` | 自动清理 |
| `AUTO_CLEANUP_INTERVAL` | `24` | 清理间隔（小时） |
| `KEEP_RAW_FILE_AFTER_PARSE` | `True` | 解析后保留原文件 |
| `FILE_COMPRESSION_ENABLED` | `False` | 文件压缩 |

**5) 数据库配置（支持 SQLite / MySQL / PostgreSQL）**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_TYPE` | `mysql` | 数据库类型：`sqlite` / `mysql` / `postgresql` |
| `SQLITE_DB_PATH` | `/opt/gw2-backend/database/app.db` | SQLite 文件路径 |
| `MYSQL_HOST` | `127.0.0.1` | MySQL 主机 |
| `MYSQL_PORT` | `3306` | MySQL 端口 |
| `MYSQL_USER` | `gw2` | MySQL 用户 |
| `MYSQL_PASSWORD` | `CHANGE_ME...` | ✅ **必须修改** |
| `MYSQL_DATABASE` | `gw2_log_system` | MySQL 数据库名 |
| `MYSQL_CHARSET` | `utf8mb4` | 字符集 |
| `MYSQL_POOL_SIZE` | `10` | 连接池大小 |
| `MYSQL_MAX_OVERFLOW` | `20` | 连接池溢出上限 |
| `MYSQL_LOCK_WAIT_TIMEOUT` | `30` | 锁等待超时（秒） |
| `POSTGRESQL_HOST` | `127.0.0.1` | PostgreSQL 主机（注释状态） |
| `POSTGRESQL_PORT` | `5432` | PostgreSQL 端口 |
| `POSTGRESQL_USER` | `postgres` | PostgreSQL 用户 |
| `POSTGRESQL_PASSWORD` | `CHANGE_ME...` | PostgreSQL 密码 |
| `POSTGRESQL_DATABASE` | `gw2_log_system` | PostgreSQL 数据库名 |
| `POSTGRESQL_POOL_SIZE` | `10` | 连接池大小 |
| `POSTGRESQL_MAX_OVERFLOW` | `20` | 连接池溢出上限 |
| `POOL_PRE_PING` | `True` | 连接池 pre_ping 检测 |
| `POOL_RECYCLE` | `300` | 连接回收时间（秒） |
| `CONNECT_TIMEOUT` | `10` | 连接超时（秒） |
| `AUTO_CREATE_TABLES` | `True` | 启动时自动创建缺失表 |
| `AUTO_MIGRATE` | `False` | 自动迁移（生产建议关闭） |

**6) AI 配置（可选）**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AI_ENABLED` | `False` | AI 功能开关 |
| `AI_MODEL_PROVIDER` | `deepseek` | 模型提供商：`deepseek` / `openai` / `qwen` |
| `DEEPSEEK_API_KEY` | — | DeepSeek API 密钥 |
| `OPENAI_API_KEY` | — | OpenAI API 密钥 |
| `QWEN_API_KEY` | — | 通义千问 API 密钥 |

**7) 管理员配置**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ADMIN_INITIAL_PASSWORD` | 被注释 | ⚠️ 建议设置 — 预置 `admin` 用户初始密码；留空则首次启动自动生成随机密码并输出到日志 |

修改后重载：
```bash
sudo systemctl daemon-reload
sudo systemctl restart gw2-backend
```

### 4.3 Nginx 配置细节

`scripts/deploy/nginx-gw2.conf` 内容：
- 监听 `80` 端口，`server_name _`
- `client_max_body_size 100M`（与 `MAX_UPLOAD_SIZE` 匹配）
- 代理路径：
  - `/api/` → `http://127.0.0.1:8000/api/`
  - `/docs` → Swagger UI
  - `/openapi.json` → OpenAPI 规范
  - `/health` → 健康检查
- 包含 WebSocket 支持头（`Upgrade`、`Connection`）
- 超时设置：`proxy_connect_timeout 60s`、`proxy_send_timeout 60s`、`proxy_read_timeout 60s`
- 附带 Let's Encrypt 配置注释 + 手动 HTTPS server 块注释

### 4.4 防火墙

脚本自动配置：
```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable
```

### 4.5 HTTPS (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx

# 申请证书（替换为你的域名）
sudo certbot --nginx -d yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run
```

---

## 五、日常运维命令

### 5.1 服务管理

```bash
# 查看状态
sudo systemctl status gw2-backend

# 启动 / 停止 / 重启
sudo systemctl start gw2-backend
sudo systemctl stop gw2-backend
sudo systemctl restart gw2-backend

# 查看实时日志
sudo journalctl -u gw2-backend -f

# 查看应用日志
tail -f /opt/gw2-backend/logs/app.log
```

### 5.2 数据库备份

```bash
# MySQL 备份
sudo mysqldump -u gw2 -p gw2_log_system > /backup/gw2_$(date +%Y%m%d).sql

# 自动备份脚本 (加入 crontab)
echo "0 3 * * * root mysqldump -u gw2 -p'密码' gw2_log_system > /backup/gw2_\$(date +\%Y\%m\%d).sql" | sudo tee /etc/cron.d/gw2-backup
```

### 5.3 更新代码

```bash
cd /opt/gw2-backend
sudo systemctl stop gw2-backend

# 上传新代码
sudo rsync -av --exclude='.git' --exclude='venv' --exclude='__pycache__' \
    /root/gw2-backend-new/ /opt/gw2-backend/

# 如果有新的依赖
sudo ./venv/bin/pip install -r requirements.txt

sudo systemctl start gw2-backend
```

---

## 六、故障排查

### 6.1 服务无法启动

```bash
# 查看详细错误
sudo journalctl -u gw2-backend -n 100 --no-pager

# 检查配置是否有效
sudo /opt/gw2-backend/venv/bin/python -c "from app.core.config import get_settings; s=get_settings(); print(s.validate_config())"

# 检查端口是否被占用
sudo ss -tlnp | grep 8000
```

### 6.2 数据库连接失败

```bash
# 测试 MySQL 连接
mysql -u gw2 -p -h 127.0.0.1 -e "SELECT 1"

# 检查数据库是否存在
mysql -u root -p -e "SHOW DATABASES LIKE 'gw2_log_system'"
```

### 6.3 权限问题

```bash
# 修复项目权限
sudo chown -R gw2:gw2 /opt/gw2-backend
sudo chmod 750 /opt/gw2-backend/logs
sudo chmod 755 /opt/gw2-backend/uploads
sudo chmod 755 /opt/gw2-backend/database
```

---

## 七、文件结构

部署完成后服务器的文件结构：

```
/opt/gw2-backend/
├── main.py              # FastAPI 入口
├── requirements.txt     # Python 依赖
├── venv/                # Python 虚拟环境
├── logs/                # 应用日志
│   └── app.log
├── uploads/             # 上传的日志文件
├── database/            # SQLite 数据库文件 (如果用 sqlite)
├── app/                 # 应用代码
│   └── core/
│       └── config.py    # 统一配置（558 行）
├── scripts/
│   └── deploy/          # 部署脚本
│       ├── install.sh
│       ├── gw2-backend.service
│       └── nginx-gw2.conf
└── docs/                # 文档

/etc/systemd/system/gw2-backend.service   # Systemd 服务
/etc/nginx/sites-available/gw2-backend    # Nginx 配置 (如果安装)
/etc/logrotate.d/gw2-backend              # 日志轮转配置（保留 30 天，含 postrotate reload）
```

---

## 八、安全建议

1. **修改默认密码**: 立即修改 `SECRET_KEY` 和 `MYSQL_PASSWORD`
2. **禁用 root 登录**: 编辑 `/etc/ssh/sshd_config`，设置 `PermitRootLogin no`
3. **修改 SSH 端口**: 将默认 22 改为高位端口
4. **启用自动更新**: `sudo apt install unattended-upgrades`
5. **配置 Fail2ban**: 防止暴力破解 `sudo apt install fail2ban`
6. **定期备份**: 数据库 + 上传文件

---

*部署文档版本: v2.0 | 更新日期: 2026-05-05 | 适用项目版本: >= 1.0.0*
