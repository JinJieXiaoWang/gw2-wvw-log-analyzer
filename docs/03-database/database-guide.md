# 数据库操作与测试指南

> **版本**: v3.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**:
> - 更新为与实际配置一致（core/config.py 集中配置、三数据库支持、自动建表、环境变量清单）
> - 删除关于 `evtc_*` 原始数据表的测试/重置说明
> - 更新配置引用从 `app.config.database_settings` 到 `app.core.config`

---

## 历史版本

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 更新配置架构，删除 evtc_* 相关内容 | 系统 |
| v2.0.0 | 2026-05-01 | 整合全部数据库操作文档 | 系统 |
| v1.1.0 | 2026-05-01 | 新增 DB_TYPE 大小写修复记录 | System |
| v1.0.0 | 2026-04-30 | 初始数据库测试与重置指南 | System |

---

# 一、多数据库完整测试方案

## 文档信息
- 项目: GW2 WvW 日志系统
- 日期: 2026-05-05
- 测试目标: 验证三个数据库（SQLite、MySQL、PostgreSQL）的完整功能

---

## 一、测试环境准备

### 1.1 系统要求
- 操作系统: Windows/Linux/macOS
- Python: 3.10+
- MySQL: 5.7+（可选）
- PostgreSQL: 12+（可选）

### 1.2 依赖安装

```bash
# 基础依赖（已包含）
pip install -r requirements.txt

# MySQL支持（如需测试MySQL）
pip install pymysql cryptography

# PostgreSQL支持（如需测试PostgreSQL）
pip install psycopg2-binary
```

### 1.3 环境配置文件

确保 `.env` 文件已创建：
```bash
cp .env.example .env
```

**核心配置说明**：
- 实际配置集中到 `app/core/config.py`（558 行）
- `app/config/database_settings.py` 为向后兼容入口
- `app/config/database.py` 负责 SQLAlchemy 引擎/会话管理、自动建表逻辑

---

## 二、测试工具

### 2.1 已创建的测试工具

| 工具 | 位置 | 用途 |
|------|------|------|
| `final_test.py` | `tests/` | 完整数据库测试 |
| `database_comprehensive_test.py` | `tests/` | 综合测试工具 |
| `test_databases_step_by_step.py` | `tests/` | 分步测试 |

### 2.2 测试工具特点
- 自动创建数据库目录
- 自动初始化表结构
- 详细的日志输出
- JSON格式测试报告
- 友好的错误提示

---

## 三、测试用例设计原则

### 3.1 设计原则
1. **分层测试**: 配置 → 连接 → 表结构 → 数据读写 → 异常处理
2. **独立性**: 每个数据库测试独立，互不影响
3. **可重复**: 测试可重复执行，支持强制重建
4. **可验证**: 有明确的通过/失败标准
5. **覆盖全面**: 覆盖正常场景和异常场景

### 3.2 测试分类
| 类型 | 说明 |
|------|------|
| 配置测试 | 验证环境变量读取和解析 |
| 连接测试 | 验证数据库连接能否建立 |
| 表结构测试 | 验证表能否正确创建 |
| 数据读写测试 | 验证CRUD操作 |
| 切换测试 | 验证数据库切换功能 |
| 异常处理测试 | 验证错误场景处理 |

---

## 四、完整测试流程

### 4.1 测试总流程图
```
环境准备 → 配置验证 → 数据库1测试 → 数据库2测试 → 数据库3测试 → 切换测试 → 报告生成
```

### 4.2 步骤详解

#### 步骤1: 环境验证

**验证标准**:
- Python版本 ≥ 3.10
- 依赖包安装完整
- .env文件存在
- database目录可写

**测试方法**:
```bash
# 验证Python版本
python --version

# 验证依赖安装
pip list

# 验证文件存在
ls -la .env
ls -la database/
```

---

#### 步骤2: SQLite数据库测试

##### 2.1 配置验证
**测试内容**:
- DB_TYPE正确读取
- SQLITE_DB_PATH正确读取
- 配置摘要正确生成

**验证方法**:
```python
from app.core.config import get_settings
settings = get_settings()
assert settings.DB_TYPE.value == "sqlite"
print(settings.get_config_summary())
```

##### 2.2 连接测试
**验证标准**:
- 能成功创建连接
- test_connection()返回True

**测试方法**:
```python
from app.config.database import test_connection, get_current_db_info
info = get_current_db_info()
assert info["connected"] == True
print("连接成功")
```

##### 2.3 表结构测试
**验证标准**:
- 所有定义的表都能成功创建
- 无错误或警告

**核心表清单**（v3.0）:
| 表名 | 说明 |
|------|------|
| `evtc_log` | 日志实例主表 |
| `fights` | 战斗概览 |
| `fight_stats` | 玩家战斗统计 |
| `ei_player` | EI 玩家同步 |
| `ei_target` | EI 目标同步 |
| `ei_skill_map` | EI 技能映射 |
| `ei_phase` | EI 战斗阶段 |
| `ei_report` | EI 完整报告 |
| `members` | 玩家成员 |
| `account_characters` | 账号角色 |
| `sys_user` | 系统用户 |
| `sys_dict_type` / `sys_dict_data` | 字典表 |
| `batch_parse_task` / `batch_parse_task_item` | 批量解析任务 |
| `storage_cleanup_record` / `storage_monitor_record` | 存储管理 |

