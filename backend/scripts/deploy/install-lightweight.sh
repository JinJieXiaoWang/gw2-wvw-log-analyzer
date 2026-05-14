#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - 轻量级一键部署脚本（2G2核 服务器优化版）
# ============================================================================
# 用法:
#   sudo ./backend/scripts/deploy/install-lightweight.sh [选项]
#
# 选项:
#   --resume, -r    从上次失败的步骤继续部署
#   --force, -f     强制重新部署（清除状态记录，从头执行）
#   --status, -s    查看当前部署状态记录
#   --help, -h      显示帮助信息
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

# ============================================================================
# 部署状态管理
# ============================================================================
STATE_FILE="/root/.gw2_deploy_state"

init_state() {
    if [ "$FORCE_DEPLOY" = "true" ] || [ ! -f "$STATE_FILE" ]; then
        echo "# GW2 Backend Deploy State" > "$STATE_FILE"
        echo "START:$(date '+%Y-%m-%d %H:%M:%S')" >> "$STATE_FILE"
        echo "SCRIPT:install-lightweight.sh" >> "$STATE_FILE"
        echo "PROJECT_DIR:${PROJECT_DIR}" >> "$STATE_FILE"
        echo "---" >> "$STATE_FILE"
    fi
}

mark_done() {
    local step="$1"
    echo "DONE:$step:$(date '+%Y-%m-%d %H:%M:%S')" >> "$STATE_FILE"
}

mark_failed() {
    local step="$1"
    local msg="$2"
    echo "FAILED:$step:$(date '+%Y-%m-%d %H:%M:%S'):$msg" >> "$STATE_FILE"
}

mark_skipped() {
    local step="$1"
    echo "SKIPPED:$step:$(date '+%Y-%m-%d %H:%M:%S')" >> "$STATE_FILE"
}

is_step_done() {
    local step="$1"
    [ -f "$STATE_FILE" ] && grep -q "^DONE:$step:" "$STATE_FILE"
}

get_last_failed() {
    [ -f "$STATE_FILE" ] && grep "^FAILED:" "$STATE_FILE" | tail -1 | cut -d: -f2 || true
}

get_done_count() {
    [ -f "$STATE_FILE" ] && grep -c "^DONE:" "$STATE_FILE" || echo 0
}

clear_state() {
    rm -f "$STATE_FILE"
}

show_deploy_status() {
    if [ ! -f "$STATE_FILE" ]; then
        info "无部署状态记录"
        return
    fi

    echo ""
    echo "========================================"
    echo "  部署状态记录"
    echo "========================================"
    cat "$STATE_FILE"
    echo "========================================"

    local failed
    failed=$(get_last_failed)
    if [ -n "$failed" ]; then
        warn "最后失败步骤: $failed"
        info "使用 --resume 从该步骤继续，或使用 --force 重新部署"
    else
        local done_count
        done_count=$(get_done_count)
        info "已完成步骤数: $done_count"
    fi
}

# 步骤执行包装器：支持跳过已完成的步骤、记录状态、捕获错误
run_step() {
    local step="$1"
    local desc="$2"
    shift 2

    echo ""
    info "【步骤】$desc"

    # 恢复模式：若步骤已完成则跳过
    if [ "$RESUME_MODE" = "true" ] && is_step_done "$step"; then
        success "  该步骤已执行完成，跳过"
        mark_skipped "$step"
        return 0
    fi

    # 执行步骤并捕获退出码
    local exit_code=0
    "$@" || exit_code=$?

    if [ $exit_code -eq 0 ]; then
        mark_done "$step"
        success "  $desc 完成"
        return 0
    else
        mark_failed "$step" "退出码 $exit_code"
        error "  $desc 失败（退出码: $exit_code）"
        error "  部署中断。修复问题后，使用以下命令继续:"
        error "    sudo $0 --resume"
        error "  或强制重新部署:"
        error "    sudo $0 --force"
        exit $exit_code
    fi
}

# ============================================================================
# 参数解析
# ============================================================================
RESUME_MODE=false
FORCE_DEPLOY=false
SHOW_STATUS=false

