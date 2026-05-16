#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - 本地一键部署脚本
# ============================================================================
# 运行位置：本地开发机（Windows Git Bash / macOS / Linux）
# 功能：本地构建前端 → 增量上传前后端 → 远程重启服务 → 健康检查
# 核心优势：服务器无需构建前端，节省内存；支持增量更新与回滚
#
# 前置条件：
#   1. 本地已安装 Node.js (>=18) 和 npm
#   2. 本地已安装 ssh、rsync
#   3. 已配置 SSH 公钥免密登录到服务器
#   4. 服务器已完成首次环境初始化（运行过 server-setup.sh）
#
# 用法：
#   # 基础用法（修改脚本内配置后直接执行）
#   ./scripts/deploy/deploy.sh
#
#   # 通过环境变量指定服务器
#   DEPLOY_HOST=1.2.3.4 DEPLOY_USER=root ./scripts/deploy/deploy.sh
#
#   # 回滚到上一版本
#   ./scripts/deploy/deploy.sh --rollback
# ============================================================================

set -e

# ============================================================================
# 配置区（根据实际情况修改，或通过环境变量覆盖）
# ============================================================================
SERVER_HOST="${DEPLOY_HOST:-}"                # 服务器 IP 或域名（必填）
SERVER_USER="${DEPLOY_USER:-root}"            # SSH 登录用户名
SERVER_DIR="${DEPLOY_DIR:-/opt/gw2-backend}"  # 服务器部署目录
MAX_RELEASES="${DEPLOY_MAX_RELEASES:-5}"      # 保留的历史版本数量

# 前端路径（脚本自动检测项目结构）
DETECT_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "${DETECT_SCRIPT_DIR}/../../frontend" ]; then
    FRONTEND_LOCAL="${DETECT_SCRIPT_DIR}/../../frontend"
elif [ -d "${DETECT_SCRIPT_DIR}/../frontend" ]; then
    FRONTEND_LOCAL="${DETECT_SCRIPT_DIR}/../frontend"
elif [ -d "./frontend" ]; then
    FRONTEND_LOCAL="./frontend"
else
    FRONTEND_LOCAL="../frontend"
fi

