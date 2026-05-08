#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - 轻量级一键部署脚本（2G2核 服务器优化版）
# ============================================================================
# 用法:
#   1. 将项目代码上传到服务器 (如 /root/gw2-wvw-log-analyzer)
#   2. cd /root/gw2-wvw-log-analyzer
#   3. chmod +x backend/scripts/deploy/install-lightweight.sh
#   4. sudo ./backend/scripts/deploy/install-lightweight.sh
#
# 前置要求:
#   - Debian 12 / Ubuntu 22.04+ 干净系统
#   - root 权限
#   - 至少 2GB 内存
#   - 至少 5GB 磁盘空间
# ============================================================================

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# 配置变量
PROJECT_NAME="gw2-backend"
PROJECT_DIR="/opt/${PROJECT_NAME}"
PROJECT_USER="gw2"
PROJECT_GROUP="gw2"
VENV_DIR="${PROJECT_DIR}/venv"
LOG_DIR="${PROJECT_DIR}/logs"
UPLOAD_DIR="${PROJECT_DIR}/uploads"
DB_DIR="${PROJECT_DIR}/database"

# 检查 root 权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "请使用 root 权限运行此脚本: sudo $0"
        exit 1
    fi
}

# 检查操作系统
check_os() {
    if [[ -f /etc/debian_version ]]; then
        OS="debian"
        OS_VERSION=$(cat /etc/debian_version | head -1)
        info "检测到系统: Debian ${OS_VERSION}"
    elif [[ -f /etc/lsb-release ]]; then
        OS="ubuntu"
        . /etc/lsb-release
        info "检测到系统: Ubuntu ${DISTRIB_RELEASE}"
    else
        error "此脚本仅支持 Debian 12 或 Ubuntu 22.04+"
        exit 1
    fi
}

# 查找可用的 Python 版本（>=3.11）
find_python() {
    for py in python3.13 python3.12 python3.11 python3; do
        if command -v "$py" &> /dev/null; then
            PY_VERSION=$($py --version 2>&1 | awk '{print $2}')
            PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
            PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
            if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 11 ]]; then
                PYTHON_CMD="$py"
                info "找到可用 Python: $py (版本 $PY_VERSION)"
                return 0
            fi
        fi
    done
    return 1
}

# 安装 Python（如果系统没有 >=3.11 的）
install_python() {
    if find_python; then
        return 0
    fi

    info "正在安装 Python 3.11..."
    apt-get update
    apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

    if find_python; then
        success "Python 安装完成"
    else
        error "无法找到或安装 Python 3.11+，请手动安装"
        exit 1
    fi
}

# 安装系统依赖
install_system_deps() {
    info "正在更新系统并安装依赖..."
    apt-get update

    # 安装基础工具
    apt-get install -y \
        curl \
        wget \
        git \
        rsync \
        build-essential \
        libffi-dev \
        libssl-dev \
        pkg-config \
        nginx

    success "系统依赖安装完成"
}

# 安装 Node.js（用于前端构建）
install_nodejs() {
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        NODE_VERSION=$(node --version 2>/dev/null || echo "unknown")
        info "Node.js 已存在: ${NODE_VERSION}"
        return 0
    fi

    info "正在安装 Node.js..."
    # 使用 NodeSource 官方源安装 Node 20 LTS
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs

    success "Node.js 安装完成: $(node --version)"
}

# 创建项目用户和目录
setup_project() {
    info "正在创建项目用户和目录..."

    # 创建用户
    if ! id -u "$PROJECT_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$PROJECT_DIR" -m "$PROJECT_USER"
    fi

    # 创建目录
    mkdir -p "$PROJECT_DIR" "$LOG_DIR" "$UPLOAD_DIR" "$DB_DIR"

    # 设置权限
    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$PROJECT_DIR"
    chmod 755 "$PROJECT_DIR"
    chmod 750 "$LOG_DIR"
    chmod 755 "$UPLOAD_DIR"
    chmod 755 "$DB_DIR"

    success "项目用户和目录创建完成"
}

# 部署后端代码
deploy_backend() {
    info "正在部署后端代码..."

    SOURCE_DIR="$(pwd)/backend"
    if [[ ! -d "$SOURCE_DIR" ]]; then
        error "后端源码目录不存在: ${SOURCE_DIR}"
        error "请确保在项目根目录运行此脚本"
        exit 1
    fi

    # 复制后端代码
    rsync -av --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
        "${SOURCE_DIR}/" "${PROJECT_DIR}/"

    # 复制前端源码（用于构建）
    FRONTEND_SOURCE="$(pwd)/frontend"
    if [[ -d "$FRONTEND_SOURCE" ]]; then
        mkdir -p "${PROJECT_DIR}/frontend"
        rsync -av --exclude='node_modules' --exclude='.git' --exclude='dist' \
            "${FRONTEND_SOURCE}/" "${PROJECT_DIR}/frontend/"
    fi

    # 复制 GW2.txt 数据文件（如果存在）
    if [[ -f "$(pwd)/backend/tests/GW2.txt" ]]; then
        mkdir -p "${PROJECT_DIR}/tests"
        cp "$(pwd)/backend/tests/GW2.txt" "${PROJECT_DIR}/tests/"
    fi

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$PROJECT_DIR"

    success "项目代码部署完成"
}

