# GW2 WvW 日志系统 - 部署操作指南

## 方案概述

本方案针对**服务器内存不足（2GB）导致前端构建频繁失败**的问题，采用**"本地构建 + 远程上传"**的部署模式：

- **本地**：完成前端构建（`npm run build`），打包前后端代码
- **服务器**：仅运行 Python 后端，通过 rsync 接收已构建的前端产物
- **结果**：服务器无需安装 Node.js，无需编译前端，节省约 500MB+ 内存

---

## 目录结构

```
scripts/deploy/
├── deploy.sh              # ⭐ 本地一键部署脚本（开发机运行）
├── server-setup.sh        # 服务器首次环境准备（服务器运行）
├── nginx-production.conf  # 生产环境 Nginx 配置模板
├── install.sh             # 服务器端全量安装脚本（备用）
└── install-lightweight.sh # 服务器端轻量安装脚本（备用）
```

---

## 首次部署流程（服务器环境准备）

### 1. 服务器要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核 |
| 内存 | 1 GB | 2 GB |
| 磁盘 | 10 GB | 20 GB |
| 系统 | Debian 12 / Ubuntu 22.04+ | Debian 12 |
| Python | 3.11+ | 3.12 |
| 网络 | 公网 IP + 开放 80/443 端口 | 域名 + HTTPS |

### 2. 在服务器上执行环境准备

```bash
# 登录服务器
ssh root@你的服务器IP

# 将 server-setup.sh 上传到服务器并执行
chmod +x server-setup.sh
sudo ./server-setup.sh
```

`server-setup.sh` 会自动完成：
- 安装 Python、Nginx、防火墙等基础依赖
- 创建 `gw2` 用户和 `/opt/gw2-backend/` 目录结构
- 创建 Python 虚拟环境
- 配置 Systemd 服务
- 配置 Nginx（HTTP 模式）
- 配置防火墙（UFW）

### 3. 配置 SSH 免密登录（本地开发机）

```bash
# 生成密钥（如未生成过）
ssh-keygen -t ed25519 -C "deploy-key"

# 复制公钥到服务器
ssh-copy-id root@你的服务器IP

# 测试免密登录
ssh root@你的服务器IP "echo OK"
```

---

## 日常部署流程（本地一键部署）

### 单条命令完成部署

```bash
# 方式一：修改脚本内配置后执行
cd backend/scripts/deploy
vim deploy.sh          # 修改 SERVER_HOST 为你的服务器IP
./deploy.sh

# 方式二：通过环境变量临时指定（推荐）
cd backend/scripts/deploy
DEPLOY_HOST=1.2.3.4 ./deploy.sh

# 方式三：完整参数
DEPLOY_HOST=1.2.3.4 DEPLOY_USER=root DEPLOY_DIR=/opt/gw2-backend ./deploy.sh
```

### deploy.sh 部署流程

```
Step 1: 本地环境检查       → 检查 Node.js、npm、rsync、SSH 连接
Step 2: 本地构建前端       → npm install + npm run build（本地完成，服务器不消耗内存）
Step 3: 备份服务器版本     → 打包当前版本到 releases/，保留最近 5 个版本
Step 4: 增量上传代码       → rsync 仅传输变更文件
       - 前端 dist/ → /opt/gw2-backend/frontend/dist/
       - 后端源码  → /opt/gw2-backend/
Step 5: 远程更新服务       → 安装依赖、数据库迁移、重启 systemd 服务
Step 6: 健康检查           → 自动访问 /health，最多重试 10 次
```

### 部署失败回滚

```bash
# 回滚到上一版本
./deploy.sh --rollback

# 脚本会列出可用的备份版本，选择后自动：
# 1. 停止服务
# 2. 备份当前失败版本
# 3. 解压历史版本
# 4. 重启服务
```

---

## 服务器目录结构

```
/opt/gw2-backend/
├── app/                  # 后端 Python 源码（由 deploy.sh 上传）
├── main.py              # FastAPI 入口
├── requirements.txt     # Python 依赖
├── venv/                # Python 虚拟环境（server-setup.sh 创建）
├── frontend/
│   └── dist/            # 前端构建产物（由 deploy.sh 上传）
├── uploads/             # 用户上传文件（持久化，不随版本变动）
├── database/
│   └── app.db           # SQLite 数据库（持久化，不随版本变动）
├── logs/
│   └── app.log          # 应用日志（持久化，不随版本变动）
├── releases/            # 版本备份（deploy.sh 自动管理）
│   ├── release_20260514_120000.tar.gz
│   ├── release_20260514_110000.tar.gz
│   └── ...
└── .deploy_history      # 部署历史记录
```

