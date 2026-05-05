#!/bin/sh
# =============================================================================
# GW2 Backend Docker 入口脚本
# 功能: 安全配置检查 + 数据库初始化检查 + 启动 Uvicorn
# 更新日期: 2026-05-05
# =============================================================================

set -e

echo "========================================"
echo "  GW2 Backend 启动中..."
echo "  $(date -Iseconds)"
echo "========================================"

# ---------------------------------------------------------------------------
# 安全配置校验
# ---------------------------------------------------------------------------
SECRET_KEY_LEN=0
if [ -n "$SECRET_KEY" ]; then
    SECRET_KEY_LEN=$(printf '%s' "$SECRET_KEY" | wc -c)
fi

if [ "$SECRET_KEY_LEN" -lt 32 ]; then
    echo "【致命错误】SECRET_KEY 未设置或长度不足 32 字符（当前: $SECRET_KEY_LEN）"
    echo "请在 .env 文件中设置强密钥，例如："
    echo "  SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || python -c 'import secrets; print(secrets.token_urlsafe(32))')"
    exit 1
fi

echo "✓ SECRET_KEY 校验通过（长度: $SECRET_KEY_LEN）"

# 校验 DEBUG 模式
if [ "${DEBUG}" = "true" ] || [ "${DEBUG}" = "True" ]; then
    echo "⚠️ 警告：DEBUG 模式已开启，生产环境请设置为 false"
fi

# 校验 ADMIN_INITIAL_PASSWORD
if [ -z "$ADMIN_INITIAL_PASSWORD" ]; then
    echo "⚠️ 警告：ADMIN_INITIAL_PASSWORD 未设置，系统将生成随机密码"
else
    ADMIN_PWD_LEN=$(printf '%s' "$ADMIN_INITIAL_PASSWORD" | wc -c)
    if [ "$ADMIN_PWD_LEN" -lt 8 ]; then
        echo "⚠️ 警告：ADMIN_INITIAL_PASSWORD 长度建议至少 8 位（当前: $ADMIN_PWD_LEN）"
    else
        echo "✓ ADMIN_INITIAL_PASSWORD 已设置"
    fi
fi

# 等待数据库就绪（如果配置了外部数据库）
if [ -n "$MYSQL_HOST" ] && [ "$DB_TYPE" = "mysql" ]; then
    echo "等待 MySQL 就绪: $MYSQL_HOST:$MYSQL_PORT..."
    python -c "
import socket, sys, time
host = '$MYSQL_HOST'
port = int('${MYSQL_PORT:-3306}')
for i in range(30):
    try:
        socket.create_connection((host, port), timeout=2).close()
        print('MySQL 已就绪')
        sys.exit(0)
    except Exception:
        print(f'  等待中... ({i+1}/30)')
        time.sleep(2)
print('MySQL 连接超时')
sys.exit(1)
" || echo "MySQL 连接检查失败，继续启动..."
fi

# 数据库初始化（仅 SQLite 或首次启动时）
if [ "${AUTO_INIT_DB:-false}" = "true" ]; then
    echo "执行数据库初始化..."
    python -c "
from app.config.database import init_db
init_db()
" || echo "数据库初始化跳过（可能已存在）"
fi

# 启动应用
echo "========================================"
# Uvicorn 只接受小写的日志级别
LOG_LEVEL=$(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')

echo "  启动 Uvicorn..."
echo "  Host: ${UVICORN_HOST:-0.0.0.0}"
echo "  Port: ${UVICORN_PORT:-8000}"
echo "  Workers: ${UVICORN_WORKERS:-1}"
echo "  Log Level: ${LOG_LEVEL}"
echo "========================================"

exec uvicorn main:app \
    --host "${UVICORN_HOST:-0.0.0.0}" \
    --port "${UVICORN_PORT:-8000}" \
    --workers "${UVICORN_WORKERS:-1}" \
    --proxy-headers \
    --forwarded-allow-ips "*" \
    --access-log \
    --log-level "${LOG_LEVEL}"
