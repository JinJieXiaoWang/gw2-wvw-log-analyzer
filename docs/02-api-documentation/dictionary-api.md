# GW2 WVW 日志解析管理系统 - 字典功能 API 文档

> **版本**: v3.0  
> **更新日期**: 2026-05-05  
> **责任人**: 帅姐姐  
> **整合来源**: dictionary_api_usage.md, 字典功能使用指南.md, 字典功能前端开发指南.md

## 版本变更记录

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 依据代码更新端点列表，补充 `/dictionary/options/{dict_type}` 公开接口 | 系统 |
| v2.0 | 2026-05-01 | 整合三份字典相关文档，统一为字典功能 API 规范 | 帅姐姐 |
| v1.0 | 2026-04-30 | 初始版本 | 技术团队 |

---

## 文档版本

| 版本号 | 更新日期 | 更新说明 |
|--------|----------|----------|
| v1.0 | 2026-04-30 | 初始版本 |

---

## 一、概述

### 1.1 功能介绍

系统字典功能是用于管理系统中各类枚举、分类、状态值的功能模块。它提供了：

- **字典类型管理**：字典分组管理，如"用户状态"、"日志类型"等
- **字典数据管理**：字典项管理，具体的可选值
- **缓存机制**：内存缓存，高性能读取
- **下拉选项接口**：标准的前端下拉选项格式
- **标签值转换**：通过dict_value转dict_label，反之亦然

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| 字典类型（Dict Type） | 字典分组，如"职业类型"、"角色定位"，通过dict_type标识 |
| 字典项（Dict Data） | 具体的可选值，如"战士"、"治疗"，通过dict_value标识 |
| 字典编码（dict_code） | 字典项的唯一主键 |
| 字典标签（dict_label） | 显示给用户的文本 |
| 字典值（dict_value） | 存储到数据库的实际值 |
| 排序（dict_sort） | 字典项的排序顺序，越小越靠前 |
| 默认值（is_default） | 标识是否为默认选项 |
| 状态（status） | 0-启用，1-禁用，禁用的不显示在下拉选项中 |

### 1.3 设计规范

- 字典类型编码（dict_type）必须唯一，使用小写英文，下划线分隔
- 同一字典类型下，字典值（dict_value）必须唯一
- 字典项按sort_order排序
- 禁用的字典项不显示在下拉选项中

---

## 二、接口规范

### 2.1 基础信息

| 项目 | 值 |
|------|-----|
| 接口前缀 | `/api/v1/dictionary` |
| 认证方式 | Bearer Token（JWT），需要登录 |
| 返回格式 | JSON |
| 字符编码 | UTF-8 |

### 2.2 通用响应格式

#### 成功响应

```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "timestamp": "2026-04-30T12:00:00Z"
}
```

