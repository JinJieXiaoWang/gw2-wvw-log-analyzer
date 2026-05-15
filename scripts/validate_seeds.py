#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
种子数据验证脚本

功能：
  1. 验证所有 JSON 种子文件的格式正确性
  2. 验证 _meta 字段完整性
  3. 验证前后端字典常量一致性（dict_values.py vs dictValues.ts）
  4. 验证引用完整性（如 dict_data 的 dict_type 必须存在于 dict_type 中）

使用方法：
    python scripts/validate_seeds.py

退出码：
    0 - 全部通过
    1 - 存在错误
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
SEEDS_DIR = PROJECT_ROOT / "backend" / "app" / "data" / "seeds"
BACKEND_CONSTANTS = PROJECT_ROOT / "backend" / "app" / "constants" / "dict_values.py"
FRONTEND_CONSTANTS = PROJECT_ROOT / "frontend" / "src" / "constants" / "dictValues.ts"


class Validator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.seeds: Dict[str, Any] = {}

    def error(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"  [ERROR] {msg}")

    def warning(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"  [WARN] {msg}")

    def load_all_seeds(self) -> None:
        """加载所有种子数据文件"""
        print("[1/5] 加载种子数据文件...")

        meta_path = SEEDS_DIR / "_meta.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                self.seeds["_meta"] = json.load(f)
        else:
            self.error("_meta.json 不存在")
            return

        for version_dir in sorted(SEEDS_DIR.iterdir()):
            if not version_dir.is_dir() or version_dir.name.startswith("_"):
                continue
            for json_file in sorted(version_dir.glob("*.json")):
                rel_path = f"{version_dir.name}/{json_file.name}"
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        self.seeds[rel_path] = json.load(f)
                except json.JSONDecodeError as e:
                    self.error(f"{rel_path}: JSON 解析失败 - {e}")

        print(f"  共加载 {len(self.seeds)} 个文件")

    def validate_meta(self) -> None:
        """验证 _meta 字段完整性"""
        print("\n[2/5] 验证 _meta 字段...")

        required_meta_fields = {"version", "target_table", "min_app_version"}

        for name, data in self.seeds.items():
            if name == "_meta":
                continue

            if "_meta" not in data:
                self.error(f"{name}: 缺少 _meta 字段")
                continue

            meta = data["_meta"]
            missing = required_meta_fields - set(meta.keys())
            if missing:
                self.error(f"{name}: _meta 缺少字段 {missing}")

            if "data" not in data:
                self.error(f"{name}: 缺少 data 字段")

        print(f"  验证完成，发现 {len([e for e in self.errors if '_meta' in e or 'data' in e])} 个问题")

    def validate_references(self) -> None:
        """验证引用完整性"""
        print("\n[3/5] 验证引用完整性...")

        # 收集所有 dict_type
        dict_types: Set[str] = set()
        dict_data_file = None

        for name, data in self.seeds.items():
            meta = data.get("_meta", {})
            if meta.get("target_table") == "sys_dict_type":
                for item in data.get("data", []):
                    dict_types.add(item.get("dict_type"))

            if meta.get("target_table") == "sys_dict_data":
                dict_data_file = name

        if not dict_types:
            self.warning("未找到 sys_dict_type 数据，跳过引用检查")
            return

        if dict_data_file:
            data = self.seeds[dict_data_file].get("data", {})
            for dict_type, items in data.items():
                if dict_type not in dict_types:
                    self.error(
                        f"{dict_data_file}: dict_type '{dict_type}' 在 sys_dict_type 中不存在"
                    )

        print(f"  共验证 {len(dict_types)} 个字典类型")

    def validate_backend_frontend_sync(self) -> None:
        """验证前后端字典常量一致性"""
        print("\n[4/5] 验证前后端常量一致性...")

        if not BACKEND_CONSTANTS.exists():
            self.warning(f"后端常量文件不存在: {BACKEND_CONSTANTS}")
            return
        if not FRONTEND_CONSTANTS.exists():
            self.warning(f"前端常量文件不存在: {FRONTEND_CONSTANTS}")
            return

        # 提取后端 ParseStatus 值
        backend_status = self._extract_python_enum(BACKEND_CONSTANTS, "ParseStatus")
        frontend_status = self._extract_ts_const(FRONTEND_CONSTANTS, "ParseStatus")

        if backend_status and frontend_status:
            backend_vals = set(backend_status.values())
            frontend_vals = set(frontend_status.values())
            if backend_vals != frontend_vals:
                self.error(
                    f"ParseStatus 不一致: 后端={backend_vals}, 前端={frontend_vals}"
                )
            else:
                print(f"  ParseStatus: OK ({len(backend_vals)} 个值)")

        # 提取 RoleType
        backend_roles = self._extract_python_enum(BACKEND_CONSTANTS, "RoleType")
        frontend_roles = self._extract_ts_const(FRONTEND_CONSTANTS, "RoleType")

        if backend_roles and frontend_roles:
            backend_vals = set(backend_roles.values())
            frontend_vals = set(frontend_roles.values())
            if backend_vals != frontend_vals:
                self.error(
                    f"RoleType 不一致: 后端={backend_vals}, 前端={frontend_vals}"
                )
            else:
                print(f"  RoleType: OK ({len(backend_vals)} 个值)")

        # 验证 dict_values 与种子数据的一致性
        self._validate_seed_vs_constants()

    def _extract_python_enum(self, path: Path, enum_name: str) -> Dict[str, str]:
        """从 Python 文件中提取 Enum 值"""
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        # 匹配 class EnumName(str, Enum): 之后的类体（跳过 docstring）
        pattern = rf"class {enum_name}\([^)]+\):"
        match = re.search(pattern, source)
        if not match:
            return {}

        # 从类定义开始位置提取后续内容
        start = match.end()
        # 找到下一个同缩进级别的类或函数定义
        next_def = re.search(r"\n(class |def )", source[start:])
        body = source[start:start + next_def.start()] if next_def else source[start:]

        result = {}
        for line in body.split("\n"):
            m = re.match(r"\s+([A-Z_]+)\s*=\s*['\"](.+?)['\"]", line)
            if m:
                result[m.group(1)] = m.group(2)
        return result

    def _extract_ts_const(self, path: Path, const_name: str) -> Dict[str, str]:
        """从 TypeScript 文件中提取 as const 对象值"""
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        # 匹配 export const ConstName = { ... } as const
        pattern = rf"export const {const_name}\s*=\s*\{{(.*?)\}}\s*as\s+const"
        match = re.search(pattern, source, re.DOTALL)
        if not match:
            return {}

        body = match.group(1)
        result = {}
        for line in body.split("\n"):
            m = re.match(r"\s+([A-Z_]+):\s*['\"](.+?)['\"]", line)
            if m:
                result[m.group(1)] = m.group(2)
        return result

    def _validate_seed_vs_constants(self) -> None:
        """验证种子数据中的字典值与代码常量一致"""
        # 收集种子数据中的 parse_status 值
        parse_status_values: Set[str] = set()
        for name, data in self.seeds.items():
            meta = data.get("_meta", {})
            if meta.get("target_table") == "sys_dict_data":
                seed_data = data.get("data", {})
                for dt, items in seed_data.items():
                    if dt == "parse_status":
                        for item in items:
                            if isinstance(item, (list, tuple)) and len(item) > 0:
                                parse_status_values.add(item[0])

        if parse_status_values:
            backend_status = self._extract_python_enum(BACKEND_CONSTANTS, "ParseStatus")
            backend_vals = set(backend_status.values()) if backend_status else set()
            missing = parse_status_values - backend_vals
            if missing:
                self.warning(
                    f"种子数据中的 parse_status 值 {missing} 未在 ParseStatus Enum 中定义"
                )
            else:
                print(f"  parse_status 种子 vs 常量: OK")

    def validate_json_schemas(self) -> None:
        """验证 JSON 文件是否符合 Schema（如存在）"""
        print("\n[5/5] 验证 JSON Schema...")

        schema_dir = SEEDS_DIR / "_schemas"
        if not schema_dir.exists():
            print("  Schema 目录不存在，跳过")
            return

        schema_files = list(schema_dir.glob("*.schema.json"))
        if not schema_files:
            print("  未找到 Schema 文件，跳过")
            return

        try:
            import jsonschema
        except ImportError:
            self.warning("jsonschema 未安装，跳过 Schema 验证")
            return

        for schema_file in schema_files:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)

            # 查找对应的数据文件
            data_name = schema_file.name.replace(".schema.json", ".json")
            # TODO: 匹配逻辑
            print(f"  Schema: {schema_file.name} (验证逻辑待完善)")

    def run(self) -> int:
        print("=" * 60)
        print("种子数据验证脚本")
        print("=" * 60)

        self.load_all_seeds()
        self.validate_meta()
        self.validate_references()
        self.validate_backend_frontend_sync()
        self.validate_json_schemas()

        print("\n" + "=" * 60)
        print("验证结果汇总")
        print("=" * 60)
        print(f"错误: {len(self.errors)} 个")
        print(f"警告: {len(self.warnings)} 个")

        if self.errors:
            print("\n详细错误:")
            for e in self.errors:
                print(f"  - {e}")
            return 1

        print("\n✅ 全部通过！")
        return 0


def main() -> int:
    validator = Validator()
    return validator.run()


if __name__ == "__main__":
    sys.exit(main())
