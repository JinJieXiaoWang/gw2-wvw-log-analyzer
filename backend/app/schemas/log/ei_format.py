# -*- coding: utf-8 -*-
# 模块功能：EI格式数据Schema定义
# 作者：系统
# 创建日期?2026-04-28
# 依赖说明：Pydantic

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

"""
基于Elite Insights 2.59.0.0输出格式
"""


# ============ 基础类型 ============
class DpsStats(BaseModel):
    dps: int = 0
    damage: int = 0
    condiDps: int = 0
    condiDamage: int = 0
    powerDps: int = 0
    powerDamage: int = 0
    breakbarDamage: float = 0.0
    actorDps: int = 0
    actorDamage: int = 0
    actorCondiDps: int = 0
    actorCondiDamage: int = 0
    actorPowerDps: int = 0
    actorPowerDamage: int = 0
    actorBreakbarDamage: float = 0.0


class CombatStats(BaseModel):
    wasted: int = 0
    timeWasted: float = 0.0
    saved: int = 0
    timeSaved: float = 0.0
    stackDist: float = 0.0
    distToCom: float = 0.0
    avgBoons: float = 0.0
    avgActiveBoons: float = 0.0
    avgConditions: float = 0.0
    avgActiveConditions: float = 0.0
    swapCount: int = 0
    skillCastUptime: float = 0.0
    skillCastUptimeNoAA: float = 0.0
    totalDamageCount: int = 0
    totalDmg: int = 0
    directDamageCount: int = 0
    directDmg: int = 0
    connectedDirectDamageCount: int = 0
    connectedDirectDmg: int = 0
    connectedDamageCount: int = 0
    connectedDmg: int = 0
    critableDirectDamageCount: int = 0
    criticalRate: float = 0.0
    criticalDmg: int = 0
    flankingRate: float = 0.0
    againstMovingRate: float = 0.0
    glanceRate: float = 0.0
    missed: int = 0
    evaded: int = 0
    blocked: int = 0
    interrupts: int = 0
    invulned: int = 0
    killed: int = 0
    downed: int = 0
    downContribution: int = 0


class Target(BaseModel):
    id: int = 0
    finalHealth: int = 0
    healthPercentBurned: float = 0.0
    firstAware: int = 0
    lastAware: int = 0
    buffs: List = []
    enemyPlayer: bool = False
    breakbarPercents: List = []
    name: str = ""
    totalHealth: int = -1
    condition: int = 0
    concentration: int = 0
    healing: int = 0
    toughness: int = 0
    hitboxHeight: int = 0
    hitboxWidth: int = 0
    instanceID: int = 0
    teamID: int = 0
    isFake: bool = False
    dpsAll: List[DpsStats] = []
    statsAll: List[CombatStats] = []


class Player(BaseModel):
    account: str = ""
    group: int = 1
    hasCommanderTag: bool = False
    profession: str = ""
    friendlyNPC: bool = False
    notInSquad: bool = False
    guildID: str = ""
    weapons: List[str] = []
    dpsTargets: List[List[DpsStats]] = []
    targetDamage1S: List = []
    targetPowerDamage1S: List = []
    targetConditionDamage1S: List = []
    targetDamageDist: List = []
    dpsAll: List[DpsStats] = []
    statsTargets: List = []
    statsAll: List[CombatStats] = []
    support: Dict = {}
    buffUptimes: List = []
    selfBuffs: List = []
    buffUptimesActive: List = []
    selfBuffsActive: List = []
    activeTimes: List = []
    name: str = ""
    totalHealth: int = -1
    condition: int = 0
    concentration: int = 0
    healing: int = 0
    toughness: int = 0
    hitboxHeight: int = 0
    hitboxWidth: int = 0
    instanceID: int = 0
    teamID: int = 0
    isFake: bool = False
    rotation: List = []
    damageModifiers: List = []
    damageModifiersTarget: List = []
    healthPercents: List = []
    barrierPercents: List = []


class Phase(BaseModel):
    start: int = 0
    end: int = 0
    name: str = ""
    targets: List = []


class SkillEntry(BaseModel):
    name: str = ""
    autoAttack: bool = False
    canCrit: bool = False
    icon: str = ""


class BuffEntry(BaseModel):
    name: str = ""
    icon: str = ""
    stacking: bool = False
    conversionBasedHealing: bool = False


class DamageModEntry(BaseModel):
    name: str = ""
    icon: str = ""
    description: str = ""
    nonMultiplier: bool = False


# ============ 主数据结?============
class EIFormatData(BaseModel):
    eliteInsightsVersion: str = "2.59.0.0"
    triggerID: int = 1
    eiEncounterID: int = 0
    fightName: str = ""
    fightIcon: str = ""
    arcVersion: str = ""
    gW2Build: int = 0
    language: str = "Chinese"
    fractalScale: int = 0
    languageID: int = 5
    recordedBy: str = ""
    recordedAccountBy: str = ""
    timeStart: str = ""
    timeEnd: str = ""
    timeStartStd: str = ""
    timeEndStd: str = ""
    duration: str = ""
    durationMS: int = 0
    logStartOffset: int = 0
    success: bool = True
    isCM: bool = False
    anonymous: bool = False
    detailedWvW: bool = True
    targets: List[Target] = []
    players: List[Player] = []
    phases: List[Phase] = []
    skillMap: Dict[str, SkillEntry] = {}
    buffMap: Dict[str, BuffEntry] = {}
    damageModMap: Dict[str, DamageModEntry] = {}


# ============ API响应模型 ============
class LogAnalysisResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[EIFormatData] = None
    rawDataUrl: Optional[str] = None
    parsedAt: str = ""


class LogListResponse(BaseModel):
    success: bool = True
    message: str = ""
    total: int = 0
    page: int = 1
    pageSize: int = 20
    items: List[Dict] = []
