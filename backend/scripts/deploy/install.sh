#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - Debian 12 裸机部署脚本
# ============================================================================
# 用法:
#   sudo ./scripts/deploy/install.sh [选项]
#
# 选项:
#   --resume, -r    从上次失败的步骤继续部署
#   --force, -f     强制重新部署（清除状态记录，从头执行）
#   --status, -s    查看当前部署状态记录
#   --help, -h      显示帮助信息
#
# 前置要求:
#   - Debian 12 (bookworm) 干净系统
#   - root 权限
#   - 至少 2GB 内存 (编译 Python 3.13 需要)
#   - 至少 10GB 磁盘空间
# ============================================================================

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
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
        echo "SCRIPT:install.sh" >> "$STATE_FILE"
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
GW2 WvW 日志系统 - Debian 12 裸机部署脚本

用法:
  sudo ./scripts/deploy/install.sh [选项]

选项:
  --resume, -r    从上次失败的步骤继续部署（智能跳过已完成的步骤）
  --force, -f     强制重新部署：清除状态记录并从头执行所有步骤
  --status, -s    查看当前部署状态记录
  --help, -h      显示此帮助信息

示例:
  # 首次部署
  sudo ./scripts/deploy/install.sh

  # 查看当前部署状态
  sudo ./scripts/deploy/install.sh --status

  # 上次部署失败后继续
  sudo ./scripts/deploy/install.sh --resume

  # 强制从头重新部署（保留数据和上传文件）
  sudo ./scripts/deploy/install.sh --force
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
PYTHON_VERSION="3.13.3"
PROJECT_NAME="gw2-backend"
PROJECT_DIR="/opt/${PROJECT_NAME}"
PROJECT_USER="gw2"
PROJECT_GROUP="gw2"
VENV_DIR="${PROJECT_DIR}/venv"
LOG_DIR="${PROJECT_DIR}/logs"
UPLOAD_DIR="${PROJECT_DIR}/uploads"
DB_DIR="${PROJECT_DIR}/database"
MYSQL_ROOT_PASSWORD=""
MYSQL_APP_PASSWORD=""

# ============================================================================
# 各部署步骤函数
# ============================================================================

# 检查 root 权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "请使用 root 权限运行此脚本: sudo $0"
        return 1
    fi
}

# 检查 Debian 版本
check_os() {
    if [[ ! -f /etc/debian_version ]]; then
        error "此脚本仅支持 Debian 系统"
        return 1
    fi
    local version
    version=$(cat /etc/debian_version | head -1)
    info "  检测到系统版本: Debian ${version}"
}

# 交互式配置
interactive_config() {
    echo ""
    echo "========================================"
    echo "  GW2 WvW 日志系统 - 部署配置"
    echo "========================================"
    echo ""

    read -rp "数据库类型 [mysql/sqlite] (默认: mysql): " DB_TYPE
    DB_TYPE=${DB_TYPE:-mysql}

    if [[ "$DB_TYPE" == "mysql" ]]; then
        read -rsp "设置 MySQL root 密码: " MYSQL_ROOT_PASSWORD
        echo ""
        read -rsp "设置应用数据库密码 (用户: gw2): " MYSQL_APP_PASSWORD
        echo ""

        if [[ -z "$MYSQL_ROOT_PASSWORD" || -z "$MYSQL_APP_PASSWORD" ]]; then
            error "MySQL 密码不能为空"
            return 1
        fi
    fi

    read -rp "是否安装 Nginx 反向代理? [y/N]: " INSTALL_NGINX
    INSTALL_NGINX=${INSTALL_NGINX:-N}

    read -rp "项目源码路径 (默认: $(pwd)): " SOURCE_DIR
    SOURCE_DIR=${SOURCE_DIR:-$(pwd)}

    echo ""
    info "配置确认:"
    echo "  数据库类型: ${DB_TYPE}"
    echo "  安装 Nginx: ${INSTALL_NGINX}"
    echo "  源码路径: ${SOURCE_DIR}"
    echo ""
    read -rp "确认开始部署? [Y/n]: " CONFIRM
    if [[ "${CONFIRM,,}" == "n" ]]; then
        info "已取消部署"
        exit 0
    fi
}

# 安装系统依赖
install_system_deps() {
    info "  正在更新系统并安装依赖..."
    apt-get update
    apt-get upgrade -y

    # 构建 Python 3.13 所需的依赖
    apt-get install -y \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libffi-dev \
        liblzma-dev \
        python3-openssl \
        git \
        pkg-config \
        default-libmysqlclient-dev \
        libpq-dev

    success "  系统依赖安装完成"
}

