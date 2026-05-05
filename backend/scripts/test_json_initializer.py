# -*- coding: utf-8 -*-
"""
测试 JSON 初始化功能
验证 builds_initial_data.json 文件是否正确加载并导入到数据库

使用方法：
    cd D:\Code\Gw2-wvw-log-analyzer\backend
    python -m scripts.test_json_initializer

作者: System
创建日期: 2026-05-06
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import init_db, SessionLocal
from app.models.build import Build
from app.services.build_data_initializer import BuildDataInitializer
from app.utils.logger import logger


def test_json_file_exists():
    """测试 JSON 文件是否存在"""
    from app.services.build_data_initializer import BUILD_INITIAL_DATA_PATH
    
    if os.path.exists(BUILD_INITIAL_DATA_PATH):
        print(f"[OK] JSON 文件存在: {BUILD_INITIAL_DATA_PATH}")
        return True
    else:
        print(f"[FAIL] JSON 文件不存在: {BUILD_INITIAL_DATA_PATH}")
        return False


def test_json_structure():
    """测试 JSON 文件结构是否符合预期"""
    import json
    from app.services.build_data_initializer import BUILD_INITIAL_DATA_PATH
    
    try:
        with open(BUILD_INITIAL_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("[FAIL] JSON 数据不是数组格式")
            return False
        
        if len(data) == 0:
            print("[WARN] JSON 数据为空数组")
            return True
        
        # 检查第一个元素是否包含必要字段
        first_item = data[0]
        required_fields = ["slug", "title", "profession", "bd_code", "role"]
        
        missing_fields = [field for field in required_fields if field not in first_item]
        if missing_fields:
            print(f"[FAIL] 缺少必填字段: {', '.join(missing_fields)}")
            return False
        
        print(f"[OK] JSON 文件结构验证通过，共 {len(data)} 条记录")
        print(f"     第一条记录: {first_item['title']} ({first_item['profession']})")
        return True
    
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON 解析失败: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] 读取 JSON 文件失败: {e}")
        return False


def test_database_import():
    """测试数据库导入功能"""
    print("\n=== 测试数据库导入 ===")
    
    # 初始化数据库
    init_db()
    db = SessionLocal()
    
    try:
        # 先清空 builds 表
        count = db.query(Build).count()
        if count > 0:
            print(f"清空现有数据: {count} 条")
            db.query(Build).delete()
            db.commit()
        
        # 创建初始化器并执行
        initializer = BuildDataInitializer(db)
        result = initializer.init_builds()
        
        print(f"初始化结果: initialized={result['initialized']}, count={result['count']}")
        
        if result["errors"]:
            print(f"错误列表:")
            for error in result["errors"]:
                print(f"  - {error}")
        
        # 验证导入结果
        imported_count = db.query(Build).count()
        print(f"数据库中现有记录数: {imported_count}")
        
        if imported_count > 0:
            # 检查第一条记录
            first_build = db.query(Build).first()
            print(f"第一条记录: id={first_build.id}, title={first_build.title}, profession={first_build.profession}")
            
            # 检查职业分布
            from sqlalchemy import func
            profession_stats = db.query(Build.profession, func.count(Build.id)).group_by(Build.profession).all()
            print("\n职业分布统计:")
            for prof, cnt in profession_stats:
                print(f"  {prof}: {cnt} 条")
            
            # 检查角色类型分布
            role_stats = db.query(Build.role, func.count(Build.id)).group_by(Build.role).all()
            print("\n角色类型分布:")
            for role, cnt in role_stats:
                print(f"  {role}: {cnt} 条")
            
            return imported_count == result["count"]
        else:
            print("[FAIL] 数据库中没有导入任何记录")
            return False
    
    finally:
        db.close()


def main():
    print("=" * 60)
    print("GW2 Build 图书馆 JSON 初始化测试")
    print("=" * 60)
    
    # 测试1: JSON 文件是否存在
    print("\n=== 测试1: JSON 文件检查 ===")
    if not test_json_file_exists():
        sys.exit(1)
    
    # 测试2: JSON 结构验证
    print("\n=== 测试2: JSON 结构验证 ===")
    if not test_json_structure():
        sys.exit(1)
    
    # 测试3: 数据库导入测试
    success = test_database_import()
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] 所有测试通过!")
    else:
        print("[FAIL] 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
