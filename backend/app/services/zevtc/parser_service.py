# 模块功能：Zevtc日志解析服务
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：Zevtc解析器, sqlalchemy
# 注意：Fight、Member、Skill等模型已被移除，相关数据库保存功能已停用

import datetime
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.zevtc.parser import (
    DataValidator,
    FileCorruptedError,
    InvalidFileFormatError,
    ParseProgress,
    ZevtcParseError,
    parse_zevtc_file,
)
from app.models.log.log import Log
from app.utils.logger import logger


class LogParser:
    # 功能：Zevtc日志解析器封装类

    def __init__(self):
        self.parser = None
        self.parsed_data = None
        self.progress: Optional[ParseProgress] = None
        self._json_cache: Optional[Dict] = None

    def parse_file(self, file_path: str, track_progress: bool = True) -> Dict[str, Any]:
        # 功能：解析Zevtc文件
        # 参数：file_path - 文件路径；track_progress - 是否跟踪进度
        # 返回：解析后的数据
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"路径不是文件: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise FileCorruptedError("文件为空")

        logger.info(f"开始解析文件: {file_path} ({file_size / (1024*1024):.2f}MB)")

        self.progress = ParseProgress() if track_progress else None
        self.parsed_data = parse_zevtc_file(file_path, self.progress)
        self._json_cache = None

        logger.info(f"文件解析完成: {len(self.parsed_data.get('players', []))}个玩家")

        return self.parsed_data

    def parse_json(self, json_path: str) -> Dict[str, Any]:
        # 功能：从JSON文件加载解析数据
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"文件不存在: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            self.parsed_data = json.load(f)

        self._json_cache = None
        logger.info(f"从JSON加载数据: {len(self.parsed_data.get('players', []))}个玩家")

        return self.parsed_data

    def get_progress(self) -> Optional[Dict]:
        # 功能：获取解析进度
        if self.progress:
            return self.progress.to_dict()
        return None

    def get_parsed_json(self) -> Optional[Dict]:
        # 功能：获取解析后的完整JSON数据
        return self.parsed_data

    def _extract_player_healing(self, player: Dict) -> int:
        """从EI JSON中提取玩家的治疗量，支持多种格式。"""
        support = player.get("support", [{}])
        if support and isinstance(support, list):
            healing = support[0].get("healing")
            if healing is not None:
                return int(healing)

        ext_healing = player.get("extHealingStats")
        if ext_healing:
            outgoing = ext_healing.get("outgoingHealing", [{}])
            if outgoing and isinstance(outgoing, list):
                healing = outgoing[0].get("healing")
                if healing is not None:
                    return int(healing)
            healing = ext_healing.get("healing")
            if healing is not None:
                return int(healing)

        return 0

    def extract_fight_info(self) -> Dict[str, Any]:
        # 功能：提取战斗信息
        if not self.parsed_data:
            return {}

        data = self.parsed_data
        time_start = data.get("timeStart", "")
        time_end = data.get("timeEnd", "")

        duration_ms = data.get("durationMS", 0)
        duration_sec = duration_ms // 1000

        total_damage, total_kills, total_deaths = self._calc_all_totals()

        fight_info = {
            "map_name": self._extract_map_name(data.get("fightName", "")),
            "server_name": self._extract_server_from_arc(data.get("arcVersion", "")),
            "total_damage": total_damage,
            "total_healing": sum(
                self._extract_player_healing(p) for p in data.get("players", [])
            ),
            "kill_count": total_kills,
            "death_count": total_deaths,
            "duration_sec": duration_sec,
            "start_time": (
                self._parse_datetime(time_start)
                if time_start
                else datetime.datetime.now()
            ),
            "end_time": (
                self._parse_datetime(time_end) if time_end else datetime.datetime.now()
            ),
            "is_ai_analyzed": False,
            "is_wvw": data.get("detailedWvW", False),
            "gw2_build": data.get("gw2Build", 0),
            "duration_str": data.get("duration", ""),
        }

        return fight_info

    def extract_players(self) -> List[Dict[str, Any]]:
        # 功能：提取玩家信息
        if not self.parsed_data:
            return []

        players = []
        for p in self.parsed_data.get("players", []):
            account = p.get("account", "")
            name = p.get("name", "")
            account_name = account if account else name or "Unknown"

            player_info = {
                "account_name": account_name,
                "profession": p.get("profession", "Unknown"),
                "team_id": p.get("teamID", 0),
                "stats": self._extract_player_stats(p),
                "name": name,
                "group": p.get("group", 1),
                "has_commander_tag": p.get("hasCommanderTag", False),
                "instance_id": p.get("instanceID", 0),
            }
            players.append(player_info)

        return players

    def extract_player_stats(self, player_identifier: str) -> Optional[Dict[str, Any]]:
        # 功能：提取指定玩家的统计信息（支持account_name、name或instanceID字符串）
        if not self.parsed_data:
            return None

        # 尝试将标识符转换为instanceID（数字）
        target_instance_id = None
        try:
            target_instance_id = int(player_identifier)
        except ValueError:
            pass

        for p in self.parsed_data.get("players", []):
            match = False

            # 1. 优先用instanceID匹配
            if (
                target_instance_id is not None
                and p.get("instanceID") == target_instance_id
            ):
                match = True
            # 2. 用account或name匹配
            elif (
                p.get("account") == player_identifier
                or p.get("name") == player_identifier
            ):
                match = True

            if match:
                return self._extract_player_stats(p)

        return None

    def _extract_player_stats(self, player: Dict) -> Dict[str, Any]:
        # 功能：提取玩家统计信息
        dps_all = player.get("dpsAll", [{}])
        dps_data = dps_all[0] if dps_all else {}

        stats_all = player.get("statsAll", [{}])
        stats_data = stats_all[0] if stats_all else {}

        defenses = player.get("defenses", [{}])
        defense_data = defenses[0] if defenses else {}

        support = player.get("support", [{}])
        support_data = support[0] if support else {}

        active_times = player.get("activeTimes", [0])
        combat_time = active_times[0] if active_times else 0

        return {
            "damage": dps_data.get("damage", 0),
            "healing": self._extract_player_healing(player),
            "power_damage": dps_data.get("powerDamage", 0),
            "condi_damage": dps_data.get("condiDamage", 0),
            "kills": stats_data.get("killed", 0),
            "deaths": defense_data.get("deadCount", 0),
            "downs": defense_data.get("downCount", 0),
            "time_in_combat": combat_time,
            "damage_taken": defense_data.get("damageTaken", 0),
            "down_count": defense_data.get("downCount", 0),
            "res_count": 0,
            "boon_strips": support_data.get("boonStrips", 0),
            "condi_cleanses": support_data.get("condiCleanse", 0),
            "role": "dps",
            "total_score": 0.0,
            "dps": dps_data.get("dps", 0),
            "breakbar_damage": dps_data.get("breakbarDamage", 0.0),
            "interrupts": stats_data.get("interrupts", 0),
            "downs_inflicted": stats_data.get("downed", 0),
        }

    def _calc_total_damage(self) -> int:
        # 功能：计算总伤害
        if not self.parsed_data:
            return 0

        total = 0
        for p in self.parsed_data.get("players", []):
            dps_all = p.get("dpsAll", [{}])
            if dps_all:
                total += dps_all[0].get("damage", 0)

        return total

    def _calc_total_kills(self) -> int:
        # 功能：计算总击杀数
        if not self.parsed_data:
            return 0

        total = 0
        for p in self.parsed_data.get("players", []):
            defenses = p.get("defenses", [{}])
            if defenses:
                total += defenses[0].get("killed", 0)

        return total

    def _calc_total_deaths(self) -> int:
        # 功能：计算总死亡数
        if not self.parsed_data:
            return 0

        total = 0
        for p in self.parsed_data.get("players", []):
            defenses = p.get("defenses", [{}])
            if defenses:
                total += defenses[0].get("deadCount", 0)

        return total

    def _calc_all_totals(self) -> Tuple[int, int, int]:
        # 功能：一次性计算所有总数（优化性能，避免多次遍历）
        if not self.parsed_data:
            return 0, 0, 0

        total_damage = 0
        total_kills = 0
        total_deaths = 0

        for p in self.parsed_data.get("players", []):
            dps_all = p.get("dpsAll", [{}])
            if dps_all:
                total_damage += dps_all[0].get("damage", 0)

            defenses = p.get("defenses", [{}])
            if defenses:
                total_kills += defenses[0].get("killed", 0)
                total_deaths += defenses[0].get("deadCount", 0)

        return total_damage, total_kills, total_deaths

    def _extract_map_name(self, fight_name: str) -> str:
        # 功能：从战斗名称提取地图名
        if "Eternal Battlegrounds" in fight_name:
            return "Eternal Battlegrounds"
        elif "Borderlands" in fight_name:
            return fight_name.split(" - ")[-1] if " - " in fight_name else fight_name
        elif "Detailed WvW - " in fight_name:
            return fight_name.replace("Detailed WvW - ", "")
        return fight_name

    def _extract_server_from_arc(self, arc_version: str) -> str:
        # 功能：从arc版本提取服务器信息
        if arc_version.startswith("EVTC"):
            return arc_version[4:] if len(arc_version) > 4 else "Unknown"
        return arc_version

    def _parse_datetime(self, dt_str: str) -> datetime.datetime:
        # 功能：解析日期时间字符串
        if not dt_str:
            return datetime.datetime.now()

        if dt_str.startswith("1970"):
            return datetime.datetime.now()

        dt_str = dt_str.strip()
        dt_str = dt_str.replace(" +00:00", "+00:00").replace(" +08:00", "+08:00")
        dt_str = dt_str.replace(" +08", "+08:00")

        formats = [
            "%Y-%m-%d %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(dt_str, fmt)
                if dt.tzinfo:
                    dt = dt.astimezone().replace(tzinfo=None)
                return dt
            except ValueError:
                continue

        return datetime.datetime.now()

    def get_skill_rotation(self, player_identifier: str) -> List[Dict]:
        # 功能：获取玩家技能循环（支持account_name、name或instanceID字符串）
        if not self.parsed_data:
            return []

        # 尝试将标识符转换为instanceID（数字）
        target_instance_id = None
        try:
            target_instance_id = int(player_identifier)
        except ValueError:
            pass

        for p in self.parsed_data.get("players", []):
            match = False

            # 1. 优先用instanceID匹配
            if (
                target_instance_id is not None
                and p.get("instanceID") == target_instance_id
            ):
                match = True
            # 2. 用account或name匹配
            elif (
                p.get("account") == player_identifier
                or p.get("name") == player_identifier
            ):
                match = True

            if match:
                rotation = p.get("rotation", [])
                skill_map = self.parsed_data.get("skillMap", {})

                events = []
                for skill_list in rotation:
                    if isinstance(skill_list, list):
                        for item in skill_list:
                            if isinstance(item, dict):
                                skill_id = item.get("id", 0)
                                skill_key = f"s{skill_id}"
                                skill_info = skill_map.get(skill_key, {})
                                events.append(
                                    {
                                        "skill_id": skill_id,
                                        "skill_name": skill_info.get(
                                            "name", f"Skill:{skill_id}"
                                        ),
                                        "time": item.get("time", 0),
                                        "duration": item.get("duration", 0),
                                    }
                                )

                return events

        return []

    def get_buff_uptime(self, player_identifier: str) -> Dict[str, float]:
        # 功能：获取玩家BUFF覆盖时间（支持account_name、name或instanceID字符串）
        if not self.parsed_data:
            return {}

        # 尝试将标识符转换为instanceID（数字）
        target_instance_id = None
        try:
            target_instance_id = int(player_identifier)
        except ValueError:
            pass

        for p in self.parsed_data.get("players", []):
            match = False

            # 1. 优先用instanceID匹配
            if (
                target_instance_id is not None
                and p.get("instanceID") == target_instance_id
            ):
                match = True
            # 2. 用account或name匹配
            elif (
                p.get("account") == player_identifier
                or p.get("name") == player_identifier
            ):
                match = True

            if match:
                buff_uptimes = p.get("buffUptimes", [])
                buff_map = self.parsed_data.get("buffMap", {})

                uptime = {}
                for buff in buff_uptimes:
                    buff_id = buff.get("id")
                    buff_key = f"b{buff_id}"
                    buff_info = buff_map.get(buff_key, {})
                    buff_name = buff_info.get("name", f"Buff:{buff_id}")
                    uptime_value = buff.get("uptime", 0)

                    if isinstance(uptime_value, (int, float)):
                        uptime_ms = uptime_value
                    elif isinstance(uptime_value, list) and uptime_value:
                        uptime_ms = (
                            uptime_value[0]
                            if isinstance(uptime_value[0], (int, float))
                            else 0
                        )
                    else:
                        uptime_ms = 0

                    uptime[buff_name] = uptime_ms

                return uptime

        return {}

    def get_buff_uptime_percent(self, player_identifier: str) -> Dict[str, float]:
        # 功能：获取玩家BUFF覆盖率百分比（支持account_name、name或instanceID字符串）
        if not self.parsed_data:
            return {}

        duration_ms = self.parsed_data.get("durationMS", 1)
        uptimes = self.get_buff_uptime(player_identifier)

        return {name: round(ms / duration_ms * 100, 2) for name, ms in uptimes.items()}

    def validate_data(self, reference: Optional[Dict] = None) -> Dict:
        # 功能：验证解析数据
        if not self.parsed_data:
            return {
                "passed": False,
                "errors": ["没有解析数据"],
                "warnings": [],
                "details": {},
            }

        return DataValidator.validate_parsed_data(self.parsed_data, reference)


def save_parsed_log_to_db(
    db: Session, log_id: int, parser: LogParser, overwrite: bool = True
) -> Tuple[Dict, Dict]:
    # 功能：将解析数据保存到数据库（已停用）
    # 参数：db - 数据库会话；log_id - 日志ID；parser - 解析器；overwrite - 是否覆盖旧数据
    # 返回：战斗信息, 战斗统计列表（均为字典格式）

    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise ValueError(f"日志不存在 {log_id}")

    logger.info(f"解析数据保存功能已停用，日志ID: {log_id}")

    # 更新日志状态为已解析
    log.parse_status = "completed"
    log.parsed_at = datetime.datetime.now()
    db.commit()

    # 返回解析数据作为字典，不保存到Fight/Member等已删除的表
    fight_info = parser.extract_fight_info()
    players = parser.extract_players()

    return fight_info, players


def parse_and_save(
    db: Session, log_id: int, file_path: str, overwrite: bool = True
) -> Tuple[Dict, Dict, Dict]:
    # 功能：解析文件并保存到数据库（已停用）
    # 参数：db - 数据库会话；log_id - 日志ID；file_path - 文件路径；overwrite - 是否覆盖旧数据
    # 返回：解析数据, 战斗信息, 玩家列表
    parser = LogParser()

    try:
        parsed_data = parser.parse_file(file_path)
        fight_info, players = save_parsed_log_to_db(db, log_id, parser, overwrite)
        return parsed_data, fight_info, players
    except ZevtcParseError as e:
        logger.error(f"解析错误: {e}")
        log = db.query(Log).filter(Log.id == log_id).first()
        if log:
            log.parse_status = "failed"
            log.error_message = str(e)
            db.commit()
        raise