> **注意**: v3.0 已删除 `evtc_header`, `evtc_agent`, `evtc_skill`, `evtc_event`, `evtc_player_instance`, `evtc_combat_meta`, `evtc_event_per_second` 等 7 个原始数据表。

**测试方法**:
```python
from app.config.database import init_db
success = init_db(force_recreate=True)
assert success == True
```

##### 2.4 数据读写测试
**验证标准**:
- 能创建测试记录
- 能读取测试记录
- 能更新测试记录
- 能删除测试记录

**测试方法**:
```python
from app.config.database import SessionLocal, get_base
from app.models.dictionary import Profession

Base = get_base()
db = SessionLocal()

# 测试创建
profession = Profession(
    id="test_warrior",
    name="Test Warrior",
    icon="test_icon"
)
db.add(profession)
db.commit()

# 测试读取
read_profession = db.query(Profession).get("test_warrior")
assert read_profession.name == "Test Warrior"

# 测试更新
read_profession.name = "Updated Warrior"
db.commit()

# 测试删除
db.delete(read_profession)
db.commit()

db.close()
print("CRUD操作全部成功")
```

---

#### 步骤3: MySQL数据库测试

##### 3.1 前置准备
**准备MySQL环境**:
```sql
-- 在MySQL中执行
CREATE DATABASE gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**修改.env配置**:
```env
DB_TYPE=mysql
MYSQL_HOST=192.168.1.26
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=gw2_log_system
```

##### 3.2 配置验证
**验证标准**:
- MySQL相关配置正确读取
- 连接URL正确生成（密码掩码）

**测试方法**:
```python
from app.core.config import get_settings
from app.config.database import get_current_db_info

settings = get_settings()
assert settings.MYSQL_HOST == "192.168.1.26"
info = get_current_db_info()
print("配置验证通过")
```

##### 3.3 连接测试
**验证标准**:
- 能成功连接MySQL
- 连接池配置正确

**测试方法**:
```python
from app.config.database import test_connection
success = test_connection()
assert success == True
```

##### 3.4 表结构测试
同SQLite的表结构测试

##### 3.5 数据读写测试
同SQLite的数据读写测试

---

#### 步骤4: PostgreSQL数据库测试

##### 4.1 前置准备
**安装驱动**:
```bash
pip install psycopg2-binary
```

**准备PostgreSQL环境**:
```sql
CREATE DATABASE gw2_log_system;
```

**修改.env配置**:
```env
DB_TYPE=postgresql
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=postgres
POSTGRESQL_DATABASE=gw2_log_system
```

##### 4.2 配置验证
同MySQL配置验证

##### 4.3 连接测试
同MySQL连接测试

##### 4.4 表结构测试
同SQLite表结构测试

##### 4.5 数据读写测试
同SQLite数据读写测试

---

#### 步骤5: 数据库切换测试

##### 5.1 运行时切换测试
**验证标准**:
- 能从SQLite切换到MySQL
- 能从MySQL切换到PostgreSQL
- 能从PostgreSQL切换回SQLite
- 每次切换后连接正常

**测试方法**:
```python
from app.config.database import switch_database, test_connection
from app.core.config import DatabaseType

# SQLite → MySQL
switch_database(DatabaseType.MYSQL)
assert test_connection() == True

# MySQL → PostgreSQL
switch_database(DatabaseType.POSTGRESQL)
assert test_connection() == True

# PostgreSQL → SQLite
switch_database(DatabaseType.SQLITE)
assert test_connection() == True

print("切换功能正常")
```

##### 5.2 数据一致性测试
**验证标准**:
- 切换后之前写入的数据保持完整
- 每个数据库有独立的数据空间

---

#### 步骤6: 异常处理测试

##### 6.1 配置错误测试
**测试场景**:
- 无效的DB_TYPE
- 缺少必需的配置
- 无效的端口号

**验证标准**:
- 有明确的错误提示
- 系统不会崩溃

##### 6.2 连接错误测试
**测试场景**:
- 数据库服务未启动
- 错误的用户名/密码
- 数据库不存在
- 网络连接失败

**验证标准**:
- 有明确的错误日志
- 连接失败时返回False

##### 6.3 SQL错误测试
**测试场景**:
- 无效的SQL语句
- 表已存在（重复创建）
- 约束冲突

**验证标准**:
- 异常被正确捕获
- 事务能正确回滚

---

## 五、验证标准

### 5.1 通过标准

| 测试项 | 通过标准 |
|--------|----------|
| 配置验证 | 所有配置正确读取 |
| 连接测试 | test_connection()返回True |
| 表结构测试 | 所有表成功创建，无错误 |
| 数据读写 | CRUD全部成功 |
| 切换测试 | 能在三个数据库间切换 |
| 异常处理 | 有清晰的错误提示，不崩溃 |

### 5.2 完整验收标准
- ✅ SQLite所有测试通过
- ✅ MySQL所有测试通过（如使用）
- ✅ PostgreSQL所有测试通过（如使用）
- ✅ 数据库切换功能正常
- ✅ 异常处理正确
- ✅ 完整测试报告生成

---

## 六、快速测试（使用提供的工具）

### 6.1 使用final_test.py
这是最简单的方法：

```bash
cd tests
python final_test.py
```

### 6.2 自动测试流程
工具会自动执行：
1. SQLite数据库完整测试
2. MySQL数据库测试（如驱动已安装）
3. 切换回SQLite的验证
4. 生成测试报告

### 6.3 查看测试报告
测试完成后会生成JSON格式的报告：
```bash
# 查看报告
cat tests/final_test_results.json
```

---

## 七、手动测试命令

### 7.1 SQLite快速测试
```bash
# 编辑.env使用SQLite
DB_TYPE=sqlite

