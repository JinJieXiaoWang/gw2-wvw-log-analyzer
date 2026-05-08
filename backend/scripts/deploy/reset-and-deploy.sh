#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - 完全重置并重新部署（保留数据库）
# 用法: sudo bash /opt/gw2-wvw-log-analyzer/backend/scripts/deploy/reset-and-deploy.sh
# ============================================================================
set -euo pipefail

REPO_DIR="/opt/gw2-wvw-log-analyzer"
BACKEND_DIR="/opt/gw2-backend"

echo "[INFO] 停止服务..."
systemctl stop gw2-backend 2>/dev/null || true

# 备份数据库（如果存在）
if [ -f "${BACKEND_DIR}/database/app.db" ]; then
    mkdir -p /root/gw2-backup
    cp "${BACKEND_DIR}/database/app.db" "/root/gw2-backup/app.db.$(date +%Y%m%d_%H%M%S)"
    echo "[OK] 数据库已备份到 /root/gw2-backup/"
fi

# 备份上传文件（如果存在）
if [ -d "${BACKEND_DIR}/uploads" ]; then
    mkdir -p /root/gw2-backup
    cp -r "${BACKEND_DIR}/uploads" "/root/gw2-backup/uploads.$(date +%Y%m%d_%H%M%S)"
    echo "[OK] 上传文件已备份到 /root/gw2-backup/"
fi

# 完全删除旧部署目录
echo "[INFO] 清理旧部署..."
rm -rf "${BACKEND_DIR}"

# 确保代码仓库存在
echo "[INFO] 拉取最新代码..."
if [ ! -d "${REPO_DIR}/.git" ]; then
    cd /opt
    git clone https://github.com/JinJieXiaoWang/gw2-wvw-log-analyzer.git gw2-wvw-log-analyzer
else
    cd "${REPO_DIR}"
    git reset --hard HEAD
    git clean -fd
    git pull origin master
fi

cd "${REPO_DIR}"

echo "[INFO] 运行安装脚本..."
bash backend/scripts/deploy/install-lightweight.sh

# 恢复上传文件（如果备份存在）
LATEST_UPLOADS=$(ls -td /root/gw2-backup/uploads.* 2>/dev/null | head -1)
if [ -n "${LATEST_UPLOADS}" ]; then
    echo "[INFO] 恢复上传文件..."
    cp -r "${LATEST_UPLOADS}"/* "${BACKEND_DIR}/uploads/" 2>/dev/null || true
    chown -R gw2:gw2 "${BACKEND_DIR}/uploads"
fi

echo "[OK] 重置部署完成！"
echo "[TIP] 如果数据库是重新创建的，请用默认账号 admin/admin123 登录"
