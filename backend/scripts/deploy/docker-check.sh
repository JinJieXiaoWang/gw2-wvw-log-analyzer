#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - Docker 部署前检查脚本
# ============================================================================
# 用法:
#   cd /opt/gw2-wvw-log-analyzer/backend
#   chmod +x scripts/deploy/docker-check.sh
#   ./scripts/deploy/docker-check.sh
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

check_pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
check_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; WARNINGS=$((WARNINGS+1)); }
check_fail() { echo -e "${RED}[FAIL]${NC} $*"; ERRORS=$((ERRORS+1)); }

info() { echo -e "${BLUE}[INFO]${NC} $*"; }

echo "========================================"
echo "  GW2 Docker 部署环境检查"
echo "========================================"
echo ""

# ---------------------------------------------------------------------------
# 1. 检查必要文件
# ---------------------------------------------------------------------------
info "检查必要文件..."

if [ -f ".env" ]; then
    check_pass ".env 文件存在"
else
    check_fail ".env 文件缺失（请复制 .env.example 并填写）"
fi

if [ -f "docker-compose.yml" ] || [ -f "../docker-compose.yml" ]; then
    check_pass "docker-compose.yml 存在"
else
    check_fail "docker-compose.yml 缺失（应在 backend 目录或 scripts/docker 目录运行）"
fi

if [ -f "scripts/docker/nginx.conf" ]; then
    check_pass "scripts/docker/nginx.conf 存在"
else
    check_fail "scripts/docker/nginx.conf 缺失"
fi

if [ -f "Dockerfile" ] || [ -f "scripts/docker/Dockerfile" ]; then
    check_pass "Dockerfile 存在"
else
    check_fail "Dockerfile 缺失"
fi

# ---------------------------------------------------------------------------
# 2. 检查必要目录
# ---------------------------------------------------------------------------
info "检查必要目录..."

if [ -d "dist" ] && [ "$(ls -A dist 2>/dev/null)" ]; then
    check_pass "dist/ 目录存在且非空（前端构建文件）"
elif [ -d "../frontend/dist" ] && [ "$(ls -A ../frontend/dist 2>/dev/null)" ]; then
    check_pass "../frontend/dist/ 目录存在且非空（前端构建文件）"
else
    check_warn "dist/ 目录缺失或为空（前端将无法正常访问）"
fi

if [ -d "ssl" ]; then
    check_pass "ssl/ 目录存在"
    # 检查证书文件是否存在
    if [ -f "ssl/live/gw2-log-analyzer.top/fullchain.pem" ]; then
        check_pass "SSL 证书文件存在"
    else
        check_warn "SSL 证书文件未找到（如使用自签名证书，请确保证书路径正确）"
    fi
else
    check_warn "ssl/ 目录缺失（HTTPS 将无法正常工作）"
fi

if [ -d "logs/nginx" ]; then
    check_pass "logs/nginx/ 目录存在"
else
    info "自动创建 logs/nginx/ 目录..."
    mkdir -p logs/nginx
    check_pass "logs/nginx/ 目录已创建"
fi

if [ -d "scripts/migrations" ]; then
    check_pass "scripts/migrations/ 目录存在"
else
    check_warn "scripts/migrations/ 目录缺失（数据库初始化脚本）"
fi

# ---------------------------------------------------------------------------
# 3. 检查 .env 关键变量
# ---------------------------------------------------------------------------
info "检查 .env 关键配置..."

