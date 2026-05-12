# -*- coding: utf-8 -*-
"""测试导入是否正常"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始测试导入..")

try:
    from app.config.database import _Base, init_db
    print("?database 模块导入成功")
except Exception as e:
    print(f"?database 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.config.database.database_sync import _sync_table_columns
    print("?database_sync 模块导入成功")
except Exception as e:
    print(f"?database_sync 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.routers.game_data.professions_query import router
    print("?professions_query 模块导入成功")
except Exception as e:
    print(f"?professions_query 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from main import app
    print("?main.py 导入成功")
    print("\n🎉 所有导入测试通过?)
except Exception as e:
    print(f"?main.py 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
