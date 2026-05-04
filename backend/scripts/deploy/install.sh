#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - Debian 12 裸机部署脚本
# ============================================================================
# 用法:
#   1. 将项目代码上传到服务器 (如 /root/gw2-backend)
#   2. chmod +x scripts/deploy/install.sh
#   3. sudo ./scripts/deploy/install.sh
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

# 配置变量
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

# 打印带颜色的信息
info() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# 检查 root 权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "请使用 root 权限运行此脚本: sudo $0"
        exit 1
    fi
}

# 检查 Debian 版本
check_os() {
    if [[ ! -f /etc/debian_version ]]; then
        error "此脚本仅支持 Debian 系统"
        exit 1
    fi
    local version
    version=$(cat /etc/debian_version | head -1)
    info "检测到系统版本: Debian ${version}"
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
            exit 1
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
    info "正在更新系统并安装依赖..."
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
        libmysqlclient-dev \
        libpq-dev

    success "系统依赖安装完成"
}

# 从源码编译安装 Python 3.13
install_python() {
    info "正在编译安装 Python ${PYTHON_VERSION}..."

    if command -v python3.13 &> /dev/null; then
        warn "Python 3.13 已存在，跳过编译"
        return
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

    success "Python ${PYTHON_VERSION} 编译安装完成"
    python3.13 --version
}

# 安装并配置 MySQL
install_mysql() {
    if [[ "$DB_TYPE" != "mysql" ]]; then
        info "跳过 MySQL 安装 (使用 ${DB_TYPE})"
        return
    fi

    info "正在安装 MySQL..."

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

    success "MySQL 安装并配置完成"
    info "数据库: gw2_log_system"
    info "用户: gw2"
}

# 创建项目用户和目录
setup_project_user() {
    info "正在创建项目用户和目录..."

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

    success "项目用户和目录创建完成"
}

# 部署项目代码
deploy_code() {
    info "正在部署项目代码..."

    if [[ ! -d "$SOURCE_DIR" ]]; then
        error "源码目录不存在: ${SOURCE_DIR}"
        exit 1
    fi

    # 复制代码到项目目录
    rsync -av --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
        "${SOURCE_DIR}/" "$PROJECT_DIR/"

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$PROJECT_DIR"

    success "项目代码部署完成"
}

# 创建虚拟环境并安装依赖
setup_venv() {
    info "正在创建虚拟环境并安装依赖..."

    cd "$PROJECT_DIR"

    # 创建虚拟环境
    python3.13 -m venv "$VENV_DIR"

    # 升级 pip
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel

    # 安装依赖
    "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

    chown -R "${PROJECT_USER}:${PROJECT_GROUP}" "$VENV_DIR"

    success "虚拟环境和依赖安装完成"
}

# 配置 Systemd 服务
setup_systemd() {
    info "正在配置 Systemd 服务..."

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

    success "Systemd 服务配置完成"
}

# 配置 Nginx
setup_nginx() {
    if [[ "${INSTALL_NGINX,,}" != "y" ]]; then
        info "跳过 Nginx 安装"
        return
    fi

    info "正在安装并配置 Nginx..."

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

    success "Nginx 配置完成"
}

# 配置日志轮转
setup_logrotate() {
    info "正在配置日志轮转..."

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

    success "日志轮转配置完成"
}

# 防火墙配置
setup_firewall() {
    info "正在配置防火墙..."

    if command -v ufw &> /dev/null; then
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow http
        ufw allow https
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

# 主流程
main() {
    check_root
    check_os
    interactive_config

    install_system_deps
    install_python
    install_mysql
    setup_project_user
    deploy_code
    setup_venv
    setup_systemd
    setup_nginx
    setup_logrotate
    setup_firewall
    start_service

    print_summary
}

main "$@"