# 启动服务验证
python main.py
```

### 7.2 MySQL快速测试
```bash
# 编辑.env使用MySQL
DB_TYPE=mysql

# 确保数据库已创建
# CREATE DATABASE gw2_log_system...

# 启动服务验证
python main.py
```

### 7.3 PostgreSQL快速测试
```bash
# 编辑.env使用PostgreSQL
DB_TYPE=postgresql

# 确保数据库已创建
# CREATE DATABASE gw2_log_system...

# 启动服务验证
python main.py
```

---

## 八、常见问题排查

### 问题1: MySQL连接失败
**症状**: `Unknown database 'gw2_log_system'`
**解决**:
```sql
CREATE DATABASE gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题2: 缺少MySQL驱动
**症状**: `ModuleNotFoundError: No module named 'pymysql'`
**解决**:
```bash
pip install pymysql cryptography
```

### 问题3: 缺少PostgreSQL驱动
**症状**: `ModuleNotFoundError: No module named 'psycopg2'`
**解决**:
```bash
pip install psycopg2-binary
```

### 问题4: database目录不存在
**症状**: `unable to open database file`
**解决**: 工具会自动创建，或手动创建：
```bash
mkdir database
```

### 问题5: DB_TYPE 大小写不兼容
**症状**: `Input should be 'sqlite', 'mysql' or 'postgresql'`
**解决**: 系统已支持大小写不敏感，如仍报错请检查 `app/core/config.py` 中的 `_validate_db_type` 校验器。

---

## 九、测试报告模板

### 9.1 报告结构
```json
{
  "test_date": "2026-05-05T...",
  "results": {
    "sqlite": true,
    "mysql": true,
    "postgresql": "skipped",
    "switch_back": true
  },
  "notes": [
    "SQLite测试通过",
    "MySQL测试通过",
    "PostgreSQL跳过（未安装驱动）"
  ]
}
```

### 9.2 验收检查清单

- [ ] Python环境验证通过
- [ ] SQLite完整测试通过
- [ ] MySQL完整测试通过（如果需要）
- [ ] PostgreSQL完整测试通过（如果需要）
- [ ] 数据库切换功能正常
- [ ] 异常处理正常
- [ ] 完整测试报告已生成
- [ ] 服务启动正常

---

## 十、性能测试（可选）

### 10.1 连接池测试
- 并发连接数测试
- 连接复用验证
- 连接超时验证

### 10.2 读写性能测试
- 批量插入测试
- 复杂查询测试
- 索引效率测试

---

## 附录

### A: 数据库管理API
可通过API进行数据库管理：
- `GET /api/v1/database/info` - 获取信息
- `POST /api/v1/database/init` - 初始化
- `POST /api/v1/database/switch` - 切换

### B: 命令行工具
```bash
# 数据库管理
python -m app.services.database_manager init
python -m app.services.database_manager check
```

---

## 总结

本测试方案覆盖了：
- ✅ 完整的环境准备
- ✅ 详细的测试用例设计
- ✅ 三个数据库的完整测试流程
- ✅ 数据读写和切换测试
- ✅ 异常处理测试
- ✅ 快速测试工具
- ✅ 常见问题排查

按照本方案执行，可确保系统在三个数据库上都能正常工作！


---

# 二、MySQL 测试流程

## MySQL数据库完整测试流程

## 文档信息
- 项目: GW2 WvW 日志系统
- 日期: 2026-05-05
- 目标: 完整的MySQL数据库测试和启动流程

---

## 一、MySQL测试完整流程

### 流程图
```
准备工作 → 检查MySQL服务 → 验证连接 → 创建数据库 → 配置.env → 测试连接 → 初始化表 → 数据测试 → 服务启动
```

---

## 二、详细步骤

### 步骤1: 检查MySQL服务状态

#### 1.1 Windows系统检查
```cmd
# 方法1: 检查服务状态
sc query MySQL80

# 或者
sc query MySQL

# 方法2: 检查端口是否监听
netstat -ano | findstr :3306

# 方法3: 检查进程
tasklist | findstr mysqld
```

#### 1.2 Linux/macOS系统检查
```bash
# 检查服务状态
systemctl status mysql
# 或
systemctl status mysqld

# 检查端口
netstat -tlnp | grep 3306
# 或
ss -tlnp | grep 3306

# 检查进程
ps aux | grep mysql
```

#### 1.3 如果MySQL服务未启动
**Windows启动MySQL:**
```cmd
# 使用服务管理器
sc start MySQL80
# 或
net start MySQL80

# 如果服务名不确定
sc query | findstr -i mysql
```

**Linux/macOS启动MySQL:**
```bash
# Systemd系统
systemctl start mysql
# 或
systemctl start mysqld

# Homebrew (macOS)
brew services start mysql
```

---

### 步骤2: 验证MySQL连接

#### 2.1 使用MySQL命令行
```bash
# 测试连接（使用配置的用户和密码）
mysql -h 192.168.1.26 -P 3306 -u root -p

# 输入密码后，如果看到mysql> 提示符，说明连接成功
```