# 从源码编译安装 Python 3.13
install_python() {
    info "  正在编译安装 Python ${PYTHON_VERSION}..."

    if command -v python3.13 &> /dev/null; then
        warn "  Python 3.13 已存在，跳过编译"
        return 0
    fi

    cd /tmp
    wget -q "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz"
    tar -xzf "Python-${PYTHON_VERSION}.tgz"
    cd "Python-${PYTHON_VERSION}"

    ./configure \
        --prefix=/usr/local \
        --enable-optimizations \
        --enable-shared \
        --with-ensurepip=install \
        LDFLAGS="-Wl,-rpath /usr/local/lib"

    make -j$(nproc)
    make altinstall

    # 更新动态链接库缓存
    ldconfig

    # 清理
    cd /tmp
    rm -rf "Python-${PYTHON_VERSION}" "Python-${PYTHON_VERSION}.tgz"

    success "  Python ${PYTHON_VERSION} 编译安装完成"
    python3.13 --version
}

# 安装 Node.js（用于前端构建）
install_nodejs() {
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        NODE_VERSION=$(node --version 2>/dev/null || echo "unknown")
        info "  Node.js 已存在: ${NODE_VERSION}"
        return 0
    fi

    info "  正在安装 Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs

    success "  Node.js 安装完成: $(node --version)"
}

# 安装并配置 MySQL
install_mysql() {
    if [[ "$DB_TYPE" != "mysql" ]]; then
        info "  跳过 MySQL 安装 (使用 ${DB_TYPE})"
        return 0
    fi

    info "  正在安装 MySQL..."

    apt-get install -y default-mysql-server

    # 启动 MySQL
    systemctl start mysql
    systemctl enable mysql

    # 安全配置
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';"
    mysql -e "DELETE FROM mysql.user WHERE User='';"
    mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
    mysql -e "DROP DATABASE IF EXISTS test;"
    mysql -e "FLUSH PRIVILEGES;"

    # 创建应用数据库和用户
    mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE DATABASE IF NOT EXISTS gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER IF NOT EXISTS 'gw2'@'localhost' IDENTIFIED BY '${MYSQL_APP_PASSWORD}';"
    mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON gw2_log_system.* TO 'gw2'@'localhost';"
    mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "FLUSH PRIVILEGES;"

    success "  MySQL 安装并配置完成"
    info "  数据库: gw2_log_system"
    info "  用户: gw2"
}

