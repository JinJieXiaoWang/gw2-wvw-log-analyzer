#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能: BD码解析集成测试
创建时间: 2026-05-04
"""

import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.game_data.bdcode_service import get_bdcode_service


class TestBDCodeIntegration:
    """BD码集成测试"""

    EXAMPLE_BD = (
        "[&DQYfHSk7UBpiHXQAdx0AAHIdAABPAQAAah0AAAAAAAAAAAAAAAAAAAAAAAADVgAvAFkAAA==]"
    )

    def test_full_workflow(self):
        """测试完整工作流程:验证 -> 解析 -> 详细分析"""
        service = get_bdcode_service()

        # 1. 验证BD码
        validation_result = service.validate_bdcode(self.EXAMPLE_BD)
        assert validation_result["is_valid"] is True

        # 2. 解析BD码
        parse_result = service.parse_bdcode(self.EXAMPLE_BD)
        assert parse_result["success"] is True
        data = parse_result["data"]

        # 3. 验证所有信息完整性
        assert "profession_id" in data
        assert "profession" in data
        assert "profession_cn" in data

        assert "specializations" in data
        assert len(data["specializations"]) == 3

        for spec in data["specializations"]:
            assert "id" in spec
            assert "name" in spec
            assert "name_cn" in spec
            assert "is_elite" in spec
            assert "traits" in spec
            assert len(spec["traits"]) == 3

            for trait in spec["traits"]:
                assert "id" in trait
                assert "name" in trait

        assert "skills" in data
        assert "heal" in data["skills"]
        assert "utility" in data["skills"]
        assert "elite" in data["skills"]

        heal_skill = data["skills"]["heal"]
        assert heal_skill is not None
        assert "id" in heal_skill
        assert "name" in heal_skill
        assert "name_cn" in heal_skill

        elite_skill = data["skills"]["elite"]
        assert elite_skill is not None
        assert "id" in elite_skill
        assert "name" in elite_skill
        assert "name_cn" in elite_skill

    def test_compare_with_and_without_icons(self):
        """测试带图标和不带图标的解析对比"""
        service = get_bdcode_service()

        # 带图标解析
        result_with_icons = service.parse_bdcode(self.EXAMPLE_BD, include_icons=True)
        assert result_with_icons["success"] is True

        # 不带图标解析
        result_without_icons = service.parse_bdcode(
            self.EXAMPLE_BD, include_icons=False
        )
        assert result_without_icons["success"] is True

        # 两种解析的核心数据应该一致
        data_with = result_with_icons["data"]
        data_without = result_without_icons["data"]

        assert data_with["profession_id"] == data_without["profession_id"]
        assert data_with["profession_cn"] == data_without["profession_cn"]

        # 专长线信息应该一致
        assert len(data_with["specializations"]) == len(data_without["specializations"])
        for i in range(len(data_with["specializations"])):
            assert (
                data_with["specializations"][i]["id"]
                == data_without["specializations"][i]["id"]
            )
            assert (
                data_with["specializations"][i]["name_cn"]
                == data_without["specializations"][i]["name_cn"]
            )

    def test_data_consistency(self):
        """测试多次解析的一致性"""
        service = get_bdcode_service()

        # 多次解析同一个BD码
        results = []
        for _ in range(5):
            result = service.parse_bdcode(self.EXAMPLE_BD)
            assert result["success"] is True
            results.append(result["data"])

        # 检查所有结果是否一致
        first = results[0]
        for data in results[1:]:
            assert data["profession_id"] == first["profession_id"]

            # 专长线一致
            assert len(data["specializations"]) == len(first["specializations"])
            for i in range(len(data["specializations"])):
                assert (
                    data["specializations"][i]["id"]
                    == first["specializations"][i]["id"]
                )

                # 特性一致
                assert len(data["specializations"][i]["traits"]) == len(
                    first["specializations"][i]["traits"]
                )
                for j in range(len(data["specializations"][i]["traits"])):
                    assert (
                        data["specializations"][i]["traits"][j]["id"]
                        == first["specializations"][i]["traits"][j]["id"]
                    )

    def test_error_handling(self):
        """测试错误处理机制"""
        service = get_bdcode_service()

        # 测试空字符串
        result1 = service.parse_bdcode("")
        assert result1["success"] is False
        assert "error" in result1

        # 测试格式错误
        result2 = service.parse_bdcode("not-a-bd-code")
        assert result2["success"] is False
        assert "error" in result2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
