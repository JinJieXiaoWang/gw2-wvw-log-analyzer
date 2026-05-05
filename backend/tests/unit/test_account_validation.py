# -*- coding: utf-8 -*-
# 模块功能：账号名称验证单元测试
# 作者：系统
# 创建日期：2026-05-06

import pytest

from app.services.zevtc.data_validator import EIJsonValidator


class TestAccountNameValidation:
    """账号名称验证测试类"""

    def test_valid_account_names(self):
        """测试有效账号名称 - 所有真实玩家账号都应该能通过"""
        valid_accounts = [
            "Player.1234",
            "JohnDoe",
            "GW2_Player_01",
            "Test-Account",
            "aa",
            "a" * 100,  # 即使很长也允许
            "Valid_Account.123",
            "My_Guild_Member",
            "123Invalid",  # 以数字开头也允许
            "player@name",  # 包含特殊字符也允许
            "player#name",  # 包含特殊字符也允许
            "player name",  # 包含空格也允许
            "a",  # 单个字符也允许
        ]
        
        for account in valid_accounts:
            assert EIJsonValidator.is_valid_account_name(account) is True, f"应该接受有效账号: {account}"

    def test_empty_account_name(self):
        """测试空账号名称"""
        empty_accounts = [
            "",
            "   ",
            None,
        ]
        
        for account in empty_accounts:
            assert EIJsonValidator.is_valid_account_name(account) is False, f"应该拒绝空账号: {account!r}"

    def test_blacklisted_account_names(self):
        """测试黑名单账号名称 - 只有 Non Squad Player 及其变体才拒绝"""
        blacklisted_accounts = [
            "Non Squad Player",
            "Non Squad Player 1",
            "Non Squad Player 2",
            "Non Squad Player 34",
            "Non Squad Player 100",
            "non squad player",  # 大小写不敏感
            "NON SQUAD PLAYER 123",
        ]
        
        for account in blacklisted_accounts:
            assert EIJsonValidator.is_valid_account_name(account) is False, f"应该拒绝黑名单账号: {account}"

    def test_non_blacklisted_allowed(self):
        """测试不在黑名单中的账号都允许通过（包括真实玩家账号和其他特殊名称）"""
        # 真实玩家账号（带 .XXXX 后缀）
        # NPC、Gadget 等开头的账号也允许通过（可能是真实玩家的角色名）
        allowed_accounts = [
            # 真实玩家账号格式
            "Player.1234",
            "JohnDoe.5678",
            "GW2_Player.0123",
            # 带数字的账号
            "Player 123",
            "Player 1",
            "Player 2",
            "Player 3",
            # NPC 开头的账号（可能是真实玩家角色名）
            "NPC一号",
            "NPC_Enemy",
            "NPC Boss",
            # 其他特殊名称
            "Unknown Player",
            "Gadget_Turret",
            "Minion_Fire",
            "Pet_Bear",
            "Summon_Elemental",
            "Clone_Mesmer",
            "Phantom_Thief",
            "Turret_Engineer",
            "Golem_Master",
            "Broken_Link",
            "Error_404",
            "Invalid_Account",
            "Test Account",
            "Anonymous_User",
            "Unnamed_Character",
        ]
        
        for account in allowed_accounts:
            assert EIJsonValidator.is_valid_account_name(account) is True, f"应该允许非黑名单账号: {account}"

    def test_validate_account_name_detailed(self):
        """测试详细验证结果"""
        test_cases = [
            ("", False, "账号名称为空或不是字符串"),
            ("   ", False, "账号名称为空"),
            ("Non Squad Player", False, "黑名单"),
            ("Non Squad Player 1", False, "黑名单"),
            ("Unknown Player", True, "验证通过"),  # 不在黑名单中，允许通过
            ("Player 123", True, "验证通过"),     # 不在黑名单中，允许通过
            ("Player.1234", True, "验证通过"),    # 真实玩家账号格式，允许通过
            ("NPC一号", True, "验证通过"),        # NPC开头也允许通过
            ("ValidAccount", True, "验证通过"),
        ]
        
        for account, expected_valid, expected_reason in test_cases:
            valid, reason = EIJsonValidator.validate_account_name(account)
            assert valid == expected_valid, f"账号 {account!r} 的验证结果不正确"
            if expected_reason == "黑名单":
                assert "黑名单" in reason, f"账号 {account!r} 的拒绝原因不正确: {reason}"
            elif expected_reason == "账号名称为空":
                assert "账号名称为空" in reason, f"账号 {account!r} 的拒绝原因不正确: {reason}"
            elif expected_valid:
                assert reason == "验证通过", f"账号 {account!r} 的验证原因不正确: {reason}"

    def test_case_insensitive_blacklist(self):
        """测试黑名单大小写不敏感"""
        variations = [
            "Non Squad Player",
            "NON SQUAD PLAYER",
            "non squad player",
            "Non squad player",
            "nOn SqUaD pLaYeR",
        ]
        
        for account in variations:
            assert EIJsonValidator.is_valid_account_name(account) is False, f"应该拒绝大小写变体: {account}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
