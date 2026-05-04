# 模块功能：字典工具函数（含缓存管理）
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-29
# 依赖说明：SQLAlchemy, typing

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.dictionary import SysDictData, SysDictType
from app.utils.logger import logger

# 全局字典缓存
_dict_cache: Dict[str, List[Dict]] = {}
_dict_label_cache: Dict[str, Dict[str, str]] = {}  # type -> {value: label}
_dict_value_cache: Dict[str, Dict[str, str]] = {}  # type -> {label: value}
_db_session: Optional[Session] = None


def clear_dict_cache() -> None:
    # 功能：清空所有字典缓存
    # 参数：无
    # 返回：无
    global _dict_cache, _dict_label_cache, _dict_value_cache
    _dict_cache = {}
    _dict_label_cache = {}
    _dict_value_cache = {}
    logger.info("字典缓存已清空")


def clear_dict_type_cache(dict_type: str) -> None:
    # 功能：清空指定类型的字典缓存
    # 参数：dict_type - 字典类型
    # 返回：无
    global _dict_cache, _dict_label_cache, _dict_value_cache
    if dict_type in _dict_cache:
        del _dict_cache[dict_type]
    if dict_type in _dict_label_cache:
        del _dict_label_cache[dict_type]
    if dict_type in _dict_value_cache:
        del _dict_value_cache[dict_type]
    logger.info(f"字典类型{dict_type}的缓存已清空")


def set_dict_cache(dict_type: str, dict_data_list: List[Dict]) -> None:
    # 功能：设置字典类型的缓存
    # 参数：dict_type - 字典类型
    #       dict_data_list - 字典数据列表
    # 返回：无
    _dict_cache[dict_type] = dict_data_list

    # 建立标签和值的缓存映射
    if dict_type not in _dict_label_cache:
        _dict_label_cache[dict_type] = {}
    if dict_type not in _dict_value_cache:
        _dict_value_cache[dict_type] = {}

    for data in dict_data_list:
        value = data.get("dict_value", "")
        label = data.get("dict_label", "")
        if value:
            _dict_label_cache[dict_type][value] = label
        if label:
            _dict_value_cache[dict_type][label] = value

    logger.debug(f"字典类型{dict_type}的缓存已更新，共{len(dict_data_list)}项")


def get_dict_cache(dict_type: Optional[str] = None) -> Any:
    # 功能：获取字典类型的缓存
    # 参数：dict_type - 字典类型（可选）
    # 返回：字典数据列表或整个缓存
    if dict_type:
        return _dict_cache.get(dict_type)
    return _dict_cache


def load_dict_from_db(db: Session, dict_type: str) -> List[Dict]:
    # 功能：从数据库加载字典数据
    # 参数：db - 数据库会话
    #       dict_type - 字典类型
    # 返回：字典数据列表
    try:
        query = (
            db.query(SysDictData)
            .filter(SysDictData.dict_type == dict_type, SysDictData.status == 0)
            .order_by(SysDictData.dict_sort)
        )

        dict_data_list = []
        for item in query.all():
            dict_data_list.append(
                {
                    "dict_code": item.dict_code,
                    "dict_sort": item.dict_sort,
                    "dict_label": item.dict_label,
                    "dict_value": item.dict_value,
                    "dict_type": item.dict_type,
                    "data_type": item.data_type,
                    "css_class": item.css_class,
                    "list_class": item.list_class,
                    "is_default": item.is_default,
                    "status": item.status,
                    "remark": item.remark,
                }
            )

        logger.debug(f"从数据库加载字典类型{dict_type}，共{len(dict_data_list)}项")
        return dict_data_list
    except Exception as e:
        logger.error(f"从数据库加载字典类型{dict_type}失败: {str(e)}", exc_info=True)
        return []


def load_all_dictionaries(db: Session) -> None:
    # 功能：加载所有字典数据到缓存
    # 参数：db - 数据库会话
    # 返回：无
    global _db_session
    _db_session = db

    # 获取所有启用的字典类型
    dict_types = (
        db.query(SysDictType)
        .filter(SysDictType.status == 0)
        .order_by(SysDictType.sort_order)
        .all()
    )

    # 加载每个字典类型的数据
    for dict_type in dict_types:
        data = load_dict_from_db(db, dict_type.dict_type)
        set_dict_cache(dict_type.dict_type, data)

    logger.info(f"已加载{len(dict_types)}个字典类型到缓存")


def get_dict_datas(dict_type: str, db: Optional[Session] = None) -> List[Dict]:
    # 功能：获取字典数据（优先从缓存获取）
    # 参数：dict_type - 字典类型
    #       db - 数据库会话（可选）
    # 返回：字典数据列表
    cached_data = get_dict_cache(dict_type)
    if cached_data is not None:
        return cached_data

    # 如果没有缓存，尝试从数据库加载
    session = db or _db_session
    if session:
        dict_data_list = load_dict_from_db(session, dict_type)
        set_dict_cache(dict_type, dict_data_list)
        return dict_data_list
    return []