show_help() {
    cat << 'EOF'
GW2 WvW 日志系统 - 轻量级一键部署脚本（2G2核 优化版）

用法:
  sudo ./backend/scripts/deploy/install-lightweight.sh [选项]

选项:
  --resume, -r    从上次失败的步骤继续部署（智能跳过已完成的步骤）
  --force, -f     强制重新部署：清除状态记录并从头执行所有步骤
  --status, -s    查看当前部署状态记录
  --help, -h      显示此帮助信息

示例:
  # 首次部署（请在项目根目录执行）
  sudo ./backend/scripts/deploy/install-lightweight.sh

  # 查看当前部署状态
  sudo ./backend/scripts/deploy/install-lightweight.sh --status

  # 上次部署失败后继续
  sudo ./backend/scripts/deploy/install-lightweight.sh --resume

  # 强制从头重新部署（保留数据和上传文件）
  sudo ./backend/scripts/deploy/install-lightweight.sh --force
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --resume|-r)
            RESUME_MODE=true
            shift
            ;;
        --force|-f)
            FORCE_DEPLOY=true
            shift
            ;;
        --status|-s)
            SHOW_STATUS=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# ============================================================================
# 配置变量
# ============================================================================
PROJECT_NAME="gw2-backend"
PROJECT_DIR="/opt/${PROJECT_NAME}"
PROJECT_USER="gw2"
PROJECT_GROUP="gw2"
VENV_DIR="${PROJECT_DIR}/venv"
LOG_DIR="${PROJECT_DIR}/logs"
UPLOAD_DIR="${PROJECT_DIR}/uploads"
DB_DIR="${PROJECT_DIR}/database"

# ============================================================================
# 各部署步骤函数
# ============================================================================

# 检查 root 权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "  请使用 root 权限运行此脚本: sudo $0"
        return 1
    fi
}

# 检查操作系统
check_os() {
    if [[ -f /etc/debian_version ]]; then
        OS="debian"
        OS_VERSION=$(cat /etc/debian_version | head -1)
        info "  检测到系统: Debian ${OS_VERSION}"
    elif [[ -f /etc/lsb-release ]]; then
        OS="ubuntu"
        . /etc/lsb-release
        info "  检测到系统: Ubuntu ${DISTRIB_RELEASE}"
    else
        error "  此脚本仅支持 Debian 12 或 Ubuntu 22.04+"
        return 1
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
                info "  找到可用 Python: $py (版本 $PY_VERSION)"
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

    info "  正在安装 Python 3.11..."
    apt-get update
    apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

    if find_python; then
        success "  Python 安装完成"
    else
        error "  无法找到或安装 Python 3.11+，请手动安装"
        return 1
    fi
}

# 安装系统依赖
install_system_deps() {
    info "  正在更新系统并安装依赖..."
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

    success "  系统依赖安装完成"
}

# 安装 Node.js（用于前端构建）
install_nodejs() {
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        NODE_VERSION=$(node --version 2>/dev/null || echo "unknown")
        info "  Node.js 已存在: ${NODE_VERSION}"
        return 0
    fi

    info "  正在安装 Node.js..."
    # 使用 NodeSource 官方源安装 Node 20 LTS
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs

    success "  Node.js 安装完成: $(node --version)"
}

# 创建项目用户和目录
setup_project() {
    info "  正在创建项目用户和目录..."

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

    success "  项目用户和目录创建完成"
}

# 部署后端代码
deploy_backend() {
    info "  正在部署后端代码..."

    # 智能检测当前目录位置（支持在项目根目录或 backend 子目录运行）
    if [[ "$(basename "$(pwd)")" == "backend" ]]; then
        SOURCE_DIR="$(pwd)"
        FRONTEND_SOURCE="$(dirname "$(pwd)")/frontend"
    else
        SOURCE_DIR="$(pwd)/backend"
        FRONTEND_SOURCE="$(pwd)/frontend"
    fi

    if [[ ! -d "$SOURCE_DIR" ]]; then
        error "  后端源码目录不存在: ${SOURCE_DIR}"
        error "  请确保在项目根目录或 backend 目录运行此脚本"
        return 1
    fi

    # 复制后端代码
    rsync -av --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
        "${SOURCE_DIR}/" "${PROJECT_DIR}/"

    # 复制前端源码（用于构建）
    if [[ -d "$FRONTEND_SOURCE" ]]; then
        mkdir -p "${PROJECT_DIR}/frontend"
        rsync -av --exclude='node_modules' --exclude='.git' --exclude='dist' \
            "${FRONTEND_SOURCE}/" "${PROJECT_DIR}/frontend/"
    fi

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$PROJECT_DIR"

    success "  项目代码部署完成"
}

# 创建虚拟环境并安装依赖
setup_venv() {
    info "  正在创建虚拟环境并安装依赖..."

    cd "$PROJECT_DIR"

    # 创建虚拟环境
    $PYTHON_CMD -m venv "$VENV_DIR"

    # 升级 pip
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel

    # 安装依赖
    "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$VENV_DIR"

    success "  虚拟环境和依赖安装完成"
}