#### 失败响应

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "data": null,
  "timestamp": "2026-04-30T12:00:00Z"
}
```

#### 分页响应格式

```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": "2026-04-30T12:00:00Z"
}
```

### 2.3 错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| UNAUTHORIZED | 未认证 | 需要登录或token过期 |
| FORBIDDEN | 权限不足 | 需要管理员权限 |
| NOT_FOUND | 资源不存在 | 检查请求的ID/编码是否正确 |
| BAD_REQUEST | 请求参数错误 | 检查请求参数格式和内容 |
| INTERNAL_ERROR | 服务器错误 | 联系后端开发者 |

---

## 三、字典类型管理接口

### 3.1 获取字典类型列表

**接口路径**：`GET /types`

**功能说明**：分页获取字典类型列表，支持状态和关键词筛选

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | Query | Integer | 否 | 页码，默认1 |
| page_size | Query | Integer | 否 | 每页数量，默认20，最大100 |
| status | Query | Integer | 否 | 状态筛选：0-启用，1-禁用 |
| keyword | Query | String | 否 | 关键词筛选，支持按名称或编码搜索 |

**响应示例**：

```json
{
  "success": true,
  "message": "获取字典类型成功",
  "data": {
    "items": [
      {
        "dict_id": 1,
        "dict_type": "profession",
        "dict_name": "职业类型",
        "status": 0,
        "sort_order": 1,
        "remark": "职业分类"
      },
      {
        "dict_id": 2,
        "dict_type": "role",
        "dict_name": "角色定位",
        "status": 0,
        "sort_order": 2,
        "remark": null
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  },
  "timestamp": "2026-04-30T12:00:00Z"
}
```

**前端使用示例**：

```javascript
// 获取启用的字典类型列表
const response = await axios.get('/api/v1/dictionary/types', {
  params: { page: 1, page_size: 20, status: 0 }
});
console.log('字典类型列表:', response.data.data.items);
```

### 3.2 获取所有启用的字典类型

**接口路径**：`GET /types/all`

**功能说明**：获取所有启用的字典类型，不分页，用于字典管理页面的左侧分类列表

**请求参数**：无

**响应示例**：

```json
{
  "success": true,
  "message": "获取字典类型成功",
  "data": [
    {
      "dict_id": 1,
      "dict_type": "profession",
      "dict_name": "职业类型",
      "status": 0,
      "sort_order": 1,
      "remark": "职业分类"
    }
  ],
  "timestamp": "2026-04-30T12:00:00Z"
}
```

### 3.3 获取单个字典类型

**接口路径**：`GET /types/{dict_id}`

**功能说明**：获取指定ID的字典类型详情

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_id | Path | Integer | 是 | 字典类型ID |

**响应示例**：

```json
{
  "success": true,
  "message": "获取字典类型成功",
  "data": {
    "dict_id": 1,
    "dict_type": "profession",
    "dict_name": "职业类型",
    "status": 0,
    "sort_order": 1,
    "remark": "职业分类"
  },
  "timestamp": "2026-04-30T12:00:00Z"
}
```

### 3.4 创建字典类型

**接口路径**：`POST /types`

**功能说明**：创建新的字典类型（需要超级管理员权限）

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_type | Body | String | 是 | 字典类型编码，必须唯一 |
| dict_name | Body | String | 是 | 字典类型名称 |
| status | Body | Integer | 否 | 状态：0-启用，1-禁用，默认0 |
| sort_order | Body | Integer | 否 | 排序，默认0 |
| remark | Body | String | 否 | 备注说明 |

**请求示例**：

```json
{
  "dict_type": "log_level",
  "dict_name": "日志级别",
  "status": 0,
  "sort_order": 10,
  "remark": "日志严重程度分级"
}
```

**响应示例**：

```json
{
  "success": true,
  "message": "创建字典类型成功",
  "data": {
    "dict_id": 3,
    "dict_type": "log_level",
    "dict_name": "日志级别",
    "status": 0,
    "sort_order": 10,
    "remark": "日志严重程度分级"
  },
  "timestamp": "2026-04-30T12:00:00Z"
}
```

### 3.5 更新字典类型

**接口路径**：`PUT /types/{dict_id}`

**功能说明**：更新字典类型信息（需要超级管理员权限）

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_id | Path | Integer | 是 | 字典类型ID |
| dict_name | Body | String | 否 | 字典类型名称 |
| status | Body | Integer | 否 | 状态 |
| sort_order | Body | Integer | 否 | 排序 |
| remark | Body | String | 否 | 备注说明 |

**注意**：`dict_type`不能修改，只能修改其他字段

**请求示例**：

```json
{
  "dict_name": "更新后的日志级别",
  "sort_order": 5,
  "remark": "修改后的备注"
}
```

### 3.6 删除字典类型

**接口路径**：`DELETE /types/{dict_id}`

**功能说明**：删除字典类型及其关联的所有字典项（需要超级管理员权限）

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_id | Path | Integer | 是 | 字典类型ID |

**响应示例**：

```json
{
  "success": true,
  "message": "删除字典类型成功",
  "data": null,
  "timestamp": "2026-04-30T12:00:00Z"
}
```

---

## 四、字典数据管理接口

### 4.1 获取字典项列表

**接口路径**：`GET /data`

**功能说明**：获取指定字典类型的字典项列表，支持分页和状态筛选

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_type | Query | String | 是 | 字典类型编码 |
| page | Query | Integer | 否 | 页码，默认1 |
| page_size | Query | Integer | 否 | 每页数量，默认50，最大200 |
| status | Query | Integer | 否 | 状态筛选 |

**响应示例**：

```json
{
  "success": true,
  "message": "获取字典项成功",
  "data": {
    "items": [
      {
        "dict_code": 1,
        "dict_type": "profession",
        "dict_label": "战士",
        "dict_value": "warrior",
        "dict_sort": 1,
        "data_type": null,
        "css_class": "#FF0000",
        "list_class": null,
        "is_default": 0,
        "status": 0,
        "remark": "近战物理"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 50,
    "total_pages": 1
  },
  "timestamp": "2026-04-30T12:00:00Z"
}
```

### 4.2 获取单个字典项

**接口路径**：`GET /data/{dict_code}`

**功能说明**：获取指定编码的字典项详情

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_code | Path | Integer | 是 | 字典项编码 |

### 4.3 获取字典下拉选项（**推荐使用**）

**接口路径**：`GET /options/{dict_type}`

**功能说明**：获取指定字典类型的标准下拉选项格式，只返回启用的字典项

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_type | Path | String | 是 | 字典类型编码 |

**响应示例**：

```json
{
  "success": true,
  "message": "获取字典选项成功",
  "data": [
    {
      "value": "warrior",
      "label": "战士",
      "css_class": "#FF0000",
      "is_default": 0
    },
    {
      "value": "mage",
      "label": "法师",
      "css_class": "#0000FF",
      "is_default": 1
    }
  ],
  "timestamp": "2026-04-30T12:00:00Z"
}
```

**前端使用示例**：

```javascript
// 获取职业类型下拉选项
const response = await axios.get('/api/v1/dictionary/options/profession');
const options = response.data.data;

// 绑定到Select组件
return (
  <Select
    placeholder="请选择职业"
    options={options}
    labelKey="label"
    valueKey="value"
    defaultValue={options.find(o => o.is_default === 1)?.value}
  />
);

// 使用css_class自定义样式
options.forEach(option => {
  if (option.css_class) {
    // 可以设置颜色或样式类
    console.log(`${option.label}: ${option.css_class}`);
  }
});
```

### 4.4 创建字典项

**接口路径**：`POST /data`

**功能说明**：创建新的字典项（需要超级管理员权限）

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_type | Body | String | 是 | 字典类型编码 |
| dict_label | Body | String | 是 | 字典标签（显示文本） |
| dict_value | Body | String | 是 | 字典值（存储值，同一类型下必须唯一） |
| dict_sort | Body | Integer | 否 | 排序，默认0 |
| data_type | Body | String | 否 | 数据类型 |
| css_class | Body | String | 否 | CSS样式类/颜色值 |
| list_class | Body | String | 否 | 列表样式类 |
| is_default | Body | Integer | 否 | 是否默认值：0-否，1-是，默认0 |
| status | Body | Integer | 否 | 状态：0-启用，1-禁用，默认0 |
| remark | Body | String | 否 | 备注说明 |

**请求示例**：

```json
{
  "dict_type": "profession",
  "dict_label": "牧师",
  "dict_value": "priest",
  "dict_sort": 3,
  "css_class": "#FFFFFF",
  "is_default": 0,
  "status": 0,
  "remark": "治疗职业"
}
```

### 4.5 更新字典项

**接口路径**：`PUT /data/{dict_code}`

**功能说明**：更新字典项信息（需要超级管理员权限）

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_code | Path | Integer | 是 | 字典项编码 |
| dict_label | Body | String | 否 | 字典标签 |
| dict_value | Body | String | 否 | 字典值 |
| dict_sort | Body | Integer | 否 | 排序 |
| data_type | Body | String | 否 | 数据类型 |
| css_class | Body | String | 否 | CSS样式类/颜色值 |
| list_class | Body | String | 否 | 列表样式类 |
| is_default | Body | Integer | 否 | 是否默认值 |
| status | Body | Integer | 否 | 状态 |
| remark | Body | String | 否 | 备注说明 |

### 4.6 删除字典项

**接口路径**：`DELETE /data/{dict_code}`

**功能说明**：删除字典项（需要超级管理员权限）

**请求参数**：

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| dict_code | Path | Integer | 是 | 字典项编码 |

---

## 五、系统管理接口

### 5.1 刷新字典缓存

**接口路径**：`POST /reload-cache`

**功能说明**：手动刷新所有字典数据到内存缓存

**请求参数**：无

**使用场景**：当系统数据通过其他方式变更（如直接修改数据库），或者发现缓存与数据库不一致时使用

### 5.2 初始化字典数据

**接口路径**：`POST /init`

**功能说明**：初始化系统预置的字典数据（需要超级管理员权限）

**请求参数**：无

**使用场景**：系统首次部署、字典数据损坏时使用，会将预置数据插入数据库

---

## 六、前端对接指南

### 6.1 数据结构映射

| 前端概念 | 字典字段 | 说明 |
|----------|----------|------|
| Option Value | `dict_value` | 下拉选项值，实际存储值 |
| Option Label | `dict_label` | 下拉选项显示文本 |
| Option Color | `css_class` | 选项颜色/样式 |
| Default Value | `is_default` | 是否默认选中 |
| Option Sort | `dict_sort` | 排序顺序 |
| Option Enabled | `status` | 是否启用（0启用，1禁用） |

### 6.2 推荐接口使用流程

#### 场景1：表单中的下拉选择

```javascript
// 1. 使用options接口获取数据
const fetchProfessionOptions = async () => {
  const res = await axios.get('/api/v1/dictionary/options/profession');
  return res.data.data; // 直接使用这个数组
};

// 2. 绑定到组件
const options = await fetchProfessionOptions();

<Select
  options={options}
  // 选项格式是 {value, label, css_class, is_default}
  // 直接可以用，不需要转换
/>
```

#### 场景2：字典数据管理页面

```javascript
// 左侧字典类型列表
const fetchTypes = async () => {
  const res = await axios.get('/api/v1/dictionary/types/all');
  return res.data.data;
};

// 右侧选中类型的字典项列表
const fetchDictData = async (dictType) => {
  const res = await axios.get('/api/v1/dictionary/data', {
    params: { dict_type: dictType }
  });
  return res.data.data;
};
```

#### 场景3：标签值转换展示

```javascript
// 当数据库只存了dict_value，需要显示dict_label时
// 方案1：在组件初始化时获取所有选项，然后做一个lookup map
const [options, setOptions] = useState([]);
const [valueToLabel, setValueToLabel] = useState({});

useEffect(() => {
  const fetchAndBuildMap = async () => {
    const data = await fetchProfessionOptions();
    setOptions(data);
    const map = {};
    data.forEach(opt => map[opt.value] = opt.label);
    setValueToLabel(map);
  };
  fetchAndBuildMap();
}, []);

// 使用
const displayLabel = valueToLabel[databaseValue] || databaseValue;
```

### 6.3 前端工具类封装

```javascript
// dictionary.js - 字典工具类
class DictionaryManager {
  constructor() {
    this.cache = {};
  }

  // 获取字典选项（带缓存）
  async getOptions(dictType, forceRefresh = false) {
    if (!forceRefresh && this.cache[dictType]) {
      return this.cache[dictType];
    }
    
    const res = await axios.get(`/api/v1/dictionary/options/${dictType}`);
    const options = res.data.data;
    this.cache[dictType] = options;
    return options;
  }

  // 值转标签
  async getLabel(dictType, value) {
    const options = await this.getOptions(dictType);
    const option = options.find(o => o.value === value);
    return option ? option.label : value;
  }

  // 标签转值
  async getValue(dictType, label) {
    const options = await this.getOptions(dictType);
    const option = options.find(o => o.label === label);
    return option ? option.value : label;
  }

  // 获取颜色
  async getColor(dictType, value) {
    const options = await this.getOptions(dictType);
    const option = options.find(o => o.value === value);
    return option ? option.css_class : null;
  }

  // 刷新所有缓存
  async refreshCache() {
    await axios.post('/api/v1/dictionary/reload-cache');
    this.cache = {}; // 清除本地缓存
  }
}

export default new DictionaryManager();
```

使用示例：

```javascript
import dictManager from './dictionary';

// 获取职业下拉选项
const options = await dictManager.getOptions('profession');

// 显示标签
const label = await dictManager.getLabel('profession', 'warrior');
console.log(label); // "战士"
```

### 6.4 字典类型常量定义

为了避免硬编码字符串，建议将常用的dict_type定义为常量：

```javascript
// dict-types.js
export const DICT_TYPES = {
  PROFESSION: 'profession',         // 职业类型
  ELITE_SPEC: 'elite_spec',         // 精英特长
  BUFF: 'buff',                     // Buff类型
  ROLE: 'role',                     // 角色定位
  LOG_STATUS: 'log_status',         // 日志状态
  LOG_SOURCE: 'log_source'          // 日志来源
};
```

使用：

```javascript
import { DICT_TYPES } from './dict-types';

const options = await dictManager.getOptions(DICT_TYPES.PROFESSION);
```

---

## 七、预置字典类型列表

| 字典类型（dict_type） | 名称（dict_name） | 说明 |
|------------------------|-------------------|------|
| profession | 职业类型 | GW2职业分类 |
| elite_spec | 精英特长 | 职业精英专精 |
| buff | Buff类型 | 增益效果分类 |
| role | 角色定位 | 坦克/治疗/输出 |
| log_status | 日志状态 | 日志解析状态 |

---

## 八、使用注意事项

### 8.1 安全注意事项

- 所有增删改接口需要超级管理员权限
- 不要修改预置字典类型的dict_type字段
- 删除字典类型会级联删除所有关联的字典数据，请谨慎操作

### 8.2 性能注意事项

- **推荐使用 `/options/{dict_type}` 接口**：这是专门为前端设计的，返回格式直接可用
- 字典数据有内存缓存，高并发读取不会影响性能
- 只有增删改操作时会清除对应类型的缓存

### 8.3 数据一致性注意事项

- `dict_value`同一类型下必须唯一
- 修改`dict_value`时，需要同步修改业务数据中存储的旧值
- 禁用的字典项不会显示在下拉选项中，但不会影响已存储的历史数据

### 8.4 常见问题

**Q: 为什么接口都需要登录？**

A: 为了安全，字典管理功能只允许内部用户使用。如果需要公开接口，请联系后端开发人员。

**Q: 如何刷新缓存？**

A: 一般不需要手动刷新，增删改操作会自动刷新对应类型的缓存。如果确实需要，可以调用`/reload-cache`接口。

**Q: css_class字段怎么用？**

A: 可以存颜色值（如 "#FF0000"）或CSS类名（如"badge-danger"），前端根据需要使用。

**Q: 如何设置默认值？**

A: 创建或编辑字典项时，设置is_default=1即可。同一类型下建议只有一个默认值。

---

## 九、更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-30 | v1.0 | 初始版本 |