**持久化目录**（`uploads/`、`database/`、`logs/`）在备份和回滚时会被排除，确保数据安全。

---

## 域名与 HTTPS 配置

### 1. 修改 Nginx 配置

```bash
# 编辑服务器上的 Nginx 配置
sudo nano /etc/nginx/sites-available/gw2-backend

# 修改 server_name 为你的域名
server_name gw2-log-analyzer.top www.gw2-log-analyzer.top;

# 重载 Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 2. 申请 Let's Encrypt 证书（免费 HTTPS）

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 申请证书（自动修改 Nginx 配置）
sudo certbot --nginx -d gw2-log-analyzer.top -d www.gw2-log-analyzer.top

# 测试自动续期
sudo certbot renew --dry-run
```

### 3. 手动配置 HTTPS（自签名证书）

```bash
# 创建证书目录
mkdir -p /opt/gw2-backend/ssl/live/gw2-log-analyzer.top

# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/gw2-backend/ssl/live/gw2-log-analyzer.top/privkey.pem \
  -out /opt/gw2-backend/ssl/live/gw2-log-analyzer.top/fullchain.pem \
  -subj "/CN=gw2-log-analyzer.top"

# 参考 scripts/deploy/nginx-production.conf 中的 HTTPS 配置块，
# 取消注释并应用到 Nginx
```

---

## 安全相关配置

### 防火墙规则（已由 server-setup.sh 自动配置）

```bash
# 查看当前规则
sudo ufw status verbose

# 默认规则
sudo ufw default deny incoming   # 默认拒绝所有入站
sudo ufw default allow outgoing  # 默认允许所有出站
sudo ufw allow ssh               # 允许 SSH (22)
sudo ufw allow http              # 允许 HTTP (80)
sudo ufw allow https             # 允许 HTTPS (443)
```

### 建议加固项

| 加固项 | 命令 |
|--------|------|
| 修改 SSH 端口 | `sudo nano /etc/ssh/sshd_config` → `Port 2222` |
| 禁用 root 密码登录 | `PermitRootLogin prohibit-password` |
| 仅允许密钥登录 | `PasswordAuthentication no` |
| 修改 SECRET_KEY | `sudo nano /etc/systemd/system/gw2-backend.service` |
| 修改管理员初始密码 | 同上，修改 `ADMIN_INITIAL_PASSWORD` |

修改后重载：
```bash
sudo systemctl daemon-reload
sudo systemctl restart gw2-backend
sudo systemctl restart sshd
```

---

## 常用运维命令

```bash
# 查看服务状态
sudo systemctl status gw2-backend

# 查看实时日志
sudo journalctl -u gw2-backend -f

# 重启后端
sudo systemctl restart gw2-backend

# 重启 Nginx
sudo systemctl reload nginx

# 查看部署历史（服务器上）
cat /opt/gw2-backend/.deploy_history

# 手动备份当前版本（服务器上）
cd /opt/gw2-backend
tar czf releases/manual_$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude='uploads' --exclude='database' --exclude='logs' --exclude='releases' .
```

---

## 故障排查

### Q: 部署时 SSH 连接失败？
```bash
# 检查 SSH 免密是否配置成功
ssh -o BatchMode=yes root@服务器IP "echo OK"

# 如失败，重新配置
ssh-copy-id root@服务器IP
```

### Q: 前端页面空白或 404？
```bash
# 检查前端产物是否上传成功
ls -la /opt/gw2-backend/frontend/dist/

# 检查 Nginx root 路径
sudo nginx -t
```

### Q: 后端服务启动失败？
```bash
# 查看详细错误
sudo journalctl -u gw2-backend -n 50

# 常见原因：
# 1. 依赖未安装 → 重新执行 deploy.sh
# 2. 端口被占用 → ss -tlnp | grep 8000
# 3. 权限不足 → chown -R gw2:gw2 /opt/gw2-backend
```

### Q: 如何完全重置服务器环境？
```bash
# 停止服务
sudo systemctl stop gw2-backend
sudo systemctl stop nginx

# 删除部署目录（注意：uploads/database/logs 会被删除！如需保留请先备份）
sudo rm -rf /opt/gw2-backend

# 重新运行 server-setup.sh
sudo ./server-setup.sh
```