# 创建虚拟环境并安装依赖
setup_venv() {
    info "正在创建虚拟环境并安装依赖..."

    cd "$PROJECT_DIR"

    # 创建虚拟环境
    $PYTHON_CMD -m venv "$VENV_DIR"

    # 升级 pip
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel

    # 安装依赖
    "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$VENV_DIR"

    success "虚拟环境和依赖安装完成"
}

# 构建前端
build_frontend() {
    info "正在构建前端..."

    FRONTEND_DIR="${PROJECT_DIR}/frontend"
    if [[ ! -f "${FRONTEND_DIR}/package.json" ]]; then
        warn "前端源码不存在，跳过构建"
        return 0
    fi

    cd "$FRONTEND_DIR"

    # 安装依赖并构建
    npm install
    npm run build

    # 确保构建产物存在
    if [[ ! -d "${FRONTEND_DIR}/dist" ]]; then
        error "前端构建失败，dist 目录不存在"
        exit 1
    fi

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$FRONTEND_DIR"

    success "前端构建完成"
}

# 配置 Systemd 服务
setup_systemd() {
    info "正在配置 Systemd 服务..."

    local service_file="/etc/systemd/system/${PROJECT_NAME}.service"
    cp "$PROJECT_DIR/scripts/deploy/gw2-backend-lightweight.service" "$service_file"

    # 生成随机 SECRET_KEY
    local secret_key
    secret_key=$(openssl rand -base64 32)
    sed -i "s|CHANGE_ME_TO_A_RANDOM_STRING_AT_LEAST_32_CHARS_LONG|${secret_key}|g" "$service_file"

    systemctl daemon-reload
    systemctl enable "$PROJECT_NAME"

    success "Systemd 服务配置完成"
}

# 配置 Nginx
setup_nginx() {
    info "正在配置 Nginx..."

    # 复制配置
    cp "$PROJECT_DIR/scripts/deploy/nginx-gw2-lightweight.conf" \
        /etc/nginx/sites-available/gw2-backend

    # 启用站点
    rm -f /etc/nginx/sites-enabled/default
    ln -sf /etc/nginx/sites-available/gw2-backend \
        /etc/nginx/sites-enabled/gw2-backend

    # 创建日志目录
    mkdir -p /var/log/nginx

    # 测试配置
    nginx -t

    systemctl restart nginx
    systemctl enable nginx

    success "Nginx 配置完成"
}

# 配置日志轮转
setup_logrotate() {
    info "正在配置日志轮转..."

    cat > /etc/logrotate.d/gw2-backend << 'EOF'
/opt/gw2-backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 gw2 gw2
    sharedscripts
    postrotate
        systemctl reload gw2-backend > /dev/null 2>&1 || true
    endscript
}
EOF

    success "日志轮转配置完成"
}

# 配置防火墙
setup_firewall() {
    info "正在配置防火墙..."

    if command -v ufw &> /dev/null; then
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow http
        # 如果后续配置 HTTPS，取消注释下行
        # ufw allow https
        ufw --force enable
        success "UFW 防火墙配置完成"
    else
        warn "未检测到 UFW，跳过防火墙配置"
    fi
}

# 启动服务
start_service() {
    info "正在启动服务..."

    systemctl start "$PROJECT_NAME"

    sleep 3

    if systemctl is-active --quiet "$PROJECT_NAME"; then
        success "服务启动成功!"
    else
        error "服务启动失败，查看日志: journalctl -u ${PROJECT_NAME} -n 50"
        exit 1
    fi
}

# 打印部署摘要
print_summary() {
    local ip
    ip=$(hostname -I | awk '{print $1}')

    echo ""
    echo "========================================"
    echo "  轻量级部署完成!"
    echo "========================================"
    echo ""
    echo "  项目目录: ${PROJECT_DIR}"
    echo "  服务名称: ${PROJECT_NAME}"
    echo "  运行用户: ${PROJECT_USER}"
    echo "  虚拟环境: ${VENV_DIR}"
    echo "  数据库: SQLite (${DB_DIR}/app.db)"
    echo ""
    echo "  服务状态:"
    echo "    systemctl status ${PROJECT_NAME}"
    echo ""
    echo "  查看日志:"
    echo "    journalctl -u ${PROJECT_NAME} -f"
    echo "    tail -f ${LOG_DIR}/app.log"
    echo ""
    echo "  访问地址:"
    echo "    http://${ip}/          (前端页面)"
    echo "    http://${ip}/api/v1/   (API)"
    echo "    http://${ip}/docs      (Swagger UI)"
    echo ""
    echo "  健康检查:"
    echo "    curl http://127.0.0.1:8000/health"
    echo ""
    echo "  常用命令:"
    echo "    sudo systemctl start|stop|restart|status ${PROJECT_NAME}"
    echo "    sudo systemctl reload ${PROJECT_NAME}"
    echo ""
    echo "  安全提醒:"
    echo "    1. 请修改 /etc/systemd/system/${PROJECT_NAME}.service 中的 SECRET_KEY"
    echo "    2. 建议配置 HTTPS (Let's Encrypt 或自签名证书)"
    echo "    3. 建议修改 SSH 端口并禁用 root 登录"
    echo ""
    echo "========================================"
}

# 主流程
main() {
    check_root
    check_os

    info "开始轻量级部署（2G2核 优化版）..."
    echo ""

    install_python
    install_system_deps
    install_nodejs
    setup_project
    deploy_backend
    setup_venv
    build_frontend
    setup_systemd
    setup_nginx
    setup_logrotate
    setup_firewall
    start_service

    print_summary
}

main "$@"
