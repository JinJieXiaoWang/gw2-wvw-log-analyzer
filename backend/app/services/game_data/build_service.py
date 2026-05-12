# -*- coding: utf-8 -*-
# 模块功能：Build图书馆服务层
# 依赖说明：SQLAlchemy

import math
import re
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.game_data.build import Build
from app.utils.logger import logger


def _generate_slug(title: str) -> str:
    """根据标题生成URL友好的slug"""
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:100]


def _calc_word_count(build: Build) -> int:
    """计算Build字数"""
    total = len(build.title or "")
    total += len(build.author or "")
    for w in build.weapons or []:
        total += len(w.get("name", ""))
    for t in build.trait_lines or []:
        total += len(t.get("name", ""))
    for r in build.rotation_commands or []:
        total += len(r.get("callout", "")) + len(r.get("action", ""))
    for m in build.mechanics or []:
        total += len(m.get("name", ""))
    for v in build.videos or []:
        total += len(v.get("title", ""))
    return total


def create_build(db: Session, data: dict) -> Build:
    """创建Build"""
    build = Build(**data)
    build.slug = _generate_slug(build.title)
    # 确保slug唯一
    existing = db.query(Build).filter(Build.slug == build.slug).first()
    if existing:
        count = (
            db.query(func.count(Build.id))
            .filter(Build.slug.like(f"{build.slug}-%"))
            .scalar()
        )
        build.slug = f"{build.slug}-{count + 1}"

    build.word_count = _calc_word_count(build)
    db.add(build)
    db.commit()
    db.refresh(build)
    logger.info(f"创建Build: {build.title} (id={build.id})")
    return build


def get_build_by_id(db: Session, build_id: int) -> Optional[Build]:
    """根据ID获取Build"""
    return db.query(Build).filter(Build.id == build_id).first()


def get_build_by_slug(db: Session, slug: str) -> Optional[Build]:
    """根据slug获取Build"""
    return db.query(Build).filter(Build.slug == slug).first()


def list_builds(
    db: Session,
    profession: Optional[str] = None,
    role: Optional[str] = None,
    sub_role: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "updated_at",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """分页查询Build列表"""
    query = db.query(Build)

    # 过滤掉无效值（undefined、null、空字符串）
    def is_valid_param(param: Optional[str]) -> bool:
        if param is None:
            return False
        param = param.strip()
        return len(param) > 0 and param.lower() not in ('undefined', 'null', 'none', '')

    if is_valid_param(profession):
        query = query.filter(Build.profession == profession)
    if is_valid_param(role):
        query = query.filter(Build.role == role)
    if is_valid_param(sub_role):
        query = query.filter(Build.sub_roles.contains(sub_role))
    if is_valid_param(search):
        like = f"%{search}%"
        query = query.filter(
            func.lower(Build.title).like(func.lower(like))
            | func.lower(Build.profession).like(func.lower(like))
            | func.lower(Build.elite_spec).like(func.lower(like))
            | func.lower(Build.author).like(func.lower(like))
        )

    # 排序
    if sort_by == "updated":
        query = query.order_by(Build.updated_at.desc())
    elif sort_by == "updated_asc":
        query = query.order_by(Build.updated_at.asc())
    elif sort_by == "profession":
        query = query.order_by(Build.profession.asc(), Build.title.asc())
    elif sort_by == "name":
        query = query.order_by(Build.title.asc())
    else:
        query = query.order_by(Build.updated_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if page_size > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def update_build(db: Session, build: Build, data: dict) -> Build:
    """更新Build"""
    for key, value in data.items():
        if hasattr(build, key) and value is not None:
            setattr(build, key, value)

    # 如果标题变更，重新生成slug
    if "title" in data and data["title"]:
        build.slug = _generate_slug(build.title)

    build.word_count = _calc_word_count(build)
    db.commit()
    db.refresh(build)
    logger.info(f"更新Build: {build.title} (id={build.id})")
    return build


def delete_build(db: Session, build: Build) -> bool:
    """删除Build"""
    db.delete(build)
    db.commit()
    logger.info(f"删除Build: id={build.id}")
    return True