#### 2.2 使用Python脚本测试
```python
# 创建并运行此脚本测试连接
import pymysql

try:
    conn = pymysql.connect(
        host='192.168.1.26',
        port=3306,
        user='root',
        password='123456',
        connect_timeout=10
    )
    print("✅ MySQL连接成功！")
    conn.close()
except Exception as e:
    print(f"❌ MySQL连接失败: {e}")
```

---

### 步骤3: 创建数据库

#### 3.1 创建数据库
连接到MySQL后，执行：
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS gw2_log_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 查看创建结果
SHOW DATABASES LIKE 'gw2_log_system';

-- 选择数据库
USE gw2_log_system;

-- 查看当前数据库
SELECT DATABASE();
```

#### 3.2 验证数据库创建
```sql
SHOW DATABASES;
-- 应该能看到 gw2_log_system
```

---

### 步骤4: 检查MySQL驱动安装

#### 4.1 验证pymysql安装
```bash
pip list | findstr -i pymysql

# 如果没有安装
pip install pymysql cryptography
```

#### 4.2 验证Python导入
```python
import pymysql
print("✅ pymysql导入成功")
```

---

### 步骤5: 检查.env配置

#### 5.1 确保配置正确
```env
DB_TYPE=MYSQL
MYSQL_HOST=192.168.1.26
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=gw2_log_system
```

#### 5.2 验证配置读取
```python
from app.core.config import get_settings
settings = get_settings()
print("DB_TYPE:", settings.DB_TYPE)
print("MYSQL_HOST:", settings.MYSQL_HOST)
print("MYSQL_PORT:", settings.MYSQL_PORT)
print("MYSQL_USER:", settings.MYSQL_USER)
print("MYSQL_DATABASE:", settings.MYSQL_DATABASE)
```

---

### 步骤6: 测试连接（使用项目代码）

#### 6.1 使用database.py测试
```python
from app.config.database import test_connection, get_current_db_info

# 获取配置信息
info = get_current_db_info()
print("当前配置:")
print(f"  类型: {info['type']}")
print(f"  URL: {info['url']}")
print(f"  配置: {info['config']}")

# 测试连接
print("\n测试连接...")
connected = test_connection()
if connected:
    print("✅ 连接成功！")
else:
    print("❌ 连接失败！")
```

---

### 步骤7: 初始化数据库表

#### 7.1 运行初始化
```python
from app.config.database import init_db

# 初始化表结构（如果force_recreate=True会删除并重建）
success = init_db(force_recreate=True)
if success:
    print("✅ 表结构创建成功！")
else:
    print("❌ 表结构创建失败！")
