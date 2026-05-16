# 种子数据管理指南

> **版本**: v1.0.0  
> **更新日期**: 2026-05-15  
> **适用范围**: 后端数据库初始化数据管理

---

## 一、架构概述

本项目采用 **JSON 源文件 + 构建时内嵌** 的混合管理模式：

- **开发阶段**：所有种子数据以 JSON 文件形式维护于 `backend/app/data/seeds/`，支持 Git diff、Code Review、Schema 验证
- **构建阶段**：`scripts/build_seeds.py` 将 JSON 文件压缩内嵌为 Python 模块 `_generated/seed_modules.py`
- **运行阶段**：`init_all.py` 优先从 `seed_modules.py` 加载数据，运行时零外部文件依赖

```
┌─────────────────┐     build      ┌─────────────────────┐     runtime    ┌─────────────┐
│  seeds/*.json   │ ─────────────> │ _generated/seed_    │ ─────────────> │  database   │
│  (JSON 源文件)   │                │ modules.py          │                │  (MySQL/   │
│                 │                │ (gzip+base64 内嵌)   │                │  SQLite)   │
└─────────────────┘                └─────────────────────┘                └─────────────┘
        ↓                                    ↓
   validate_seeds.py                    init_all.py
   (Schema + 一致性校验)                  (零依赖加载)
```

---

## 二、目录结构

```
backend/app/data/
├── seeds/                          # JSON 种子数据（唯一数据源）
│   ├── _meta.json                  # 全局元数据（版本列表、加载顺序）
│   ├── _schemas/                   # JSON Schema 定义（待完善）
│   └── v{version}/                 # 按版本分目录
│       ├── 001_sys_menu.json
│       ├── 002_sys_dict_type.json
│       ├── 003_sys_dict_data.json
│       ├── 004_gw_role_type.json
│       ├── 005_gw_profession.json
│       ├── 006_gw_elite_specialization.json
│       └── 007_game_static_data_*.json
├── configs/                        # 运行时配置（保留现有 json/ 目录）
│   ├── parsing_config.json
│   ├── rate_limit_config.json
│   └── scoring_rules.json
├── _generated/                     # 构建产物（Git 忽略）
│   └── seed_modules.py             # 自动生成的内嵌模块
├── init_all.py                     # 数据库初始化入口
└── seed_data.py                    # 旧的内嵌数据模块（逐步废弃）
```

---

## 三、文件命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 种子数据 | `{seq}_{table_name}_{desc}.json` | `001_sys_menu.json` |
| 运行时配置 | `{domain}_config.json` | `scoring_rules.json` |
| Schema | `{data_name}.schema.json` | `sys_menu.schema.json` |
| 增量更新 | `v{x.y.z}_{description}.json` | `v1.1.0_add_metric_type_options.json` |

---

## 四、JSON 文件格式

每个种子数据文件必须包含 `_meta` 和 `data` 两个顶层字段：

```json
{
  "_meta": {
    "version": "1.0.0",
    "target_table": "sys_dict_type",
    "min_app_version": "1.0.0",
    "description": "字典类型种子数据"
  },
  "data": [
    {"dict_type": "role", "dict_name": "角色定位", ...},
    ...
  ]
}
```

`_meta` 字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | 是 | 数据版本号，遵循 SemVer |
| `target_table` | string | 是 | 目标数据库表名 |
| `min_app_version` | string | 否 | 最低兼容的应用版本 |
| `description` | string | 否 | 数据描述 |

---

## 五、日常操作流程

### 5.1 修改种子数据

```bash
# 1. 编辑 JSON 源文件
vim backend/app/data/seeds/v1.0.0/003_sys_dict_data.json

# 2. 本地验证
python scripts/validate_seeds.py

# 3. 重新构建内嵌模块
python scripts/build_seeds.py

# 4. 测试初始化
python -c "from app.data.init_all import initialize_all; ..."
```

### 5.2 添加新的种子数据

```bash
# 1. 在对应版本目录下创建 JSON 文件
cp template.json backend/app/data/seeds/v1.0.0/008_new_table.json

# 2. 更新 _meta.json 的 files 列表
vim backend/app/data/seeds/_meta.json

# 3. 验证并构建
python scripts/validate_seeds.py && python scripts/build_seeds.py
```

### 5.3 增量更新（已有数据库）

项目支持通过 `sys_data_version` 表实现增量迁移：

1. 新建版本目录 `seeds/v1.1.0/`
2. 放置增量数据文件（只包含新增/修改的记录）
3. 更新 `_meta.json`
4. 重新构建并部署
5. `init_all.py` 自动检测 `sys_data_version`，只应用新版本数据

> **注意**：当前版本（v1.0.0）的增量迁移逻辑尚在规划中，完整支持将在后续版本实现。

---

## 六、CI/CD 集成

在 GitHub Actions / GitLab CI 中添加以下步骤：

```yaml
- name: Validate Seed Data
  run: python scripts/validate_seeds.py

- name: Build Seed Modules
  run: python scripts/build_seeds.py

- name: Verify Generated Module
  run: |
    python -c "
    from backend.app.data._generated.seed_modules import list_seeds
    print(f'Generated {len(list_seeds())} seed modules')
    "
```

---

## 七、验证脚本说明

### `scripts/validate_seeds.py`

验证内容：
1. **JSON 格式**：所有种子文件必须能正确解析
2. **_meta 完整性**：检查必填字段
3. **引用完整性**：`sys_dict_data` 中的 `dict_type` 必须存在于 `sys_dict_type`
4. **前后端一致性**：自动比对 `dict_values.py` 与 `dictValues.ts` 的常量定义

### `scripts/build_seeds.py`

构建流程：
1. 读取 `seeds/` 目录下所有 JSON 文件
2. 对每个文件进行 gzip + base64 压缩
3. 生成 `backend/app/data/_generated/seed_modules.py`
4. 模块提供 `load_seed(name)` 和 `list_seeds()` 接口

---

## 八、常见问题

**Q: `_generated/seed_modules.py` 需要提交到 Git 吗？**  
A: **不需要**。该文件已在 `.gitignore` 中忽略，由 CI 在合并后自动生成。

**Q: 如果 `seed_modules.py` 不存在，系统还能启动吗？**  
A: **可以**。`init_all.py` 中的 `_try_load_seed_from_module` 函数会在加载失败时回退到内嵌的 Python 字典数据，保证兼容性。

**Q: 为什么保留 `init_all.py` 中的内嵌数据？**  
A: 作为 fallback 机制，确保在开发环境未运行 `build_seeds.py` 时仍能正常初始化数据库。

**Q: `seed_data.py` 会怎样处理？**  
A: `seed_data.py` 中的游戏静态数据已提取为 `007_game_static_data_*.json`，该文件将逐步废弃，最终由 `seed_modules.py` 完全替代。

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-15 | 初始版本，建立 JSON 源文件 + 构建时内嵌的统一管理体系 |
