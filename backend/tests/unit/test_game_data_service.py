# -*- coding: utf-8 -*-
# 模块功能：游戏数据服务单元测试
# 作者：System
# 创建日期：2026-05-13
# 测试内容：职业与精英特长数据从数据库查询的比对逻辑

from unittest.mock import Mock, patch

import pytest
from app.services.game.game_data_service import GameDataService
from app.services.game.profession_service import ProfessionService
from sqlalchemy.orm import Session


class TestGameDataService:
    """游戏数据服务单元测试类"""

    def test_get_professions_data_from_db(self):
        """测试从数据库获取职业数据"""
        # 创建模拟数据库会话
        mock_db = Mock(spec=Session)
        
        # 创建模拟职业数据
        mock_professions = [
            {
                "profession_key": "Guardian",
                "profession_name": "守护",
                "profession_name_en": "Guardian",
                "color": "#3BA55D",
                "role_type": "support",
                "icon": "guardian.png"
            },
            {
                "profession_key": "Warrior",
                "profession_name": "战士",
                "profession_name_en": "Warrior",
                "color": "#C41E3A",
                "role_type": "dps",
                "icon": "warrior.png"
            }
        ]
        
        # 创建模拟精英特长数据
        mock_specs = [
            {
                "spec_key": "Dragonhunter",
                "spec_name": "猎龙者",
                "spec_name_en": "Dragonhunter",
                "profession_key": "Guardian",
                "color": "#3BA55D",
                "role_type": "dps",
                "icon": "dragonhunter.png",
                "scoring_config": {"damage": 80, "support": 20}
            },
            {
                "spec_key": "Firebrand",
                "spec_name": "燃火者",
                "spec_name_en": "Firebrand",
                "profession_key": "Guardian",
                "color": "#F58220",
                "role_type": "support",
                "icon": "firebrand.png",
                "scoring_config": {"support": 70, "damage": 30}
            }
        ]
        
        # 模拟 ProfessionService
        with patch('app.services.game.game_data_service.ProfessionService') as MockProfService:
            mock_prof_service = Mock()
            MockProfService.return_value = mock_prof_service
            mock_prof_service.get_all_professions.return_value = mock_professions
            mock_prof_service.get_all_specs.return_value = mock_specs
            
            # 创建 GameDataService 实例
            service = GameDataService(db=mock_db)
            
            # 调用获取职业数据方法
            result = service._get_professions_data()
            
            # 验证结果
            assert result is not None
            assert result["version"] == "2.0.0"
            assert "base_professions" in result
            assert "elite_specs" in result
            
            # 验证基础职业数据
            assert "Guardian" in result["base_professions"]
            assert "Warrior" in result["base_professions"]
            assert result["base_professions"]["Guardian"]["name_cn"] == "守护"
            assert result["base_professions"]["Warrior"]["name_cn"] == "战士"
            
            # 验证精英特长数据
            assert "Dragonhunter" in result["elite_specs"]
            assert "Firebrand" in result["elite_specs"]
            assert result["elite_specs"]["Dragonhunter"]["name_cn"] == "猎龙者"
            assert result["elite_specs"]["Firebrand"]["base_profession"] == "Guardian"
            
            # 验证调用次数
            mock_prof_service.get_all_professions.assert_called_once()
            mock_prof_service.get_all_specs.assert_called_once()

    def test_get_professions_data_without_db(self):
        """测试在没有数据库会话时的错误处理"""
        # 创建没有数据库会话的 GameDataService 实例
        service = GameDataService(db=None)
        
        # 调用获取职业数据方法
        result = service._get_professions_data()
        
        # 验证结果为空（没有数据库会话时应返回空数据）
        assert result is not None
        assert result["version"] == "2.0.0"
        assert len(result["base_professions"]) == 0
        assert len(result["elite_specs"]) == 0

    def test_get_profession_name_cn(self):
        """测试获取职业中文名"""
        mock_db = Mock(spec=Session)
        
        mock_professions = [
            {
                "profession_key": "Guardian",
                "profession_name": "守护",
                "profession_name_en": "Guardian",
                "color": "#3BA55D",
                "role_type": "support",
                "icon": "guardian.png"
            }
        ]
        
        mock_specs = [
            {
                "spec_key": "Dragonhunter",
                "spec_name": "猎龙者",
                "spec_name_en": "Dragonhunter",
                "profession_key": "Guardian",
                "color": "#3BA55D",
                "role_type": "dps",
                "icon": "dragonhunter.png",
                "scoring_config": {}
            },
            {
                "spec_key": "Firebrand",
                "spec_name": "燃火者",
                "spec_name_en": "Firebrand",
                "profession_key": "Guardian",
                "color": "#ff7043",
                "role_type": "support",
                "icon": "firebrand.png",
                "scoring_config": {}
            }
        ]
        
        with patch('app.services.game.game_data_service.ProfessionService') as MockProfService:
            mock_prof_service = Mock()
            MockProfService.return_value = mock_prof_service
            mock_prof_service.get_all_professions.return_value = mock_professions
            mock_prof_service.get_all_specs.return_value = mock_specs
            
            service = GameDataService(db=mock_db)
            
            # 测试获取基础职业中文名
            cn_name = service.get_profession_name_cn("Guardian")
            assert cn_name == "守护"
            
            # 测试获取精英特长中文名
            cn_name = service.get_profession_name_cn("Dragonhunter")
            assert cn_name == "猎龙者"
            
            # 测试获取不存在的职业
            cn_name = service.get_profession_name_cn("Unknown")
            assert cn_name == "Unknown"

    def test_get_role_type(self):
        """测试获取精英特长角色定位"""
        # 清除全局缓存，避免受之前测试影响
        from app.services.game.game_data_service import get_global_cache
        get_global_cache().clear_memory()
        
        mock_db = Mock(spec=Session)
        
        mock_professions = [
            {
                "profession_key": "Guardian",
                "profession_name": "守护",
                "profession_name_en": "Guardian",
                "color": "#3BA55D",
                "role_type": "support",
                "icon": "guardian.png"
            }
        ]
        
        mock_specs = [
            {
                "spec_key": "Dragonhunter",
                "spec_name": "猎龙者",
                "spec_name_en": "Dragonhunter",
                "profession_key": "Guardian",
                "color": "#3BA55D",
                "role_type": "dps",
                "icon": "dragonhunter.png",
                "scoring_config": {}
            }
        ]
        
        with patch('app.services.game.game_data_service.ProfessionService') as MockProfService:
            mock_prof_service = Mock()
            MockProfService.return_value = mock_prof_service
            mock_prof_service.get_all_professions.return_value = mock_professions
            mock_prof_service.get_all_specs.return_value = mock_specs
            
            service = GameDataService(db=mock_db)
            
            # 测试获取精英特长的角色定位
            role = service.get_role_type("Dragonhunter")
            assert role == "dps"
            
            # 测试获取另一精英特长的角色定位
            role = service.get_role_type("Firebrand")
            assert role == "support"
            
            # 测试获取不存在的职业
            role = service.get_role_type("Unknown")
            assert role == "dps"

    def test_cache_mechanism(self):
        """测试缓存机制"""
        mock_db = Mock(spec=Session)
        
        mock_professions = [
            {
                "profession_key": "Guardian",
                "profession_name": "守护",
                "profession_name_en": "Guardian",
                "color": "#3BA55D",
                "role_type": "support",
                "icon": "guardian.png"
            }
        ]
        
        mock_specs = []
        
        with patch('app.services.game.game_data_service.ProfessionService') as MockProfService:
            mock_prof_service = Mock()
            MockProfService.return_value = mock_prof_service
            mock_prof_service.get_all_professions.return_value = mock_professions
            mock_prof_service.get_all_specs.return_value = mock_specs
            
            service = GameDataService(db=mock_db)
            
            # 第一次调用
            result1 = service._get_professions_data()
            
            # 第二次调用（应该使用缓存）
            result2 = service._get_professions_data()
            
            # 验证两次返回相同结果
            assert result1 == result2
            
            # 验证数据库查询只执行了一次（缓存生效）
            assert mock_prof_service.get_all_professions.call_count == 1
            assert mock_prof_service.get_all_specs.call_count == 1

    def test_reload_data(self):
        """测试重新加载数据"""
        mock_db = Mock(spec=Session)
        
        mock_professions_v1 = [
            {
                "profession_key": "Guardian",
                "profession_name": "守护",
                "profession_name_en": "Guardian",
                "color": "#3BA55D",
                "role_type": "support",
                "icon": "guardian.png"
            }
        ]
        
        mock_professions_v2 = [
            {
                "profession_key": "Guardian",
                "profession_name": "守护者",  # 修改名称
                "profession_name_en": "Guardian",
                "color": "#3BA55D",
                "role_type": "support",
                "icon": "guardian.png"
            },
            {
                "profession_key": "Warrior",
                "profession_name": "战士",
                "profession_name_en": "Warrior",
                "color": "#C41E3A",
                "role_type": "dps",
                "icon": "warrior.png"
            }
        ]
        
        mock_specs = []
        
        with patch('app.services.game.game_data_service.ProfessionService') as MockProfService:
            mock_prof_service = Mock()
            MockProfService.return_value = mock_prof_service
            mock_prof_service.get_all_professions.side_effect = [mock_professions_v1, mock_professions_v2]
            mock_prof_service.get_all_specs.return_value = mock_specs
            
            service = GameDataService(db=mock_db)
            
            # 第一次加载
            result1 = service._get_professions_data()
            assert len(result1["base_professions"]) == 1
            assert result1["base_professions"]["Guardian"]["name_cn"] == "守护"
            
            # 强制重新加载
            result2 = service._get_professions_data(force_reload=True)
            assert len(result2["base_professions"]) == 2
            assert result2["base_professions"]["Guardian"]["name_cn"] == "守护者"
            assert "Warrior" in result2["base_professions"]
            
            # 验证数据库查询执行了两次
            assert mock_prof_service.get_all_professions.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
