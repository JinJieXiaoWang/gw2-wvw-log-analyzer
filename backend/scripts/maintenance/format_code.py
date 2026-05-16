#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：代码格式化脚本
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-04
# 说明：使用 black 和 isort 自动格式化代码

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(command)}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    project_root = Path(__file__).parent.parent.parent

    # 检查是否安装了 black 和 isort
    try:
        import black
        import isort

        print(f"Black 版本: {black.__version__}")
        print(f"isort 版本: {isort.__version__}")
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行: pip install black isort")
        return 1

    # 1. 使用 isort 格式化导入
    success = run_command(
        [
            sys.executable,
            "-m",
            "isort",
            "app/",
            "tests/",
            "scripts/",
            "--profile",
            "black",
        ],
        "使用 isort 格式化导入",
    )

    if not success:
        print("警告: isort 执行失败，继续尝试 black...")

    # 2. 使用 black 格式化代码
    success = run_command(
        [sys.executable, "-m", "black", "app/", "tests/", "scripts/", "main.py"],
        "使用 black 格式化代码",
    )

    print(f"\n{'='*60}")
    print("代码格式化完成！")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
