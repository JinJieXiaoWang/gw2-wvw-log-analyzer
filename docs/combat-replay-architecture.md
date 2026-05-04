# Combat Replay 战斗回放系统架构文档

> **版本**: v2.0  
> **创建日期**: 2026-05-02  
> **更新日期**: 2026-05-05  
> **状态**: 后端仅做数据存储与透传，渲染逻辑完全在前端

> **更新说明**: 与实际代码对齐。后端无专门的 Combat Replay 处理逻辑，`ei_report.cr_data_path` 仅存储原始 gzip 压缩数据文件路径，前端 `components/eiDetail/CombatReplay.vue` 负责全部渲染。

---

## 1. 现有问题分析

### 1.1 原有实现缺陷

| 问题 | 影响 | 严重程度 |
|------|------|----------|
| 无背景地图 | 无法定位战斗发生在地图的哪个区域 | 高 |
| 无职业图标 | 圆点无法区分职业，可读性差 | 高 |
| `setInterval` 动画 | 帧率不稳定，高负载时卡顿 | 中 |
| `left/top` 定位 | 触发回流重绘，性能差 | 中 |
| 硬编码颜色 | 与项目统一的职业颜色不一致 | 低 |
| 模拟轨迹随机 | 不同职业没有差异化移动模式 | 低 |

### 1.2 数据限制

GW2 Elite Insights 日志**不包含玩家实时坐标数据**。Combat Replay 的位置数据通常需要：
- arcdps 的 Combat Replay 插件额外导出
- 或者使用服务器端的位置追踪系统

当前方案中，后端仅负责存储和透传 EI 原始 Combat Replay 数据，所有渲染逻辑在前端完成。

---

## 2. 技术架构调整

### 2.1 整体架构

```
CombatLogDetailView
    │
    ▼
CombatReplay.vue (主容器组件)
    ├── ReplayCanvas (画布区域)
    │   ├── MapBackground (背景地图层)
    │   ├── TeamZones (队伍区域高亮)
    │   ├── PlayerMarkers (玩家标记)
    │   │   ├── ProfessionIcon (职业图标)
    │   │   ├── Nameplate (名称标签)
    │   │   └── StateIndicator (状态指示器)
    │   ├── TargetMarkers (目标标记)
    │   └── SkillEffects (技能效果)
    │
    ├── ReplayControls (控制面板)
    │   ├── PlaybackControls (播放/暂停/步进)
    │   ├── Timeline (时间轴)
    │   ├── SpeedSelector (速度选择)
    │   └── DisplayOptions (显示选项)
    │
    └── EventLog (事件日志)

useCombatReplay.ts (核心逻辑)
    ├── AnimationLoop (requestAnimationFrame)
    ├── TrajectoryGenerator (轨迹生成)
    ├── IconCache (图标缓存)
    └── CoordinateSystem (坐标映射)
```

### 2.2 坐标系统设计

```
游戏世界坐标 (游戏内单位)
    │
    │  归一化映射
    ▼
归一化坐标 [0.0, 1.0] × [0.0, 1.0]
    │
    │  CSS transform: translate3d(calc(x% - 50%), calc(y% - 50%), 0)
    ▼
屏幕像素坐标
```

**坐标转换公式：**
```typescript
// 游戏坐标 → 归一化坐标
const normalizedX = (gameX - mapMinX) / (mapMaxX - mapMinX)
const normalizedY = (gameY - mapMinY) / (mapMaxY - mapMinY)

// 归一化坐标 → CSS transform
const style = {
  transform: `translate3d(calc(${normalizedX * 100}% - 50%), calc(${normalizedY * 100}% - 50%), 0)`
}
```

### 2.3 渲染性能优化

| 优化项 | 实现方式 | 效果 |
|--------|----------|------|
| GPU 加速 | `transform: translate3d()` + `will-change: transform` | 避免回流重绘 |
| 动画循环 | `requestAnimationFrame` 替代 `setInterval` | 帧率同步显示器 |
| 图标缓存 | `Map<string, HTMLImageElement>` 全局缓存 | 避免重复加载 |
| 批量预加载 | `Promise.allSettled()` 并行加载 | 减少等待时间 |
| 过渡动画 | `TransitionGroup` + CSS transition | 平滑进入/离开 |

---

## 3. 轨迹生成算法

### 3.1 初始位置分配

基于职业类型分配初始距离中心点的半径：

```
近战职业 (Warrior/Guardian/Revenant)
    └── 半径: 0.15-0.27 (靠近中心)

辅助职业 (Druid/Tempest/Firebrand)
    └── 半径: 0.22-0.37 (中排)

远程职业 (Elementalist/Engineer/Ranger/Mesmer/Necromancer)
    └── 半径: 0.30-0.48 (外围)
```

基于 `group` 分配角度偏移：

```
Group 1: 角度 +0°
Group 2: 角度 +60°
Group 3: 角度 +120°
...
```

### 3.2 运动轨迹生成

使用多层正弦波叠加生成自然运动：

```typescript
x = baseX + sin(t * f1 + p1) * a1 + cos(t * f2 + p2) * a2 + sin(t * f3 + p3) * a3
y = baseY + cos(t * f1 + p1 + 1) * a1 + sin(t * f2 + p2 + 1) * a2 + cos(t * f3 + p3 + 1) * a3
```

其中频率和振幅基于 `instanceID` 的伪随机数确定，保证：
- 同一玩家每次回放轨迹一致
- 不同玩家轨迹差异化
- 运动范围限制在画布内 `[0.02, 0.98]`

---

## 4. 资源准备清单

