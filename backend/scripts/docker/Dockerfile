# =============================================================================
# GW2 WvW 日志解析与评分系统 — Docker 镜像
# 域名: gw2-log-analyzer.top
# 构建: docker build -t gw2-backend:latest .
# 运行: docker run -d -p 8000:8000 --env-file .env gw2-backend:latest
# 更新日期: 2026-05-05
# =============================================================================

# -----------------------------------------------------------------------------
# 阶段 1: 构建依赖（Builder）
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS builder

# 换国内源加速 apt 和 pip
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境（隔离依赖）
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装 Python 依赖（使用清华 PyPI 镜像）
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple --upgrade pip && \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

# -----------------------------------------------------------------------------
# 阶段 2: 运行时（Runtime）
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

LABEL maintainer="帅妹妹丶.8297"
LABEL description="GW2 WvW 日志解析与评分系统后端"
LABEL version="1.0.0"

# 换国内源加速 apt
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r gw2 && useradd -r -g gw2 -d /app -s /sbin/nologin gw2

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY --chown=gw2:gw2 app/ ./app/
COPY --chown=gw2:gw2 main.py .
COPY --chown=gw2:gw2 scripts/docker/entrypoint.sh ./entrypoint.sh

# 复制 GW2.txt 数据文件（Build 图书馆初始化依赖）
COPY --chown=gw2:gw2 tests/GW2.txt ./tests/GW2.txt

# 创建数据目录并设置权限
RUN mkdir -p /app/uploads /app/logs /app/database /app/ssl && \
    chown -R gw2:gw2 /app

# 切换到非 root 用户
USER gw2

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 入口脚本
ENTRYPOINT ["sh", "./entrypoint.sh"]
