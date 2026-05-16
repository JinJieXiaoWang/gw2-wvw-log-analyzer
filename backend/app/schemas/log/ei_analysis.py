# -*- coding: utf-8 -*-
# 模块功能：EI分析相关系统 Pydantic 模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-12

from typing import Any, List, Optional

from pydantic import BaseModel


class SkillMapItem(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    gw2_id: int
    skill_key: str


class PlayerRotationResponse(BaseModel):
    account: str
    character_name: Optional[str] = None
    profession: Optional[str] = None
    rotation: List[Any]
    skill_casts: dict
    skill_map: dict
