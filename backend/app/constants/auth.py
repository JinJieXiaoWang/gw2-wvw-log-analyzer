# -*- coding: utf-8 -*-
"""
认证相关常量配置
集中管理 JWT、登录安全等认证模块的常量?"""

from datetime import timedelta

# JWT 算法与令牌过?JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

# 登录安全限制
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
ATTEMPT_WINDOW_MINUTES = 5

# 计算后的时间间隔（直接使用）
LOCKOUT_DURATION = timedelta(minutes=LOCKOUT_DURATION_MINUTES)
ATTEMPT_WINDOW = timedelta(minutes=ATTEMPT_WINDOW_MINUTES)
