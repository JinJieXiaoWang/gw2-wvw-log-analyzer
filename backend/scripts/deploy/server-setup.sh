#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - 服务器首次环境准备脚本
# ============================================================================
# 运行位置：目标服务器（root 权限）
# 功能：安装基础环境、创建用户目录、配置防火墙，为后续 deploy.sh 做准备
# 注意：此脚本只需执行一次，后续更新使用 deploy.sh（本地运行）
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }
step()    { echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${CYAN}▶ $*${NC}"; }

# ============================================================================
# 配置
# ============================================================================
PROJECT_NAME="gw2-backend"
PROJECT_DIR="/opt/${PROJECT_NAME}"
PROJECT_USER="gw2"
PROJECT_GROUP="gw2"
VENV_DIR="${PROJECT_DIR}/venv"

# ============================================================================
# 1. 基础检查
# ============================================================================
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "请使用 root 权限运行: sudo $0"
        exit 1
    fi
}

check_os() {
    if [[ -f /etc/debian_version ]]; then
        info "  系统: Debian $(cat /etc/debian_version | head -1)"
    elif [[ -f /etc/lsb-release ]]; then
        . /etc/lsb-release
        info "  系统: Ubuntu ${DISTRIB_RELEASE}"
    else
        error "此脚本仅支持 Debian/Ubuntu"
        exit 1
    fi
}

# ============================================================================
# 2. 安装基础依赖（服务器上不需要 Node.js！）
# ============================================================================
install_deps() {
    info "  更新软件源..."
    apt-get update

    info "  安装基础工具..."
    apt-get install -y \
        python3 \
        python3-venv \
        python3-pip \
        python3-dev \
        nginx \
        git \
        rsync \
        curl \
        wget \
        build-essential \
        libffi-dev \
        libssl-dev \
        pkg-config \
        ufw \
        logrotate

    success "  基础依赖安装完成"
}

# ============================================================================
# 3. 创建项目用户和目录结构
# ============================================================================
setup_directories() {
    info "  创建项目用户..."
    if ! id -u "$PROJECT_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$PROJECT_DIR" -m "$PROJECT_USER"
    fi

    info "  创建目录结构..."
    mkdir -p \
        "$PROJECT_DIR" \
        "$PROJECT_DIR/uploads" \
        "$PROJECT_DIR/database" \
        "$PROJECT_DIR/logs" \
        "$PROJECT_DIR/releases" \
        "$PROJECT_DIR/frontend/dist"

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$PROJECT_DIR"
    chmod 755 "$PROJECT_DIR"
    chmod 750 "$PROJECT_DIR/logs"
    chmod 755 "$PROJECT_DIR/uploads"
    chmod 755 "$PROJECT_DIR/database"

    success "  目录结构创建完成"
    info "  ${PROJECT_DIR}/"
    info "    ├── uploads/      (上传文件存储)"
    info "    ├── database/     (SQLite 数据库)"
    info "    ├── logs/         (应用日志)"
    info "    ├── releases/     (版本备份)"
    info "    ├── frontend/dist/(前端构建产物)"
    info "    └── venv/         (Python 虚拟环境)"
}

# ============================================================================
# 4. 创建虚拟环境
# ============================================================================
setup_venv() {
    if [ -d "$VENV_DIR" ]; then
        warn "  虚拟环境已存在，跳过"
        return 0
    fi

    info "  创建 Python 虚拟环境..."
    python3 -m venv "$VENV_DIR"
    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$VENV_DIR"
    success "  虚拟环境创建完成: ${VENV_DIR}"
}

# ============================================================================
# 5. 配置 Systemd 服务
# ============================================================================
setup_systemd() {
    local service_file="/etc/systemd/system/${PROJECT_NAME}.service"

    if [ -f "$service_file" ]; then
        warn "  Systemd 服务已存在，跳过"
        return 0
    fi

    info "  创建 Systemd 服务..."

    cat > "$service_file" << EOF
[Unit]
Description=GW2 WvW 日志系统后端 API
After=network.target

[Service]
Type=simple
User=${PROJECT_USER}
Group=${PROJECT_GROUP}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=${PROJECT_DIR}"
Environment="APP_NAME=GW2 WvW日志系统"
Environment="APP_VERSION=1.0.0"
Environment="DEBUG=False"
Environment="API_PREFIX=/api/v1"
Environment="SECRET_KEY=CHANGE_ME_TO_A_RANDOM_STRING_AT_LEAST_32_CHARS_LONG"
Environment="LOG_LEVEL=INFO"
Environment="LOG_FILE=${PROJECT_DIR}/logs/app.log"
Environment="UPLOAD_DIR=${PROJECT_DIR}/uploads"
Environment="MAX_UPLOAD_SIZE=104857600"
Environment="ADMIN_INITIAL_PASSWORD=admin123"
Environment="ADMIN_PASSWORD_SYNC=true"
Environment="DB_TYPE=sqlite"
Environment="SQLITE_DB_PATH=${PROJECT_DIR}/database/app.db"
Environment="AUTO_CREATE_TABLES=True"
ExecStart=${VENV_DIR}/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
ExecReload=/bin/kill -s HUP \$MAINPID
ExecStop=/bin/kill -s TERM \$MAINPID
Restart=on-failure
RestartSec=5
LimitNOFILE=65535
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$PROJECT_NAME"

    success "  Systemd 服务配置完成"
    warn "  安全提醒：请务必修改 ${service_file} 中的 SECRET_KEY"
}

