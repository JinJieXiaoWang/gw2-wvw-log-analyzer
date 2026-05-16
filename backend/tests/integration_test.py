# -*- coding: utf-8 -*-
"""
GW2 WvW 日志分析系统 - 集成测试脚本
测试范围：后端API核心功能
"""

import json
import sys
from pathlib import Path

# 确保能导入app
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
from app.config.database import init_db

# 确保数据库表已创建
init_db()

client = TestClient(app)

# 全局认证令牌
_auth_token = None

def _get_token():
    """登录获取JWT令牌"""
    global _auth_token
    if _auth_token:
        return _auth_token
    
    # 确保管理员已初始化
    from app.config.database import get_db_context
    from app.services.auth.auth_service import init_predefined_admin
    with get_db_context() as db:
        init_predefined_admin(db)
    
    resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    if resp.status_code == 200:
        data = resp.json()
        if data.get("success"):
            _auth_token = data.get("data", {}).get("access_token")
            return _auth_token
    return None

TEST_RESULTS = []

def test(name, method, path, expected_status=200, payload=None, params=None, check_fn=None, auth=False):
    """执行单个API测试"""
    try:
        headers = {}
        if auth:
            token = _get_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        if method == "GET":
            resp = client.get(path, params=params, headers=headers)
        elif method == "POST":
            resp = client.post(path, json=payload, headers=headers)
        elif method == "PUT":
            resp = client.put(path, json=payload, headers=headers)
        elif method == "DELETE":
            resp = client.delete(path, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        success = resp.status_code == expected_status
        data = resp.json() if resp.content else None

        if check_fn and success:
            success = check_fn(data)

        TEST_RESULTS.append({
            "name": name,
            "method": method,
            "path": path,
            "status": resp.status_code,
            "expected": expected_status,
            "success": success,
            "data_preview": str(data)[:200] if data else None,
            "error": None if success else (data.get("message", "Unknown error") if data else resp.text[:200])
        })
        return data
    except Exception as e:
        TEST_RESULTS.append({
            "name": name,
            "method": method,
            "path": path,
            "status": -1,
            "expected": expected_status,
            "success": False,
            "data_preview": None,
            "error": str(e)
        })
        return None


print("=" * 70)
print("GW2 WvW 日志分析系统 - 后端API集成测试")
print("=" * 70)

# =============================================================================
# 1. 健康检查
# =============================================================================
print("\n[1/6] 健康检查...")
test("健康检查", "GET", "/health")
test("API健康检查", "GET", "/api/v1/health")

# =============================================================================
# 2. 参考数据API
# =============================================================================
print("\n[2/6] 参考数据API...")
test("符文列表", "GET", "/api/v1/ref-data/runes", check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) > 0)
test("法印列表", "GET", "/api/v1/ref-data/sigils", check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) > 0)
test("古物列表", "GET", "/api/v1/ref-data/relics", check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) > 0)
test("食物列表", "GET", "/api/v1/ref-data/foods", check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) > 0)
test("增强剂列表", "GET", "/api/v1/ref-data/utilities", check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) > 0)
test("符文搜索", "GET", "/api/v1/ref-data/runes", params={"search": "学者", "limit": 5}, check_fn=lambda d: d.get("success"))
test("符文列表数量验证", "GET", "/api/v1/ref-data/runes", check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) == 100)

# =============================================================================
# 3. BD码解析API
# =============================================================================
print("\n[3/6] BD码解析API...")
test_bd_code = "[&DQg1KTIlIjbBEigPQAGBAIEAQAHxEnUBAxOVAAAAAAAAAAAAAAAAAAAAAAA=]"
test("BD码解析", "POST", "/api/bdcode/parse", payload={"bd_code": test_bd_code, "include_icons": False},
      check_fn=lambda d: d.get("success") and d.get("data", {}).get("profession") == "Necromancer")
test("BD码验证", "POST", "/api/bdcode/validate", payload={"bd_code": test_bd_code},
      check_fn=lambda d: d.get("is_valid") is True)
test("BD码批量解析", "POST", "/api/bdcode/batch", payload={"bd_codes": [test_bd_code], "include_icons": False},
      check_fn=lambda d: d.get("success_count") == 1)

