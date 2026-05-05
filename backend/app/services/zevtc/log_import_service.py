# -*- coding: utf-8 -*-
# 模块功能：日志导入服务（parse → scalar extraction → DB insert）
# 作者：系统
# 创建日期：2026-04-27
# 更新日期：2026-05-04
# 说明：
#   1. 解析 zevtc 文件（使用 EnhancedZevtcParser）
#   2. 【优化】优先使用 dps.report API 获取高质量 EI JSON 数据
#   3. 【优化】数据验证：确保关键字段的存在和有效性
#   4. 【优化】字段映射：统一不同数据源的字段名
#   5. 写入 fights (1 行) + fight_stats (~50 行) + members（更新或插入）
#   6. 重要：不自动删除源文件，保留用户重新解析的可能性
#   7. 用户确认数据正确后，可调用 cleanup_file() 或 cleanup_files_batch() 删除文件

import gc
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.zevtc.parser import EnhancedZevtcParser, ZevtcParseError
from app.services.system.dps_report_service import (
    DpsReportError,
    DpsReportTimeoutError,
    upload_and_parse,
)
from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.log import Log
from app.models.member import Member
from app.models.zevtc_data import EiPlayer, EiSkillMap, EiTarget
from app.services.zevtc.data_validator import EIJsonValidator
from app.services.zevtc.field_mapper import EIJsonFieldMapper
from app.utils.logger import logger

# 无效账号名称统计（用于日志记录）
INVALID_ACCOUNT_STATS = {
    'total_skipped': 0,
    'blacklist_matches': 0,
    'format_errors': 0,
    'empty_accounts': 0,
}


