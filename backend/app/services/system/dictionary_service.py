# -*- coding: utf-8 -*-
# 模块功能：字典服务层
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-29
# 依赖说明：SQLAlchemy, typing

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.dictionary import SysDictData, SysDictType
from app.utils.dict_utils import (
    clear_dict_cache,
    clear_dict_type_cache,
    get_dict_categories,
    get_dict_datas,
    get_dict_item_by_code,
    get_dict_item_by_value,
    get_dict_label,
    get_dict_options,
    get_dict_value,
    load_all_dictionaries,
    set_dict_cache,
)
from app.utils.logger import logger


class DictionaryService:
    # 功能：字典服务类
    # 参数：db - 数据库会话
    # 返回：无

    def __init__(self, db: Session):
        self.db = db

    def _dict_type_to_dict(self, dict_type: SysDictType) -> Dict:
        # 功能：将 SysDictType 模型对象转为字典
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

    def _dict_data_to_dict(self, dict_data: SysDictData) -> Dict:
        # 功能：将 SysDictData 模型对象转为字典
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

    def get_dict_label(
        self, dict_type: str, dict_value: str, separator: str = ","
    ) -> str:
        # 功能：通过值获取标签
        # 参数：dict_type - 字典类型
        #       dict_value - 字典值
        #       separator - 分隔符
        # 返回：字典标签
        return get_dict_label(dict_type, dict_value, separator)

    def get_dict_value(
        self, dict_type: str, dict_label: str, separator: str = ","
    ) -> str:
        # 功能：通过标签获取值
        # 参数：dict_type - 字典类型
        #       dict_label - 字典标签
        #       separator - 分隔符
        # 返回：字典值
        return get_dict_value(dict_type, dict_label, separator)

    def get_dict_datas(self, dict_type: str) -> List[Dict]:
        # 功能：获取字典数据列表
        # 参数：dict_type - 字典类型
        # 返回：字典数据列表
        return get_dict_datas(dict_type, self.db)

    def get_dict_options(self, dict_type: str) -> List[Dict]:
        # 功能：获取下拉选项格式的字典数据
        # 参数：dict_type - 字典类型
        # 返回：下拉选项列表
        dict_datas = get_dict_datas(dict_type, self.db)
        return [
            {
                "value": item.get("dict_value", ""),
                "label": item.get("dict_label", ""),
                "css_class": item.get("css_class", ""),
                "is_default": item.get("is_default", 0),
            }
            for item in dict_datas
        ]

    def get_dict_categories(self) -> List[Dict]:
        # 功能：获取所有字典分类
        # 参数：无
        # 返回：字典分类列表
        return get_dict_categories(self.db)

    def get_dict_item_by_code(self, dict_code: int) -> Optional[Dict]:
        # 功能：通过编码获取字典项详情
        # 参数：dict_code - 字典编码
        # 返回：字典项详情或None
        return get_dict_item_by_code(dict_code, self.db)

    def get_dict_item_by_value(self, dict_type: str, dict_value: str) -> Optional[Dict]:
        # 功能：通过值获取字典项详情
        # 参数：dict_type - 字典类型
        #       dict_value - 字典值
        # 返回：字典项详情或None
        return get_dict_item_by_value(dict_type, dict_value, self.db)

    def create_dict_group(self, data: Dict) -> Dict:
        # 功能：创建字典分组（字典类型）
        # 参数：data - 字典分组数据
        # 返回：创建后的字典分组数据
        try:
            existing = (
                self.db.query(SysDictType)
                .filter(SysDictType.dict_type == data.get("dict_type"))
                .first()
            )

            if existing:
                raise ValueError(f"字典类型{data.get('dict_type')}已存在")

            dict_type = SysDictType(
                dict_type=data.get("dict_type"),
                dict_name=data.get("dict_name"),
                status=data.get("status", 0),
                sort_order=data.get("sort_order", 0),
                remark=data.get("remark"),
            )

            self.db.add(dict_type)
            self.db.commit()
            self.db.refresh(dict_type)

            logger.info(f"成功创建字典类型: {data.get('dict_type')}")

            return {
                "dict_id": dict_type.dict_id,
                "dict_type": dict_type.dict_type,
                "dict_name": dict_type.dict_name,
                "status": dict_type.status,
                "sort_order": dict_type.sort_order,
                "remark": dict_type.remark,
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建字典类型失败: {str(e)}", exc_info=True)
            raise

    def update_dict_group(self, dict_id: int, data: Dict) -> Dict:
        # 功能：更新字典分组
        # 参数：dict_id - 字典分组ID
        #       data - 更新数据
        # 返回：更新后的字典分组数据
        try:
            dict_type = (
                self.db.query(SysDictType)
                .filter(SysDictType.dict_id == dict_id)
                .first()
            )

            if not dict_type:
                raise ValueError(f"字典类型ID{dict_id}不存在")

            if "dict_name" in data:
                dict_type.dict_name = data["dict_name"]
            if "status" in data:
                dict_type.status = data["status"]
            if "sort_order" in data:
                dict_type.sort_order = data["sort_order"]
            if "remark" in data:
                dict_type.remark = data["remark"]

            self.db.commit()
            self.db.refresh(dict_type)

            # 清除相关缓存
            if dict_type.dict_type:
                clear_dict_type_cache(dict_type.dict_type)

            logger.info(f"成功更新字典类型: {dict_type.dict_type}")

            return {
                "dict_id": dict_type.dict_id,
                "dict_type": dict_type.dict_type,
                "dict_name": dict_type.dict_name,
                "status": dict_type.status,
                "sort_order": dict_type.sort_order,
                "remark": dict_type.remark,
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新字典类型失败: {str(e)}", exc_info=True)
            raise

    def delete_dict_group(self, dict_id: int) -> bool:
        # 功能：删除字典分组
        # 参数：dict_id - 字典分组ID
        # 返回：是否删除成功
        # 异常：ValueError - 预置字典类型不允许删除
        try:
            dict_type = (
                self.db.query(SysDictType)
                .filter(SysDictType.dict_id == dict_id)
                .first()
            )

            if not dict_type:
                raise ValueError(f"字典类型ID{dict_id}不存在")

            # 检查是否为系统预置类型
            if hasattr(dict_type, "is_system") and dict_type.is_system == 1:
                raise ValueError("预置字典类型不允许删除")

            type_name = dict_type.dict_type

            # 删除相关字典数据
            self.db.query(SysDictData).filter(
                SysDictData.dict_type == type_name
            ).delete()

            # 删除字典类型
            self.db.delete(dict_type)
            self.db.commit()

            # 清除相关缓存
            clear_dict_type_cache(type_name)

            logger.info(f"成功删除字典类型: {type_name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除字典类型失败: {str(e)}", exc_info=True)
            raise

    def create_dict_item(self, data: Dict) -> Dict:
        # 功能：创建字典项
        # 参数：data - 字典项数据
        # 返回：创建后的字典项数据
        try:
            existing = (
                self.db.query(SysDictData)
                .filter(
                    SysDictData.dict_type == data.get("dict_type"),
                    SysDictData.dict_value == data.get("dict_value"),
                )
                .first()
            )

            if existing:
                raise ValueError(
                    f"字典项{data.get('dict_type')}/{data.get('dict_value')}已存在"
                )

            dict_data = SysDictData(
                dict_type=data.get("dict_type"),
                dict_label=data.get("dict_label"),
                dict_value=data.get("dict_value"),
                dict_sort=data.get("dict_sort", 0),
                data_type=data.get("data_type"),
                css_class=data.get("css_class"),
                list_class=data.get("list_class"),
                is_default=data.get("is_default", 0),
                status=data.get("status", 0),
                remark=data.get("remark"),
            )

            self.db.add(dict_data)
            self.db.commit()
            self.db.refresh(dict_data)

            # 清除相关缓存
            if dict_data.dict_type:
                clear_dict_type_cache(dict_data.dict_type)

            logger.info(
                f"成功创建字典项: {data.get('dict_type')}/{data.get('dict_value')}"
            )

            return {
                "dict_code": dict_data.dict_code,
                "dict_type": dict_data.dict_type,
                "dict_label": dict_data.dict_label,
                "dict_value": dict_data.dict_value,
                "dict_sort": dict_data.dict_sort,
                "data_type": dict_data.data_type,
                "css_class": dict_data.css_class,
                "list_class": dict_data.list_class,
                "is_default": dict_data.is_default,
                "status": dict_data.status,
                "remark": dict_data.remark,
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建字典项失败: {str(e)}", exc_info=True)
            raise

    def update_dict_item(self, dict_code: int, data: Dict) -> Dict:
        # 功能：更新字典项
        # 参数：dict_code - 字典项编码
        #       data - 更新数据
        # 返回：更新后的字典项数据
        try:
            dict_item = (
                self.db.query(SysDictData)
                .filter(SysDictData.dict_code == dict_code)
                .first()
            )

            if not dict_item:
                raise ValueError(f"字典项编码{dict_code}不存在")

            dict_type = dict_item.dict_type

            if "dict_label" in data:
                dict_item.dict_label = data["dict_label"]
            if "dict_value" in data:
                dict_item.dict_value = data["dict_value"]
            if "dict_sort" in data:
                dict_item.dict_sort = data["dict_sort"]
            if "data_type" in data:
                dict_item.data_type = data["data_type"]
            if "css_class" in data:
                dict_item.css_class = data["css_class"]
            if "list_class" in data:
                dict_item.list_class = data["list_class"]
            if "is_default" in data:
                dict_item.is_default = data["is_default"]
            if "status" in data:
                dict_item.status = data["status"]
            if "remark" in data:
                dict_item.remark = data["remark"]

            self.db.commit()
            self.db.refresh(dict_item)

            # 清除相关缓存
            if dict_type:
                clear_dict_type_cache(dict_type)

            logger.info(f"成功更新字典项: {dict_type}/{dict_item.dict_value}")

            return {
                "dict_code": dict_item.dict_code,
                "dict_type": dict_item.dict_type,
                "dict_label": dict_item.dict_label,
                "dict_value": dict_item.dict_value,
                "dict_sort": dict_item.dict_sort,
                "data_type": dict_item.data_type,
                "css_class": dict_item.css_class,
                "list_class": dict_item.list_class,
                "is_default": dict_item.is_default,
                "status": dict_item.status,
                "remark": dict_item.remark,
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新字典项失败: {str(e)}", exc_info=True)
            raise

    def delete_dict_item(self, dict_code: int) -> bool:
        # 功能：删除字典项
        # 参数：dict_code - 字典项编码
        # 返回：是否删除成功
        try:
            dict_item = (
                self.db.query(SysDictData)
                .filter(SysDictData.dict_code == dict_code)
                .first()
            )

            if not dict_item:
                raise ValueError(f"字典项编码{dict_code}不存在")

            dict_type = dict_item.dict_type

            self.db.delete(dict_item)
            self.db.commit()

            # 清除相关缓存
            if dict_type:
                clear_dict_type_cache(dict_type)

            logger.info(f"成功删除字典项: {dict_type}/{dict_item.dict_value}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除字典项失败: {str(e)}", exc_info=True)
            raise

    def clear_dict_cache(self) -> None:
        # 功能：清除所有字典缓存
        # 参数：无
        # 返回：无
        clear_dict_cache()

    def get_all_dict_types(self) -> List[Dict]:
        # 功能：获取所有启用的字典类型
        # 参数：无
        # 返回：字典类型列表
        items = (
            self.db.query(SysDictType)
            .filter(SysDictType.status == 0)
            .order_by(SysDictType.sort_order)
            .all()
        )
        return [self._dict_type_to_dict(item) for item in items]

    def get_dict_types(
        self,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        # 功能：获取字典类型列表（分页）
        # 参数：status - 状态筛选
        #       keyword - 关键词筛选
        #       page - 页码
        #       page_size - 每页数量
        # 返回：分页结果
        query = self.db.query(SysDictType)
        if status is not None:
            query = query.filter(SysDictType.status == status)
        if keyword:
            query = query.filter(
                (SysDictType.dict_type.like(f"%{keyword}%"))
                | (SysDictType.dict_name.like(f"%{keyword}%"))
            )
        total = query.count()
        skip = (page - 1) * page_size
        items = (
            query.order_by(SysDictType.sort_order).offset(skip).limit(page_size).all()
        )
        return {
            "items": [self._dict_type_to_dict(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    def get_dict_type_by_id(self, dict_id: int) -> Optional[SysDictType]:
        # 功能：通过ID获取字典类型
        # 参数：dict_id - 字典类型ID
        # 返回：字典类型或None
        return self.db.query(SysDictType).filter(SysDictType.dict_id == dict_id).first()

    def get_dict_type_by_code(self, dict_type: str) -> Optional[SysDictType]:
        # 功能：通过编码获取字典类型
        # 参数：dict_type - 字典类型编码
        # 返回：字典类型或None
        return (
            self.db.query(SysDictType)
            .filter(SysDictType.dict_type == dict_type)
            .first()
        )

    def create_dict_type(
        self,
        dict_type: str,
        dict_name: str,
        remark: Optional[str] = None,
        sort_order: int = 0,
        status: int = 0,
    ) -> SysDictType:
        # 功能：创建字典类型
        # 参数：dict_type - 字典类型编码
        #       dict_name - 字典类型名称
        #       remark - 备注
        #       sort_order - 排序
        #       status - 状态
        # 返回：创建的字典类型
        existing = self.get_dict_type_by_code(dict_type)
        if existing:
            raise ValueError(f"字典类型{dict_type}已存在")

        dict_type_obj = SysDictType(
            dict_type=dict_type,
            dict_name=dict_name,
            status=status,
            sort_order=sort_order,
            remark=remark,
            is_system=0,
        )
        self.db.add(dict_type_obj)
        self.db.commit()
        self.db.refresh(dict_type_obj)
        return dict_type_obj

    def update_dict_type(
        self,
        dict_id: int,
        dict_name: Optional[str] = None,
        remark: Optional[str] = None,
        sort_order: Optional[int] = None,
        status: Optional[int] = None,
    ) -> Optional[SysDictType]:
        # 功能：更新字典类型
        # 参数：dict_id - 字典类型ID
        #       其他可选参数
        # 返回：更新后的字典类型或None
        dict_type_obj = self.get_dict_type_by_id(dict_id)
        if not dict_type_obj:
            return None

        if dict_name is not None:
            dict_type_obj.dict_name = dict_name
        if remark is not None:
            dict_type_obj.remark = remark
        if sort_order is not None:
            dict_type_obj.sort_order = sort_order
        if status is not None:
            dict_type_obj.status = status

        self.db.commit()
        self.db.refresh(dict_type_obj)
        clear_dict_type_cache(dict_type_obj.dict_type)
        return dict_type_obj

    def delete_dict_type(self, dict_id: int) -> bool:
        # 功能：删除字典类型
        # 参数：dict_id - 字典类型ID
        # 返回：是否删除成功
        # 异常：ValueError - 预置字典类型不允许删除
        dict_type_obj = self.get_dict_type_by_id(dict_id)
        if not dict_type_obj:
            return False

        # 检查是否为系统预置类型
        if hasattr(dict_type_obj, "is_system") and dict_type_obj.is_system == 1:
            raise ValueError("预置字典类型不允许删除")

        type_name = dict_type_obj.dict_type
        self.db.query(SysDictData).filter(SysDictData.dict_type == type_name).delete()
        self.db.delete(dict_type_obj)
        self.db.commit()
        clear_dict_type_cache(type_name)
        return True

    def get_dict_data_by_type(
        self,
        dict_type: str,
        status: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        # 功能：获取字典数据列表（分页）
        # 参数：dict_type - 字典类型
        #       status - 状态筛选
        #       page - 页码
        #       page_size - 每页数量
        # 返回：分页结果
        query = self.db.query(SysDictData).filter(SysDictData.dict_type == dict_type)
        if status is not None:
            query = query.filter(SysDictData.status == status)
        total = query.count()
        skip = (page - 1) * page_size
        items = (
            query.order_by(SysDictData.dict_sort).offset(skip).limit(page_size).all()
        )
        return {
            "items": [self._dict_data_to_dict(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    def get_dict_data_by_id(self, dict_code: int) -> Optional[SysDictData]:
        # 功能：通过编码获取字典数据
        # 参数：dict_code - 字典数据编码
        # 返回：字典数据或None
        return (
            self.db.query(SysDictData)
            .filter(SysDictData.dict_code == dict_code)
            .first()
        )

    def create_dict_data(
        self,
        dict_type: str,
        dict_label: str,
        dict_value: str,
        dict_sort: int = 0,
        data_type: Optional[str] = None,
        css_class: Optional[str] = None,
        list_class: Optional[str] = None,
        is_default: int = 0,
        status: int = 0,
        remark: Optional[str] = None,
    ) -> SysDictData:
        # 功能：创建字典数据
        # 参数：所有字典数据字段
        # 返回：创建的字典数据
        existing = (
            self.db.query(SysDictData)
            .filter(
                SysDictData.dict_type == dict_type, SysDictData.dict_value == dict_value
            )
            .first()
        )
        if existing:
            raise ValueError(f"字典项{dict_type}/{dict_value}已存在")

        dict_data = SysDictData(
            dict_type=dict_type,
            dict_label=dict_label,
            dict_value=dict_value,
            dict_sort=dict_sort,
            data_type=data_type,
            css_class=css_class,
            list_class=list_class,
            is_default=is_default,
            status=status,
            remark=remark,
        )
        self.db.add(dict_data)
        self.db.commit()
        self.db.refresh(dict_data)
        clear_dict_type_cache(dict_type)
        return dict_data

    def update_dict_data(
        self,
        dict_code: int,
        dict_label: Optional[str] = None,
        dict_value: Optional[str] = None,
        dict_sort: Optional[int] = None,
        data_type: Optional[str] = None,
        css_class: Optional[str] = None,
        list_class: Optional[str] = None,
        is_default: Optional[int] = None,
        status: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> Optional[SysDictData]:
        # 功能：更新字典数据
        # 参数：dict_code - 字典数据编码，其他可选参数
        # 返回：更新后的字典数据或None
        dict_data = self.get_dict_data_by_id(dict_code)
        if not dict_data:
            return None

        dict_type = dict_data.dict_type

        if dict_label is not None:
            dict_data.dict_label = dict_label
        if dict_value is not None:
            dict_data.dict_value = dict_value
        if dict_sort is not None:
            dict_data.dict_sort = dict_sort
        if data_type is not None:
            dict_data.data_type = data_type
        if css_class is not None:
            dict_data.css_class = css_class
        if list_class is not None:
            dict_data.list_class = list_class
        if is_default is not None:
            dict_data.is_default = is_default
        if status is not None:
            dict_data.status = status
        if remark is not None:
            dict_data.remark = remark

        self.db.commit()
        self.db.refresh(dict_data)
        clear_dict_type_cache(dict_type)
        return dict_data

    def delete_dict_data(self, dict_code: int) -> bool:
        # 功能：删除字典数据
        # 参数：dict_code - 字典数据编码
        # 返回：是否删除成功
        dict_data = self.get_dict_data_by_id(dict_code)
        if not dict_data:
            return False

        dict_type = dict_data.dict_type
        self.db.delete(dict_data)
        self.db.commit()
        clear_dict_type_cache(dict_type)
        return True
