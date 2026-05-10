# -*- coding: utf-8 -*-
"""
API 接口文档生成脚本
====================
基于 FastAPI OpenAPI Schema 生成完整接口文档（Markdown 格式），
包含：URL、方法、认证要求、请求参数、请求示例、响应结构、错误码说明。

用法:
    python scripts/generate_api_docs.py

输出:
    docs/02-api/API_INTERFACE_DOCUMENTATION.md
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

OPENAPI_PATH = Path("docs/openapi_schema.json")
OUTPUT_PATH = Path("docs/02-api-documentation/api-interface-documentation.md")


def get_type_str(schema: Dict[str, Any]) -> str:
    """从 schema 提取类型描述字符串"""
    if "type" in schema:
        t = schema["type"]
        if t == "array" and "items" in schema:
            item_type = get_type_str(schema["items"])
            return f"array[{item_type}]"
        return t
    if "$ref" in schema:
        ref = schema["$ref"]
        return ref.split("/")[-1]
    return "any"


def schema_to_example(
    schema: Dict[str, Any], components: Dict[str, Any], depth: int = 0
) -> Any:
    """根据 schema 生成示例值"""
    if depth > 5:
        return "..."
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        ref_schema = components.get("schemas", {}).get(ref_name, {})
        return schema_to_example(ref_schema, components, depth + 1)
    if "anyOf" in schema:
        return schema_to_example(schema["anyOf"][0], components, depth + 1)
    if "allOf" in schema:
        result = {}
        for sub in schema["allOf"]:
            sub_ex = schema_to_example(sub, components, depth + 1)
            if isinstance(sub_ex, dict):
                result.update(sub_ex)
        return result

    t = schema.get("type", "any")
    if t == "object":
        result = {}
        for prop_name, prop_schema in schema.get("properties", {}).items():
            result[prop_name] = schema_to_example(prop_schema, components, depth + 1)
        return result
    if t == "array":
        item = schema_to_example(schema.get("items", {}), components, depth + 1)
        return [item] if item != "..." else []
    if t == "string":
        fmt = schema.get("format", "")
        if fmt == "date-time":
            return "2026-01-01T00:00:00Z"
        if fmt == "uuid":
            return "550e8400-e29b-41d4-a716-446655440000"
        if "enum" in schema:
            return schema["enum"][0]
        return f"string({prop_name[:20]})" if "prop_name" in dir() else "string"
    if t == "integer":
        return 0
    if t == "number":
        return 0.0
    if t == "boolean":
        return True
    return None


def build_param_table(params: List[Dict[str, Any]]) -> str:
    """构建参数表格"""
    if not params:
        return "无"
    lines = [
        "| 参数名 | 位置 | 类型 | 必填 | 说明 |",
        "|--------|------|------|------|------|",
    ]
    for p in params:
        name = p.get("name", "-")
        loc = p.get("in", "-")
        schema = p.get("schema", {})
        t = get_type_str(schema)
        req = "是" if p.get("required") else "否"
        desc = p.get("description", "-").replace("\n", " ")
        lines.append(f"| {name} | {loc} | {t} | {req} | {desc} |")
    return "\n".join(lines)


def extract_request_body_example(
    spec: Dict[str, Any], components: Dict[str, Any]
) -> str:
    """提取请求体示例"""
    body = spec.get("requestBody", {})
    if not body:
        return ""
    content = body.get("content", {})
    for mime, mime_spec in content.items():
        schema = mime_spec.get("schema", {})
        example = schema_to_example(schema, components)
        return f"\n**Content-Type**: `{mime}`\n\n```json\n{json.dumps(example, ensure_ascii=False, indent=2)}\n```\n"
    return ""


def extract_response_examples(spec: Dict[str, Any], components: Dict[str, Any]) -> str:
    """提取响应示例"""
    responses = spec.get("responses", {})
    parts = []
    for code, resp_spec in sorted(responses.items(), key=lambda x: x[0]):
        desc = resp_spec.get("description", "")
        content = resp_spec.get("content", {})
        example_str = ""
        for mime, mime_spec in content.items():
            schema = mime_spec.get("schema", {})
            example = schema_to_example(schema, components)
            example_str = (
                f"\n```json\n{json.dumps(example, ensure_ascii=False, indent=2)}\n```\n"
            )
        parts.append(f"**HTTP {code}** - {desc}{example_str}")
    return "\n".join(parts)


def generate_endpoint_doc(
    path: str, method: str, spec: Dict[str, Any], components: Dict[str, Any]
) -> str:
    """为单个端点生成文档块"""
    summary = spec.get("summary", spec.get("operationId", "未命名接口"))
    desc = spec.get("description", "暂无描述").strip()
    tags = spec.get("tags", ["未分类"])
    tag = tags[0] if tags else "未分类"

    # 判断是否需要认证：检查是否有 security 或 401/403 响应
    needs_auth = bool(spec.get("security"))
    if not needs_auth:
        for code in spec.get("responses", {}):
            if code in ("401", "403"):
                needs_auth = True
                break

    # 参数
    params = spec.get("parameters", [])
    param_table = build_param_table(params)

    # 请求体
    req_example = extract_request_body_example(spec, components)

    # 响应
    resp_examples = extract_response_examples(spec, components)

    auth_badge = "🔒 需要认证" if needs_auth else "🌐 公开访问"

    doc = f"""### {summary}