# ============================================================================
# 6. 配置 Nginx（HTTP 模式，HTTPS 需手动配置证书）
# ============================================================================
setup_nginx() {
    local nginx_conf="/etc/nginx/sites-available/${PROJECT_NAME}"

    if [ -f "$nginx_conf" ]; then
        warn "  Nginx 配置已存在，跳过"
        return 0
    fi

    info "  配置 Nginx..."

    cat > "$nginx_conf" << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name _;

    access_log /var/log/nginx/gw2-access.log;
    error_log /var/log/nginx/gw2-error.log warn;

    client_max_body_size 100M;
    client_body_buffer_size 16k;
    client_body_timeout 300s;

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_request_buffering off;
        proxy_buffering off;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 上传文件
    location /uploads/ {
        alias /opt/gw2-backend/uploads/;
        expires 7d;
        add_header Cache-Control "public, immutable";
        try_files $uri $uri/ =404;
    }

    # 前端 SPA
    location / {
        root /opt/gw2-backend/frontend/dist;
        index index.html;
        try_files $uri $uri/ @spa;
    }

    location @spa {
        rewrite ^ /index.html break;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|otf)$ {
        root /opt/gw2-backend/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
EOF

    rm -f /etc/nginx/sites-enabled/default
    ln -sf "$nginx_conf" /etc/nginx/sites-enabled/"$PROJECT_NAME"

    nginx -t
    systemctl restart nginx
    systemctl enable nginx

    success "  Nginx 配置完成"
}

# ============================================================================
# 7. 配置防火墙
# ============================================================================
setup_firewall() {
    info "  配置 UFW 防火墙..."

    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw --force enable

    success "  防火墙配置完成"
    info "  当前规则:"
    ufw status verbose | sed 's/^/    /'
}

# ============================================================================
# 8. 配置日志轮转
# ============================================================================
setup_logrotate() {
    local lr_file="/etc/logrotate.d/${PROJECT_NAME}"

    if [ -f "$lr_file" ]; then
        warn "  日志轮转已配置，跳过"
        return 0
    fi

    cat > "$lr_file" << EOF
${PROJECT_DIR}/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ${PROJECT_USER} ${PROJECT_GROUP}
    sharedscripts
    postrotate
        systemctl reload ${PROJECT_NAME} > /dev/null 2>&1 || true
    endscript
}
EOF

    success "  日志轮转配置完成"
}

# ============================================================================
# 9. SSH 配置提示（用于 deploy.sh 免密登录）
# ============================================================================
show_ssh_hint() {
    echo ""
    step "环境准备完成"
    success "服务器已就绪，可通过 deploy.sh 从本地一键部署"
    echo ""
    info "下一步：配置 SSH 免密登录（在本地开发机上执行）"
    echo ""
    echo "  1. 生成 SSH 密钥（如果还没有）"
    echo "     ssh-keygen -t rsa -b 4096 -C 'your-email@example.com'"
    echo ""
    echo "  2. 将公钥复制到服务器"
    echo "     ssh-copy-id root@你的服务器IP"
    echo ""
    echo "  3. 测试免密登录"
    echo "     ssh root@你的服务器IP 'echo OK'"
    echo ""
    info "之后即可在本地执行部署："
    echo "  DEPLOY_HOST=你的服务器IP ./scripts/deploy/deploy.sh"
    echo ""
    warn "安全提醒："
    warn "  1. 修改 /etc/systemd/system/gw2-backend.service 中的 SECRET_KEY"
    warn "  2. 建议配置 HTTPS（放置证书到 ${PROJECT_DIR}/ssl/）"
    warn "  3. 建议修改 SSH 默认端口并禁用 root 密码登录"
}

# ============================================================================
# 主流程
# ============================================================================
main() {
    step "GW2 WvW 日志系统 - 服务器环境准备"

    check_root
    check_os

    step "Step 1/6: 安装基础依赖"
    install_deps

    step "Step 2/6: 创建用户与目录"
    setup_directories

    step "Step 3/6: 创建 Python 虚拟环境"
    setup_venv

    step "Step 4/6: 配置 Systemd 服务"
    setup_systemd

    step "Step 5/6: 配置 Nginx"
    setup_nginx

    step "Step 6/6: 配置防火墙与日志"
    setup_firewall
    setup_logrotate

    show_ssh_hint
}

main "$@"
