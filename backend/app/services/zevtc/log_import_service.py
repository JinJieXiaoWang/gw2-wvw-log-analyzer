# -*- coding: utf-8 -*-
# 模块功能：日志导入服务（parse → scalar extraction → DB insert）
# 作者：系统
# 创建日期：2026-04-27
# 更新日期：2026-05-04
# 说明：
#   1. 使用 dps.report API 获取高质量 EI JSON 数据
#   2. 数据验证：确保关键字段的存在和有效性
#   3. 字段映射：统一不同数据源的字段名
#   4. 写入 fights (1 行) + fight_stats (~50 行) + members（更新或插入）
#   5. 重要：不自动删除源文件，保留用户重新解析的可能性
#   6. 用户确认数据正确后，可调用 cleanup_file() 或 cleanup_files_batch() 删除文件

import gc
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
    def _resolve_commander_tag(ei_player: Dict) -> bool:
        """从 EI JSON 解析指挥官标记。"""
        if "hasCommanderTag" in ei_player:
            return bool(ei_player["hasCommanderTag"])
        if "isCommander" in ei_player:
            return bool(ei_player["isCommander"])
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

    def import_log(self, log_id: int, file_path: str) -> Dict[str, Any]:
        """主入口：导入单个日志文件（完全依赖 dps.report API）。

        流程：
        1. 调用 dps.report API 获取 EI JSON
        2. 数据验证
        3. 字段映射
        4. 数据库存储
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"文件不存在: {file_path}"}

        try:
            # =============================================
            # 步骤 1: 调用 dps.report API
            # =============================================
            dps_result = upload_and_parse(file_path)
            # 【内存优化】pop 出 ei_json，让 dps_result 提前释放引用
            ei_json = dps_result.pop("ei_json", {})
            permalink = dps_result.pop("permalink", None)
            del dps_result
            logger.info("[import] dps.report 解析成功")

            # =============================================
            # 步骤 2: 数据验证
            # =============================================
            logger.info("[import] 开始验证数据")
            valid_players, valid_encounter, errors, warnings = EIJsonValidator.validate_ei_json(ei_json)

            if errors:
                logger.warning(f"[import] 数据验证发现 {len(errors)} 个错误: {errors}")
            if warnings:
                logger.info(f"[import] 数据验证发现 {len(warnings)} 个警告: {warnings}")

            if not valid_players:
                logger.warning("[import] 没有通过验证的玩家数据，但将继续处理")

            logger.info(f"[import] 数据验证完成，有效玩家数: {len(valid_players)}")

            # =============================================
            # 步骤 2.5: 丢弃不需要的大字段，降低内存峰值
            # =============================================
            dropped_fields = []
            for big_field in ("phases", "mechanics", "combatReplayData"):
                if big_field in ei_json:
                    ei_json.pop(big_field, None)
                    dropped_fields.append(big_field)
            if dropped_fields:
                logger.info(f"[import] 已丢弃 EI JSON 大字段: {dropped_fields}，降低内存峰值")

            # =============================================
            # 步骤 3: 提取标量数据
            # =============================================
            fight_data = self._extract_fight_data(ei_json)
            player_stats = self._extract_player_stats(ei_json)

            # =============================================
            # 步骤 4: 写入数据库
            # =============================================
            fight = self._insert_fight(log_id, fight_data)
            self._insert_players(fight.id, player_stats)

            # 【内存优化】player_stats 和 fight_data 已用完，立即释放
            players_count = len(player_stats)
            del player_stats, fight_data
            gc.collect()

            # =============================================
            # 步骤 5: 更新 Log 状态
            # =============================================
            log = self.db.query(Log).filter(Log.id == log_id).first()
            if log:
                log.parse_status = "completed"
                log.parsed_at = datetime.now(timezone.utc)
                log.parse_time_ms = ei_json.get("durationMS", 0)
                log.parser = "dps_report_ei_v1"
                log.parsed_data = None
                if permalink:
                    log.dps_report_permalink = permalink
                self.db.flush()

            # =============================================
            # 步骤 6: 同步 EI Player 数据
            # =============================================
            self._insert_ei_players(log_id, ei_json)
            ei_json.pop("players", None)
            ei_json.pop("deathRecap", None)
            gc.collect()

            self._insert_skill_maps(log_id, ei_json)
            ei_json.pop("skillMap", None)

            self._insert_targets(log_id, ei_json)
            ei_json.pop("targets", None)
            gc.collect()

            # =============================================
            # 步骤 7: 数据完整性验证
            # =============================================
            # 【v4.0】player_stats 已释放，完整性验证简化为数据库查询对比
            integrity_issues = self._validate_data_integrity(fight.id, log_id)
            if integrity_issues:
                logger.warning(f"[import] 数据完整性检查发现 {len(integrity_issues)} 个问题: {integrity_issues}")

            # =============================================
            # 步骤 8: 提交事务
            # =============================================
            self.db.commit()

            # =============================================
            # 步骤 9: 保留源文件，不自动删除
            # =============================================
            result = {
                "success": True,
                "fight_id": fight.id,
                "players_count": players_count,
                "map_name": fight.map_name,
                "duration_sec": fight.duration_sec,
                "data_source": "dps_report",
                "validation_errors": errors,
                "validation_warnings": warnings,
                "integrity_issues": integrity_issues,
            }
            del ei_json
            gc.collect()
            return result

        except Exception as e:
            logger.error(f"导入日志失败 log_id={log_id}: {e}", exc_info=True)
            try:
                self.db.rollback()
            except Exception:
                pass
            return {"success": False, "error": str(e)}

    def _extract_fight_data(self, ei_json: Dict) -> Dict[str, Any]:
        """提取战斗级标量数据（直接从 EI JSON）。"""
        ei_duration_ms = ei_json.get("durationMS", 0)
        duration_sec = max(1, int(ei_duration_ms / 1000))

        ei_start = ei_json.get("timeStartStd") or ei_json.get("timeStart")
        ei_end = ei_json.get("timeEndStd") or ei_json.get("timeEnd")

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

        parsed_start = self._parse_ei_time(ei_start)
        parsed_end = self._parse_ei_time(ei_end)

        if not parsed_start:
            logger.warning(f"[import] 无法解析开始时间: {ei_start}，使用当前时间")
            parsed_start = datetime.now(timezone.utc)
        if not parsed_end:
            parsed_end = parsed_start

        return {
            "start_time": parsed_start,
            "end_time": parsed_end,
            "duration_sec": duration_sec,
            "duration_ms": ei_duration_ms,
            "map_name": ei_json.get("fightName"),
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

    def _extract_player_stats(self, ei_json: Dict) -> List[Dict[str, Any]]:
        """提取每个玩家的标量统计（直接从 EI JSON）。"""
        results = []

        for ei_p in ei_json.get("players", []):
            if self._should_skip_player(ei_p):
                continue

            dps_all = ei_p.get("dpsAll", [{}])[0]
            stats_all = ei_p.get("statsAll", [{}])[0]
            defenses = ei_p.get("defenses", [{}])[0]
            support = ei_p.get("support", [{}])[0]

            # 从 buffUptimes / buffUptimesActive 中提取覆盖率
            # 注：EI JSON 中 buffUptimes 项使用 id 而非 name 标识增益，
            # 尤其在 detailed WvW 模式下 name 字段可能缺失。
            # 另外，uptime 可能位于 buffData[0].uptime 而非顶层。
            BUFF_ID_MAP = {
                725: "might",
                726: "fury",
                740: "quickness",
                743: "alacrity",
                717: "protection",
                1122: "stability",
            }

            def _extract_uptime(bu: dict) -> float:
                """兼容多种 buffUptimes 结构提取 uptime。"""
                # 方案1：顶层 uptime（常规 EI）
                uptime = bu.get("uptime")
                if uptime is not None:
                    return uptime
                # 方案2：buffData[0].uptime（detailed WvW）
                buff_data = bu.get("buffData")
                if buff_data and isinstance(buff_data, list) and len(buff_data) > 0:
                    return buff_data[0].get("uptime", 0)
                return 0

            buff_uptimes = {}
            for bu in ei_p.get("buffUptimes", []):
                buff_id = bu.get("id")
                name = bu.get("name", "")
                uptime = _extract_uptime(bu)
                if buff_id and buff_id in BUFF_ID_MAP:
                    buff_uptimes[BUFF_ID_MAP[buff_id]] = uptime
                elif name:
                    buff_uptimes[name.lower()] = uptime

            buff_uptimes_active = {}
            for bu in ei_p.get("buffUptimesActive", []):
                buff_id = bu.get("id")
                name = bu.get("name", "")
                uptime = _extract_uptime(bu)
                if buff_id and buff_id in BUFF_ID_MAP:
                    buff_uptimes_active[BUFF_ID_MAP[buff_id]] = uptime
                elif name:
                    buff_uptimes_active[name.lower()] = uptime

            has_cmd = self._resolve_commander_tag(ei_p)

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
                "condi_cleanse_ally": max(
                    0, support.get("condiCleanse", 0) - support.get("condiCleanseSelf", 0)
                ),
                "boon_strips_ally": support.get("boonStrips", 0),
                "might_uptime": buff_uptimes.get("might", 0),
                "fury_uptime": buff_uptimes.get("fury", 0),
                "quickness_uptime": buff_uptimes.get("quickness", 0),
                "alacrity_uptime": buff_uptimes.get("alacrity", 0),
                "protection_uptime": buff_uptimes.get("protection", 0),
                "stability_uptime": buff_uptimes.get("stability", 0),
                "healing": self._extract_player_healing(ei_p),
                "killed": stats_all.get("killed", 0),
                "downed": stats_all.get("downed", 0),
                "damage_taken": defenses.get("damageTaken", 0),
                # === 高级战斗指标（dps.report API 专有）===
                "down_contribution": dps_all.get("downContribution", 0),
                "against_downed_damage": dps_all.get("againstDownedDamage", 0),
                "applied_cc_duration": support.get("appliedCcDuration", 0),
                "barrier_damage_absorbed": defenses.get("damageBarrier", 0),
                "condition_damage_taken": defenses.get("conditionDamageTaken", 0),
                "power_damage_taken": defenses.get("powerDamageTaken", 0),
                "received_cc_duration": support.get("receivedCcDuration", 0),
                "might_uptime_active": buff_uptimes_active.get("might", 0),
                "quickness_uptime_active": buff_uptimes_active.get("quickness", 0),
                "alacrity_uptime_active": buff_uptimes_active.get("alacrity", 0),
                "avg_boons": stats_all.get("avgBoons", 0),
                "avg_conditions": stats_all.get("avgConditions", 0),
                # === 技能效率与位置（EI 扩展字段）===
                "wasted": stats_all.get("wasted", 0),
                "saved": stats_all.get("saved", 0),
                "skill_cast_uptime": stats_all.get("skillCastUptime", 0),
                "stack_dist": stats_all.get("stackDist", 0),
                "dist_to_com": stats_all.get("distToCom", 0),
                # === 倒地/死亡详情（EI 扩展字段）===
                "downed_damage_taken": defenses.get("downedDamageTaken", 0),
                "interrupted_count": defenses.get("interruptedCount", 0),
                "down_duration": defenses.get("downDuration", 0),
                "dead_duration": defenses.get("deadDuration", 0),
                "dc_count": defenses.get("dcCount", 0),
                "dc_duration": defenses.get("dcDuration", 0),
                # === 支援详情（EI 扩展字段）===
                "stun_break": support.get("stunBreak", 0),
                "removed_stun_duration": support.get("removedStunDuration", 0),
                # === CC 输出详情 ===
                "applied_cc_count": stats_all.get("appliedCrowdControl", 0),
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

        【v4.0 变更】删除导入时评分计算，只保存原始数据。
        评分移至查询阶段（PlayerScoreService），规则更新立即生效。
        """
        from datetime import date
        from app.models.account_character import AccountCharacter

        today = date.today()
        seen_accounts: set = set()
        member_map: Dict[str, Member] = {}

        # 【优化】批量预查询：收集所有 account 和 account-character 对
        needed_accounts = set()
        needed_pairs = set()
        for p in players:
            account = p.get("account", "").strip()[:100]
            if account:
                needed_accounts.add(account)
                needed_pairs.add((account, p.get("character_name", "").strip()[:100]))

        # 【优化】一次性查询所有已存在的 AccountCharacter（2次查询替代N次）
        existing_acs = {}
        if needed_pairs:
            existing_acs = {
                (ac.account_name, ac.character_name): ac
                for ac in self.db.query(AccountCharacter).filter(
                    tuple_(AccountCharacter.account_name, AccountCharacter.character_name).in_(needed_pairs)
                ).all()
            }

        # 【优化】一次性查询所有已存在的 Member
        existing_members = {}
        if needed_accounts:
            existing_members = {
                m.account_name: m
                for m in self.db.query(Member).filter(Member.account_name.in_(needed_accounts)).all()
            }

        # 第一步：处理 Member 和 AccountCharacter（内存字典 O(1) 查找）
        new_acs = []
        for p in players:
            account = p.get("account", "").strip()[:100]
            if not account:
                continue
            if account in seen_accounts:
                continue
            seen_accounts.add(account)

            character_name = p.get("character_name", "").strip()[:100]
            profession = p.get("profession", "").strip()[:50]

            # AccountCharacter：内存字典查找 O(1)，替代数据库查询
            ac = existing_acs.get((account, character_name))
            if ac:
                ac.last_seen_date = today
                ac.seen_count += 1
                if profession and ac.profession != profession:
                    ac.profession = profession
            else:
                new_acs.append(AccountCharacter(
                    account_name=account,
                    character_name=character_name,
                    profession=profession,
                    first_seen_date=today,
                    last_seen_date=today,
                    seen_count=1,
                ))

            # Member：内存字典查找 O(1)
            member = existing_members.get(account)
            if not member:
                member = Member(account_name=account)
                self.db.add(member)
                existing_members[account] = member

            member_map[account] = member

        # 批量插入新的 AccountCharacter
        if new_acs:
            self.db.add_all(new_acs)

        # 第二步：flush 获取所有 member.id / ac.id
        self.db.flush()

        # 第三步：创建 fight_stats（此时 member.id 已可用）
        # 先构建 account -> player 映射（取每个 account 的第一个 player）
        account_to_player: Dict[str, Dict] = {}
        for p in players:
            account = p.get("account", "").strip()
            if account and account not in account_to_player:
                account_to_player[account] = p

        # 【v4.0】使用 bulk_insert_mappings 批量插入原始数据，绕过 ORM 跟踪
        # 评分字段不再在导入时计算（ai_score / score_grade / score_breakdown / role_type / rule_version）
        fight_stats_mappings = []
        for account, member in member_map.items():
            if account not in account_to_player:
                continue
            p = account_to_player[account]

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
                "downed": p.get("downed", 0),
                "damage_taken": p.get("damage_taken", 0),
                "down_contribution": p.get("down_contribution", 0),
                "against_downed_damage": p.get("against_downed_damage", 0),
                "applied_cc_duration": p.get("applied_cc_duration", 0),
                "barrier_damage_absorbed": p.get("barrier_damage_absorbed", 0),
                "condition_damage_taken": p.get("condition_damage_taken", 0),
                "power_damage_taken": p.get("power_damage_taken", 0),
                "received_cc_duration": p.get("received_cc_duration", 0),
                "might_uptime_active": p.get("might_uptime_active", 0),
                "quickness_uptime_active": p.get("quickness_uptime_active", 0),
                "alacrity_uptime_active": p.get("alacrity_uptime_active", 0),
                "avg_boons": p.get("avg_boons", 0),
                "avg_conditions": p.get("avg_conditions", 0),
                # === 技能效率与位置（EI 扩展字段）===
                "wasted": p.get("wasted", 0),
                "saved": p.get("saved", 0),
                "skill_cast_uptime": p.get("skill_cast_uptime", 0),
                "stack_dist": p.get("stack_dist", 0),
                "dist_to_com": p.get("dist_to_com", 0),
                # === 倒地/死亡详情（EI 扩展字段）===
                "downed_damage_taken": p.get("downed_damage_taken", 0),
                "interrupted_count": p.get("interrupted_count", 0),
                "down_duration": p.get("down_duration", 0),
                "dead_duration": p.get("dead_duration", 0),
                "dc_count": p.get("dc_count", 0),
                "dc_duration": p.get("dc_duration", 0),
                # === 支援详情（EI 扩展字段）===
                "stun_break": p.get("stun_break", 0),
                "removed_stun_duration": p.get("removed_stun_duration", 0),
                # === CC 输出详情 ===
                "applied_cc_count": p.get("applied_cc_count", 0),
                # 评分字段留空，查询时计算
                "ai_score": 0,
                "score_grade": "",
                "score_breakdown": None,
                "role_type": None,
                "rule_version": 0,
                "scoring_profession_rule": None,
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
        self, fight_id: int, log_id: int
    ) -> List[str]:
        """数据完整性验证（v4.0 纯数据库查询版）。
        在事务提交前检查 fights / fight_stats / ei_player 之间的一致性。
        返回问题列表（空列表表示通过）。
        """
        from sqlalchemy import func
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

    def _insert_ei_players(self, log_id: int, ei_json: Dict[str, Any]):
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

            has_cmd = self._resolve_commander_tag(p)

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