**路径**: `{method.upper()} {path}`  
**分类**: {tag}  
**访问控制**: {auth_badge}

**接口说明**:  
{desc}

**请求参数**:
{param_table}
{req_example}
**响应说明**:
{resp_examples}

---
"""
    return doc


def generate_full_documentation(schema: Dict[str, Any]) -> str:
    """生成完整文档"""
    components = schema.get("components", {})
    paths = schema.get("paths", {})
    info = schema.get("info", {})

    # 按 tag 分组
    grouped: Dict[str, List[str]] = {}
    for path in sorted(paths.keys()):
        methods = paths[path]
        for method, spec in methods.items():
            if method == "parameters":
                continue
            tags = spec.get("tags", ["未分类"])
            tag = tags[0] if tags else "未分类"
            doc_block = generate_endpoint_doc(path, method, spec, components)
            grouped.setdefault(tag, []).append(doc_block)

    title = info.get("title", "API 接口文档")
    version = info.get("version", "1.0.0")
    total_endpoints = sum(len(m) for m in paths.values())
    lines = [
        f"# {title}",
        "",
        f"> **版本**: {version}  ",
        f"> **生成时间**: {datetime.now().isoformat()}  ",
        f"> **端点总数**: {total_endpoints}  ",
        "",
        "## Ŀ¼",
        "",
    ]

    for tag in sorted(grouped.keys()):
        anchor = re.sub(r"[^\w\s-]", "", tag).strip().replace(" ", "-")
        lines.append(f"- [{tag}](#{anchor})")

    lines.append("")
    lines.append("---")
    lines.append("")

    for tag in sorted(grouped.keys()):
        anchor = re.sub(r"[^\w\s-]", "", tag).strip().replace(" ", "-")
        lines.append(f"## {tag}")
        lines.append("")
        for block in grouped[tag]:
            lines.append(block)
        lines.append("")

    # 添加通用说明附录
    lines.append("""## 附录

### 通用响应结构

所有接口统一返回以下结构：

```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 认证方式

受保护接口需在请求头中携带 JWT Token：

```
Authorization: Bearer <access_token>
```

Token 通过 `POST /api/v1/auth/login` 获取，默认有效期 2 小时。

### 常见 HTTP 状态码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | 成功 | 请求处理成功 |
| 400 | 请求参数错误 | 业务校验失败（如密码错误） |
| 401 | 未认证 | 缺少 Token 或 Token 无效/过期 |
| 403 | 无权限 | 用户存在但无操作权限 |
| 404 | 资源不存在 | 请求的日志/用户/战斗等不存在 |
| 422 | 参数校验失败 | FastAPI 自动校验失败（类型错误、必填缺失） |
| 500 | 服务器内部错误 | 未捕获异常 |

### 分页参数约定

列表接口通常支持以下查询参数：

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量 |
| search | string | - | 关键字搜索 |
| sort_by | string | - | 排序字段 |
| sort_order | string | desc | 排序方向 (asc/desc) |

### 前端集成注意事项

1. **Base URL**: 所有 `/api/v1/*` 端点前缀固定，开发环境建议配置代理。
2. **超时设置**: 上传/解析类接口可能耗时较长，建议设置 60s 以上超时。
3. **重试策略**: 500 错误可指数退避重试；401 错误应跳转登录页。
4. **数据缓存**: 字典数据、游戏数据等静态内容可本地缓存。
5. **路由前缀 Bug**: `/api/v1/api/v1/ei-analysis/*` 和 `/api/v1/api/v1/monitoring/*` 存在重复前缀，
   前端调用时请使用实际路径（以 `/docs` 中展示为准）。
""")

    return "\n".join(lines)


def main():
    if not OPENAPI_PATH.exists():
        print(f"错误: 找不到 OpenAPI Schema 文件: {OPENAPI_PATH}")
        print(
            "请先运行: python -c \"from main import app; import json; json.dump(app.openapi(), open('docs/openapi_schema.json','w'))\""
        )
        return

    with open(OPENAPI_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    doc_content = generate_full_documentation(schema)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(doc_content)

    print(f"[OK] API 接口文档已生成: {OUTPUT_PATH}")
    ep_count = sum(
        1 for m in schema.get("paths", {}).values() for k in m if k != "parameters"
    )
    print(f"   端点总数: {ep_count}")
    tag_count = len(
        set(
            tag
            for p in schema.get("paths", {}).values()
            for m, s in p.items()
            if m != "parameters"
            for tag in s.get("tags", ["未分类"])
        )
    )
    print(f"   Tag 分类数: {tag_count}")


if __name__ == "__main__":
    main()