class LogImportService:
    """日志导入服务：zevtc → fights/fight_stats/members

    重要变更 (2026-05-03)：
    - 不再自动删除源文件，保留用户重新解析的可能性
    - 如需删除文件，请调用 cleanup_file() 或 cleanup_files_batch()
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _resolve_commander_tag(ei_player: Dict, local_player, data_source: str = "local_parser") -> bool:
        """统一解析指挥官标记，明确数据源优先级，避免 isCommander/hasCommanderTag 冲突。

        优先级：
        1. dps_report 数据源且 EI JSON 显式包含 isCommander 字段 -> 使用 isCommander
        2. EI JSON 显式包含 hasCommanderTag 字段 -> 使用 hasCommanderTag
        3. EI JSON 显式包含 isCommander 字段 -> 使用 isCommander
        4. 本地解析器 player_stats.has_commander_tag -> fallback
        """
        if data_source == "dps_report" and "isCommander" in ei_player:
            return bool(ei_player["isCommander"])
        if "hasCommanderTag" in ei_player:
            return bool(ei_player["hasCommanderTag"])
        if "isCommander" in ei_player:
            return bool(ei_player["isCommander"])
        if hasattr(local_player, "has_commander_tag"):
            return bool(local_player.has_commander_tag)
        return False

    @staticmethod
    def _should_skip_player(player_data) -> bool:
        """判断是否为需要跳过的假玩家/NPC或无效账号。
        
        跳过规则：
        1. isFake 或 friendlyNPC 标记为真
        2. 账号名称在黑名单中（如 "Non Squad Player"）
        3. 账号为空或全是空格
        
        Args:
            player_data: 玩家数据（dict 或 PlayerStats dataclass）
            
        Returns:
            True 表示需要跳过，False 表示有效玩家
        """
        # 检查假玩家/NPC 标记
        if isinstance(player_data, dict):
            is_fake = bool(player_data.get("isFake") or player_data.get("friendlyNPC"))
            account = player_data.get("account", "").strip()
        else:
            # PlayerStats dataclass
            is_fake = bool(
                getattr(player_data, "is_fake", False) or getattr(player_data, "friendly_npc", False)
            )
            account = getattr(player_data, "account", "").strip()
        
        if is_fake:
            logger.debug(f"[import] 跳过假玩家/NPC: {account}")
            return True
        
        # 检查账号名称有效性（只检查黑名单和空值）
        if not EIJsonValidator.is_valid_account_name(account):
            # 统计跳过原因
            if not account:
                INVALID_ACCOUNT_STATS['empty_accounts'] += 1
                logger.debug(f"[import] 跳过空账号")
            else:
                valid, reason = EIJsonValidator.validate_account_name(account)
                if "黑名单" in reason:
                    INVALID_ACCOUNT_STATS['blacklist_matches'] += 1
                INVALID_ACCOUNT_STATS['total_skipped'] += 1
                logger.debug(f"[import] 跳过无效账号 '{account}': {reason}")
            return True
        
        return False

    @staticmethod
    def _extract_player_healing(player: Dict) -> int:
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

    def import_log(
        self, log_id: int, file_path: str, allow_fallback: bool = True
    ) -> Dict[str, Any]:
        """【优化后】主入口：导入单个日志文件。
        
        优化流程：
        1. 获取数据（优先 dps.report API，fallback 本地解析器）
        2. 数据验证（确保关键字段有效性）
        3. 字段映射（统一不同数据源的字段名）
        4. 数据转换（类型标准化）
        5. 数据库存储（事务处理）
        
        Args:
            allow_fallback: 当 dps.report API 失败时是否回退到本地解析器。
                           Batch 解析时应设为 False，确保 429 等错误能被上层重试。
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"文件不存在: {file_path}"}

        try:
            # =============================================
            # 步骤 1: 获取数据（优先 dps.report API，超时/失败才 fallback 本地解析）
            # =============================================
            parser: Optional[EnhancedZevtcParser] = None
            local_ei_json: Optional[Dict] = None
            ei_json: Optional[Dict] = None
            data_source: Optional[str] = None
            dps_result: Optional[Dict] = None

            try:
                dps_result = upload_and_parse(file_path)
                ei_json = dps_result["ei_json"]
                data_source = "dps_report"
                logger.info(
                    f"[import] dps.report 解析成功，直接使用高质量 EI JSON 数据，"
                    f"跳过本地解析器以节省内存"
                )
            except (DpsReportTimeoutError, DpsReportError) as e:
                # dps.report 超时/失败，fallback 到本地解析
                logger.warning(
                    f"[import] dps.report 失败: {e}，fallback 到本地解析"
                )
                parser = EnhancedZevtcParser(file_path)
                local_ei_json = parser.parse()
                ei_json = local_ei_json
                data_source = "local_parser"
                gc.collect()

            # =============================================
            # 步骤 2: 数据验证（宽松策略 + fallback）
            # =============================================
            logger.info(f"[import] 开始验证数据（来源: {data_source}）")
            valid_players, valid_encounter, errors, warnings = EIJsonValidator.validate_ei_json(ei_json)

            if errors:
                logger.warning(f"[import] 数据验证发现 {len(errors)} 个错误: {errors}")
            if warnings:
                logger.info(f"[import] 数据验证发现 {len(warnings)} 个警告: {warnings}")

            # 如果使用 dps.report 数据但验证失败，fallback 到本地解析器
            if data_source == "dps_report" and not valid_players:
                logger.warning("[import] dps.report 数据验证失败，fallback 到本地解析器")
                if parser is None:
                    parser = EnhancedZevtcParser(file_path)
                    local_ei_json = parser.parse()
                ei_json = local_ei_json
                data_source = "local_parser"
                # 重新验证本地解析器数据
                valid_players, valid_encounter, errors, warnings = EIJsonValidator.validate_ei_json(ei_json)
                if errors:
                    logger.warning(f"[import] 本地解析器数据验证发现 {len(errors)} 个错误: {errors}")
                if warnings:
                    logger.info(f"[import] 本地解析器数据验证发现 {len(warnings)} 个警告: {warnings}")

            # 即使没有 valid_players 也继续处理
            if not valid_players:
                logger.warning("[import] 没有通过验证的玩家数据，但将继续处理")

            logger.info(f"[import] 数据验证完成，有效玩家数: {len(valid_players)}, 数据来源: {data_source}")

            # =============================================
            # 步骤 3: 提取标量数据（保留原有逻辑，增强验证）
            # =============================================
            fight_data = self._extract_fight_data(parser, ei_json)
            player_stats = self._extract_player_stats(parser, ei_json, data_source)

            # =============================================
            # 步骤 4: 写入数据库
            # =============================================
            fight = self._insert_fight(log_id, fight_data)
            self._insert_players(fight.id, player_stats)

            # =============================================
            # 步骤 5: 更新 Log 状态
            # =============================================
            log = self.db.query(Log).filter(Log.id == log_id).first()
            if log:
                log.parse_status = "completed"
                log.parsed_at = datetime.now(timezone.utc)
                # dps.report 成功时从 EI JSON 获取 duration，本地解析时从 parser 获取
                if parser is not None:
                    log.parse_time_ms = parser.meta.duration_ms
                else:
                    log.parse_time_ms = ei_json.get("durationMS", 0)
                log.parser = "dps_report_ei_v1" if data_source == "dps_report" else "enhanced_zevtc_v2"
                log.parsed_data = None
                if dps_result and dps_result.get("permalink"):
                    log.dps_report_permalink = dps_result.get("permalink")
                self.db.flush()

            # =============================================
            # 步骤 6: 同步 EI Player 数据
            # =============================================
            self._insert_ei_players(log_id, ei_json, data_source)
            # 释放已处理的大块 JSON 数据，降低内存峰值
            ei_json.pop("players", None)
            ei_json.pop("deathRecap", None)

            self._insert_skill_maps(log_id, ei_json)
            ei_json.pop("skillMap", None)

            self._insert_targets(log_id, ei_json)
            ei_json.pop("targets", None)

            # =============================================
            # 步骤 7: 数据完整性验证
            # =============================================
            integrity_issues = self._validate_data_integrity(fight.id, log_id, player_stats, ei_json)
            if integrity_issues:
                logger.warning(f"[import] 数据完整性检查发现 {len(integrity_issues)} 个问题: {integrity_issues}")

            # =============================================
            # 步骤 8: 提交事务
            # =============================================
            self.db.commit()

            # =============================================
            # 步骤 9: 重要：保留源文件，不自动删除
            # =============================================

            # 显式触发 GC，加速解析器大对象的回收，降低内存峰值
            gc.collect()

            return {
                "success": True,
                "fight_id": fight.id,
                "players_count": len(player_stats),
                "map_name": fight.map_name,
                "duration_sec": fight.duration_sec,
                "data_source": data_source,
                "validation_errors": errors,
                "validation_warnings": warnings,
                "integrity_issues": integrity_issues,
            }

        except ZevtcParseError as e:
            logger.error(f"解析日志失败 log_id={log_id}: {e.message}", exc_info=True)
            try:
                self.db.rollback()
            except Exception:
                pass
            return {"success": False, "error": e.message}
        except Exception as e:
            logger.error(f"导入日志失败 log_id={log_id}: {e}", exc_info=True)
            try:
                self.db.rollback()
            except Exception:
                pass
            return {"success": False, "error": str(e)}

    def _extract_fight_data(
        self, parser: Optional[EnhancedZevtcParser], ei_json: Dict
    ) -> Dict[str, Any]:
        """提取战斗级标量数据。

        支持两种模式：
        1. dps.report 成功（parser=None）：所有数据从 EI JSON 中提取
        2. 本地解析（parser!=None）：优先使用 EI JSON，部分字段 fallback 到 parser
        """
        # 优先从 EI JSON 获取 duration（dps.report 的数据最准确）
        ei_duration_ms = ei_json.get("durationMS")
        if ei_duration_ms is None and parser is not None:
            ei_duration_ms = parser.meta.duration_ms
        elif ei_duration_ms is None:
            ei_duration_ms = 0

        duration_sec = max(1, int(ei_duration_ms / 1000))

        # 时间字段优先级：EI JSON > parser.meta
        ei_start = ei_json.get("timeStartStd") or ei_json.get("timeStart")
        ei_end = ei_json.get("timeEndStd") or ei_json.get("timeEnd")

        if parser is not None:
            ei_start = ei_start or parser.meta.start_datetime
            ei_end = ei_end or parser.meta.end_datetime

        # 从 EI JSON players 计算总伤害、击杀、死亡（排除宠物/非玩家）
        ei_players = ei_json.get("players", [])
        total_damage = 0
        total_kills = 0
        total_deaths = 0
        player_count = 0
        for p in ei_players:
            if p.get("isFake") or p.get("friendlyNPC"):
                continue
            dps_all = p.get("dpsAll", [{}])[0]
            total_damage += dps_all.get("damage", 0)
            stats_all = p.get("statsAll", [{}])[0]
            total_kills += stats_all.get("killed", 0)
            defenses = p.get("defenses", [{}])[0]
            total_deaths += defenses.get("deadCount", 0)
            player_count += 1

        # fallback：如果 EI JSON 中没有 players，使用本地 parser 数据
        if not ei_players and parser is not None:
            total_damage = sum(p.total_damage for p in parser.player_stats.values())
            total_kills = sum(p.kills_inflicted for p in parser.player_stats.values())
            total_deaths = sum(p.own_deaths for p in parser.player_stats.values())
            player_count = len(parser.player_stats)

        parsed_start = self._parse_ei_time(ei_start)
        parsed_end = self._parse_ei_time(ei_end)

        if not parsed_start:
            logger.warning(f"[import] 无法解析开始时间: {ei_start}，使用当前时间")
            parsed_start = datetime.now(timezone.utc)
        if not parsed_end:
            parsed_end = parsed_start

        # map_name 来源：EI JSON > parser.meta
        map_name = ei_json.get("fightName")
        if map_name is None and parser is not None:
            map_name = parser.meta.map_name

        return {
            "start_time": parsed_start,
            "end_time": parsed_end,
            "duration_sec": duration_sec,
            "duration_ms": ei_duration_ms,
            "map_name": map_name,
            "server_name": "Unknown",
            "recorded_by": ei_json.get("recordedBy"),
            "recorded_account": ei_json.get("recordedAccountBy"),
            "total_damage": total_damage,
            "total_healing": sum(
                self._extract_player_healing(p) for p in ei_json.get("players", [])
            ),
            "kill_count": total_kills,
            "death_count": total_deaths,
            "player_count": player_count,
        }

    def _extract_player_stats(
        self, parser: Optional[EnhancedZevtcParser], ei_json: Dict, data_source: str = "local_parser"
    ) -> List[Dict[str, Any]]:
        """提取每个玩家的标量统计。

        支持两种模式：
        1. dps.report 成功（parser=None）：直接从 EI JSON players 遍历
        2. 本地解析（parser!=None）：优先使用 EI JSON，部分字段 fallback 到 parser
        """
        duration_ms = ei_json.get("durationMS", 0)
        if duration_ms == 0 and parser is not None:
            duration_ms = parser.meta.duration_ms
        duration_sec = max(1, int(duration_ms / 1000))
        results = []

        if parser is None:
            # ========== dps.report 模式：直接从 EI JSON 提取 ==========
            for ei_p in ei_json.get("players", []):
                if self._should_skip_player(ei_p):
                    continue

                dps_all = ei_p.get("dpsAll", [{}])[0]
                stats_all = ei_p.get("statsAll", [{}])[0]
                defenses = ei_p.get("defenses", [{}])[0]
                support = ei_p.get("support", [{}])[0]

                # 从 buffUptimes 中提取覆盖率（格式: [{"id": 740, "name": "Might", "uptime": 85.5}, ...]）
                buff_uptimes = {}
                for bu in ei_p.get("buffUptimes", []):
                    name = bu.get("name", "")
                    if name:
                        buff_uptimes[name] = bu.get("uptime", 0)

                has_cmd = bool(
                    ei_p.get("isCommander") or ei_p.get("hasCommanderTag")
                )

                player = {
                    "account": ei_p.get("account", ""),
                    "character_name": ei_p.get("name", ""),
                    "profession": ei_p.get("profession", ""),
                    "group_id": ei_p.get("group", 0),
                    "team_id": ei_p.get("teamID", 0),
                    "has_commander_tag": has_cmd,
                    "damage": dps_all.get("damage", 0),
                    "dps": dps_all.get("dps", 0),
                    "power_damage": dps_all.get("powerDamage", 0),
                    "condi_damage": dps_all.get("condiDamage", 0),
                    "breakbar_damage": int(dps_all.get("breakbarDamage", 0) or 0),
                    "critical_rate": stats_all.get("criticalRate", 0),
                    "flanking_rate": stats_all.get("flankingRate", 0),
                    "glance_rate": stats_all.get("glanceRate", 0),
                    "missed": stats_all.get("missed", 0),
                    "interrupts": stats_all.get("interrupts", 0),
                    "swap_count": stats_all.get("swapCount", 0),
                    "blocked_count": defenses.get("blockedCount", 0),
                    "evaded_count": defenses.get("evadedCount", 0),
                    "dodge_count": defenses.get("dodgeCount", 0),
                    "down_count": defenses.get("downCount", 0),
                    "dead_count": defenses.get("deadCount", 0),
                    "boon_strips": support.get("boonStrips", 0),
                    "condition_cleanses": support.get("condiCleanse", 0),
                    "resurrects": support.get("resurrects", 0),
                    "condi_cleanse_ally": support.get("condiCleanse", 0),
                    "boon_strips_ally": support.get("boonStrips", 0),
                    "might_uptime": buff_uptimes.get("Might", 0),
                    "fury_uptime": buff_uptimes.get("Fury", 0),
                    "quickness_uptime": buff_uptimes.get("Quickness", 0),
                    "alacrity_uptime": buff_uptimes.get("Alacrity", 0),
                    "protection_uptime": buff_uptimes.get("Protection", 0),
                    "stability_uptime": buff_uptimes.get("Stability", 0),
                    "healing": self._extract_player_healing(ei_p),
                    "killed": stats_all.get("killed", 0),
                    "damage_taken": defenses.get("damageTaken", 0),
                }
                results.append(player)
            return results

        # ========== 本地解析模式：保持原有逻辑 ==========
        # 建立 account -> ei player json 的映射
        ei_players_by_account = {}
        for p in ei_json.get("players", []):
            ei_players_by_account[p.get("account", "")] = p

        for addr, pstats in parser.player_stats.items():
            if self._should_skip_player(pstats):
                logger.info(f"[import] 跳过假玩家/NPC: {pstats.account} / {pstats.name}")
                continue

            ei_p = ei_players_by_account.get(pstats.account, {})
            dps_all = ei_p.get("dpsAll", [{}])[0]
            stats_all = ei_p.get("statsAll", [{}])[0]
            defenses = ei_p.get("defenses", [{}])[0]
            support = ei_p.get("support", [{}])[0]
            buff_uptime = pstats.buff_uptime

            if dps_all and dps_all.get("damage"):
                dmg = dps_all.get("damage", 0)
                dps = dps_all.get("dps", 0)
                power_dmg = dps_all.get("powerDamage", 0)
                condi_dmg = dps_all.get("condiDamage", 0)
                breakbar_dmg = int(dps_all.get("breakbarDamage", 0) or 0)
            else:
                dmg = pstats.total_damage
                dps = int(dmg / duration_sec) if duration_sec > 0 else 0
                power_dmg = pstats.power_damage
                condi_dmg = pstats.condi_damage
                breakbar_dmg = int(pstats.breakbar_damage)

            has_cmd = self._resolve_commander_tag(ei_p, pstats, data_source)

            player = {
                "account": pstats.account,
                "character_name": pstats.name,
                "profession": pstats.profession,
                "group_id": pstats.group,
                "team_id": pstats.team if pstats.team is not None else 0,
                "has_commander_tag": has_cmd,
                "damage": dmg,
                "dps": dps,
                "power_damage": power_dmg,
                "condi_damage": condi_dmg,
                "breakbar_damage": breakbar_dmg,
                "critical_rate": stats_all.get("criticalRate", 0),
                "flanking_rate": stats_all.get("flankingRate", 0),
                "glance_rate": stats_all.get("glanceRate", 0),
                "missed": stats_all.get("missed", 0),
                "interrupts": stats_all.get("interrupts", 0),
                "swap_count": stats_all.get("swapCount", 0),
                "blocked_count": defenses.get("blockedCount", 0),
                "evaded_count": defenses.get("evadedCount", 0),
                "dodge_count": defenses.get("dodgeCount", 0),
                "down_count": pstats.own_downs,
                "dead_count": pstats.own_deaths,
                "boon_strips": pstats.boon_strips,
                "condition_cleanses": pstats.condi_cleanses,
                "resurrects": support.get("resurrects", 0),
                "condi_cleanse_ally": support.get("condiCleanse", 0),
                "boon_strips_ally": support.get("boonStrips", 0),
                "might_uptime": buff_uptime.get("Might", 0),
                "fury_uptime": buff_uptime.get("Fury", 0),
                "quickness_uptime": buff_uptime.get("Quickness", 0),
                "alacrity_uptime": buff_uptime.get("Alacrity", 0),
                "protection_uptime": buff_uptime.get("Protection", 0),
                "stability_uptime": buff_uptime.get("Stability", 0),
                "healing": self._extract_player_healing(ei_p),
                "killed": pstats.kills_inflicted,
                "damage_taken": defenses.get("damageTaken", 0),
            }
            results.append(player)

        return results

    def _insert_fight(self, log_id: int, data: Dict[str, Any]) -> Fight:
        """插入 fight 记录（如已存在则替换）"""
        # 清理旧的 fight 及关联的 fight_stats
        old_fights = self.db.query(Fight).filter(Fight.log_id == log_id).all()
        for old in old_fights:
            self.db.delete(old)
        if old_fights:
            self.db.flush()

        fight = Fight(
            log_id=log_id,
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            duration_sec=data.get("duration_sec", 0),
            duration_ms=data.get("duration_ms", 0),
            map_name=data.get("map_name"),
            server_name=data.get("server_name"),
            recorded_by=data.get("recorded_by"),
            recorded_account=data.get("recorded_account"),
            total_damage=data.get("total_damage", 0),
            total_healing=data.get("total_healing", 0),
            kill_count=data.get("kill_count", 0),
            death_count=data.get("death_count", 0),
            player_count=data.get("player_count", 0),
            is_ai_analyzed=False,
        )
        self.db.add(fight)
        self.db.flush()
        return fight

    def _insert_players(self, fight_id: int, players: List[Dict[str, Any]]):
        """插入/更新 members + fight_stats（并发安全版）

        过滤规则：
        - 仅导入包含account数据的记录
        - 同一 fight 内同一 account 去重，防止断线重连导致重复记录
        - 更新AccountCharacter映射，支持同一account多个角色

        逻辑：遍历 players → 查询或创建 Member/AccountCharacter → flush 获取 id → 创建 FightStats
        批量解析已改为单线程顺序执行，不存在并发冲突。
        """
        from datetime import date
        from app.models.account_character import AccountCharacter
        from app.services.wvw.scoring_service import ScoringService

        today = date.today()
        seen_accounts: set = set()
        member_map: Dict[str, Member] = {}

        # 预计算评分所需的同场最大值（用于归一化）
        max_values = {}
        if players:
            max_values = {
                "damage": max(p.get("damage", 0) for p in players),
                "power_damage": max(p.get("power_damage", 0) for p in players),
                "condition_damage": max(p.get("condi_damage", 0) for p in players),
                "healing": max(p.get("healing", 0) for p in players),
                "strips": max(p.get("boon_strips", 0) for p in players),
                "cleanses": max(p.get("condition_cleanses", 0) for p in players),
                "kills": max(p.get("killed", 0) for p in players),
                "breakbar": max(p.get("breakbar_damage", 0) for p in players),
            }

        # 获取评分规则（默认 dps，后续可按职业自动判断）
        scoring_rules = ScoringService.get_scoring_rules(self.db, "dps")

        # 第一步：处理 Member 和 AccountCharacter
        for p in players:
            account = p.get("account", "").strip()[:100]
            if not account:
                continue
            if account in seen_accounts:
                continue
            seen_accounts.add(account)

            character_name = p.get("character_name", "").strip()[:100]
            profession = p.get("profession", "").strip()[:50]

            # AccountCharacter：查到就更新 seen_count++，没有就新建
            ac = (
                self.db.query(AccountCharacter)
                .filter(
                    AccountCharacter.account_name == account,
                    AccountCharacter.character_name == character_name,
                )
                .first()
            )
            if ac:
                ac.last_seen_date = today
                ac.seen_count += 1
                if profession and ac.profession != profession:
                    ac.profession = profession
            else:
                self.db.add(
                    AccountCharacter(
                        account_name=account,
                        character_name=character_name,
                        profession=profession,
                        first_seen_date=today,
                        last_seen_date=today,
                        seen_count=1,
                    )
                )

            # Member：只存 account_name，角色信息去 account_characters 查
            member = self.db.query(Member).filter(Member.account_name == account).first()
            if not member:
                member = Member(account_name=account)
                self.db.add(member)

            member_map[account] = member

        # 第二步：flush 获取所有 member.id
        self.db.flush()

        # 第三步：创建 fight_stats（此时 member.id 已可用）
        # 先构建 account -> player 映射（取每个 account 的第一个 player）
        account_to_player: Dict[str, Dict] = {}
        for p in players:
            account = p.get("account", "").strip()
            if account and account not in account_to_player:
                account_to_player[account] = p

        # 【优化】使用 bulk_insert_mappings 批量插入 FightStats，绕过 ORM 跟踪
        fight_stats_mappings = []
        for account, member in member_map.items():
            if account not in account_to_player:
                continue
            p = account_to_player[account]

            # 计算该玩家的评分
            stat_dict = {
                "damage": p.get("damage", 0),
                "power_damage": p.get("power_damage", 0),
                "condi_damage": p.get("condi_damage", 0),
                "healing": p.get("healing", 0),
                "boon_strips": p.get("boon_strips", 0),
                "condition_cleanses": p.get("condition_cleanses", 0),
                "killed": p.get("killed", 0),
                "breakbar_damage": p.get("breakbar_damage", 0),
                "dead_count": p.get("dead_count", 0),
            }
            score_result = ScoringService.calculate_player_score(stat_dict, scoring_rules, max_values)

            fight_stats_mappings.append({
                "fight_id": fight_id,
                "member_id": member.id,
                "account": account,
                "character_name": p.get("character_name", "").strip()[:100],
                "profession": p.get("profession", "").strip()[:50],
                "group_id": p.get("group_id", 1),
                "team_id": p.get("team_id", 0),
                "has_commander_tag": 1 if p.get("has_commander_tag") else 0,
                "damage": p.get("damage", 0),
                "dps": p.get("dps", 0),
                "power_damage": p.get("power_damage", 0),
                "condi_damage": p.get("condi_damage", 0),
                "breakbar_damage": p.get("breakbar_damage", 0),
                "critical_rate": p.get("critical_rate", 0),
                "flanking_rate": p.get("flanking_rate", 0),
                "glance_rate": p.get("glance_rate", 0),
                "missed": p.get("missed", 0),
                "interrupts": p.get("interrupts", 0),
                "swap_count": p.get("swap_count", 0),
                "blocked_count": p.get("blocked_count", 0),
                "evaded_count": p.get("evaded_count", 0),
                "dodge_count": p.get("dodge_count", 0),
                "down_count": p.get("down_count", 0),
                "dead_count": p.get("dead_count", 0),
                "boon_strips": p.get("boon_strips", 0),
                "condition_cleanses": p.get("condition_cleanses", 0),
                "resurrects": p.get("resurrects", 0),
                "condi_cleanse_ally": p.get("condi_cleanse_ally", 0),
                "boon_strips_ally": p.get("boon_strips_ally", 0),
                "might_uptime": p.get("might_uptime", 0),
                "fury_uptime": p.get("fury_uptime", 0),
                "quickness_uptime": p.get("quickness_uptime", 0),
                "alacrity_uptime": p.get("alacrity_uptime", 0),
                "protection_uptime": p.get("protection_uptime", 0),
                "stability_uptime": p.get("stability_uptime", 0),
                "healing": p.get("healing", 0),
                "killed": p.get("killed", 0),
                "damage_taken": p.get("damage_taken", 0),
                "ai_score": score_result["total_score"],
                "score_grade": score_result["grade"][:10] if score_result.get("grade") else "",
                "score_breakdown": score_result["breakdown"],
            })

        if fight_stats_mappings:
            try:
                self.db.bulk_insert_mappings(FightStats, fight_stats_mappings)
                self.db.flush()
            except IntegrityError as exc:
                # 记录完整错误信息，方便排查具体是哪条数据有问题
                logger.error(
                    f"[import] bulk_insert_mappings(FightStats) 失败: "
                    f"fight_id={fight_id}, mappings_count={len(fight_stats_mappings)}, "
                    f"error={exc}",
                    exc_info=True,
                )
                # 尝试逐条插入，精确定位问题记录
                for idx, mapping in enumerate(fight_stats_mappings):
                    try:
                        self.db.bulk_insert_mappings(FightStats, [mapping])
                        self.db.flush()
                    except IntegrityError as inner_exc:
                        logger.error(
                            f"[import] 单条插入失败 idx={idx}, "
                            f"account={mapping.get('account')}, "
                            f"member_id={mapping.get('member_id')}, "
                            f"error={inner_exc}"
                        )
                        raise
                raise

    def _validate_data_integrity(
        self, fight_id: int, log_id: int,
        player_stats: List[Dict[str, Any]], ei_json: Dict[str, Any]
    ) -> List[str]:
        """数据完整性验证。
        在事务提交前检查 fights / fight_stats / ei_player 之间的一致性。
        返回问题列表（空列表表示通过）。
        """
        issues = []

        # 1. 检查 fight_stats 行数与 Fight.player_count 是否一致
        fight = self.db.query(Fight).filter(Fight.id == fight_id).first()
        if fight:
            stats_count = (
                self.db.query(FightStats)
                .filter(FightStats.fight_id == fight_id)
                .count()
            )
            if stats_count != fight.player_count:
                issues.append(
                    f"fight_stats 行数 ({stats_count}) 与 Fight.player_count ({fight.player_count}) 不一致"
                )

        # 2. 检查 fight_stats 中指挥官数量与 ei_player 是否一致
        stats_cmd_count = (
            self.db.query(FightStats)
            .filter(FightStats.fight_id == fight_id, FightStats.has_commander_tag == 1)
            .count()
        )
        ei_cmd_count = (
            self.db.query(EiPlayer)
            .filter(EiPlayer.log_id == log_id, EiPlayer.has_commander_tag == 1)
            .count()
        )
        if stats_cmd_count != ei_cmd_count:
            issues.append(
                f"fight_stats 指挥官数量 ({stats_cmd_count}) 与 ei_player ({ei_cmd_count}) 不一致"
            )

        # 3. 检查 fight_stats 中是否有重复 account（同一 fight 内）
        from sqlalchemy import func
        dup_accounts = (
            self.db.query(FightStats.account)
            .filter(FightStats.fight_id == fight_id)
            .group_by(FightStats.account)
            .having(func.count(FightStats.account) > 1)
            .all()
        )
        if dup_accounts:
            dup_list = [a[0] for a in dup_accounts]
            issues.append(f"fight_stats 中发现重复 account: {dup_list}")

        # 4. 检查 Fight.total_damage 与 fight_stats.damage 总和是否一致（允许 1% 误差）
        if fight and fight.total_damage > 0:
            total_dmg = (
                self.db.query(func.sum(FightStats.damage))
                .filter(FightStats.fight_id == fight_id)
                .scalar() or 0
            )
            if total_dmg > 0:
                diff_ratio = abs(fight.total_damage - total_dmg) / fight.total_damage
                if diff_ratio > 0.01:
                    issues.append(
                        f"Fight.total_damage ({fight.total_damage}) 与 fight_stats 总和 ({total_dmg}) 差异过大 ({diff_ratio:.2%})"
                    )

        return issues

    def _insert_ei_players(self, log_id: int, ei_json: Dict[str, Any], data_source: str = "local_parser"):
        """插入/更新 EiPlayer（技能循环、stats、defenses、deathRecap 等）
        过滤假玩家 / NPC，确保 ei_player 与 fight_stats 数据一致。
        【优化】使用 bulk_insert_mappings 绕过 ORM 跟踪，降低内存峰值。
        """
        from sqlalchemy import text

        self.db.execute(
            text("DELETE FROM ei_player WHERE log_id = :log_id"), {"log_id": log_id}
        )
        self.db.flush()

        mappings = []
        for idx, p in enumerate(ei_json.get("players", [])):
            # 过滤假玩家 / NPC
            if self._should_skip_player(p):
                logger.info(f"[import] EiPlayer 跳过假玩家/NPC: {p.get('account')} / {p.get('name')}")
                continue

            has_cmd = self._resolve_commander_tag(p, None, data_source)

            mappings.append({
                "log_id": log_id,
                "agent_index": idx,
                "account": p.get("account", ""),
                "character_name": p.get("name", ""),
                "profession": p.get("profession", ""),
                "group_id": p.get("group", 1),
                "has_commander_tag": 1 if has_cmd else 0,
                "is_fake": 1 if p.get("isFake") else 0,
                "weapons_json": p.get("weapons") or None,
                "consumables_json": p.get("consumables") or None,
                "dps_all_json": p.get("dpsAll") or None,
                "stats_all_json": p.get("statsAll") or None,
                "defenses_json": p.get("defenses") or None,
                "support_json": p.get("support") or None,
                "buff_uptimes_json": p.get("buffUptimes") or None,
                "rotation_json": p.get("rotation") or None,
                "death_recap_json": p.get("deathRecap") or None,
            })

        if mappings:
            self.db.bulk_insert_mappings(EiPlayer, mappings)
            self.db.flush()

    def _insert_skill_maps(self, log_id: int, ei_json: Dict[str, Any]):
        """插入/更新 EiSkillMap（技能映射，name 去除双引号）
        【优化】使用 bulk_insert_mappings 绕过 ORM 跟踪，降低内存峰值。
        """
        from sqlalchemy import text

        self.db.execute(
            text("DELETE FROM ei_skill_map WHERE log_id = :log_id"), {"log_id": log_id}
        )
        self.db.flush()

        mappings = []
        for sk_key, sk in ei_json.get("skillMap", {}).items():
            name = sk.get("name", "")
            # 去除 name 中可能存在的首尾双引号
            if isinstance(name, str):
                name = name.strip('"')
            mappings.append({
                "log_id": log_id,
                "skill_key": sk_key,
                "gw2_skill_id": (
                    sk.get("gw2_skill_id", 0) or int(sk_key.lstrip("s"))
                    if sk_key.startswith("s") and sk_key[1:].isdigit()
                    else 0
                ),
                "name": name,
                "auto_attack": 1 if sk.get("autoAttack") else 0,
                "can_crit": 1 if sk.get("canCrit") else 0,
                "is_swap": 1 if sk.get("isSwap") else 0,
                "is_instant_cast": 1 if sk.get("isInstantCast") else 0,
                "is_trait_proc": 1 if sk.get("isTraitProc") else 0,
                "icon": sk.get("icon", ""),
            })

        if mappings:
            self.db.bulk_insert_mappings(EiSkillMap, mappings)
            self.db.flush()

    def _insert_targets(self, log_id: int, ei_json: Dict[str, Any]):
        """插入/更新 EiTarget（敌方目标等）
        【优化】使用 bulk_insert_mappings 绕过 ORM 跟踪，降低内存峰值。
        """
        from sqlalchemy import text

        self.db.execute(
            text("DELETE FROM ei_target WHERE log_id = :log_id"), {"log_id": log_id}
        )
        self.db.flush()

        mappings = []
        for idx, t in enumerate(ei_json.get("targets", [])):
            mappings.append({
                "log_id": log_id,
                "agent_index": idx,
                "name": t.get("name", ""),
                "enemy_player": 1 if t.get("enemyPlayer") else 0,
                "total_health": t.get("totalHealth", 0),
                "final_health": t.get("finalHealth", 0),
                "health_percent_burned": t.get("healthPercentBurned", 0),
                "dps_all_json": t.get("dpsAll") or None,
                "defenses_json": t.get("defenses") or None,
            })

        if mappings:
            self.db.bulk_insert_mappings(EiTarget, mappings)
            self.db.flush()

    def cleanup_file(self, log_id: int) -> Dict[str, Any]:
        """显式清理指定日志的源文件

        功能：删除已解析日志的源文件
        参数：log_id - 日志ID
        返回：成功返回 {"success": True}，失败返回 {"success": False, "error": 错误信息}

        说明：
        - 用户在确认解析数据正确后，可调用此方法删除源文件
        - 如果解析数据有误，用户可以保留源文件重新解析
        - 文件删除后，log.file_path 将被设置为 None
        """
        from app.models.log import Log

        try:
            log = self.db.query(Log).filter(Log.id == log_id).first()
            if not log:
                return {"success": False, "error": f"日志不存在: {log_id}"}

            file_path = log.file_path
            if not file_path:
                return {"success": False, "error": "文件路径为空，可能已被删除"}

            if not os.path.exists(file_path):
                # 文件不存在，标记为已清理
                log.file_path = None
                self.db.commit()
                return {"success": True, "message": "文件不存在，已更新数据库记录"}

            # 删除文件
            os.remove(file_path)
            logger.info(f"已删除日志文件: log_id={log_id}, path={file_path}")

            # 更新数据库中的文件路径
            log.file_path = None
            self.db.commit()

            return {"success": True, "message": f"文件已删除: {file_path}"}

        except Exception as e:
            logger.error(f"清理文件失败 log_id={log_id}: {e}", exc_info=True)
            self.db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def cleanup_files_batch(log_ids: List[int]) -> Dict[str, Any]:
        """批量清理指定日志的源文件

        功能：批量删除多个日志的源文件
        参数：log_ids - 日志ID列表
        返回：{"success": True, "deleted_count": N, "failed_count": M, "errors": [...]}
        """
        from app.config.database import SessionLocal
        from app.models.log import Log

        db = SessionLocal()
        deleted_count = 0
        failed_count = 0
        errors = []

        try:
            for log_id in log_ids:
                try:
                    log = db.query(Log).filter(Log.id == log_id).first()
                    if not log:
                        errors.append(f"log_id={log_id}: 日志不存在")
                        failed_count += 1
                        continue

                    file_path = log.file_path
                    if not file_path:
                        errors.append(f"log_id={log_id}: 文件路径为空")
                        failed_count += 1
                        continue

                    if not os.path.exists(file_path):
                        log.file_path = None
                        deleted_count += 1
                        continue

                    os.remove(file_path)
                    log.file_path = None
                    deleted_count += 1
                    logger.info(f"批量删除日志文件: log_id={log_id}")

                except Exception as e:
                    errors.append(f"log_id={log_id}: {str(e)}")
                    failed_count += 1

            db.commit()
            return {
                "success": failed_count == 0,
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"批量清理文件异常: {e}", exc_info=True)
            db.rollback()
            return {
                "success": False,
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "errors": errors + [str(e)],
            }
        finally:
            db.close()

    def _delete_file(self, file_path: str):
        """内部方法：安全删除文件（私有方法，不建议外部调用）"""
        try:
            os.remove(file_path)
            logger.info(f"已删除解析文件: {file_path}")
        except Exception as e:
            logger.warning(f"删除文件失败 {file_path}: {e}")

    @staticmethod
    def _parse_ei_time(time_str: str) -> datetime:
        """将 EI 时间字符串解析为 datetime

        支持格式：
            - ISO 8601: 2026-04-14T11:29:53.1234567-04:00
            - EI 自定义: 2026-04-14 11:29:53 +00:00
            - 纯日期: 2026-04-14
        """
        if not time_str:
            return None
        ts = str(time_str).strip()
        # 1. 直接 ISO 8601（含小数秒和时区）
        try:
            return datetime.fromisoformat(ts)
        except ValueError:
            pass
        # 2. EI 自定义格式: "2026-04-14 11:29:53 +00:00"
        try:
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            pass
        # 3. 处理 " +" / " -" 空格的变体
        try:
            return datetime.fromisoformat(
                ts.replace(" +", "+").replace(" -", "-")
            )
        except ValueError:
            pass
        # 4. 纯日期
        try:
            return datetime.strptime(ts, "%Y-%m-%d")
        except ValueError:
            pass
        logger.warning(f"[import] 无法解析时间字符串: {time_str}")
        return None