# 构建前端
build_frontend() {
    info "  正在构建前端..."

    FRONTEND_DIR="${PROJECT_DIR}/frontend"
    if [[ ! -f "${FRONTEND_DIR}/package.json" ]]; then
        warn "  前端源码不存在，跳过构建"
        return 0
    fi

    cd "$FRONTEND_DIR"

    # 安装依赖并构建
    npm install
    npm run build

    # 确保构建产物存在
    if [[ ! -d "${FRONTEND_DIR}/dist" ]]; then
        error "  前端构建失败，dist 目录不存在"
        return 1
    fi

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$FRONTEND_DIR"

    success "  前端构建完成"
}

# 配置 Systemd 服务
setup_systemd() {
    info "  正在配置 Systemd 服务..."

    local service_file="/etc/systemd/system/${PROJECT_NAME}.service"
    cp "$PROJECT_DIR/scripts/deploy/gw2-backend-lightweight.service" "$service_file"

    # 生成随机 SECRET_KEY
    local secret_key
    secret_key=$(openssl rand -base64 32)
    sed -i "s|CHANGE_ME_TO_A_RANDOM_STRING_AT_LEAST_32_CHARS_LONG|${secret_key}|g" "$service_file"

    systemctl daemon-reload
    systemctl enable "$PROJECT_NAME"

    success "  Systemd 服务配置完成"
}

# 配置 Nginx
setup_nginx() {
    info "  正在配置 Nginx..."

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

    success "  Nginx 配置完成"
}

# 配置日志轮转
setup_logrotate() {
    info "  正在配置日志轮转..."

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

    success "  日志轮转配置完成"
}

# 配置防火墙
setup_firewall() {
    info "  正在配置防火墙..."

    if command -v ufw &> /dev/null; then
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow http
        # 如果后续配置 HTTPS，取消注释下行
        # ufw allow https
        ufw --force enable
        success "  UFW 防火墙配置完成"
    else
        warn "  未检测到 UFW，跳过防火墙配置"
    fi
}

# 启动服务
start_service() {
    info "  正在启动服务..."

    systemctl start "$PROJECT_NAME"

    sleep 3

    if systemctl is-active --quiet "$PROJECT_NAME"; then
        success "  服务启动成功!"
    else
        error "  服务启动失败，查看日志: journalctl -u ${PROJECT_NAME} -n 50"
        return 1
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

# ============================================================================
# 主流程
# ============================================================================
main() {
    # 显示状态模式
    if [ "$SHOW_STATUS" = "true" ]; then
        show_deploy_status
        exit 0
    fi

    # 强制模式：清除状态
    if [ "$FORCE_DEPLOY" = "true" ]; then
        warn "强制重新部署模式：将清除状态并从头执行"
        clear_state
    fi

    # 恢复模式：检查上次失败记录
    if [ "$RESUME_MODE" = "true" ]; then
        local failed
        failed=$(get_last_failed)
        if [ -n "$failed" ]; then
            warn "恢复模式：从失败步骤继续部署"
            info "上次失败步骤: $failed"
            info "已完成的步骤将被自动跳过"
        else
            info "未发现失败记录，从头开始部署"
        fi
    fi

    init_state

    info "开始轻量级部署（2G2核 优化版）..."

    # 按顺序执行部署步骤
    run_step "check_root"        "检查 root 权限"          check_root
    run_step "check_os"          "检查操作系统"            check_os
    run_step "install_python"    "安装 Python 3.11+"       install_python
    run_step "install_system_deps" "安装系统依赖"          install_system_deps
    run_step "install_nodejs"    "安装 Node.js"            install_nodejs
    run_step "setup_project"     "创建项目用户和目录"      setup_project
    run_step "deploy_backend"    "部署项目代码"            deploy_backend
    run_step "setup_venv"        "创建虚拟环境"            setup_venv
    run_step "build_frontend"    "构建前端"                build_frontend
    run_step "setup_systemd"     "配置 Systemd 服务"       setup_systemd
    run_step "setup_nginx"       "配置 Nginx"              setup_nginx
    run_step "setup_logrotate"   "配置日志轮转"            setup_logrotate
    run_step "setup_firewall"    "配置防火墙"              setup_firewall
    run_step "start_service"     "启动服务"                start_service

    # 标记整体完成
    echo "DONE:ALL:$(date '+%Y-%m-%d %H:%M:%S')" >> "$STATE_FILE"

    print_summary
}

main "$@"