# 服务器上前端部署位置（nginx 配置的 root 目录）
FRONTEND_REMOTE="${SERVER_DIR}/frontend/dist"
# ============================================================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()     { echo -e "${BLUE}[INFO]${NC}  $*"; }
success()  { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()     { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()    { echo -e "${RED}[ERROR]${NC} $*"; }
step()     { echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${CYAN}▶ $*${NC}"; }

# 执行步骤并记录退出码
run_step() {
    local desc="$1"
    shift
    info "  $desc ..."
    if "$@"; then
        success "  $desc 完成"
        return 0
    else
        error "  $desc 失败"
        return 1
    fi
}

# ============================================================================
# 1. 本地环境检查
# ============================================================================
check_local_env() {
    # Node.js
    if ! command -v node &> /dev/null; then
        error "本地未找到 Node.js，请先安装 https://nodejs.org/"
        return 1
    fi
    info "  Node.js: $(node --version)"

    # npm
    if ! command -v npm &> /dev/null; then
        error "本地未找到 npm"
        return 1
    fi
    info "  npm: $(npm --version)"

    # rsync
    if ! command -v rsync &> /dev/null; then
        error "本地未找到 rsync"
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
            error "  Windows 用户请使用 Git Bash，它自带 rsync"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            error "  macOS 请执行: brew install rsync"
        else
            error "  Linux 请执行: sudo apt-get install rsync"
        fi
        return 1
    fi

    # ssh
    if ! command -v ssh &> /dev/null; then
        error "本地未找到 ssh"
        return 1
    fi

    # 检查 SSH 免密连接
    info "  测试 SSH 连接 ${SERVER_USER}@${SERVER_HOST} ..."
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
            "${SERVER_USER}@${SERVER_HOST}" "echo ok" &>/dev/null; then
        error "  无法通过 SSH 免密连接到 ${SERVER_USER}@${SERVER_HOST}"
        error "  请先配置 SSH 公钥免密登录："
        error "    ssh-copy-id ${SERVER_USER}@${SERVER_HOST}"
        error "  或手动将本地 ~/.ssh/id_rsa.pub 内容添加到服务器的 ~/.ssh/authorized_keys"
        return 1
    fi
    success "  SSH 免密连接正常"

    # 检查前端目录
    if [ ! -f "${FRONTEND_LOCAL}/package.json" ]; then
        error "  未找到前端目录: ${FRONTEND_LOCAL}"
        error "  请确认脚本运行位置正确，或手动设置 FRONTEND_LOCAL"
        return 1
    fi
    info "  前端目录: ${FRONTEND_LOCAL}"

    return 0
}

# ============================================================================
# 2. 读取版本号
# ============================================================================
get_version() {
    if [ -f "${FRONTEND_LOCAL}/package.json" ]; then
        VERSION=$(grep '"version"' "${FRONTEND_LOCAL}/package.json" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
    else
        VERSION="unknown"
    fi
    info "  版本号: ${VERSION}"
}

# ============================================================================
# 3. 本地构建前端（关键：在本地完成，服务器无需 node/npm）
# ============================================================================
build_frontend() {
    cd "${FRONTEND_LOCAL}"

    info "  执行 npm install..."
    npm install

    info "  执行 npm run build..."
    npm run build

    if [ ! -d "dist" ] || [ -z "$(ls -A dist 2>/dev/null)" ]; then
        error "  前端构建失败，dist 目录不存在或为空"
        return 1
    fi

    local size
    size=$(du -sh dist 2>/dev/null | awk '{print $1}')
    success "  前端构建成功，产物大小: ${size}"
}

# ============================================================================
# 4. 备份服务器当前版本（用于回滚）
# ============================================================================
backup_remote() {
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local archive_name="release_${timestamp}.tar.gz"

    info "  在服务器创建备份..."

    ssh "${SERVER_USER}@${SERVER_HOST}" "
        set -e
        mkdir -p ${SERVER_DIR}/releases

        # 打包当前版本（排除动态数据、虚拟环境、缓存）
        cd ${SERVER_DIR}
        tar czf releases/${archive_name} \
            --exclude='uploads' \
            --exclude='database' \
            --exclude='logs' \
            --exclude='releases' \
            --exclude='.venv' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            . 2>/dev/null || true

        # 记录部署历史
        echo '${timestamp}' >> ${SERVER_DIR}/.deploy_history

        # 清理超期备份
        cd ${SERVER_DIR}/releases
        ls -t *.tar.gz 2>/dev/null | tail -n +$((MAX_RELEASES + 1)) | xargs -r rm -f

        # 输出备份文件名
        echo '${archive_name}'
    "
}

# ============================================================================
# 5. 上传后端代码（增量更新，仅传输变更）
# ============================================================================
deploy_backend() {
    # 自动检测后端源码位置
    local src_dir
    if [ -d "./app" ] && [ -f "./main.py" ]; then
        src_dir="./"                    # 当前在 backend/ 目录
    elif [ -d "./backend/app" ] && [ -f "./backend/main.py" ]; then
        src_dir="./backend/"            # 当前在项目根目录
    elif [ -d "../app" ] && [ -f "../main.py" ]; then
        src_dir="../"                   # 当前在 scripts/deploy/ 目录
    else
        error "  无法自动定位后端源码目录"
        return 1
    fi

    info "  后端源码: ${src_dir} → ${SERVER_USER}@${SERVER_HOST}:${SERVER_DIR}/"

    rsync -avz --progress \
        --exclude='.git' \
        --exclude='.venv' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='node_modules' \
        --exclude='dist' \
        --exclude='uploads' \
        --exclude='database' \
        --exclude='logs' \
        --exclude='releases' \
        --exclude='.deploy_history' \
        "${src_dir}" \
        "${SERVER_USER}@${SERVER_HOST}:${SERVER_DIR}/"
}

# ============================================================================
# 6. 上传前端构建产物（删除旧文件，保持纯净）
# ============================================================================
deploy_frontend() {
    info "  前端产物: ${FRONTEND_LOCAL}/dist/ → ${SERVER_USER}@${SERVER_HOST}:${FRONTEND_REMOTE}/"

    ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${FRONTEND_REMOTE}"

    rsync -avz --delete --progress \
        "${FRONTEND_LOCAL}/dist/" \
        "${SERVER_USER}@${SERVER_HOST}:${FRONTEND_REMOTE}/"
}

# ============================================================================
# 7. 远程执行服务更新（服务器只需 Python，无需 Node.js）
# ============================================================================
remote_update() {
    info "  在服务器执行更新..."

    local result
    result=$(ssh "${SERVER_USER}@${SERVER_HOST}" "
        set -e
        cd ${SERVER_DIR}

        # 确保虚拟环境存在（首次运行时会创建）
        if [ ! -d venv ]; then
            echo 'VENV_MISSING'
            exit 1
        fi

        source venv/bin/activate

        # 安装/更新 Python 依赖
        echo '>>> 安装 Python 依赖...'
        pip install -q -r requirements.txt

        # 数据库初始化/迁移（自动建表，不删数据）
        echo '>>> 初始化数据库...'
        python -c \"import sys; sys.path.insert(0, '${SERVER_DIR}'); from app.config.database import init_db; init_db()\" 2>/dev/null || true

        # 设置文件权限
        chown -R gw2:gw2 ${SERVER_DIR} 2>/dev/null || true

        # 测试后端能否正常启动（先做一次预热加载）
        echo '>>> 预加载应用...'
        python -c \"import sys; sys.path.insert(0, '${SERVER_DIR}'); import main\" 2>/dev/null || true

        # 重启后端服务
        echo '>>> 重启 gw2-backend 服务...'
        systemctl restart gw2-backend

        # 等待服务启动
        sleep 3

        # 检查服务状态
        if systemctl is-active --quiet gw2-backend; then
            echo 'BACKEND_OK'
        else
            echo 'BACKEND_FAIL'
            exit 1
        fi
    ")

    echo "$result"

    if echo "$result" | grep -q "VENV_MISSING"; then
        error "  服务器上未找到虚拟环境 ${SERVER_DIR}/venv"
        error "  请先运行 server-setup.sh 完成首次环境初始化"
        return 1
    fi

    if echo "$result" | grep -q "BACKEND_FAIL"; then
        error "  后端服务启动失败"
        return 1
    fi

    success "  后端服务重启成功"
}

# ============================================================================
# 8. 健康检查（自动验证部署结果）
# ============================================================================
health_check() {
    local url="http://${SERVER_HOST}/health"
    info "  目标: $url"

    local i
    for i in {1..10}; do
        local http_code
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

        if [ "$http_code" = "200" ]; then
            success "  健康检查通过 (HTTP 200)"
            return 0
        fi

        info "  第 ${i}/10 次检查... (HTTP ${http_code})"
        sleep 2
    done

    error "  健康检查失败，服务未正常响应"
    return 1
}

# ============================================================================
# 9. 回滚机制
# ============================================================================
rollback() {
    step "回滚部署"

    info "  获取服务器上的备份列表..."
    local releases
    releases=$(ssh "${SERVER_USER}@${SERVER_HOST}" \
        "ls -t ${SERVER_DIR}/releases/*.tar.gz 2>/dev/null | head -${MAX_RELEASES}")

    if [ -z "$releases" ]; then
        error "  服务器上没有找到可用的备份版本"
        return 1
    fi

    echo ""
    echo "  可回滚版本:"
    local idx=1
    local selected=""
    local release_array=()
    while IFS= read -r line; do
        release_array+=("$line")
        printf "    [%d] %s\n" "$idx" "$(basename "$line")"
        idx=$((idx + 1))
    done <<< "$releases"
    echo ""

    read -rp "  选择要回滚的版本编号 [1]: " choice
    choice=${choice:-1}

    if [ "$choice" -lt 1 ] || [ "$choice" -gt "${#release_array[@]}" ]; then
        error "  无效的选择"
        return 1
    fi

    selected="${release_array[$((choice - 1))]}"
    local archive_name
    archive_name=$(basename "$selected")

    warn "  即将回滚到: ${archive_name}"
    read -rp "  确认回滚? [y/N]: " confirm
    if [[ "${confirm,,}" != "y" ]]; then
        info "  已取消回滚"
        return 0
    fi

    info "  执行回滚..."
    local result
    result=$(ssh "${SERVER_USER}@${SERVER_HOST}" "
        set -e
        cd ${SERVER_DIR}

        # 停止服务
        systemctl stop gw2-backend || true

        # 备份当前失败版本（方便排查）
        local failed_name=\"failed_\$(date +%Y%m%d_%H%M%S).tar.gz\"
        tar czf releases/\${failed_name} \
            --exclude='uploads' --exclude='database' --exclude='logs' --exclude='releases' \
            . 2>/dev/null || true
        echo \"已保存失败版本: \${failed_name}\"

        # 清空当前目录（保留动态数据目录）
        find . -mindepth 1 -maxdepth 1 \
            ! -name 'uploads' \
            ! -name 'database' \
            ! -name 'logs' \
            ! -name 'releases' \
            ! -name '.deploy_history' \
            -exec rm -rf {} + 2>/dev/null || true

        # 解压历史版本
        tar xzf ${selected}

        # 恢复动态数据目录的权限
        chown -R gw2:gw2 uploads database logs 2>/dev/null || true

        # 重启服务
        systemctl start gw2-backend
        sleep 3

        if systemctl is-active --quiet gw2-backend; then
            echo 'ROLLBACK_OK'
        else
            echo 'ROLLBACK_FAIL'
            exit 1
        fi
    ")

    echo "  $result"

    if echo "$result" | grep -q "ROLLBACK_OK"; then
        success "  回滚成功"
        info "  请检查服务状态: http://${SERVER_HOST}/health"
    else
        error "  回滚失败"
        return 1
    fi
}

# ============================================================================
# 帮助信息
# ============================================================================
show_help() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║          GW2 WvW 日志系统 - 本地一键部署脚本                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  运行位置：本地开发机（Windows Git Bash / macOS / Linux）                     ║
║  核心优势：本地构建前端，服务器零内存压力；增量上传；自动回滚                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  用法:                                                                        ║
║    ./deploy.sh [选项]                                                         ║
║                                                                               ║
║  选项:                                                                        ║
║    (无参数)          执行完整部署流程                                         ║
║    --rollback, -r    回滚到历史版本                                           ║
║    --help, -h        显示此帮助                                               ║
║                                                                               ║
║  环境变量（覆盖脚本内默认配置）:                                              ║
║    DEPLOY_HOST       服务器地址，如 1.2.3.4 或 gw2.example.com               ║
║    DEPLOY_USER       SSH 用户名，默认 root                                    ║
║    DEPLOY_DIR        服务器部署目录，默认 /opt/gw2-backend                   ║
║    DEPLOY_MAX_RELEASES 保留的历史版本数，默认 5                               ║
║                                                                               ║
║  示例:                                                                        ║
║    # 修改脚本内 SERVER_HOST 后执行                                            ║
║    ./scripts/deploy/deploy.sh                                                 ║
║                                                                               ║
║    # 通过环境变量临时指定服务器                                               ║
║    DEPLOY_HOST=1.2.3.4 ./scripts/deploy/deploy.sh                             ║
║                                                                               ║
║    # 部署失败后回滚                                                           ║
║    ./scripts/deploy/deploy.sh --rollback                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
}

# ============================================================================
# 主流程
# ============================================================================
main() {
    case "${1:-}" in
        --rollback|-r)
            rollback
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
    esac

    # 检查必填配置
    if [ -z "$SERVER_HOST" ]; then
        error "未配置服务器地址"
        echo ""
        error "请修改脚本中的 SERVER_HOST，或通过环境变量指定："
        error "  DEPLOY_HOST=your-server-ip ./scripts/deploy/deploy.sh"
        echo ""
        show_help
        exit 1
    fi

    step "部署配置确认"
    info "  目标服务器: ${SERVER_USER}@${SERVER_HOST}"
    info "  部署目录:   ${SERVER_DIR}"
    info "  前端目录:   ${FRONTEND_LOCAL}"
    info "  保留版本:   ${MAX_RELEASES} 个"

    step "Step 1/6: 本地环境检查"
    run_step "检查本地工具链" check_local_env
    run_step "读取版本信息" get_version

    step "Step 2/6: 本地构建前端（服务器无需 Node.js）"
    run_step "npm install + build" build_frontend

    step "Step 3/6: 备份服务器当前版本"
    ARCHIVE_NAME=$(backup_remote)
    success "  备份完成: ${ARCHIVE_NAME}"

    step "Step 4/6: 增量上传代码到服务器"
    run_step "上传前端构建产物" deploy_frontend
    run_step "上传后端代码（增量）" deploy_backend

    step "Step 5/6: 远程更新服务"
    run_step "安装依赖并重启服务" remote_update

    step "Step 6/6: 部署验证"
    run_step "服务健康检查" health_check

    echo ""
    success "╔══════════════════════════════════════════════════════════════╗"
    success "║                    🎉 部署成功！                             ║"
    success "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    info "访问地址:"
    echo "  前端页面: http://${SERVER_HOST}/"
    echo "  API 接口: http://${SERVER_HOST}/api/v1/"
    echo "  接口文档: http://${SERVER_HOST}/docs"
    echo "  健康检查: http://${SERVER_HOST}/health"
    echo ""
    info "常用命令:"
    echo "  查看日志:  ssh ${SERVER_USER}@${SERVER_HOST} 'journalctl -u gw2-backend -f'"
    echo "  回滚版本:  ./scripts/deploy/deploy.sh --rollback"
    echo ""
}

main "$@"
