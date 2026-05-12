# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.routers.dictionary.dict_data import router as data_router
from app.routers.dictionary.dict_types import router as types_router

router = APIRouter()
router.include_router(data_router)
router.include_router(types_router)
