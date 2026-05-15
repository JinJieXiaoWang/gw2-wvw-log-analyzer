
# -*- coding: utf-8 -*-
# 模块功能：ORM 模型统一导入
# 说明：确保所有模型类注册到 Base.metadata

from app.models.auth.account_character import AccountCharacter
from app.models.auth.member import Member
from app.models.auth.sys_user import SysUser
from app.models.game.build import Build
from app.models.game.dictionary import SysDictData, SysDictType
from app.models.game.game_static_data import (
    GwBuff,
    GwSkill,
    GwSkillPalette,
    GwSpecialization,
    GwTrait,
)
from app.models.game.profession import GwEliteSpecialization, GwProfession, GwRoleType
from app.models.log.batch_parse import BatchParseTask, BatchParseTaskItem
from app.models.log.ei_report import EiReport
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats
from app.models.log.log import Log
from app.models.log.zevtc_data import EiPhase, EiPlayer, EiSkillMap, EiTarget
from app.models.scoring.scoring_rule import ScoringRule, ScoringRulePreset
from app.models.scoring.scoring_rule_version import ScoringRuleVersion
from app.models.system.ai_report import AIReport
from app.models.system.storage import StorageCleanupRecord, StorageMonitorRecord
from app.models.system.sys_config import SysConfig
from app.models.system.sys_data_version import SysDataVersion
from app.models.system.sys_menu import SysMenu
from app.models.system.sys_notice import SysNotice, SysNoticeRead