```

#### 7.2 验证表创建
```sql
USE gw2_log_system;
SHOW TABLES;
-- 应该能看到所有项目需要的表（evtc_log, fights, fight_stats, ei_*, members 等）
```

---

### 步骤8: 启动服务测试

#### 8.1 启动服务
```bash
cd backend
python main.py
```

#### 8.2 观察启动日志
成功的启动日志应该包括：
```
INFO: GW2日志系统启动中...
INFO: 初始化数据库连接: DatabaseType.MYSQL
INFO: 创建数据库表结构
INFO: 数据库表结构创建完成
INFO: GW2日志系统启动完成
INFO: Application startup complete.
```

---

## 三、自动化测试工具

### 使用提供的MySQL测试脚本

我已为您创建了一个完整的MySQL测试工具，运行：
```bash
cd tests
python mysql_test_tool.py
```

工具会自动执行：
1. 检查MySQL服务状态
2. 检查pymysql安装
3. 测试MySQL连接
4. 创建数据库（如果不存在）
5. 测试项目连接
6. 初始化表结构
7. 测试数据读写
8. 生成测试报告

---

## 四、常见问题排查

### 问题1: 连接失败 - 无法连接到服务器
**症状**:
```
(2003, "Can't connect to MySQL server on '192.168.1.26' ([WinError 10061] ...)
```

**解决方案**:
1. 检查MySQL服务是否启动
2. 检查IP地址是否正确
3. 检查防火墙设置
4. 检查bind-address配置

### 问题2: 连接失败 - 密码错误
**症状**:
```
(1045, "Access denied for user 'root'@'...' (using password: YES)")
```

**解决方案**:
1. 确认密码正确
2. 检查用户权限
3. 重置root密码（必要时）

### 问题3: 数据库不存在
**症状**:
```
(1049, "Unknown database 'gw2_log_system'")
```

**解决方案**:
1. 按照步骤3创建数据库
2. 确保数据库名拼写正确

### 问题4: pymysql未安装
**症状**:
```
ModuleNotFoundError: No module named 'pymysql'
```

**解决方案**:
```bash
pip install pymysql cryptography
```

### 问题5: 权限不足
**症状**:
```
(1045, "Access denied for user...")
```

**解决方案**:
```sql
-- 在MySQL中执行
GRANT ALL PRIVILEGES ON gw2_log_system.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

### 问题6: 字符集问题
**症状**:
```
字符集不兼容或乱码
```

**解决方案**:
确保使用 utf8mb4 字符集（配置中已设置）

---

## 五、检查清单

### MySQL启动检查清单

- [ ] MySQL服务正在运行
- [ ] 端口3306正在监听
- [ ] 能使用mysql命令行连接
- [ ] 已创建 gw2_log_system 数据库
- [ ] pymysql已正确安装
- [ ] .env配置正确
- [ ] 项目能连接到MySQL
- [ ] 表结构能成功创建
- [ ] 服务能正常启动
- [ ] API能正常响应

---

## 六、快速诊断脚本

### 创建一个诊断脚本 mysql_diagnose.py

```python
# -*- coding: utf-8 -*-
# MySQL诊断脚本
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("MySQL数据库诊断工具")
print("=" * 80)

# 检查1: 检查pymysql安装
print("\n1. 检查pymysql安装:")
try:
    import pymysql
    print("   ✅ pymysql已安装")
except ImportError:
    print("   ❌ pymysql未安装")
    print("   → 请运行: pip install pymysql cryptography")
    sys.exit(1)

# 检查2: 检查.env配置
print("\n2. 检查配置文件:")
from app.core.config import get_settings
settings = get_settings()
print(f"   DB_TYPE: {settings.DB_TYPE}")
print(f"   MYSQL_HOST: {settings.MYSQL_HOST}")
print(f"   MYSQL_PORT: {settings.MYSQL_PORT}")
print(f"   MYSQL_USER: {settings.MYSQL_USER}")
print(f"   MYSQL_DATABASE: {settings.MYSQL_DATABASE}")
print("   ✅ 配置读取成功")

# 检查3: 测试直接连接
print("\n3. 测试直接MySQL连接:")
try:
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        connect_timeout=10
    )
    print("   ✅ MySQL连接成功")
    conn.close()
except Exception as e:
    print(f"   ❌ MySQL连接失败: {e}")
    print("\n请检查:")
    print("   1. MySQL服务是否运行")
    print("   2. 主机地址是否正确")
    print("   3. 用户名密码是否正确")
    print("   4. 网络连接是否正常")
    sys.exit(1)

# 检查4: 检查数据库是否存在
print("\n4. 检查数据库是否存在:")
try:
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        connect_timeout=10
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES LIKE %s", (settings.MYSQL_DATABASE,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print(f"   ✅ 数据库 {settings.MYSQL_DATABASE} 存在")
    else:
        print(f"   ❌ 数据库 {settings.MYSQL_DATABASE} 不存在")
        print("   → 请运行: CREATE DATABASE gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
except Exception as e:
    print(f"   ❌ 检查失败: {e}")
    sys.exit(1)

# 检查5: 测试项目连接
print("\n5. 测试项目连接:")
try:
    from app.config.database import test_connection, get_current_db_info
    info = get_current_db_info()
    connected = test_connection()
    if connected:
        print("   ✅ 项目连接成功")
        print(f"   连接信息: {info}")
    else:
        print("   ❌ 项目连接失败")
except Exception as e:
    print(f"   ❌ 连接异常: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ MySQL诊断完成！所有检查通过")
print("=" * 80)
print("\n现在可以:")
print("1. 初始化表结构: python -c 'from app.config.database import init_db; init_db(force_recreate=True)'")
print("2. 启动服务: python main.py")
```

---

## 七、快速开始命令

### 如果您想快速开始

```bash
# 1. 运行诊断
cd tests
python mysql_diagnose.py

# 2. 如果全部通过，运行测试
python mysql_test_tool.py

# 3. 启动服务
cd ..
python main.py
```

---

## 总结

按照这个流程，您应该能：
- ✅ 检查MySQL服务状态
- ✅ 验证连接配置
- ✅ 创建必要的数据库
- ✅ 测试数据读写
- ✅ 启动完整服务

详细的故障排除步骤和自动化工具都已准备好！


---

# 三、数据库重置指南

## 数据库数据清理与表结构重置指南

## 文档版本

| 版本号 | 更新日期 | 更新说明 |
|--------|----------|----------|
| v3.0 | 2026-05-05 | 更新为与实际模型一致，删除 evtc_* 相关说明 |
| v1.0 | 2026-04-30 | 初始版本 |

---

## 一、概述

本指南介绍如何使用 `tests/db_reset.py` 脚本进行数据库数据清理与表结构重置，确保测试环境处于初始状态，避免因残留数据导致的测试结果不准确。

### 1.1 脚本功能

| 功能 | 说明 |
|------|------|
| 完全清除所有表 | 清空数据库中所有表结构 |
| 重新生成表结构 | 根据最新模型定义重新创建表 |
| 自动备份数据库 | 执行前自动备份数据库（SQLite） |
| 事务回滚机制 | 执行失败时自动恢复备份 |
| 初始化字典数据 | 自动初始化系统预置字典 |
| 创建测试账号 | 自动创建测试管理员账号 |
| 详细执行日志 | 输出详细的执行日志 |

### 1.2 使用场景

| 场景 | 推荐操作 |
|------|----------|
| 全面接口测试前 | 执行完整重置 |
| 模型结构变更后 | 执行表结构重置 |
| 测试数据污染时 | 执行清理重置 |
| 新环境初始化 | 执行完整初始化 |

---

## 二、快速开始

### 2.1 完整重置（推荐）

```bash
# 完整重置（备份+初始化字典+创建管理员）
python tests/db_reset.py --confirm
```

### 2.2 仅重置表结构

```bash
# 仅重置表结构，不初始化数据
python tests/db_reset.py --no-dict --no-admin --confirm
```

### 2.3 详细模式

```bash
# 详细模式，输出DEBUG日志
python tests/db_reset.py -v --confirm
```

---

## 三、命令行参数说明

| 参数 | 短参数 | 说明 | 默认值 |
|------|--------|------|--------|
| `--no-backup` | - | 不备份数据库 | False（备份） |
| `--no-dict` | - | 不初始化字典数据 | False（初始化） |
| `--no-admin` | - | 不创建测试管理员 | False（创建） |
| `--verbose` | `-v` | 详细模式，输出DEBUG日志 | False |
| `--confirm` | - | 自动确认，跳过交互提示 | False（需要确认） |

### 3.1 使用示例

#### 示例1：完整重置

```bash
python tests/db_reset.py --confirm
```

执行步骤：
1. 备份数据库
2. 删除所有表
3. 根据模型创建新表（evtc_log, fights, fight_stats, ei_*, members 等）
4. 初始化字典数据
5. 创建测试管理员账号

#### 示例2：不初始化字典

```bash
python tests/db_reset.py --no-dict --confirm
```

仅重置表结构，保留数据需要手动处理。

#### 示例3：快速重置（跳过备份）

```bash
python tests/db_reset.py --no-backup --confirm
```

适用于测试环境，不需要备份。

#### 示例4：详细调试

```bash
python tests/db_reset.py -v --confirm
```

输出DEBUG级别日志，用于问题排查。

---

## 四、测试执行顺序

### 4.1 推荐的测试执行流程

```
1. 数据库重置
   ↓
2. 基础功能测试
   ↓
3. 接口功能测试
   ↓
4. 集成测试
   ↓
5. 性能测试
```

### 4.2 完整测试命令示例

```bash
# 完整测试流程
python tests/db_reset.py --confirm

# 执行单元测试
pytest tests/ -v

# 执行接口测试
pytest tests/test_api/ -v
```

### 4.3 与pytest集成

#### 使用pytest fixture自动重置

创建 `tests/conftest.py` 或使用现有的fixture：

```python
import pytest
from tests.db_reset import reset_database

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """会话级别fixture：在测试开始前重置数据库"""
    reset_database(backup=True, init_dict=True, create_admin=True, confirm=True)
```

---

## 五、文件与目录

### 5.1 目录结构

```
tests/
├── db_reset.py              # 数据库重置脚本（主文件）
├── logs/                    # 执行日志目录
│   └── db_reset_YYYYMMDD_HHMMSS.log
└── backups/                 # 数据库备份目录
    └── app_backup_YYYYMMDD_HHMMSS.db
```

### 5.2 日志文件

日志文件保存在 `tests/logs/` 目录下，文件名格式：
```
db_reset_YYYYMMDD_HHMMSS.log
```

日志级别：
- INFO: 主要执行步骤
- DEBUG: 详细操作信息（-v参数启用）

---

## 六、安全与回滚

### 6.1 自动备份

- 默认每次执行前都会自动备份
- 备份保存在 `tests/backups/` 目录
- 备份文件名包含时间戳

### 6.2 失败回滚

如果执行失败，脚本会自动从最近的备份恢复数据库：

```
执行失败 ←
    ↓
检测到备份 ←
    ↓
自动恢复 ←
    ↓
完成回滚
```

### 6.3 手动恢复

如需手动恢复：

```bash
# 查看可用备份
ls tests/backups/

# 复制备份到数据库位置
cp tests/backups/app_backup_20260430_123456.db ./database/app.db
```

---

## 七、数据库初始化

### 7.1 字典数据初始化

执行成功后会自动初始化以下字典类型：

| 字典类型 | 说明 |
|----------|------|
| `profession` | 职业类型 |
| `specialization` | 精英特长 |
| `role` | 角色定位 |
| `scoring_dimension` | 评分维度 |
| `scoring_rule` | 评分规则 |
| `game_mode` | 游戏模式 |
| `buff_id` | 增益ID |

### 7.2 测试管理员账号

默认创建的测试账号：

| 属性 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |
| 邮箱 | `admin@localhost` |
| 角色 | `super_admin` |
| 状态 | 已激活 |

---

## 八、高级用法

### 8.1 编程式调用

脚本支持Python模块导入调用：

```python
from tests.db_reset import reset_database, setup_logging

# 配置日志
logger = setup_logging(verbose=True)

# 执行重置
success = reset_database(
    backup=True,
    init_dict=True,
    create_admin=True,
    logger=logger
)

if success:
    print("数据库重置成功")
else:
    print("数据库重置失败")
```

### 8.2 CI/CD集成

在CI/CD流程中使用：

```yaml
# .github/workflows/test.yml
- name: Reset Database
  run: python tests/db_reset.py --confirm

- name: Run Tests
  run: pytest tests/ -v
```

---

## 九、常见问题

### Q1：执行时提示找不到模块？

**A**: 确保在项目根目录执行命令：

```bash
cd d:\Code\Gw2-wvw-log-analyzer\backend
python tests/db_reset.py
```

### Q2：如何确认重置成功？

**A**: 检查输出日志，看到以下信息表示成功：

```
======================================
数据库重置成功完成
======================================
```

### Q3：字典数据没有初始化？

**A**: 检查是否使用了 `--no-dict` 参数。如果没有，查看日志了解原因。

### Q4：如何只重置特定表？

**A**: 当前脚本不支持选择性重置。可以：
1. 使用本脚本完整重置
2. 或编写自定义SQL脚本

### Q5：数据库类型兼容？

**A**: 当前脚本支持：
- SQLite（完全支持）
- MySQL（基础支持，可能需要调整）
- PostgreSQL（基础支持，可能需要调整）

---

## 十、技术细节

### 10.1 删除表的实现

对于SQLite：

```python
# 临时禁用外键约束
PRAGMA foreign_keys = OFF;

# 删除所有表
DROP TABLE ...;

# 重新启用外键约束
PRAGMA foreign_keys = ON;
```

### 10.2 创建表的实现

使用SQLAlchemy的metadata：

```python
Base.metadata.create_all(bind=engine)
```

---

## 十一、附录

### 11.1 完整示例脚本

```bash
#!/bin/bash
# 完整测试流程脚本

echo "步骤1: 数据库重置"
python tests/db_reset.py --confirm

echo "步骤2: 执行测试"
pytest tests/ -v --html=tests/reports/test_report.html

echo "测试完成"
```

### 11.2 快速参考卡

| 目标 | 命令 |
|------|------|
| 完整重置 | `python tests/db_reset.py --confirm` |
| 只重置表结构 | `python tests/db_reset.py --no-dict --no-admin --confirm` |
| 详细日志 | `python tests/db_reset.py -v --confirm` |
| 查看备份 | `ls tests/backups/` |
| 查看日志 | `ls tests/logs/` |


---

# 四、数据库升级指南

## 数据库多类型支持升级文档

## 📋 概述

本次升级为GW2 WvW日志系统增加了完整的多数据库支持，现在可以无缝切换SQLite、MySQL和PostgreSQL数据库。

## ✅ 已完成功能

### 1. 数据验证工具
- 创建了完整的数据完整性检查工具
- 自动检测数据异常和缺失
- 发现了数据丢失问题的根本原因

### 2. 多数据库架构
- 支持SQLite（默认，Python内置）
- 支持MySQL（需安装pymysql）
- 支持PostgreSQL（需安装psycopg2-binary）
- 统一的配置管理

### 3. 数据库配置管理
- 配置集中到 `app/core/config.py`（558 行，统一 Settings 类）
- `app/config/database_settings.py` 为向后兼容入口
- 环境变量支持
- 运行时切换功能
- 连接池优化

### 4. 自动建表功能
- 系统启动时自动检查并创建缺失表（`AUTO_CREATE_TABLES=True`）
- 支持强制重建模式
- 向后兼容原代码

### 5. 管理工具
- 命令行管理工具
- Web API管理端点
- 连接测试功能
- 表结构验证

## 📁 文件结构

### 核心文件
```
backend/app/
├── core/
│   └── config.py                  # 统一配置管理（558行，集中配置）
├── config/
│   ├── database_settings.py       # 向后兼容入口（从 core.config 导入）
│   └── database.py               # 数据库连接与自动建表
├── services/
│   └── system/
│       └── database_manager.py   # 数据库管理器
└── routers/
    └── system/
        └── database_management.py # 数据库管理API
```

### 环境变量
```
backend/.env.example               # 配置示例
```

## 🚀 快速开始

### 1. 使用SQLite（默认，无需额外配置）

复制配置文件并启动：

```bash
cp .env.example .env
# 编辑.env（可选修改SQLite路径）

# 初始化数据库
python -c "
from app.config.database import init_db
init_db()
print('数据库初始化完成')
"

# 启动服务
python main.py
```

### 2. 使用MySQL

#### 安装MySQL驱动
```bash
pip install pymysql cryptography
```

#### 配置MySQL
编辑.env文件：

```env
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=gw2_log_system
MYSQL_CHARSET=utf8mb4
```

#### 准备MySQL数据库
```sql
CREATE DATABASE gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 初始化并启动
```bash
# 测试连接
python -c "from app.config.database import test_connection; print(test_connection())"

# 启动服务
python main.py
```

### 3. 使用PostgreSQL

#### 安装PostgreSQL驱动
```bash
pip install psycopg2-binary
```

#### 配置PostgreSQL
编辑.env文件：

```env
DB_TYPE=postgresql
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=gw2_log_system
```

#### 准备PostgreSQL数据库
```sql
CREATE DATABASE gw2_log_system;
```

#### 初始化并启动
```bash
# 测试连接
python -c "from app.config.database import test_connection; print(test_connection())"

# 启动服务
python main.py
```

## 🎯 数据库管理API

### 获取数据库信息
```
GET /api/v1/database/info
```

### 检查表结构
```
GET /api/v1/database/check
```

### 初始化数据库
```
POST /api/v1/database/init?force_recreate=true
```

### 切换数据库
```
POST /api/v1/database/switch?db_type=sqlite
```

## 🔧 命令行工具

### 初始化数据库
```bash
python -m app.services.system.database_manager init
python -m app.services.system.database_manager init --force  # 强制重建
```

### 检查表结构
```bash
python -m app.services.system.database_manager check
```

## 📝 配置说明

### 环境变量完整列表

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DB_TYPE | 数据库类型 (sqlite/mysql/postgresql) | sqlite |
| SQLITE_DB_PATH | SQLite文件路径 | ./database/app.db |
| MYSQL_HOST | MySQL主机 | localhost |
| MYSQL_PORT | MySQL端口 | 3306 |
| MYSQL_USER | MySQL用户名 | root |
| MYSQL_PASSWORD | MySQL密码 | - |
| MYSQL_DATABASE | MySQL数据库名 | gw2_log_system |
| MYSQL_CHARSET | MySQL字符集 | utf8mb4 |
| MYSQL_POOL_SIZE | 连接池大小 | 10 |
| MYSQL_MAX_OVERFLOW | 最大溢出连接 | 20 |
| POSTGRESQL_HOST | PostgreSQL主机 | localhost |
| POSTGRESQL_PORT | PostgreSQL端口 | 5432 |
| POSTGRESQL_USER | PostgreSQL用户名 | postgres |
| POSTGRESQL_PASSWORD | PostgreSQL密码 | - |
| POSTGRESQL_DATABASE | PostgreSQL数据库名 | gw2_log_system |
| POSTGRESQL_POOL_SIZE | 连接池大小 | 10 |
| POSTGRESQL_MAX_OVERFLOW | 最大溢出连接 | 20 |
| POOL_PRE_PING | 连接前验证 | True |
| POOL_RECYCLE | 连接回收时间（秒） | 300 |
| AUTO_CREATE_TABLES | 自动建表 | True |
| AUTO_MIGRATE | 自动迁移（待实现） | False |

## 🧪 测试验证

### 运行数据库测试
```bash
python tests/test_database_multitype.py
```

### 测试内容
- SQLite基本功能
- 配置加载和验证
- 数据库管理器功能
- 连接池管理

## 🔄 升级指南

### 从旧版本升级

1. 更新代码
2. 复制.env.example为.env
3. 配置数据库（SQLite或MySQL或PostgreSQL）
4. 运行数据库初始化
5. 重启服务

### 迁移现有数据

如果需要迁移SQLite到MySQL（将来版本），将提供迁移工具。

## 🎨 性能优化

### MySQL配置建议
- 使用连接池减少连接开销
- 配置合适的pool_size（默认10）
- 启用pool_pre_ping防断开
- 根据负载调整max_overflow（默认20）

### PostgreSQL配置建议
- 使用连接池减少连接开销
- 配置合适的pool_size（默认10）
- 根据负载调整max_overflow（默认20）

### SQLite优化
- 使用Write-Ahead Logging(WAL)
- 设置适当的缓存大小
- 定期vacuum优化

## 🛡️ 安全建议

1. 永远不要将数据库密码提交到代码仓库
2. 使用最小权限原则创建数据库用户
3. 使用环境变量管理敏感配置
4. 在生产环境启用SSL连接（MySQL/PostgreSQL）

## 🚀 下一步计划

1. 实现Alembic数据迁移
2. 添加备份和恢复功能
3. 优化查询性能
4. 完善监控和告警

---

## 📞 支持

如有问题，请检查：
1. logs/app.log中的错误日志
2. 数据库连接配置
3. 数据库用户权限
4. 驱动程序是否正确安装


---

# 五、问题修复记录：DB_TYPE 大小写不兼容

## 问题信息

### 发生时间
2026-05-01

### 错误症状
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for DatabaseSettings
DB_TYPE
  Input should be 'sqlite', 'mysql' or 'postgresql'
  [type=enum, input_value='MYSQL', input_type=str]
```

### 问题原因
- `.env`文件中使用了`DB_TYPE=MYSQL`（大写）
- `DatabaseType`枚举定义为小写值
- Pydantic严格匹配枚举值，不支持自动转换

---

## 修复方案

### 修复方法
在 `app/core/config.py` 的 `DatabaseType` 枚举中添加 `_missing_` 类方法，支持不区分大小写的输入：

```python
class DatabaseType(str, Enum):
    """数据库类型"""
    SQLITE = "sqlite"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    
    @classmethod
    def _missing_(cls, value):
        """支持不区分大小写"""
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None
```

同时，在 `Settings` 类中添加字段校验器：

```python
@field_validator("DB_TYPE", mode="before")
@classmethod
def _validate_db_type(cls, v: Any) -> DatabaseType:
    """支持大小写不敏感的数据库类型"""
    if isinstance(v, str):
        normalized = v.lower()
        for member in DatabaseType:
            if member.value == normalized:
                return member
    return v
```

### 修复文件
- `backend/app/core/config.py`

---

## 支持的输入值

现在支持以下所有格式：

| 数据库 | 支持的输入值 |
|--------|-------------|
| SQLite | `sqlite`, `SQLite`, `SQLITE`, `SQLite` |
| MySQL | `mysql`, `MySQL`, `MYSQL`, `MySql` |
| PostgreSQL | `postgresql`, `PostgreSQL`, `POSTGRESQL` |

---

## 验证结果

### 服务启动验证
✅ 修复后服务成功启动：
```
2026-05-05 03:04:14,465 - app - INFO - GW2日志系统启动完成
INFO:     Application startup complete.
```

### 数据库连接验证
✅ SQLite数据库连接正常
✅ MySQL数据库连接正常
✅ PostgreSQL数据库连接正常
✅ 表结构创建正常
✅ 字典数据加载正常

---

## 测试建议

### 快速测试大小写兼容性
可以使用以下配置测试：

```env
# 测试1: 小写
DB_TYPE=sqlite

# 测试2: 大写
DB_TYPE=MYSQL

# 测试3: 混合大小写
DB_TYPE=PostgreSQL
```

都应该能正常工作！

---

## 相关文档

- `docs/03-database/database-guide.md` - 完整的多数据库测试方案
- `docs/03-database/storage-strategy.md` - 存储策略文档

---

## 文件清单

### 修复的文件
- `backend/app/core/config.py` - 添加 _missing_ 方法和字段校验器

### 创建的文档
- `docs/03-database/database-guide.md` - 本文件

---

## 总结

✅ **问题已完全修复！**

现在系统支持：
- 任意大小写的DB_TYPE配置
- SQLite、MySQL、PostgreSQL三个数据库
- 完整的运行时切换功能
- 详细的测试方案和工具

服务已正常运行于 http://0.0.0.0:8000！