# =============================================================================
# 4. Build图书馆API
# =============================================================================
print("\n[4/6] Build图书馆API...")

# 4.1 获取Build列表（空库）
test("Build列表-空库", "GET", "/api/v1/builds", params={"page": 1, "page_size": 20},
     check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) == 0)

# 4.2 创建Build
new_build = {
    "title": "测试-全息输出",
    "profession": "Engineer",
    "role": "dps",
    "sub_roles": [],
    "armor_type": "狂战士",
    "weapons": [{"set": 1, "name": "大锤", "sigils": ["武勇", "嗜血"]}],
    "relic": "潜行者",
    "rune": "学者符文",
    "food": "黑胡椒粉真空烹调肉排",
    "wrench": "超级磨刀石",
    "infusion": "威能灌注+16",
    "bd_code": "[&DQMmHwY7OSsqDyoPlQFfAVcWjAEHAY0B8BWJAQAAAAAAAAAAAAAAAAAAAAABMwAA]",
    "trait_lines": [],
    "rotation_commands": [],
    "mechanics": [],
    "videos": [],
    "author": "测试用户"
}

create_result = test("创建Build", "POST", "/api/v1/builds", payload=new_build, auth=True,
                     check_fn=lambda d: d.get("success") and d.get("data", {}).get("id") is not None)

build_id = create_result.get("data", {}).get("id") if create_result else None

# 4.3 获取Build列表（有数据）
test("Build列表-有数据", "GET", "/api/v1/builds", params={"page": 1, "page_size": 20},
     check_fn=lambda d: d.get("success") and len(d.get("data", {}).get("items", [])) >= 1)

# 4.4 获取单个Build
if build_id:
    test("获取单个Build", "GET", f"/api/v1/builds/{build_id}",
         check_fn=lambda d: d.get("success") and d.get("data", {}).get("id") == build_id)

    # 4.5 更新Build（relic多选测试）
    update_payload = {"relic": "河流 / 风裔", "rune": "光辉"}
    test("更新Build-relic多选", "PUT", f"/api/v1/builds/{build_id}", payload=update_payload, auth=True,
         check_fn=lambda d: d.get("success") and d.get("data", {}).get("relic") == "河流 / 风裔")

    # 4.6 删除Build
    test("删除Build", "DELETE", f"/api/v1/builds/{build_id}", auth=True,
         check_fn=lambda d: d.get("success") is True)

# =============================================================================
# 5. 职业数据API
# =============================================================================
print("\n[5/6] 职业数据API...")
test("职业列表", "GET", "/api/v1/professions", check_fn=lambda d: d.get("success"))
test("精英特长", "GET", "/api/v1/professions/elite-specs", check_fn=lambda d: d.get("success"))

# =============================================================================
# 6. 系统API
# =============================================================================
print("\n[6/6] 系统API...")
test("数据看板", "GET", "/api/v1/dashboard/overview", check_fn=lambda d: d.get("success"))
test("游戏数据信息", "GET", "/api/v1/game-data/info", check_fn=lambda d: d.get("success"))

# =============================================================================
# 测试报告
# =============================================================================
print("\n" + "=" * 70)
print("测试报告")
print("=" * 70)

total = len(TEST_RESULTS)
passed = sum(1 for r in TEST_RESULTS if r["success"])
failed = total - passed

print(f"\n总计: {total}  |  通过: {passed}  |  失败: {failed}")
print(f"通过率: {passed/total*100:.1f}%")

if failed > 0:
    print("\n--- 失败项 ---")
    for r in TEST_RESULTS:
        if not r["success"]:
            print(f"\n❌ {r['name']}")
            print(f"   请求: {r['method']} {r['path']}")
            print(f"   状态: {r['status']} (期望: {r['expected']})")
            print(f"   错误: {r['error']}")
            if r['data_preview']:
                print(f"   响应: {r['data_preview']}")

print("\n--- 通过项 ---")
for r in TEST_RESULTS:
    if r["success"]:
        print(f"✅ {r['name']}")

print("\n" + "=" * 70)
if failed == 0:
    print("🎉 所有测试通过！系统达到部署标准。")
else:
    print(f"⚠️ 发现 {failed} 个问题，需要修复后才能部署。")
print("=" * 70)