# 创建项目用户和目录
setup_project_user() {
    info "  正在创建项目用户和目录..."

    # 创建用户 (无登录权限的系统用户)
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

# 部署项目代码
deploy_code() {
    info "  正在部署项目代码..."

    if [[ ! -d "$SOURCE_DIR" ]]; then
        error "  源码目录不存在: ${SOURCE_DIR}"
        return 1
    fi

    # 复制后端代码到项目目录
    rsync -av --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
        --exclude='node_modules' --exclude='dist' \
        "${SOURCE_DIR}/" "$PROJECT_DIR/"

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$PROJECT_DIR"

    success "  后端代码部署完成"
}

# 创建虚拟环境并安装依赖
setup_venv() {
    info "  正在创建虚拟环境并安装依赖..."

    cd "$PROJECT_DIR"

    # 创建虚拟环境
    python3.13 -m venv "$VENV_DIR"

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

    # 查找前端源码（支持项目根目录或后端同级）
    FRONTEND_SOURCE=""
    if [[ -d "${SOURCE_DIR}/frontend" ]]; then
        FRONTEND_SOURCE="${SOURCE_DIR}/frontend"
    elif [[ -d "$(dirname "$SOURCE_DIR")/frontend" ]]; then
        FRONTEND_SOURCE="$(dirname "$SOURCE_DIR")/frontend"
    fi

    if [[ -z "$FRONTEND_SOURCE" || ! -f "${FRONTEND_SOURCE}/package.json" ]]; then
        warn "  未找到前端源码，跳过前端构建"
        return 0
    fi

    cd "$FRONTEND_SOURCE"
    npm install
    npm run build

    if [[ ! -d "${FRONTEND_SOURCE}/dist" ]]; then
        error "  前端构建失败，dist 目录不存在"
        return 1
    fi

    # 复制构建产物到 Nginx 静态文件目录
    mkdir -p /var/www/html
    rsync -av "${FRONTEND_SOURCE}/dist/" /var/www/html/
    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" /var/www/html

    success "  前端构建并部署到 /var/www/html 完成"
}

# 配置 Systemd 服务
setup_systemd() {
    info "  正在配置 Systemd 服务..."

    local service_file="/etc/systemd/system/${PROJECT_NAME}.service"

    # 复制服务文件模板
    cp "$PROJECT_DIR/scripts/deploy/gw2-backend.service" "$service_file"

    # 替换配置变量
    if [[ "$DB_TYPE" == "mysql" ]]; then
        sed -i "s/Environment=\"DB_TYPE=mysql\"/Environment=\"DB_TYPE=mysql\"/" "$service_file"
        sed -i "s/CHANGE_ME_TO_STRONG_MYSQL_PASSWORD/${MYSQL_APP_PASSWORD}/g" "$service_file"
    else
        sed -i "s/Environment=\"DB_TYPE=mysql\"/Environment=\"DB_TYPE=sqlite\"/" "$service_file"
    fi

    # 生成随机 SECRET_KEY
    local secret_key
    secret_key=$(openssl rand -base64 32)
    sed -i "s/CHANGE_ME_TO_A_RANDOM_STRING_AT_LEAST_32_CHARS_LONG/${secret_key}/g" "$service_file"

    # 如果不用 MySQL，注释掉 MySQL 相关配置
    if [[ "$DB_TYPE" != "mysql" ]]; then
        sed -i '/mysql.service/d' "$service_file"
        sed -i '/Wants=mysql.service/d' "$service_file"
    fi

    systemctl daemon-reload
    systemctl enable "$PROJECT_NAME"

    success "  Systemd 服务配置完成"
}

# 配置 Nginx
setup_nginx() {
    if [[ "${INSTALL_NGINX,,}" != "y" ]]; then
        info "  跳过 Nginx 安装"
        return 0
    fi

    info "  正在安装并配置 Nginx..."

    apt-get install -y nginx

    # 复制配置
    cp "$PROJECT_DIR/scripts/deploy/nginx-gw2.conf" \
        /etc/nginx/sites-available/gw2-backend

    # 启用站点
    rm -f /etc/nginx/sites-enabled/default
    ln -sf /etc/nginx/sites-available/gw2-backend \
        /etc/nginx/sites-enabled/gw2-backend

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
    rotate 30
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

# 防火墙配置
setup_firewall() {
    info "  正在配置防火墙..."

    if command -v ufw &> /dev/null; then
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow http
        ufw allow https
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
    echo "  部署完成!"
    echo "========================================"
    echo ""
    echo "  项目目录: ${PROJECT_DIR}"
    echo "  服务名称: ${PROJECT_NAME}"
    echo "  运行用户: ${PROJECT_USER}"
    echo "  虚拟环境: ${VENV_DIR}"
    echo ""
    echo "  服务状态:"
    echo "    systemctl status ${PROJECT_NAME}"
    echo ""
    echo "  查看日志:"
    echo "    journalctl -u ${PROJECT_NAME} -f"
    echo "    tail -f ${LOG_DIR}/app.log"
    echo ""
    echo "  API 地址:"
    if [[ "${INSTALL_NGINX,,}" == "y" ]]; then
        echo "    http://${ip}/api/v1/"
        echo "    http://${ip}/docs      (Swagger UI)"
    else
        echo "    http://${ip}:8000/api/v1/"
        echo "    http://${ip}:8000/docs  (Swagger UI)"
    fi
    echo ""
    echo "  健康检查:"
    echo "    curl http://127.0.0.1:8000/health"
    echo ""
    echo "  常用命令:"
    echo "    sudo systemctl start|stop|restart|status ${PROJECT_NAME}"
    echo "    sudo systemctl reload ${PROJECT_NAME}"
    echo ""

    if [[ "$DB_TYPE" == "mysql" ]]; then
        echo "  数据库信息:"
        echo "    主机: 127.0.0.1:3306"
        echo "    数据库: gw2_log_system"
        echo "    用户: gw2"
        echo ""
    fi

    echo "  安全提醒:"
    echo "    1. 请修改 /etc/systemd/system/${PROJECT_NAME}.service 中的 SECRET_KEY"
    echo "    2. 如果使用 MySQL，root 密码已设置，请妥善保管"
    echo "    3. 建议配置 HTTPS (Let's Encrypt)"
    echo "    4. 建议修改 SSH 端口并禁用 root 登录"
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

    # 按顺序执行部署步骤
    run_step "check_root"        "检查 root 权限"          check_root
    run_step "check_os"          "检查操作系统"            check_os
    run_step "interactive_config" "交互式配置"             interactive_config
    run_step "install_system_deps" "安装系统依赖"          install_system_deps
    run_step "install_python"    "编译安装 Python 3.13"    install_python
    run_step "install_nodejs"    "安装 Node.js"            install_nodejs
    run_step "install_mysql"     "安装并配置 MySQL"        install_mysql
    run_step "setup_project_user" "创建项目用户和目录"     setup_project_user
    run_step "deploy_code"       "部署后端代码"            deploy_code
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
