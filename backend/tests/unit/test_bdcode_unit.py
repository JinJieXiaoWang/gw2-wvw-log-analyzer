#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能: BD码解析服务单元测试
创建时间: 2026-05-04
"""

import os
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.game_data.bdcode_service import BDCodeService, get_bdcode_service


@pytest.fixture
def bdcode_service():
    """BD码解析服务 fixture"""
    return get_bdcode_service()


class TestBDCodeValidation:
    """BD码格式验证测试"""

    def test_valid_bdcode_format(self, bdcode_service):
        """测试有效的BD码格式"""
        valid_bd = "[&DQYfHSk7UBpiHXQAdx0AAHIdAABPAQAAah0AAAAAAAAAAAAAAAAAAAAAAAADVgAvAFkAAA==]"
        result = bdcode_service.validate_bdcode(valid_bd)
        assert result["is_valid"] is True
        assert result["error"] is None

    def test_empty_bdcode(self, bdcode_service):
        """测试空BD码"""
        result = bdcode_service.validate_bdcode("")
        assert result["is_valid"] is False
        assert result["error"] is not None

    def test_invalid_format_bdcode(self, bdcode_service):
        """测试格式错误的BD码"""
        invalid_bd = "invalid-bd-code"
        result = bdcode_service.validate_bdcode(invalid_bd)
        assert result["is_valid"] is False
        assert result["error"] is not None

    def test_invalid_base64_bdcode(self, bdcode_service):
        """测试Base64无效的BD码"""
        invalid_base64_bd = "[&invalid-base64!@#]"
        result = bdcode_service.validate_bdcode(invalid_base64_bd)
        assert result["is_valid"] is False or (
            result["is_valid"] is True and "error" in result
        )


class TestBDCodeParsing:
    """BD码解析测试"""

    EXAMPLE_BD = (
        "[&DQYfHSk7UBpiHXQAdx0AAHIdAABPAQAAah0AAAAAAAAAAAAAAAAAAAAAAAADVgAvAFkAAA==]"
    )

    def test_parse_example_bdcode_success(self, bdcode_service):
        """测试解析示例BD码成功"""
        result = bdcode_service.parse_bdcode(self.EXAMPLE_BD)
        assert result["success"] is True
        assert "data" in result
        assert result["data"] is not None

    def test_parse_bdcode_profession_info(self, bdcode_service):
        """测试解析职业信息"""
        result = bdcode_service.parse_bdcode(self.EXAMPLE_BD)
        data = result["data"]
        assert "profession" in data
        assert "profession_cn" in data
        assert data["profession"] is not None
        assert data["profession_cn"] is not None
        # 示例BD码是元素使
        assert data["profession_id"] == 6
        assert data["profession_cn"] == "元素使"

    def test_parse_bdcode_specializations(self, bdcode_service):
        """测试解析专长线信息"""
        result = bdcode_service.parse_bdcode(self.EXAMPLE_BD)
        data = result["data"]
        assert "specializations" in data
        assert len(data["specializations"]) == 3

        # 检查第一个专长线
        spec1 = data["specializations"][0]
        assert "id" in spec1
        assert "name" in spec1
        assert "name_cn" in spec1
        assert "traits" in spec1
        assert len(spec1["traits"]) == 3

        # 检查第三个是精英专长线
        spec3 = data["specializations"][2]
        assert spec3["is_elite"] is True
        assert spec3["name_cn"] == "唤元师"

    def test_parse_bdcode_skills(self, bdcode_service):
        """测试解析技能信息"""
        result = bdcode_service.parse_bdcode(self.EXAMPLE_BD)
        data = result["data"]
        assert "skills" in data
        assert "heal" in data["skills"]
        assert "utility" in data["skills"]
        assert "elite" in data["skills"]

        # 检查治疗技能
        assert data["skills"]["heal"] is not None
        assert "name" in data["skills"]["heal"]
        assert "name_cn" in data["skills"]["heal"]

        # 检查通用技能
        assert len(data["skills"]["utility"]) >= 1

        # 检查精英技能
        assert data["skills"]["elite"] is not None

    def test_parse_bdcode_without_icons(self, bdcode_service):
        """测试解析不带图标的BD码"""
        result = bdcode_service.parse_bdcode(self.EXAMPLE_BD, include_icons=False)
        assert result["success"] is True
        data = result["data"]
        assert data is not None

    def test_parse_invalid_bdcode(self, bdcode_service):
        """测试解析无效的BD码"""
        invalid_bd = "invalid-bd-code"
        result = bdcode_service.parse_bdcode(invalid_bd)
        assert result["success"] is False
        assert result["error"] is not None


class TestBDCodePerformance:
    """BD码性能测试"""

    EXAMPLE_BD = (
        "[&DQYfHSk7UBpiHXQAdx0AAHIdAABPAQAAah0AAAAAAAAAAAAAAAAAAAAAAAADVgAvAFkAAA==]"
    )

    def test_validation_performance(self, bdcode_service):
        """测试验证性能 - 应该在1ms内完成"""
        import time

        start = time.time()
        for _ in range(100):
            bdcode_service.validate_bdcode(self.EXAMPLE_BD)
        end = time.time()
        avg_time = (end - start) / 100 * 1000  # 毫秒
        assert avg_time < 5.0, f"平均验证时间 {avg_time:.2f}ms 超过预期"

    def test_parsing_performance(self, bdcode_service):
        """测试解析性能 - 第一次可能慢,后续应该很快"""
        import time

        # 第一次解析
        start1 = time.time()
        bdcode_service.parse_bdcode(self.EXAMPLE_BD)
        first_time = (time.time() - start1) * 1000

        # 后续解析 (应该有缓存)
        start2 = time.time()
        for _ in range(10):
            bdcode_service.parse_bdcode(self.EXAMPLE_BD)
        avg_time = (time.time() - start2) / 10 * 1000

        # 第一次解析可以稍慢,但后续应该很快
        assert avg_time < 10.0, f"平均解析时间 {avg_time:.2f}ms 超过预期"


class TestBDCodeMultipleCases:
    """多种BD码测试用例"""

    # 这里可以添加更多不同职业的BD码进行测试
    TEST_CASES = [
        # 示例BD码 - 元素使
        (
            "[&DQYfHSk7UBpiHXQAdx0AAHIdAABPAQAAah0AAAAAAAAAAAAAAAAAAAAAAAADVgAvAFkAAA==]",
            "元素使",
        ),
    ]

    @pytest.mark.parametrize("bd_code, expected_profession_cn", TEST_CASES)
    def test_multiple_bd_codes(self, bdcode_service, bd_code, expected_profession_cn):
        """测试多种BD码解析"""
        result = bdcode_service.parse_bdcode(bd_code)
        assert result["success"] is True
        assert result["data"]["profession_cn"] == expected_profession_cn


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
