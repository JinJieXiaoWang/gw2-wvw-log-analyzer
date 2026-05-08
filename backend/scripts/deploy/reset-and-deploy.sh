#!/bin/bash
# ============================================================================
# GW2 WvW 日志系统 - 完全重置并重新部署（一步到位）
# 用法: sudo bash /root/reset-and-deploy.sh
# ============================================================================
set -e

echo "[INFO] 停止并清理旧部署..."
systemctl stop gw2-backend 2>/dev/null || true
systemctl disable gw2-backend 2>/dev/null || true
rm -f /etc/systemd/system/gw2-backend.service
rm -f /etc/nginx/sites-enabled/gw2-backend
rm -f /etc/nginx/sites-available/gw2-backend
systemctl daemon-reload

# 备份数据库（如果存在）
if [ -f /opt/gw2-backend/database/app.db ]; then
    mkdir -p /root/gw2-backup
    cp /opt/gw2-backend/database/app.db /root/gw2-backup/app.db.$(date +%Y%m%d_%H%M%S)
    echo "[OK] 数据库已备份到 /root/gw2-backup/"
fi

# 完全删除旧目录
rm -rf /opt/gw2-backend

echo "[INFO] 拉取最新代码..."
cd /opt
git clone https://github.com/JinJieXiaoWang/gw2-wvw-log-analyzer.git gw2-wvw-log-analyzer 2>/dev/null || (
    cd /opt/gw2-wvw-log-analyzer && git reset --hard HEAD && git clean -fd && git pull origin master
)

cd /opt/gw2-wvw-log-analyzer

echo "[INFO] 运行安装脚本..."
bash backend/scripts/deploy/install-lightweight.sh
