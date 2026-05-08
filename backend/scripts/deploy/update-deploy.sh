#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - 增量更新部署脚本（保留数据和上传文件）
# 用法: sudo bash /opt/gw2-backend/scripts/deploy/update-deploy.sh
#        或 cd /opt/gw2-backend && sudo bash scripts/deploy/update-deploy.sh
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

# 自动探测项目目录
if [ -d "/opt/gw2-backend/.git" ]; then
    PROJECT_DIR="/opt/gw2-backend"
elif [ -d "/opt/gw2-wvw-log-analyzer/.git" ]; then
    PROJECT_DIR="/opt/gw2-wvw-log-analyzer"
else
    error "未找到项目目录，请确保在 /opt/gw2-backend 或 /opt/gw2-wvw-log-analyzer 下运行"
    exit 1
fi

info "探测到项目目录: ${PROJECT_DIR}"
cd "${PROJECT_DIR}"

# 检查 root 权限
if [[ $EUID -ne 0 ]]; then
    error "请使用 root 权限运行: sudo bash $0"
    exit 1
fi

# ========== 1. 备份 ==========
info "备份数据库和上传文件..."
mkdir -p /root/gw2-backup

if [ -f "${PROJECT_DIR}/database/app.db" ]; then
    cp "${PROJECT_DIR}/database/app.db" "/root/gw2-backup/app.db.$(date +%Y%m%d_%H%M%S)"
    success "数据库已备份"
fi

if [ -d "${PROJECT_DIR}/uploads" ]; then
    cp -r "${PROJECT_DIR}/uploads" "/root/gw2-backup/uploads.$(date +%Y%m%d_%H%M%S)"
    success "上传文件已备份"
fi

# ========== 2. 拉取最新代码 ==========
info "拉取最新代码..."
git reset --hard HEAD
git clean -fd
git pull origin master
success "代码更新完成"

# ========== 3. 安装后端依赖 ==========
info "更新后端依赖..."
if [ -d "${PROJECT_DIR}/venv" ]; then
    source "${PROJECT_DIR}/venv/bin/activate"
    pip install --upgrade pip setuptools wheel
    pip install -r "${PROJECT_DIR}/requirements.txt"
    success "后端依赖更新完成"
else
    warn "未找到虚拟环境，跳过依赖更新（如首次部署请使用 install-lightweight.sh）"
fi

# ========== 4. 构建前端 ==========
info "重新构建前端..."
FRONTEND_DIR="${PROJECT_DIR}/frontend"
if [ -f "${FRONTEND_DIR}/package.json" ]; then
    cd "${FRONTEND_DIR}"
    npm install
    npm run build
    if [ ! -d "${FRONTEND_DIR}/dist" ]; then
        error "前端构建失败"
        exit 1
    fi
    success "前端构建完成"
else
    warn "前端源码不存在，跳过构建"
fi

cd "${PROJECT_DIR}"

# ========== 5. 初始化数据库（创建缺失表，不删数据） ==========
info "初始化数据库..."
if [ -d "${PROJECT_DIR}/venv" ]; then
    source "${PROJECT_DIR}/venv/bin/activate"
    python -c "
import sys
sys.path.insert(0, '${PROJECT_DIR}')
from app.config.database import init_db
init_db()
print('数据库初始化完成')
"
    success "数据库初始化完成"
fi

# ========== 6. 更新 systemd 服务文件 ==========
info "更新 systemd 服务..."
if [ -f "${PROJECT_DIR}/scripts/deploy/gw2-backend-lightweight.service" ]; then
    cp "${PROJECT_DIR}/scripts/deploy/gw2-backend-lightweight.service" /etc/systemd/system/gw2-backend.service
    systemctl daemon-reload
    success "服务文件已更新"
fi

# ========== 7. 更新 Nginx 配置（可选） ==========
info "检查 Nginx 配置更新..."
if [ -f "${PROJECT_DIR}/scripts/deploy/nginx-gw2-lightweight.conf" ]; then
    read -p "是否更新 Nginx 配置? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "${PROJECT_DIR}/scripts/deploy/nginx-gw2-lightweight.conf" /etc/nginx/sites-available/gw2-backend
        ln -sf /etc/nginx/sites-available/gw2-backend /etc/nginx/sites-enabled/gw2-backend
        nginx -t && systemctl reload nginx
        success "Nginx 配置已更新"
    else
        info "跳过 Nginx 配置更新"
    fi
fi

# ========== 8. 重启后端服务 ==========
info "重启后端服务..."
systemctl restart gw2-backend
sleep 3

if systemctl is-active --quiet gw2-backend; then
    success "服务启动成功!"
else
    error "服务启动失败，查看日志: journalctl -u gw2-backend -n 50"
    exit 1
fi

# ========== 9. 快速测试 ==========
info "运行健康检查..."
HEALTH=$(curl -s http://127.0.0.1:8000/api/v1/health 2>/dev/null || echo "")
if [ -n "$HEALTH" ]; then
    success "健康检查通过: ${HEALTH}"
else
    warn "健康检查未返回预期结果，请手动检查"
fi

echo ""
echo "========================================"
echo "  增量更新部署完成!"
echo "========================================"
echo ""
echo "  访问地址: https://www.gw2-log-analyzer.top"
echo "  服务状态: systemctl status gw2-backend"
echo "  查看日志: journalctl -u gw2-backend -f"
echo ""
echo "========================================"
