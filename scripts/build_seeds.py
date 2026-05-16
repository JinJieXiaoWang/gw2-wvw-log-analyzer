#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
种子数据构建脚本

功能：将 backend/app/data/seeds/ 下的 JSON 源文件构建为 Python 内嵌模块，
      供 init_all.py 在运行时零依赖加载。

构建产物：backend/app/data/_generated/seed_modules.py

使用方法：
    python scripts/build_seeds.py

CI 集成：
    在合并后自动运行，生成最新的 seed_modules.py
"""

import base64
import gzip
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SEEDS_DIR = PROJECT_ROOT / "backend" / "app" / "data" / "seeds"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "app" / "data" / "_generated"
OUTPUT_FILE = OUTPUT_DIR / "seed_modules.py"


def _compress(data: Any) -> bytes:
    """将 Python 对象压缩为 gzip + base64 字节"""
    json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
    compressed = gzip.compress(json_bytes, compresslevel=9)
    return base64.b64encode(compressed)


def _format_base64(data: bytes, line_width: int = 120) -> str:
    """将 base64 数据格式化为多行字符串"""
    text = data.decode("ascii")
    lines = [text[i : i + line_width] for i in range(0, len(text), line_width)]
    return "\n".join(lines)


def load_seed_files() -> Dict[str, Any]:
    """加载 seeds 目录下的所有 JSON 文件"""
    seeds: Dict[str, Any] = {}

    # 读取 _meta.json
    meta_path = SEEDS_DIR / "_meta.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            seeds["_meta"] = json.load(f)

    # 按版本目录遍历
    for version_dir in sorted(SEEDS_DIR.iterdir()):
        if not version_dir.is_dir() or version_dir.name.startswith("_"):
            continue

        for json_file in sorted(version_dir.glob("*.json")):
            rel_path = f"{version_dir.name}/{json_file.name}"
            with open(json_file, "r", encoding="utf-8") as f:
                seeds[rel_path] = json.load(f)
            print(f"[build_seeds] Loaded {rel_path}")

    return seeds


def generate_module(seeds: Dict[str, Any]) -> str:
    """生成 Python 模块源码"""
    lines = [
        '# -*- coding: utf-8 -*-',
        '"""',
        '种子数据内嵌模块（自动生成）',
        '',
        '警告：请勿手动编辑本文件！',
        '源文件位于：backend/app/data/seeds/',
        '生成脚本：scripts/build_seeds.py',
        '"""',
        '',
        'import base64',
        'import gzip',
        'import json',
        'from typing import Any, Dict',
        '',
        '',
        'def _decompress(data: bytes) -> Any:',
        '    """解压 base64 + gzip 数据"""',
        '    cleaned = b"".join(data.split())',
        '    decoded = base64.b64decode(cleaned)',
        '    decompressed = gzip.decompress(decoded)',
        '    return json.loads(decompressed)',
        '',
    ]

    for name, data in seeds.items():
        var_name = _to_var_name(name)
        compressed = _compress(data)
        formatted = _format_base64(compressed)

        lines.append(f"# {name}")
        lines.append(f'{var_name} = b"""')
        lines.append(formatted)
        lines.append('"""')
        lines.append("")

    # 添加统一加载函数
    lines.extend([
        "_SEED_REGISTRY: Dict[str, bytes] = {",
    ])
    for name in seeds:
        var_name = _to_var_name(name)
        lines.append(f'    "{name}": {var_name},')
    lines.extend([
        "}",
        "",
        "",
        "def load_seed(name: str) -> Any:",
        '    """按名称加载种子数据"""',
        "    raw = _SEED_REGISTRY.get(name)",
        "    if raw is None:",
        '        raise KeyError(f"种子数据不存在: {name}")',
        "    return _decompress(raw)",
        "",
        "",
        "def list_seeds() -> list:",
        '    """返回所有可用的种子数据名称"""',
        "    return list(_SEED_REGISTRY.keys())",
        "",
    ])

    return "\n".join(lines)


def _to_var_name(name: str) -> str:
    """将文件路径转换为合法的 Python 变量名"""
    return "_" + name.replace("/", "_").replace(".", "_").replace("-", "_").upper()


def main() -> int:
    print("=" * 60)
    print("种子数据构建脚本")
    print("=" * 60)

    if not SEEDS_DIR.exists():
        print(f"错误：种子数据目录不存在: {SEEDS_DIR}")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    seeds = load_seed_files()
    if not seeds:
        print("警告：未找到任何种子数据文件")
        return 1

    print(f"\n共加载 {len(seeds)} 个种子数据文件")

    module_source = generate_module(seeds)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(module_source)

    print(f"\n生成成功: {OUTPUT_FILE}")
    print(f"模块大小: {len(module_source):,} 字符")
    return 0


if __name__ == "__main__":
    sys.exit(main())
