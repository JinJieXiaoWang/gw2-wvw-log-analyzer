# GW2 WvW 日志解析与评分系统

基于 FastAPI + SQLite 的激战2(Guild Wars 2) WvW战场日志解析系统，提供战斗数据分析、出勤统计、Build管理和AI智能复盘功能。

## 技术栈

- **Web框架**: FastAPI 0.100+
- **数据库**: SQLite (内置，无需额外安装)
- **ORM**: SQLAlchemy 2.0+
- **数据验证**: Pydantic 2.0+
- **密码加密**: passlib[bcrypt]
- **ASGI服务器**: Uvicorn
- **测试框架**: Pytest

## 项目结构

```
gw2-log-system/
├── app/
│   ├── config/              # 配置管理
│   ├── models/              # 数据模型
│   ├── schemas/             # 数据验证
│   ├── services/            # 业务逻辑
│   ├── routers/             # API路由
│   └── utils/               # 工具函数
├── database/
│   └── migrations/           # 数据库迁移
├── tests/                   # 单元测试
├── main.py                  # 应用入口
├── requirements.txt         # 依赖列表
├── SPEC.md                  # 技术规范
└── DEV_PLAN.md             # 开发计划
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python database/migrations/init_db.py
```

这会创建数据库并添加示例数据：
- 管理员账户: admin / admin123
- 示例成员和战斗数据

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn 直接启动：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能

### 日志管理
- zevtc文件上传
- 日志解析状态跟踪
- 按服务器/地图筛选

### 战斗分析
- 伤害/治疗统计
- 击杀/死亡数据
- 职业分布分析

### 出勤统计
- 成员参战时长
- 战绩评分排名
- 多维度数据导出

### 技能循环
- 技能释放时序
- 理想vs实战对比
- 失误点识别

### Build解析
- 代码解析展示
- 装备/天赋/技能
- Build对比功能

### AI分析
- 战斗短板识别
- 技能循环优化建议
- Build适配度分析
- 趋势预测

### 数据看板
- 公会数据大盘
- 近期战斗动态
- 趋势图表展示

## API接口

### 认证 `/api/v1/auth`
- `POST /login` - 管理员登录
- `POST /logout` - 登出
- `GET /status` - 登录状态

### 日志 `/api/v1/logs`
- `GET /` - 获取日志列表
- `GET /{id}` - 获取日志详情
- `POST /` - 上传日志
- `DELETE /{id}` - 删除日志

### 战斗 `/api/v1/fights`
- `GET /` - 获取战斗列表
- `GET /{id}` - 获取战斗详情
- `GET /{id}/stats` - 获取战斗统计

### 成员 `/api/v1/members`
- `GET /` - 获取成员列表
- `GET /{id}` - 获取成员详情
- `GET /ranking` - 获取排名
- `GET /professions` - 职业分布

### AI `/api/v1/ai`
- `GET /reports` - AI报告列表
- `POST /analyze/fight/{id}` - 分析战斗
- `GET /trend` - 趋势分析

详见 API文档 http://localhost:8000/docs

## 权限设计

- **访客**: 无需登录，可浏览所有公开数据
- **管理员**: 需要登录，可进行上传、修改、删除等操作

## 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=app --cov-report=term-missing

# 生成HTML覆盖率报告
pytest --cov=app --cov-report=html
```

## 配置说明

在 `app/config/settings.py` 中修改配置，或创建 `.env` 文件：

```bash
APP_NAME=GW2 WvW日志系统
DEBUG=True
DATABASE_URL=sqlite:///./database/app.db
LOG_LEVEL=INFO
```

## 前端对接

API 基础地址: `http://localhost:8000/api/v1`

已配置 CORS 支持:
- `http://localhost:5173` (Vite 默认)
- `http://localhost:3000`

统一响应格式:
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

## 开发规范

- Python: PEP 8，4空格缩进
- 所有函数添加中文注释
- 变量和函数: snake_case
- 类名: PascalCase
- Git提交: feat/fix/docs/refactor/test

## 许可证

MIT License