if [ -f ".env" ]; then
    # 检查 SECRET_KEY
    if grep -q "^SECRET_KEY=" .env && [ "$(grep "^SECRET_KEY=" .env | cut -d= -f2 | tr -d '"' | wc -c)" -gt 32 ]; then
        check_pass "SECRET_KEY 已设置且长度符合要求"
    else
        check_fail "SECRET_KEY 未设置或长度不足 32 字符"
    fi

    # 检查 ADMIN_INITIAL_PASSWORD
    if grep -q "^ADMIN_INITIAL_PASSWORD=" .env && [ "$(grep "^ADMIN_INITIAL_PASSWORD=" .env | cut -d= -f2 | tr -d '"' | wc -c)" -gt 1 ]; then
        check_pass "ADMIN_INITIAL_PASSWORD 已设置"
    else
        check_fail "ADMIN_INITIAL_PASSWORD 未设置"
    fi

    # 检查 MySQL 密码
    if grep -q "^MYSQL_PASSWORD=" .env; then
        check_pass "MYSQL_PASSWORD 已设置"
    else
        check_warn "MYSQL_PASSWORD 未显式设置（将使用默认值，生产环境建议修改）"
    fi
else
    check_fail "跳过 .env 内容检查（文件不存在）"
fi

# ---------------------------------------------------------------------------
# 4. Docker 环境检查
# ---------------------------------------------------------------------------
info "检查 Docker 环境..."

if command -v docker &> /dev/null; then
    check_pass "Docker 已安装"
    if docker info &> /dev/null; then
        check_pass "Docker 守护进程运行正常"
    else
        check_fail "Docker 守护进程未运行或无权限访问"
    fi
else
    check_fail "Docker 未安装"
fi

if command -v docker compose &> /dev/null; then
    check_pass "Docker Compose (v2) 已安装"
elif command -v docker-compose &> /dev/null; then
    check_pass "Docker Compose (v1) 已安装（建议升级到 v2）"
else
    check_fail "Docker Compose 未安装"
fi

# ---------------------------------------------------------------------------
# 5. Nginx 配置语法检查（使用 Docker）
# ---------------------------------------------------------------------------
info "检查 Nginx 配置语法..."

if command -v docker &> /dev/null && docker info &> /dev/null; then
    # 先确保镜像存在
    if docker image inspect nginx:1.27-alpine &> /dev/null; then
        NGINX_IMAGE="nginx:1.27-alpine"
    else
        info "正在拉取 nginx:1.27-alpine 镜像..."
        if docker pull nginx:1.27-alpine &> /dev/null; then
            NGINX_IMAGE="nginx:1.27-alpine"
        else
            NGINX_IMAGE="nginx:alpine"
            check_warn "无法拉取 nginx:1.27-alpine，将使用 nginx:alpine 进行语法检查"
        fi
    fi

    # 使用 --add-host 临时解析 upstream 中的 app 主机名，避免语法检查时因 DNS 解析失败而报错
    if docker run --rm \
        --add-host app:127.0.0.1 \
        -v "$(pwd)/scripts/docker/nginx.conf:/etc/nginx/nginx.conf:ro" \
        "$NGINX_IMAGE" \
        nginx -t 2>&1 | grep -q "successful"; then
        check_pass "Nginx 配置语法正确"
    else
        check_fail "Nginx 配置语法错误（请查看上方详细输出）"
        docker run --rm \
            --add-host app:127.0.0.1 \
            -v "$(pwd)/scripts/docker/nginx.conf:/etc/nginx/nginx.conf:ro" \
            "$NGINX_IMAGE" \
            nginx -t 2>&1 || true
    fi
else
    check_warn "Docker 不可用，跳过 Nginx 语法检查"
fi

# ---------------------------------------------------------------------------
# 6. 端口占用检查
# ---------------------------------------------------------------------------
info "检查端口占用..."

if command -v ss &> /dev/null || command -v netstat &> /dev/null; then
    PORT_CHECK_CMD="ss -tlnp"
    if ! command -v ss &> /dev/null; then
        PORT_CHECK_CMD="netstat -tlnp"
    fi

    if $PORT_CHECK_CMD 2>/dev/null | grep -q ':80 '; then
        check_warn "80 端口已被占用（部署后可能冲突）"
    else
        check_pass "80 端口可用"
    fi

    if $PORT_CHECK_CMD 2>/dev/null | grep -q ':443 '; then
        check_warn "443 端口已被占用（部署后可能冲突）"
    else
        check_pass "443 端口可用"
    fi
else
    check_warn "未找到 ss/netstat，跳过端口检查"
fi

# ---------------------------------------------------------------------------
# 7. 磁盘空间检查
# ---------------------------------------------------------------------------
info "检查磁盘空间..."

DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_pass "磁盘使用率 ${DISK_USAGE}%（充足）"
else
    check_warn "磁盘使用率 ${DISK_USAGE}%（建议清理）"
fi

# ---------------------------------------------------------------------------
# 8. 内存检查
# ---------------------------------------------------------------------------
info "检查内存..."

if [ -f /proc/meminfo ]; then
    MEM_TOTAL_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MEM_TOTAL_MB=$((MEM_TOTAL_KB / 1024))
    if [ "$MEM_TOTAL_MB" -gt 2048 ]; then
        check_pass "内存 ${MEM_TOTAL_MB}MB（充足）"
    else
        check_warn "内存 ${MEM_TOTAL_MB}MB（建议至少 2GB）"
    fi
else
    check_warn "无法读取内存信息"
fi

# ---------------------------------------------------------------------------
# 结果汇总
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}所有检查通过！${NC}"
    echo ""
    echo "部署命令:"
    echo "  docker compose down"
    echo "  docker compose up -d --build"
    echo ""
    echo "查看日志:"
    echo "  docker compose logs -f nginx"
    echo "  docker compose logs -f app"
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}检查通过，但有 $WARNINGS 个警告${NC}"
    echo "建议修复警告后再部署，或直接执行："
    echo "  docker compose up -d --build"
else
    echo -e "${RED}发现 $ERRORS 个错误，$WARNINGS 个警告${NC}"
    echo "请修复错误后再部署。"
    exit 1
fi
echo "========================================"
