# -*- coding: utf-8 -*-
"""
数据迁移脚本：从 tests/GW2.txt 导入配置数据到数据库

功能说明：
1. 清空现有 builds 表数据
2. 解析 GW2.txt 提取标题、BD Code、配装描述
3. 对每个 BD Code 调用后端解析 API 获取职业、特性线等结构化数据
4. 组合数据后写入数据库（author 统一为空字符串）
5. 生成导入报告

使用方法：
    cd D:\Code\backend
    python -m scripts.import_gw2_txt_builds

作者: System
创建日期: 2026-05-05
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal, init_db
from app.services.build_service import create_build, delete_build, get_build_by_id
from app.models.build import Build
from app.utils.logger import logger

# 前端数据文件路径
GW2_TXT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "tests", "GW2.txt"
)


def parse_bd_code_via_api(bd_code: str) -> Optional[Dict[str, Any]]:
    """调用本地 BD Code 解析 API 获取结构化数据"""
    try:
        import requests
        resp = requests.post(
            "http://localhost:8000/api/bdcode/parse",
            json={"bd_code": bd_code, "include_icons": False},
            timeout=15
        )
        if resp.status_code == 200:
            result = resp.json()
            return result.get("data")
    except Exception as e:
        logger.warning(f"BD Code 解析 API 调用失败: {e}")
    return None


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

    if len(matches) >= 2:
        for i in range(0, len(matches), 2):
            if i + 1 < len(matches):
                between = weapon_text[matches[i].end():matches[i+1].start()]
                if '+' in between or '＋' in between or '、' in between or len(between.strip()) < 5:
                    for j in [i, i+1]:
                        m = matches[j]
                        w_name = m.group(1).strip()
                        sigils_raw = m.group(2)
                        sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
                        weapons.append({"set": len(weapons) + 1, "name": w_name, "sigils": sigils})
                    break
        else:
            for i, m in enumerate(matches):
                w_name = m.group(1).strip()
                sigils_raw = m.group(2)
                sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
                weapons.append({"set": i + 1, "name": w_name, "sigils": sigils})
    elif len(matches) == 1:
        m = matches[0]
        w_name = m.group(1).strip()
        sigils_raw = m.group(2)
        sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
        weapons.append({"set": 1, "name": w_name, "sigils": sigils})

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
        if not line or line.startswith("=") or line.startswith("-"):
            i += 1
            continue

        bd_match = re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', line)
        if bd_match:
            bd_code = bd_match.group(1)

            # 向前找标题
            title = None
            j = i - 1
            while j >= 0:
                prev = lines[j].strip()
                if prev and not prev.startswith("=") and not prev.startswith("-"):
                    if not re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', prev):
                        title = prev
                        break
                j -= 1

            title = (title or "未命名配置").rstrip("：:").strip()

            # 向后找描述
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
                if next_line.startswith("循环"):
                    j += 1
                    while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("="):
                        j += 1
                    break
                desc_lines.append(next_line)
                j += 1

            description = " ".join(desc_lines)

            build = {"title": title, "bd_code": bd_code, "description": description}

            # 护甲类型
            armor_patterns = [r'([^（\s]*?套)', r'(全[\u4e00-\u9fa5]+)', r'([^\s]*混搭)', r'([^\s]*者套)']
            for pattern in armor_patterns:
                armor_match = re.search(pattern, description)
                if armor_match:
                    build["armor_type"] = armor_match.group(1).strip()
                    break

            # 武器
            build["weapons"] = extract_weapons(description)

            # 符文
            rune_match = re.search(r'(?:[^\u4e00-\u9fa5]|^)([\u4e00-\u9fa5]+符文)', description)
            if rune_match:
                build["rune"] = rune_match.group(1).strip()

            # 古物
            relic_match = re.search(r'古物[：:\s]+([\u4e00-\u9fa5]+(?:[/|\\][\u4e00-\u9fa5]+)?)', description)
            if relic_match:
                build["relic"] = relic_match.group(1).strip()

            builds.append(build)
            i = j
        else:
            i += 1

    return builds


def build_data_to_db_format(parsed: Dict[str, Any], api_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """将解析数据和 API 数据组合为数据库格式"""
    result = {
        "title": parsed["title"],
        "bd_code": parsed["bd_code"],
        "author": "",
        "armor_type": parsed.get("armor_type", ""),
        "weapons": parsed.get("weapons", []),
        "rune": parsed.get("rune", ""),
        "relic": parsed.get("relic", ""),
        "food": "",
        "wrench": "",
        "infusion": "",
        "attr_requirements": [],
        "trait_lines": [],
        "rotation_commands": [],
        "mechanics": [],
        "videos": [],
        "sub_roles": [],
        "is_meta": False,
        "profession": "",
        "profession_color": None,
        "elite_spec": None,
        "role": "dps",
    }

    if api_data:
        # 职业
        profession = api_data.get("profession")
        if profession:
            prof_map = {
                "Guardian": "Guardian",
                "Revenant": "Revenant",
                "Warrior": "Warrior",
                "Engineer": "Engineer",
                "Ranger": "Ranger",
                "Thief": "Thief",
                "Elementalist": "Elementalist",
                "Mesmer": "Mesmer",
                "Necromancer": "Necromancer",
            }
            result["profession"] = prof_map.get(profession, profession)

            # 职业颜色
            color_map = {
                "Warrior": "#E85D04",
                "Guardian": "#FAA307",
                "Revenant": "#9D4EDD",
                "Ranger": "#06D6A0",
                "Engineer": "#7B8FA1",
                "Necromancer": "#8D0801",
                "Mesmer": "#4361EE",
                "Elementalist": "#FF6B6B",
                "Thief": "#C0363D",
            }
            result["profession_color"] = color_map.get(result["profession"], "#888888")

        # 精英特长
        specs = api_data.get("specializations", [])
        elite = next((s for s in specs if s.get("is_elite")), None)
        if elite:
            result["elite_spec"] = elite.get("name_cn") or elite.get("name")

        # 特性线
        result["trait_lines"] = []
        for s in specs:
            traits = s.get("selected_traits", [])
            if len(traits) == 3:
                result["trait_lines"].append({
                    "name": s.get("name_cn") or s.get("name") or "",
                    "choices": [int(t) for t in traits]
                })

    return result


def clear_existing_builds(db) -> int:
    """清空现有 builds 表数据"""
    count = db.query(Build).count()
    if count > 0:
        db.query(Build).delete()
        db.commit()
        logger.info(f"已清空 builds 表，删除 {count} 条旧数据")
    return count


def import_builds(db, builds_data: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
    """导入配置数据到数据库"""
    success_count = 0
    failure_count = 0
    errors: List[str] = []

    for idx, raw in enumerate(builds_data, 1):
        try:
            # 调用 BD Code 解析 API
            api_data = parse_bd_code_via_api(raw["bd_code"])
            if api_data:
                logger.info(f"[{idx}/{len(builds_data)}] BD解析成功: {raw['title']} -> {api_data.get('profession', 'Unknown')}")
            else:
                logger.warning(f"[{idx}/{len(builds_data)}] BD解析失败或跳过: {raw['title']}")

            db_data = build_data_to_db_format(raw, api_data)
            build = create_build(db, db_data)
            logger.info(f"[{idx}/{len(builds_data)}] 导入成功: {build.title} (id={build.id})")
            success_count += 1
        except Exception as e:
            err_msg = f"[{idx}/{len(builds_data)}] 导入失败: {raw.get('title', 'Unknown')} - {e}"
            logger.error(err_msg)
            errors.append(err_msg)
            failure_count += 1

    return success_count, failure_count, errors


def print_report(cleared: int, success: int, failure: int, errors: List[str]) -> None:
    """打印导入结果报告"""
    total = success + failure
    print("\n" + "=" * 60)
    print("GW2.txt Build 数据导入报告")
    print("=" * 60)
    print(f"数据文件: {GW2_TXT_PATH}")
    print(f"导入时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"清空旧数据: {cleared} 条")
    print(f"总记录数: {total}")
    print(f"  [OK] 成功: {success}")
    print(f"  [FAIL] 失败: {failure}")
    print(f"成功率:   {success / total * 100:.1f}%" if total > 0 else "N/A")

    if errors:
        print("\n失败明细:")
        print("-" * 60)
        for err in errors:
            print(f"  • {err}")

    print("=" * 60)

    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "logs", "gw2_txt_import_report.txt"
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"GW2.txt Build 数据导入报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"清空旧数据: {cleared} 条\n")
        f.write(f"总记录数: {total}\n")
        f.write(f"成功: {success}\n")
        f.write(f"失败: {failure}\n")
        if errors:
            f.write("\n失败明细:\n")
            for err in errors:
                f.write(f"  • {err}\n")
    print(f"\n报告已保存至: {report_path}")


def main():
    print("=" * 60)
    print("GW2.txt Build 数据迁移工具")
    print("=" * 60)

    if not os.path.exists(GW2_TXT_PATH):
        print(f"错误: 找不到数据文件 {GW2_TXT_PATH}")
        sys.exit(1)

    print(f"\n数据文件路径: {GW2_TXT_PATH}")

    # 初始化数据库
    print("\n初始化数据库连接...")
    init_db()

    # 加载数据
    print("解析 GW2.txt...")
    builds_data = parse_gw2_txt(GW2_TXT_PATH)
    print(f"共解析到 {len(builds_data)} 个配置")

    # 确认导入
    print(f"\n即将执行以下操作:")
    print(f"  1. 清空现有 builds 表数据")
    print(f"  2. 导入 {len(builds_data)} 条来自 GW2.txt 的配置")
    print(f"  3. 所有记录的 author 字段将设为空字符串")
    confirm = input("\n确认继续? [Y/n]: ").strip().lower()
    if confirm and confirm not in ("y", "yes"):
        print("操作已取消。")
        sys.exit(0)

    db = SessionLocal()
    try:
        # 清空旧数据
        cleared = clear_existing_builds(db)

        # 执行导入
        print("\n开始导入数据...")
        success, failure, errors = import_builds(db, builds_data)
        print_report(cleared, success, failure, errors)
    finally:
        db.close()

    if failure == 0:
        print("\n[OK] 所有数据导入成功!")
    else:
        print(f"\n[WARN] 导入完成，有 {failure} 条记录失败，请查看日志。")


if __name__ == "__main__":
    main()
