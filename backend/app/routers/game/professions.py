# -*- coding: utf-8 -*-
"""职业数据API路由（聚合入口）"""

from fastapi import APIRouter

from app.routers.game.professions_query import router as query_router
from app.routers.game.professions_admin import router as admin_router

router = APIRouter(prefix="/professions", tags=["职业数据"])
router.include_router(query_router)
router.include_router(admin_router)