### 4.1 已有资源 ✅

| 资源 | 位置 | 状态 |
|------|------|------|
| 职业图标 (42个) | `src/assets/images/prof/*.png` | ✅ 已有 |
| 职业颜色映射 | `src/utils/profession/professionUtils.ts` | ✅ 已有 |
| 图标 URL 生成 | `getProfessionIconUrl()` | ✅ 已有 |

### 4.2 需要补充的资源

| 资源 | 用途 | 优先级 | 获取方式 |
|------|------|--------|----------|
| 永恒战场地图图片 | 背景地图 | 高 | GW2 Wiki / 官方 API |
| 红蓝边境地图图片 | 其他 WvW 地图 | 中 | GW2 Wiki / 官方 API |
| 玩家位置数据 | 真实坐标轨迹 | 高 | arcdps Combat Replay 插件 |

**地图图片规格建议：**
- 格式: WebP / JPG
- 尺寸: 1920×1080 或更高
- 风格: 俯视角，与游戏内地图一致
- 透明度: 不需要透明通道

---

## 5. 分阶段开发计划

### Phase 1: 基础重构 ✅ 已完成

- [x] 提取 `useCombatReplay` composable
- [x] `requestAnimationFrame` 动画循环
- [x] `transform: translate3d` 定位优化
- [x] 图标预加载缓存机制

### Phase 2: 视觉增强 ✅ 已完成

- [x] CSS 生成战场风格背景（网格 + 地形分区）
- [x] 职业图标显示（使用现有资源）
- [x] 统一职业颜色（使用 `professionUtils.ts`）
- [x] 玩家名称标签 + 状态指示器
- [x] 选中高亮效果（旋转虚线光环）

### Phase 3: 坐标与轨迹 ✅ 已完成

- [x] 归一化坐标系统 `[0, 1]`
- [x] 基于职业/团队的初始位置分配
- [x] 多层正弦波轨迹生成
- [x] 轨迹插值（线性插值）
- [x] 响应式布局适配

### Phase 4: 真实地图接入 🔄 待进行

- [ ] 接入 GW2 地图瓦片服务
- [ ] 游戏世界坐标 → 地图像素坐标转换
- [ ] 地图缩放/平移支持
- [ ] 地图标记叠加（营地、塔楼、要塞）

**地图瓦片接入方案：**

```typescript
// 方案 A: GW2 官方瓦片
const tileUrl = `https://tiles.guildwars2.com/{continent}/{floor}/{z}/{x}/{y}.jpg`

// 方案 B: 静态地图图片
const mapUrl = `https://wiki.guildwars2.com/images/.../Eternal_Battlegrounds_map.jpg`

// 方案 C: 本地地图图片（推荐）
const mapUrl = new URL('@/assets/images/maps/eternal_battlegrounds.jpg', import.meta.url).href
```

### Phase 5: 真实位置数据 🔄 待进行

- [ ] 解析 arcdps Combat Replay 数据格式
- [ ] 位置数据与 EI 日志关联
- [ ] 实时位置插值（Catmull-Rom 样条）
- [ ] 朝向计算与图标旋转

**数据格式示例：**

```typescript
interface CombatReplayData {
  players: {
    instanceID: number
    positions: {
      time: number      // 时间戳 (ms)
      x: number         // 游戏世界 X 坐标
      y: number         // 游戏世界 Y 坐标
      facing: number    // 朝向角度 (弧度)
    }[]
  }[]
}
```

### Phase 6: 高级功能 🔄 待进行

- [ ] 技能范围可视化（圆形/锥形/矩形区域）
- [ ] 位移技能轨迹线（虚线动画）
- [ ] 死亡/复活事件标记
- [ ] 指挥官标签显示
- [ ] 时间轴事件标记点

---

## 6. 使用方式

### 6.1 基础使用（当前实现）

```vue
<CombatReplay
  :players="players"
  :targets="targets"
  :duration="durationMs"
  :selected-player-id="selectedId"
  @select-player="handleSelect"
/>
```

### 6.2 自定义地图背景

```vue
<CombatReplay
  :players="players"
  :targets="targets"
  :duration="durationMs"
  map-image-url="/maps/eternal_battlegrounds.jpg"
/>
```

### 6.3 接入真实坐标数据（未来）

```typescript
// 在 useCombatReplay 中替换轨迹生成逻辑
const replayPlayers = computed(() => {
  return playersRef.value.map(p => {
    // 使用真实位置数据替代模拟轨迹
    const position = getRealPosition(p.instanceID, currentTime.value)
    return {
      ...p,
      position,
      // ...
    }
  })
})
```

---

## 7. 性能基准

| 指标 | 目标值 | 测试环境 |
|------|--------|----------|
| 动画帧率 | ≥ 60 FPS | 50 玩家同时移动 |
| 图标加载时间 | < 2s | 42 个职业图标并行加载 |
| 首屏渲染时间 | < 500ms | 本地构建 |
| 内存占用 | < 50MB | 含图标缓存 |

---

## 8. 已知限制与解决方案

| 限制 | 原因 | 解决方案 |
|------|------|----------|
| 轨迹为模拟生成 | EI 日志不含位置数据 | Phase 5 接入 arcdps Combat Replay 数据 |
| 地图为 CSS 生成 | 无地图图片资源 | Phase 4 接入真实地图瓦片/图片 |
| 无技能范围显示 | 缺少技能坐标数据 | Phase 6 接入技能事件数据 |
| 图标无朝向 | 无 facing 数据 | Phase 5 接入朝向数据后旋转图标 |