def get_dict_label(dict_type: str, dict_value: str, separator: str = ",") -> str:
    # 功能：通过字典值获取标签（支持多值）
    # 参数：dict_type - 字典类型
    #       dict_value - 字典值（可以是单个值或多个值用分隔符分开）
    #       separator - 分隔符
    # 返回：字典标签
    try:
        if not dict_value:
            return ""

        # 确保缓存已加载
        if dict_type not in _dict_cache:
            get_dict_datas(dict_type)

        # 处理单个值
        if separator not in dict_value:
            type_labels = _dict_label_cache.get(dict_type, {})
            return type_labels.get(dict_value, dict_value)

        # 处理多个值
        values = dict_value.split(separator)
        labels = []
        type_labels = _dict_label_cache.get(dict_type, {})
        for value in values:
            value = value.strip()
            if value:
                label = type_labels.get(value, value)
                labels.append(label)
        return separator.join(labels)
    except Exception as e:
        logger.error(
            f"获取字典标签失败: type={dict_type}, value={dict_value}, error={str(e)}"
        )
        return dict_value


def get_dict_value(dict_type: str, dict_label: str, separator: str = ",") -> str:
    # 功能：通过字典标签获取值（支持多标签）
    # 参数：dict_type - 字典类型
    #       dict_label - 字典标签
    #       separator - 分隔符
    # 返回：字典值
    try:
        if not dict_label:
            return ""

        # 确保缓存已加载
        if dict_type not in _dict_cache:
            get_dict_datas(dict_type)

        # 处理单个标签
        if separator not in dict_label:
            type_values = _dict_value_cache.get(dict_type, {})
            return type_values.get(dict_label, dict_label)

        # 处理多个标签
        labels = dict_label.split(separator)
        values = []
        type_values = _dict_value_cache.get(dict_type, {})
        for label in labels:
            label = label.strip()
            if label:
                value = type_values.get(label, label)
                values.append(value)
        return separator.join(values)
    except Exception as e:
        logger.error(
            f"获取字典值失败: type={dict_type}, label={dict_label}, error={str(e)}"
        )
        return dict_label


def get_dict_options(dict_type: str) -> List[Dict[str, Any]]:
    # 功能：获取下拉选项格式的字典数据
    # 参数：dict_type - 字典类型
    # 返回：下拉选项列表
    dict_datas = get_dict_datas(dict_type)
    return [
        {
            "value": item.get("dict_value", ""),
            "label": item.get("dict_label", ""),
            "css_class": item.get("css_class", ""),
            "is_default": item.get("is_default", 0),
        }
        for item in dict_datas
    ]


def get_dict_categories(db: Optional[Session] = None) -> List[Dict]:
    # 功能：获取所有字典分类（字典类型列表）
    # 参数：db - 数据库会话（可选）
    # 返回：字典类型列表
    try:
        session = db or _db_session
        if not session:
            return []

        query = (
            session.query(SysDictType)
            .filter(SysDictType.status == 0)
            .order_by(SysDictType.sort_order)
        )

        result = []
        for item in query.all():
            data = {
                "dict_id": item.dict_id,
                "dict_type": item.dict_type,
                "dict_name": item.dict_name,
                "status": item.status,
                "sort_order": item.sort_order,
                "remark": item.remark,
            }
            if hasattr(item, "is_system"):
                data["is_system"] = item.is_system
            result.append(data)
        return result
    except Exception as e:
        logger.error(f"获取字典分类失败: {str(e)}", exc_info=True)
        return []


def get_dict_item_by_value(
    dict_type: str, dict_value: str, db: Optional[Session] = None
) -> Optional[Dict]:
    # 功能：通过值获取字典项详情
    # 参数：dict_type - 字典类型
    #       dict_value - 字典值
    #       db - 数据库会话（可选）
    # 返回：字典项详情或None
    dict_datas = get_dict_datas(dict_type, db)
    for item in dict_datas:
        if item.get("dict_value") == dict_value:
            return item
    return None


def get_dict_item_by_code(
    dict_code: int, db: Optional[Session] = None
) -> Optional[Dict]:
    # 功能：通过编码获取字典项详情
    # 参数：dict_code - 字典项编码
    #       db - 数据库会话（可选）
    # 返回：字典项详情或None
    try:
        session = db or _db_session
        if not session:
            return None

        item = (
            session.query(SysDictData)
            .filter(SysDictData.dict_code == dict_code)
            .first()
        )
        if item:
            return {
                "dict_code": item.dict_code,
                "dict_sort": item.dict_sort,
                "dict_label": item.dict_label,
                "dict_value": item.dict_value,
                "dict_type": item.dict_type,
                "data_type": item.data_type,
                "css_class": item.css_class,
                "list_class": item.list_class,
                "is_default": item.is_default,
                "status": item.status,
                "remark": item.remark,
            }
        return None
    except Exception as e:
        logger.error(f"通过编码获取字典项失败: {str(e)}", exc_info=True)
        return None
