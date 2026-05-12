# -*- coding: utf-8 -*-
# 模块功能：Build图书馆数据验证Schema
# 依赖说明：Pydantic v2

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BuildWeapon(BaseModel):
    set: int
    name: str
    sigils: List[str]


class BuildTraitLine(BaseModel):
    name: str
    choices: List[int]


class BuildRotationCommand(BaseModel):
    callout: str
    action: str
    note: Optional[str] = None


class BuildMechanic(BaseModel):
    name: str
    sources: List[str]


class BuildVideo(BaseModel):
    title: str
    url: str
    author: Optional[str] = None


class BuildBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, description="Build标题")
    profession: str = Field(..., description="职业名称")
    profession_color: Optional[str] = Field(None, description="职业颜色")
    elite_spec: Optional[str] = Field(None, description="精英特长")
    role: str = Field(..., pattern=r"^(dps|support)$", description="主角角色类型")
    sub_roles: List[str] = Field(default_factory=list, description="子角色列")
    armor_type: Optional[str] = Field(None, description="护甲类型")
    weapons: List[BuildWeapon] = Field(default_factory=list, description="武器配置")
    relic: Optional[str] = Field(None, description="Relic")
    rune: Optional[str] = Field(None, description="符文")
    food: Optional[str] = Field(None, description="食物")
    wrench: Optional[str] = Field(None, description="扳手")
    infusion: Optional[str] = Field(None, description="灌注")
    attr_requirements: List[str] = Field(default_factory=list, description="属性要求")
    bd_code: str = Field(
        ...,
        pattern=r"^\[&[A-Za-z0-9+/=]+\]$",
        description="GW2 Build Code",
    )
    trait_lines: List[BuildTraitLine] = Field(default_factory=list, description="特性线")
    rotation_commands: List[BuildRotationCommand] = Field(
        default_factory=list, description="循环指令"
    )
    mechanics: List[BuildMechanic] = Field(default_factory=list, description="机制说明")
    videos: List[BuildVideo] = Field(default_factory=list, description="视频链接")
    author: str = Field(default="", max_length=50, description="作者")

    @field_validator("profession")
    @classmethod
    def validate_profession(cls, v: str) -> str:
        valid = {
            "Elementalist",
            "Engineer",
            "Guardian",
            "Mesmer",
            "Necromancer",
            "Ranger",
            "Revenant",
            "Warrior",
        }
        if v not in valid:
            raise ValueError(f"无效的职? {v}")
        return v

    @field_validator("sub_roles")
    @classmethod
    def validate_sub_roles(cls, v: List[str]) -> List[str]:
        valid = {"boon", "heal", "tank", "cc"}
        invalid = set(v) - valid
        if invalid:
            raise ValueError(f"无效的子角色: {invalid}")
        return v


class BuildCreate(BuildBase):
    pass


class BuildUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, min_length=2, max_length=100)
    profession: Optional[str] = None
    profession_color: Optional[str] = None
    elite_spec: Optional[str] = None
    role: Optional[str] = Field(None, pattern=r"^(dps|support)$")
    sub_roles: Optional[List[str]] = None
    armor_type: Optional[str] = None
    weapons: Optional[List[BuildWeapon]] = None
    relic: Optional[str] = None
    rune: Optional[str] = None
    food: Optional[str] = None
    wrench: Optional[str] = None
    infusion: Optional[str] = None
    attr_requirements: Optional[List[str]] = None
    bd_code: Optional[str] = Field(None, pattern=r"^\[&[A-Za-z0-9+/=]+\]$")
    trait_lines: Optional[List[BuildTraitLine]] = None
    rotation_commands: Optional[List[BuildRotationCommand]] = None
    mechanics: Optional[List[BuildMechanic]] = None
    videos: Optional[List[BuildVideo]] = None
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    is_meta: Optional[bool] = None


class BuildResponse(BuildBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    word_count: int = 0
    is_meta: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BuildListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[BuildResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
