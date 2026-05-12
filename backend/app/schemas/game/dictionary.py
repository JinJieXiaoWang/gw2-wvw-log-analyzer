# 模块功能：字典相关数据验证模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-29
# 依赖说明：pydantic v2

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DictTypeBase(BaseModel):
    # 功能：字典类型基础模型
    model_config = ConfigDict(from_attributes=True)

    dict_type: str = Field(..., description="字典类型编码")
    dict_name: str = Field(..., description="字典类型名称")
    status: int = Field(0, description="状态：0-启用，1-禁用")
    sort_order: int = Field(0, description="排序顺序")
    remark: Optional[str] = Field(None, description="备注说明")


class DictTypeCreate(DictTypeBase):
    # 功能：字典类型创建模型
    pass


class DictTypeUpdate(BaseModel):
    # 功能：字典类型更新模型
    model_config = ConfigDict(from_attributes=True)

    dict_name: Optional[str] = Field(None, description="字典类型名称")
    status: Optional[int] = Field(None, description="状态：0-启用，1-禁用")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    remark: Optional[str] = Field(None, description="备注说明")


class DictTypeResponse(DictTypeBase):
    # 功能：字典类型响应模型
    dict_id: int = Field(..., description="字典类型ID")
    is_system: int = Field(0, description="是否系统预置：0-否，1-是")


class DictDataBase(BaseModel):
    # 功能：字典项基础模型
    model_config = ConfigDict(from_attributes=True)

    dict_type: str = Field(..., description="所属字典类型")
    dict_label: str = Field(..., description="字典标签（显示值）")
    dict_value: str = Field(..., description="字典值（存储值）")
    dict_sort: int = Field(0, description="排序顺序")
    data_type: Optional[str] = Field(None, description="数据类型")
    css_class: Optional[str] = Field(None, description="CSS样式（颜色）")
    list_class: Optional[str] = Field(None, description="列表样式")
    is_default: int = Field(0, description="是否默认值：0-否，1-是")
    status: int = Field(0, description="状态：0-启用，1-禁用")
    remark: Optional[str] = Field(None, description="备注说明")


class DictDataCreate(DictDataBase):
    # 功能：字典项创建模型
    pass


class DictDataUpdate(BaseModel):
    # 功能：字典项更新模型
    model_config = ConfigDict(from_attributes=True)

    dict_label: Optional[str] = Field(None, description="字典标签")
    dict_value: Optional[str] = Field(None, description="字典值")
    dict_sort: Optional[int] = Field(None, description="排序顺序")
    data_type: Optional[str] = Field(None, description="数据类型")
    css_class: Optional[str] = Field(None, description="CSS样式")
    list_class: Optional[str] = Field(None, description="列表样式")
    is_default: Optional[int] = Field(None, description="是否默认")
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注说明")


class DictDataResponse(DictDataBase):
    # 功能：字典项响应模型
    dict_code: int = Field(..., description="字典项编号")


class DictOption(BaseModel):
    # 功能：字典下拉选项模型
    model_config = ConfigDict(from_attributes=True)

    value: Any = Field(..., description="字典值")
    label: str = Field(..., description="字典标签")
    css_class: Optional[str] = Field(None, description="CSS样式（颜色）")
    is_default: int = Field(0, description="是否默认")
