
# -*- coding: utf-8 -*-
# 模块功能：ORM 模型统一导入
# 说明：确保所有模型类注册到 Base.metadata

import sys
from pathlib import Path

# 强制从文件加载 log 模块，而不是从目录加载
if 'app.models.log' not in sys.modules:
    log_file = Path(__file__).parent / 'log.py'
    import importlib.util
    spec = importlib.util.spec_from_file_location('app.models.log', log_file)
    log_module = importlib.util.module_from_spec(spec)
    sys.modules['app.models.log'] = log_module
    spec.loader.exec_module(log_module)

from app.models.account_character import AccountCharacter
from app.models.ai_report import AIReport
from app.models.build import Build
from app.models.batch_parse import BatchParseTask, BatchParseTaskItem
from app.models.dictionary import SysDictData, SysDictType
from app.models.ei_report import EiReport
from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.log import Log
from app.models.member import Member
from app.models.storage import StorageCleanupRecord, StorageMonitorRecord
from app.models.sys_user import SysUser
from app.models.scoring_rule import ScoringRule, ScoringRulePreset
from app.models.scoring_rule_version import ScoringRuleVersion
from app.models.sys_config import SysConfig
from app.models.sys_notice import SysNotice, SysNoticeRead
from app.models.zevtc_data import EiPhase, EiPlayer, EiSkillMap, EiTarget

