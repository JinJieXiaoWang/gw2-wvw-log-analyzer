# -*- coding: utf-8 -*-
"""字典服务辅助函数"""

from typing import Any, Dict, Optional

from app.models.game.dictionary import SysDictData, SysDictType


def dict_type_to_dict(dict_type: SysDictType) -> Dict[str, Any]:
    result = {
        "dict_id": dict_type.dict_id,
        "dict_type": dict_type.dict_type,
        "dict_name": dict_type.dict_name,
        "status": dict_type.status,
        "sort_order": dict_type.sort_order,
        "remark": dict_type.remark,
    }
    if hasattr(dict_type, "is_system"):
        result["is_system"] = dict_type.is_system
    return result


def dict_data_to_dict(dict_data: SysDictData) -> Dict[str, Any]:
    return {
        "dict_code": dict_data.dict_code,
        "dict_sort": dict_data.dict_sort,
        "dict_label": dict_data.dict_label,
        "dict_value": dict_data.dict_value,
        "dict_type": dict_data.dict_type,
        "data_type": dict_data.data_type,
        "css_class": dict_data.css_class,
        "list_class": dict_data.list_class,
        "is_default": dict_data.is_default,
        "status": dict_data.status,
        "remark": dict_data.remark,
    }
