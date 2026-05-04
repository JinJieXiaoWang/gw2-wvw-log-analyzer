# GW2 WVW日志解析管理系统

基于Vue3 + PrimeVue + Tailwind CSS 开发的激战2 WVW战场日志解析管理工具。

## 功能特性

- 日志上传与解析：支持.zevtc文件上传、批量解析
- 出勤统计：团队/个人排名、数据导出
- 技能循环分析：理想vs实战对比、失误统计
- Build代码解析：导入、解析、对比Build配置
- 数据看板：多维度可视化分析

## 技术栈

- Vue 3.4 + Composition API
- PrimeVue 3.51 组件库
- Tailwind CSS 3.4 样式
- Vue Router 4.3 路由管理
- TypeScript 5.4 类型定义
- Vite 5.2 构建工具

## 开发环境

### Node.js 版本
- 要求：>= 18.0.0

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 类型检查
```bash
npm run type-check
```

### 代码检查
```bash
npm run lint
```

### 构建生产版本
```bash
npm run build
```

## 项目结构

```
src/
├── api/            # API接口层（按模块组织的请求封装）
├── assets/         # 静态资源（图片、字体）
├── components/     # Vue组件
│   ├── common/     # 通用基础组件（PageHeader、MetricCard、EmptyState等）
│   ├── dict/       # 字典相关组件（DictTag、DictSelect、DictValue）
│   └── settings/   # 设置页面子组件
├── composables/    # Vue组合式函数（useDictMapping、usePermission等）
├── config/         # 配置文件
├── constants/      # 常量定义
├── directives/     # 自定义Vue指令
├── layout/         # 布局组件（MainLayout、侧边栏、顶部导航）
│   └── components/
├── locales/        # 国际化语言包
├── models/         # 数据模型定义
├── router/         # 路由配置
├── services/       # 服务层（API调用、错误处理、业务逻辑）
├── store/          # Pinia状态管理
├── styles/         # 全局样式、主题、工具类
├── types/          # TypeScript类型定义
├── utils/          # 工具函数（helpers、performance、permissionUtils等）
├── views/          # 页面视图组件
├── App.vue         # 根组件
└── main.ts         # 入口文件
```

## 设计规范

### 色彩系统
- 主色：#165DFF（电竞蓝）
- 辅助色：#FF7D00（橙红）
- 背景色：#141414（深黑）
- 卡片背景：#2A2A2A（深灰）
- 边框色：#3D3D3D（中灰）
- 文字色：#E5E5E5（主文字）
- 次要文字：#909399

### 字体规范
- 主字体：Inter
- 标题：18-24px
- 正文：14px
- 辅助：12px

## 性能优化

- 路由懒加载
- 组件按需引入
- 代码分割
- 首次加载优化目标：< 3秒

## 许可证

MIT License
