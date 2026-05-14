# -*- coding: utf-8 -*-
"""
解析 tests/GW2.txt 文件，提取 Build 配置数据

解析规则：
1. 找到所有 BD Code 行（以 [& 开头）
2. BD Code 之前的最近非空行作为标题
3. BD Code 之后到下一个 BD Code 或分隔线之前的行作为描述
4. 从描述中尝试提取：护甲类型、武器、符文、古物

使用方法：
    python scripts/import/parse_gw2_txt.py

作者: System
创建日期: 2026-05-05
"""

import re
import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

GW2_TXT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "import", "GW2.txt"
)


def extract_weapons(text: str) -> List[Dict[str, Any]]:
    """从描述文本中提取武器配置"""
    weapons = []

    # 策略1: 匹配 "武器: xxx + yyy" 或 "武器：xxx + yyy"
    weapon_prefix = re.search(r'武器[\s:：]+(.+?)(?:符文|古物|宠物|$)', text)
    if weapon_prefix:
        weapon_text = weapon_prefix.group(1)
    else:
        weapon_text = text

    # 匹配 "名称（法印1、法印2）" 模式
    weapon_pattern = re.compile(r'([\u4e00-\u9fa5a-zA-Z]+(?:\d)?)[\s]*(?:（|\()([^）)]+)(?:）|\))')
    matches = list(weapon_pattern.finditer(weapon_text))

    # 如果找到多个武器对，尝试用 + 或 空格 分组
    if len(matches) >= 2:
        # 检查两个匹配之间是否有 + 号
        for i in range(0, len(matches), 2):
            if i + 1 < len(matches):
                between = weapon_text[matches[i].end():matches[i+1].start()]
                if '+' in between or '＋' in between or '、' in between or len(between.strip()) < 5:
                    for j in [i, i+1]:
                        m = matches[j]
                        w_name = m.group(1).strip()
                        sigils_raw = m.group(2)
                        sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
                        weapons.append({
                            "set": len(weapons) + 1,
                            "name": w_name,
                            "sigils": sigils
                        })
                    break
        else:
            # 如果没找到成对的，逐个添加
            for i, m in enumerate(matches):
                w_name = m.group(1).strip()
                sigils_raw = m.group(2)
                sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
                weapons.append({
                    "set": i + 1,
                    "name": w_name,
                    "sigils": sigils
                })
    elif len(matches) == 1:
        m = matches[0]
        w_name = m.group(1).strip()
        sigils_raw = m.group(2)
        sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
        weapons.append({
            "set": 1,
            "name": w_name,
            "sigils": sigils
        })

    return weapons


def parse_gw2_txt(path: str) -> List[Dict[str, Any]]:
    """解析 GW2.txt 文件，返回配置列表"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    builds = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行和分隔线
        if not line or line.startswith("=") or line.startswith("-"):
            i += 1
            continue

        # 检查是否是 BD Code 行
        bd_match = re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', line)
        if bd_match:
            bd_code = bd_match.group(1)

            # 向前找标题（跳过空行和分隔线）
            title = None
            j = i - 1
            while j >= 0:
                prev = lines[j].strip()
                if prev and not prev.startswith("=") and not prev.startswith("-"):
                    if not re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', prev):
                        title = prev
                        break
                j -= 1

            if not title:
                title = "未命名配置"
            # 清理标题中的冒号
            title = title.rstrip("：:").strip()

            # 向后找描述（到下一个 BD Code、分隔线、或空块结束）
            desc_lines = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line:
                    j += 1
                    continue
                if next_line.startswith("=") or next_line.startswith("-"):
                    break
                if re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', next_line):
                    break
                # 跳过 "循环：" 及其后面的多行循环描述
                if next_line.startswith("循环"):
                    j += 1
                    while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("="):
                        j += 1
                    break
                desc_lines.append(next_line)
                j += 1

            description = " ".join(desc_lines)

            build = {
                "title": title,
                "bd_code": bd_code,
                "description": description,
                "armor_type": "",
                "weapons": [],
                "rune": "",
                "relic": "",
                "food": "",
                "infusion": "",
            }

            # 提取护甲类型
            armor_patterns = [
                r'([^（\s]*?套)',
                r'(ȫ[\u4e00-\u9fa5]+)',
                r'([^\s]*混搭)',
                r'([^\s]*者套)',
            ]
            for pattern in armor_patterns:
                armor_match = re.search(pattern, description)
                if armor_match:
                    build["armor_type"] = armor_match.group(1).strip()
                    break

            # 提取武器
            build["weapons"] = extract_weapons(description)

            # 提取符文
            rune_match = re.search(r'(?:[^\u4e00-\u9fa5]|^)([\u4e00-\u9fa5]+符文)', description)
            if rune_match:
                build["rune"] = rune_match.group(1).strip()

            # 提取古物
            relic_match = re.search(r'古物[：:\s]+([\u4e00-\u9fa5]+(?:[/|\\][\u4e00-\u9fa5]+)?)', description)
            if relic_match:
                build["relic"] = relic_match.group(1).strip()

            # 提取食物（如果有）
            food_match = re.search(r'食物[：:\s]+([\u4e00-\u9fa5]+)', description)
            if food_match:
                build["food"] = food_match.group(1).strip()

            builds.append(build)
            i = j
        else:
            i += 1

    return builds


def main():
    if not os.path.exists(GW2_TXT_PATH):
        print(f"错误: 找不到文件 {GW2_TXT_PATH}")
        sys.exit(1)

    builds = parse_gw2_txt(GW2_TXT_PATH)
    print(f"共解析到 {len(builds)} 个配置\n")

    for idx, b in enumerate(builds, 1):
        print(f"[{idx}] {b['title']}")
        print(f"    BD: {b['bd_code']}")
        print(f"    护甲: {b['armor_type']}")
        print(f"    武器: {b['weapons']}")
        print(f"    符文: {b['rune']}")
        print(f"    古物: {b['relic']}")
        print()


if __name__ == "__main__":
    main()
