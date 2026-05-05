<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="bg-gradient-to-r from-primary/10 via-transparent to-ai/10 rounded-xl p-6 border border-primary/20">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-3">
            <router-link
              to="/logs"
              class="p-2 rounded-lg bg-neutral-card/50 hover:bg-primary/10 transition-all duration-200 text-neutral-text-secondary hover:text-primary group"
            >
              <i class="pi pi-arrow-left group-hover:translate-x-[-2px] transition-transform" />
            </router-link>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-neutral-text tracking-tight">
                战斗分析
              </h1>
              <p class="text-neutral-text-secondary text-sm mt-1">
                {{ logDetail.filename || '日志详情' }} · {{ fightSummary.map_name || '未知地图' }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex flex-wrap gap-3">
          <Button
            label="重新解析"
            icon="pi pi-refresh"
            :loading="parsing"
            class="transition-all duration-200 hover:shadow-lg hover:shadow-secondary/20"
            @click="reparseLog"
          />
        </div>
      </div>
    </div>

    <!-- 加载/错误 -->
    <div
      v-if="loading"
      class="card flex items-center justify-center py-16 bg-neutral-card/50 border-neutral-border/50"
    >
      <div class="flex flex-col items-center gap-4">
        <div class="relative">
          <ProgressSpinner style="width: 50px; height: 50px" />
          <div class="absolute inset-0 animate-ping opacity-20">
            <ProgressSpinner style="width: 50px; height: 50px" />
          </div>
        </div>
        <span class="text-neutral-text-secondary font-medium">加载战斗数据中...</span>
      </div>
    </div>
    <div
      v-else-if="error"
      class="card bg-error/10 border-error/30 text-error p-6 rounded-xl"
    >
      <div class="flex items-center gap-4">
        <div class="p-3 rounded-lg bg-error/20">
          <i class="pi pi-exclamation-triangle text-2xl" />
        </div>
        <div>
          <p class="font-semibold text-lg">
            加载失败
          </p>
          <p class="text-sm text-error/80">
            {{ error }}
          </p>
        </div>
      </div>
    </div>

    <template v-else>
      <!-- 快速信息栏 -->
      <div class="card p-4 bg-gradient-to-r from-neutral-card to-neutral-bg-secondary border-neutral-border/50 rounded-xl">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-wrap items-center gap-6">
            <div class="flex items-center gap-2 group cursor-pointer hover:text-primary transition-colors">
              <div class="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                <i class="pi pi-clock text-primary" />
              </div>
              <div>
                <p class="text-xs text-neutral-text-secondary">
                  战斗时长
                </p>
                <p class="text-sm font-semibold text-neutral-text">
                  {{ fmtDuration(fightSummary.duration_sec || 0) }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2 group cursor-pointer hover:text-primary transition-colors">
              <div class="p-2 rounded-lg bg-success/10 group-hover:bg-success/20 transition-colors">
                <i class="pi pi-users text-success" />
              </div>
              <div>
                <p class="text-xs text-neutral-text-secondary">
                  参战人数
                </p>
                <p class="text-sm font-semibold text-neutral-text">
                  {{ summary?.total_players || 0 }} 人
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2 group cursor-pointer hover:text-primary transition-colors">
              <div class="p-2 rounded-lg bg-info/10 group-hover:bg-info/20 transition-colors">
                <i class="pi pi-map text-info" />
              </div>
              <div>
                <p class="text-xs text-neutral-text-secondary">
                  地图
                </p>
                <p class="text-sm font-semibold text-neutral-text">
                  {{ fightSummary.map_name || '-' }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2 group cursor-pointer hover:text-primary transition-colors">
              <div class="p-2 rounded-lg bg-secondary/10 group-hover:bg-secondary/20 transition-colors">
                <i class="pi pi-calendar text-secondary" />
              </div>
              <div>
                <p class="text-xs text-neutral-text-secondary">
                  上传时间
                </p>
                <p class="text-sm font-semibold text-neutral-text">
                  {{ fmtDate(logDetail.upload_time) }}
                </p>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <a
              v-if="summary?.dps_report_permalink"
              :href="summary.dps_report_permalink"
              target="_blank"
              class="no-underline"
            >
              <Tag
                value="EI报告"
                icon="pi pi-external-link"
                severity="info"
                class="text-xs cursor-pointer hover:bg-info/30 transition-all"
              />
            </a>
            <Tag
              :value="`击杀 ${fightSummary.kill_count || 0}`"
              severity="success"
              class="text-xs px-2 py-1"
            />
            <Tag
              :value="`死亡 ${fightSummary.death_count || 0}`"
              severity="danger"
              class="text-xs px-2 py-1"
            />
            <Tag
              v-if="agg.player_count"
              :value="`平均DPS ${fmtCompact(agg.avg_dps)}`"
              severity="info"
              class="text-xs px-2 py-1"
            />
          </div>
        </div>
      </div>

      <!-- 标签页 -->
      <div class="card p-0 overflow-hidden">
        <TabMenu
          v-model:active-index="activeTab"
          :model="tabItems"
        />
        <div class="p-5">
          <!-- ========== 1. 战斗概览 ========== -->
          <div
            v-if="activeTab === 0"
            class="space-y-5"
          >
            <!-- KPI 卡片 -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              <div
                v-for="(k, idx) in kpiList"
                :key="k.label" 
                class="card p-4 bg-gradient-to-br rounded-xl border border-neutral-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 group"
                :class="k.bg"
                :style="{ animationDelay: `${idx * 100}ms` }"
              >
                <div class="flex items-center justify-between mb-3">
                  <span class="text-xs font-medium text-neutral-text-secondary/80 uppercase tracking-wider">{{ k.label }}</span>
                  <div class="p-2 rounded-lg bg-white/5 group-hover:bg-white/10 transition-colors">
                    <i
                      :class="k.icon + ' ' + k.color"
                      class="text-lg"
                    />
                  </div>
                </div>
                <div class="flex items-end">
                  <p class="text-2xl font-bold text-neutral-text">
                    {{ k.value }}
                  </p>
                  <span class="ml-2 text-xs text-neutral-text-secondary mb-1">{{ k.unit }}</span>
                </div>
                <div class="mt-3 h-1 bg-white/10 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-700"
                    :class="k.barColor"
                    :style="{ width: k.percent + '%' }"
                  />
                </div>
              </div>
            </div>

            <!-- 战斗属性统计模块 -->
            <div class="card p-5 rounded-xl border-neutral-border/50">
              <h3 class="text-sm font-semibold text-neutral-text mb-5 flex items-center gap-2">
                <div class="p-1.5 rounded-lg bg-primary/10">
                  <i class="pi pi-chart-bar text-primary" />
                </div>
                战斗属性统计
              </h3>
              <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                <!-- 伤害构成 -->
                <div
                  class="card p-3 rounded-xl border-primary/20 bg-gradient-to-br from-primary/5 to-transparent hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 cursor-pointer"
                  @click="showDamageDetailDialog = true"
                >
                  <div class="flex flex-col items-center">
                    <div class="relative w-12 h-12 mb-2">
                      <svg
                        viewBox="0 0 100 100"
                        class="w-full h-full -rotate-90"
                      >
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="var(--color-border)"
                          stroke-width="8"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="#165DFF"
                          stroke-width="8"
                          :stroke-dasharray="donut.pd"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="#22c55e"
                          stroke-width="8"
                          :stroke-dasharray="donut.cd"
                          :stroke-dashoffset="donut.co"
                        />
                      </svg>
                      <div class="absolute inset-0 flex items-center justify-center">
                        <i class="pi pi-chart-pie text-primary text-sm" />
                      </div>
                    </div>
                    <p class="text-lg font-bold text-neutral-text">
                      {{ fmtCompact(donut.total) }}
                    </p>
                    <p class="text-xs text-neutral-text-secondary">
                      伤害构成
                    </p>
                  </div>
                </div>

                <!-- 保护覆盖率 -->
                <div
                  class="card p-3 rounded-xl border-info/20 bg-gradient-to-br from-info/5 to-transparent hover:border-info/40 hover:shadow-lg hover:shadow-info/10 transition-all duration-300 cursor-pointer"
                  @click="openStatDetailDialog('protection', '保护覆盖率')"
                >
                  <div class="flex flex-col items-center">
                    <div class="relative w-12 h-12 mb-2">
                      <svg
                        viewBox="0 0 100 100"
                        class="w-full h-full -rotate-90"
                      >
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="var(--color-border)"
                          stroke-width="8"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="#3b82f6"
                          stroke-width="8"
                          :stroke-dasharray="264"
                          :stroke-dashoffset="264 - (264 * statAverages.protection / 100)"
                          stroke-linecap="round"
                        />
                      </svg>
                      <div class="absolute inset-0 flex items-center justify-center">
                        <i class="pi pi-shield text-info text-sm" />
                      </div>
                    </div>
                    <p class="text-lg font-bold text-neutral-text">
                      {{ statAverages.protection.toFixed(0) }}%
                    </p>
                    <p class="text-xs text-neutral-text-secondary">
                      保护
                    </p>
                  </div>
                </div>

                <!-- 稳固覆盖率 -->
                <div
                  class="card p-3 rounded-xl border-warning/20 bg-gradient-to-br from-warning/5 to-transparent hover:border-warning/40 hover:shadow-lg hover:shadow-warning/10 transition-all duration-300 cursor-pointer"
                  @click="openStatDetailDialog('stability', '稳固覆盖率')"
                >
                  <div class="flex flex-col items-center">
                    <div class="relative w-12 h-12 mb-2">
                      <svg
                        viewBox="0 0 100 100"
                        class="w-full h-full -rotate-90"
                      >
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="var(--color-border)"
                          stroke-width="8"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="#f59e0b"
                          stroke-width="8"
                          :stroke-dasharray="264"
                          :stroke-dashoffset="264 - (264 * statAverages.stability / 100)"
                          stroke-linecap="round"
                        />
                      </svg>
                      <div class="absolute inset-0 flex items-center justify-center">
                        <i class="pi pi-lock text-warning text-sm" />
                      </div>
                    </div>
                    <p class="text-lg font-bold text-neutral-text">
                      {{ statAverages.stability.toFixed(0) }}%
                    </p>
                    <p class="text-xs text-neutral-text-secondary">
                      稳固
                    </p>
                  </div>
                </div>

                <!-- 清症总数 -->
                <div
                  class="card p-3 rounded-xl border-success/20 bg-gradient-to-br from-success/5 to-transparent hover:border-success/40 hover:shadow-lg hover:shadow-success/10 transition-all duration-300 cursor-pointer"
                  @click="openStatDetailDialog('condition_cleanses', '清症统计')"
                >
                  <div class="flex flex-col items-center">
                    <div class="p-2 rounded-lg bg-success/10 mb-2">
                      <i class="pi pi-heart text-success text-lg" />
                    </div>
                    <p class="text-lg font-bold text-neutral-text">
                      {{ fmtCompact(agg.total_condition_cleanses) }}
                    </p>
                    <p class="text-xs text-neutral-text-secondary">
                      清症
                    </p>
                  </div>
                </div>

                <!-- 削增益总数 -->
                <div
                  class="card p-3 rounded-xl border-error/20 bg-gradient-to-br from-error/5 to-transparent hover:border-error/40 hover:shadow-lg hover:shadow-error/10 transition-all duration-300 cursor-pointer"
                  @click="openStatDetailDialog('boon_strips', '削增益统计')"
                >
                  <div class="flex flex-col items-center">
                    <div class="p-2 rounded-lg bg-error/10 mb-2">
                      <i class="pi pi-minus-circle text-error text-lg" />
                    </div>
                    <p class="text-lg font-bold text-neutral-text">
                      {{ fmtCompact(agg.total_boon_strips) }}
                    </p>
                    <p class="text-xs text-neutral-text-secondary">
                      削增益
                    </p>
                  </div>
                </div>

                <!-- 承伤总量 -->
                <div
                  class="card p-3 rounded-xl border-secondary/20 bg-gradient-to-br from-secondary/5 to-transparent hover:border-secondary/40 hover:shadow-lg hover:shadow-secondary/10 transition-all duration-300 cursor-pointer"
                  @click="openStatDetailDialog('damage_taken', '承伤统计')"
                >
                  <div class="flex flex-col items-center">
                    <div class="p-2 rounded-lg bg-secondary/10 mb-2">
                      <i class="pi pi-exclamation-triangle text-secondary text-lg" />
                    </div>
                    <p class="text-lg font-bold text-neutral-text">
                      {{ fmtCompact(agg.total_damage_taken) }}
                    </p>
                    <p class="text-xs text-neutral-text-secondary">
                      承伤
                    </p>
                  </div>
                </div>

                <!-- 命中率 -->
                <div
                  class="card p-3 rounded-xl border-primary/20 bg-gradient-to-br from-primary/5 to-transparent hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 cursor-pointer"
                  @click="openStatDetailDialog('hitRate', '命中率统计')"
                >
                  <div class="flex flex-col items-center">
                    <div class="relative w-12 h-12 mb-2">
                      <svg
                        viewBox="0 0 100 100"
                        class="w-full h-full -rotate-90"
                      >
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="var(--color-border)"
                          stroke-width="8"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          fill="none"
                          stroke="#165DFF"
                          stroke-width="8"
                          :stroke-dasharray="264"
                          :stroke-dashoffset="264 - (264 * statAverages.hitRate / 100)"
                          stroke-linecap="round"
                        />
                      </svg>
                      <div class="absolute inset-0 flex items-center justify-center">
                        <i class="pi pi-bolt text-primary text-sm" />
                      </div>
                    </div>
                    <p class="text-lg font-bold text-neutral-text">
                      {{ statAverages.hitRate.toFixed(1) }}%
                    </p>
                    <p class="text-xs text-neutral-text-secondary">
                      命中率
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 职业分布（紧凑版） -->
            <div class="card p-4 rounded-xl border-neutral-border/50">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
                  <div class="p-1.5 rounded-lg bg-info/10">
                    <i class="pi pi-users text-info" />
                  </div>
                  职业分布
                </h3>
                <span class="text-xs text-neutral-text-secondary">{{ summary?.total_players || 0 }} 人参战</span>
              </div>
              <div class="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-2">
                <div
                  v-for="(count, prof) in summary?.profession_distribution"
                  :key="prof" 
                  class="flex flex-col items-center p-2 rounded-lg bg-neutral-bg/50 hover:bg-neutral-bg-secondary transition-all"
                >
                  <span
                    class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-1" 
                    :style="{ backgroundColor: getProfessionColor(prof) + '20', color: getProfessionColor(prof) }"
                  >
                    {{ count }}
                  </span>
                  <span
                    class="text-[10px] text-center text-neutral-text-secondary"
                    :style="{ backgroundColor: getProfessionColor(prof) + '20', color: getProfessionColor(prof) }"
                  >{{ getProfessionName(prof) }}</span>
                </div>
              </div>
            </div>

            <!-- 详细统计 -->
            <div class="card p-5 rounded-xl border-neutral-border/50">
              <div class="flex items-center justify-between mb-5">
                <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
                  <div class="p-1.5 rounded-lg bg-secondary/10">
                    <i class="pi pi-sliders-h text-secondary" />
                  </div>
                  详细战斗统计
                </h3>
                <Button
                  :label="showDetailStats ? '收起' : '展开'"
                  :icon="showDetailStats ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" 
                  severity="secondary"
                  size="small"
                  class="transition-all duration-200"
                  @click="showDetailStats = !showDetailStats"
                />
              </div>
              
              <div
                v-show="showDetailStats"
                class="space-y-5"
              >
                <!-- 伤害细分 -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <div class="card p-4 rounded-xl bg-gradient-to-br from-primary/10 to-transparent border-primary/20">
                    <div class="flex items-center justify-between mb-3">
                      <span class="text-xs font-medium text-neutral-text-secondary uppercase tracking-wider">直伤总量</span>
                      <div class="p-1.5 rounded-lg bg-primary/20">
                        <i class="pi pi-bolt text-primary text-sm" />
                      </div>
                    </div>
                    <div class="text-center">
                      <p class="text-3xl font-bold text-primary">
                        {{ fmtCompact(agg.total_power_damage) }}
                      </p>
                      <div class="mt-2 flex items-center justify-center gap-2">
                        <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden">
                          <div
                            class="h-full bg-primary rounded-full transition-all duration-700"
                            :style="{ width: powerPct + '%' }"
                          />
                        </div>
                        <span class="text-sm font-semibold text-primary">{{ powerPct }}%</span>
                      </div>
                    </div>
                  </div>
                  <div class="card p-4 rounded-xl bg-gradient-to-br from-success/10 to-transparent border-success/20">
                    <div class="flex items-center justify-between mb-3">
                      <span class="text-xs font-medium text-neutral-text-secondary uppercase tracking-wider">症状总量</span>
                      <div class="p-1.5 rounded-lg bg-success/20">
                        <i class="pi pi-flame text-success text-sm" />
                      </div>
                    </div>
                    <div class="text-center">
                      <p class="text-3xl font-bold text-success">
                        {{ fmtCompact(agg.total_condi_damage) }}
                      </p>
                      <div class="mt-2 flex items-center justify-center gap-2">
                        <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden">
                          <div
                            class="h-full bg-success rounded-full transition-all duration-700"
                            :style="{ width: condiPct + '%' }"
                          />
                        </div>
                        <span class="text-sm font-semibold text-success">{{ condiPct }}%</span>
                      </div>
                    </div>
                  </div>
                  <div class="card p-4 rounded-xl bg-gradient-to-br from-secondary/10 to-transparent border-secondary/20">
                    <div class="flex items-center justify-between mb-3">
                      <span class="text-xs font-medium text-neutral-text-secondary uppercase tracking-wider">破甲总量</span>
                      <div class="p-1.5 rounded-lg bg-secondary/20">
                        <i class="pi pi-hammer text-secondary text-sm" />
                      </div>
                    </div>
                    <div class="text-center">
                      <p class="text-3xl font-bold text-secondary">
                        {{ fmtCompact(agg.total_breakbar_damage) }}
                      </p>
                      <div class="mt-2 flex items-center justify-center gap-2">
                        <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden">
                          <div
                            class="h-full bg-secondary rounded-full transition-all duration-700"
                            :style="{ width: breakbarPct + '%' }"
                          />
                        </div>
                        <span class="text-sm font-semibold text-secondary">{{ breakbarPct }}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 详细数据表格 -->
                <DataTable
                  :value="summary?.players || []"
                  striped-rows
                  :paginator="true"
                  :rows="10"
                  class="w-full"
                  scrollable
                >
                  <Column
                    field="character_name"
                    header="玩家"
                    style="min-width: 140px"
                  >
                    <template #body="{ data }">
                      <div class="flex items-center gap-2">
                        <img
                          :src="getProfessionIconUrl(data.profession)"
                          class="w-7 h-7 rounded-full"
                        >
                        <div>
                          <p class="text-sm font-medium">
                            {{ data.character_name || data.account }}
                          </p>
                          <p
                            v-if="data.account && data.character_name"
                            class="text-[10px] text-neutral-text-secondary truncate"
                          >
                            {{ data.account }}
                          </p>
                          <p class="text-[10px] text-neutral-text-secondary">
                            {{ getProfessionName(data.profession) }}
                          </p>
                        </div>
                      </div>
                    </template>
                  </Column>
                  <Column
                    field="breakbar_damage"
                    header="破甲"
                    style="min-width: 90px"
                  >
                    <template #body="{ data }">
                      <span class="text-sm">{{ fmtCompact(data.breakbar_damage) }}</span>
                    </template>
                  </Column>
                  <Column
                    field="flanking_rate"
                    header="侧身率"
                    style="min-width: 80px"
                  >
                    <template #body="{ data }">
                      <span class="text-sm">{{ data.flanking_rate.toFixed(1) }}%</span>
                    </template>
                  </Column>
                  <Column
                    field="glance_rate"
                    header="擦过率"
                    style="min-width: 80px"
                  >
                    <template #body="{ data }">
                      <span class="text-sm">{{ data.glance_rate.toFixed(1) }}%</span>
                    </template>
                  </Column>
                  <Column
                    field="missed"
                    header="未命中"
                    style="min-width: 80px"
                  />
                  <Column
                    field="interrupts"
                    header="打断"
                    style="min-width: 70px"
                  />
                  <Column
                    field="swap_count"
                    header="换武器"
                    style="min-width: 80px"
                  />
                  <Column
                    field="blocked_count"
                    header="格挡"
                    style="min-width: 70px"
                  />
                  <Column
                    field="evaded_count"
                    header="闪避"
                    style="min-width: 70px"
                  />
                  <Column
                    field="dodge_count"
                    header="翻滚"
                    style="min-width: 70px"
                  />
                  <Column
                    field="boon_strips"
                    header="剥增益"
                    style="min-width: 85px"
                  />
                  <Column
                    field="condition_cleanses"
                    header="清症"
                    style="min-width: 70px"
                  />
                  <Column
                    field="resurrects"
                    header="复活"
                    style="min-width: 70px"
                  />
                  <Column
                    field="healing"
                    header="治疗"
                    style="min-width: 90px"
                  >
                    <template #body="{ data }">
                      <span class="text-sm">{{ fmtCompact(data.healing) }}</span>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </div>
          </div>

          <!-- ========== 2. 玩家排行 + 小队编制（统一模块） ========== -->
          <div
            v-if="activeTab === 1"
            class="space-y-5"
          >
            <!-- 顶部功能栏 -->
            <div class="flex items-center gap-3">
              <div class="p-2 rounded-lg bg-yellow-500/10">
                <i class="pi pi-trophy text-yellow-500" />
              </div>
              <h3 class="text-lg font-semibold text-neutral-text">
                玩家排行 & 小队编制
              </h3>
              <Tag
                :value="`${players.length}人`"
                severity="info"
                class="text-xs"
              />
            </div>

            <!-- 统一内容区：左侧排行榜 + 右侧小队视图 -->
            <div class="grid grid-cols-1 xl:grid-cols-5 gap-5">
              <!-- 左侧：玩家排行榜 -->
              <div class="xl:col-span-3 card rounded-xl border-neutral-border/50 overflow-hidden">
                <div class="p-4 border-b border-neutral-border/50">
                  <h4 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
                    <i class="pi pi-list text-primary" />
                    玩家排行榜
                  </h4>
                </div>
                <div class="max-h-[600px] overflow-auto">
                  <DataTable
                    :value="sortedPlayerList"
                    :paginator="true"
                    :rows="12"
                    class="w-full cursor-pointer" 
                    striped-rows
                    @row-click="onRowClick"
                  >
                    <Column
                      field="rank"
                      header="#"
                      style="width: 50px"
                    >
                      <template #body="{ index }">
                        <span
                          class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold"
                          :class="rankClass(index)"
                        >{{ index + 1 }}</span>
                      </template>
                    </Column>
                    <Column
                      field="profession"
                      header="职业"
                      style="min-width: 90px"
                    >
                      <template #body="{ data }">
                        <div class="flex items-center gap-2">
                          <img
                            :src="getProfessionIconUrl(data.profession)"
                            class="w-6 h-6 rounded-full"
                          >
                          <span
                            class="text-xs"
                            :style="{ backgroundColor: getProfessionColor(data.profession) + '20', color: getProfessionColor(data.profession) }"
                          >{{ getProfessionName(data.profession) }}</span>
                        </div>
                      </template>
                    </Column>
                    <Column
                      field="name"
                      header="玩家"
                      style="min-width: 120px"
                    >
                      <template #body="{ data }">
                        <div class="flex items-center gap-2">
                          <span class="text-xs font-medium text-neutral-text truncate max-w-[100px]">{{ data.character_name || data.account }}</span>
                          <Tag
                            v-if="data.has_commander_tag"
                            icon="pi pi-star-fill"
                            severity="warn"
                            value=""
                            class="text-[8px] w-4 h-4 p-0 flex items-center justify-center"
                          />
                        </div>
                      </template>
                    </Column>
                    <Column
                      field="group_id"
                      header="小队"
                      style="width: 60px"
                    >
                      <template #body="{ data }">
                        <span
                          class="text-xs px-1.5 py-0.5 rounded font-medium" 
                          :style="{ backgroundColor: groupColor(data.group_id) + '20', color: groupColor(data.group_id) }"
                        >
                          G{{ data.group_id || '-' }}
                        </span>
                      </template>
                    </Column>
                    <Column
                      field="dps"
                      header="DPS"
                      style="width: 80px"
                    >
                      <template #body="{ data }">
                        <span class="text-xs font-semibold text-primary">{{ fmtCompact(data.dps) }}</span>
                      </template>
                    </Column>
                    <Column
                      field="damage"
                      header="伤害"
                      style="min-width: 90px"
                    >
                      <template #body="{ data }">
                        <span class="text-xs font-bold text-neutral-text">{{ fmtCompact(data.damage) }}</span>
                      </template>
                    </Column>
                    <Column
                      field="killed"
                      header="击杀"
                      style="width: 50px"
                    >
                      <template #body="{ data }">
                        <span class="text-xs font-semibold text-success">{{ data.killed || 0 }}</span>
                      </template>
                    </Column>
                    <Column
                      field="dead_count"
                      header="死亡"
                      style="width: 50px"
                    >
                      <template #body="{ data }">
                        <span
                          :class="data.dead_count > 0 ? 'text-error font-semibold' : 'text-neutral-text-secondary'"
                          class="text-xs"
                        >{{ data.dead_count || 0 }}</span>
                      </template>
                    </Column>
                    <Column
                      field="ai_score"
                      header="评分"
                      style="width: 60px"
                      sortable
                    >
                      <template #body="{ data }">
                        <span
                          class="text-xs font-bold"
                          :class="scoreValueColor(data.ai_score)"
                        >
                          {{ data.ai_score != null ? data.ai_score.toFixed(1) : '-' }}
                        </span>
                      </template>
                    </Column>
                    <Column
                      field="score_grade"
                      header="等级"
                      style="width: 50px"
                    >
                      <template #body="{ data }">
                        <Tag
                          :value="data.score_grade || '-'"
                          :severity="scoreSeverity(data.score_grade)"
                          class="text-[10px] px-1"
                        />
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </div>

              <!-- 右侧：小队编制视图 -->
              <div class="xl:col-span-2 space-y-4">
                <!-- 指挥官区域 -->
                <div class="card p-4 rounded-xl border-yellow-500/20 bg-gradient-to-br from-yellow-500/5 to-transparent">
                  <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
                    <div class="p-1 rounded bg-yellow-500/20">
                      <i class="pi pi-star-fill text-yellow-500 text-xs" />
                    </div>
                    指挥官 ({{ commanders.length }})
                  </h4>
                  <div class="flex flex-wrap gap-2">
                    <div
                      v-for="cmd in commanders"
                      :key="cmd.id"
                      class="flex items-center gap-2 px-3 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/30 hover:border-yellow-500/50 transition-all cursor-pointer"
                      @click="openPlayerDialog(cmd)"
                    >
                      <img
                        :src="getProfessionIconUrl(cmd.profession)"
                        class="w-8 h-8 rounded-full border border-yellow-500/50"
                      >
                      <div class="min-w-0">
                        <p class="text-xs font-semibold text-neutral-text truncate max-w-[80px]">
                          {{ cmd.character_name || cmd.account }}
                        </p>
                        <p class="text-[10px] text-yellow-500/80">
                          {{ getProfessionName(cmd.profession) }}
                        </p>
                      </div>
                    </div>
                    <div
                      v-if="commanders.length === 0"
                      class="flex items-center gap-2 text-neutral-text-secondary text-xs px-3 py-2 rounded-lg bg-neutral-bg-secondary"
                    >
                      <i class="pi pi-info-circle" />
                      <span>无指挥官</span>
                    </div>
                  </div>
                </div>

                <!-- 小队列表 -->
                <div class="space-y-3">
                  <div
                    v-for="g in groups"
                    :key="g.id" 
                    class="card p-3 rounded-xl border transition-all cursor-pointer"
                    :style="{ borderColor: groupColor(g.id) + '40', backgroundColor: groupColor(g.id) + '08' }"
                    @click="selectedTeamId = selectedTeamId === g.id ? null : g.id"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span
                          class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" 
                          :style="{ backgroundColor: groupColor(g.id) }"
                        >{{ g.id || '?' }}</span>
                        <span class="text-sm font-semibold text-neutral-text">小队 {{ g.id || '未分组' }}</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span
                          class="text-xs px-2 py-0.5 rounded-full" 
                          :style="{ backgroundColor: groupColor(g.id) + '20', color: groupColor(g.id) }"
                        >
                          {{ g.players.length }}人
                        </span>
                        <i
                          :class="selectedTeamId === g.id ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" 
                          class="text-neutral-text-secondary text-xs"
                        />
                      </div>
                    </div>
                    
                    <!-- 小队成员预览 -->
                    <div class="flex flex-wrap gap-1 mb-2">
                      <div
                        v-for="p in g.players.slice(0, 5)"
                        :key="p.id"
                        class="relative group"
                      >
                        <img
                          :src="getProfessionIconUrl(p.profession)"
                          class="w-6 h-6 rounded-full border" 
                          :style="{ borderColor: groupColor(g.id) + '60' }"
                          :title="p.character_name || p.account"
                        >
                        <div
                          v-if="p.has_commander_tag"
                          class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-yellow-500 rounded-full flex items-center justify-center"
                        >
                          <i class="pi pi-star-fill text-[6px] text-yellow-900" />
                        </div>
                      </div>
                      <div
                        v-if="g.players.length > 5"
                        class="w-6 h-6 rounded-full bg-neutral-bg flex items-center justify-center text-[10px] text-neutral-text-secondary"
                      >
                        +{{ g.players.length - 5 }}
                      </div>
                    </div>

                    <!-- 展开的小队详情 -->
                    <div
                      v-show="selectedTeamId === g.id"
                      class="pt-2 border-t border-neutral-border/30 space-y-2"
                    >
                      <div class="flex items-center justify-between text-xs">
                        <span class="text-neutral-text-secondary">总伤害</span>
                        <span class="font-semibold text-primary">{{ fmtCompact(getTeamTotalDamage(g)) }}</span>
                      </div>
                      <div class="flex items-center justify-between text-xs">
                        <span class="text-neutral-text-secondary">平均DPS</span>
                        <span class="font-semibold text-neutral-text">{{ fmtCompact(getTeamAvgDps(g)) }}</span>
                      </div>
                      <div class="flex items-center justify-between text-xs">
                        <span class="text-neutral-text-secondary">平均评分</span>
                        <span
                          class="font-semibold"
                          :class="scoreValueColor(getTeamAvgScore(g))"
                        >
                          {{ getTeamAvgScore(g)?.toFixed(1) ?? '-' }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- 未分组玩家 -->
                  <div
                    v-if="ungroupedPlayers.length > 0"
                    class="card p-3 rounded-xl border border-dashed border-neutral-border/50"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-neutral-bg text-neutral-text-secondary">?</span>
                        <span class="text-sm font-semibold text-neutral-text-secondary">未分组 ({{ ungroupedPlayers.length }})</span>
                      </div>
                    </div>
                    <div class="flex flex-wrap gap-1">
                      <div
                        v-for="p in ungroupedPlayers.slice(0, 8)"
                        :key="p.id"
                        class="relative group"
                      >
                        <img
                          :src="getProfessionIconUrl(p.profession)"
                          class="w-6 h-6 rounded-full border border-neutral-border/50 cursor-pointer hover:border-primary/50 transition-colors"
                          @click="openPlayerDialog(p)"
                        >
                        <div
                          v-if="p.has_commander_tag"
                          class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-yellow-500 rounded-full flex items-center justify-center"
                        >
                          <i class="pi pi-star-fill text-[6px] text-yellow-900" />
                        </div>
                      </div>
                      <div
                        v-if="ungroupedPlayers.length > 8"
                        class="w-6 h-6 rounded-full bg-neutral-bg flex items-center justify-center text-[10px] text-neutral-text-secondary"
                      >
                        +{{ ungroupedPlayers.length - 8 }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 敌方目标（简化显示） -->
            <div
              v-if="summary?.enemy_players?.length"
              class="card p-4 rounded-xl border-error/20 bg-error/5"
            >
              <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
                <div class="p-1 rounded bg-error/20">
                  <i class="pi pi-exclamation-triangle text-error text-xs" />
                </div>
                敌方目标 ({{ summary.enemy_players.length }})
              </h4>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="p in summary.enemy_players.slice(0, 10)"
                  :key="p.id" 
                  class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-error/10 border border-error/20"
                >
                  <img
                    :src="getProfessionIconUrl(p.profession)"
                    class="w-6 h-6 rounded-full border border-error/30"
                  >
                  <span class="text-xs text-neutral-text">{{ p.character_name || '未知' }}</span>
                  <span class="text-[10px] text-error font-semibold">{{ fmtCompact(p.damage) }}</span>
                </div>
                <div
                  v-if="(summary.enemy_players.length || 0) > 10"
                  class="flex items-center px-3 py-1.5 text-xs text-neutral-text-secondary"
                >
                  +{{ (summary.enemy_players.length || 0) - 10 }} 更多
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>

  <!-- 伤害构成详情弹框 -->
  <Dialog
    v-model:visible="showDamageDetailDialog"
    header="伤害构成详情"
    :style="{ width: '800px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
  >
    <div class="space-y-6">
      <!-- 环形图 -->
      <div class="flex flex-col sm:flex-row items-center gap-6">
        <div class="relative w-48 h-48">
          <svg
            viewBox="0 0 100 100"
            class="w-full h-full -rotate-90 transform transition-all duration-500"
          >
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-border)"
              stroke-width="12"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-primary)"
              stroke-width="12" 
              :stroke-dasharray="donut.pd"
              class="transition-all duration-700"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-success)"
              stroke-width="12" 
              :stroke-dasharray="donut.cd"
              :stroke-dashoffset="donut.co"
              class="transition-all duration-700"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-secondary)"
              stroke-width="12" 
              :stroke-dasharray="donut.bd"
              :stroke-dashoffset="donut.bo"
              class="transition-all duration-700"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-3xl font-bold text-neutral-text">{{ fmtCompact(donut.total) }}</span>
            <span class="text-xs text-neutral-text-secondary mt-1">总伤害</span>
          </div>
        </div>
        <div class="flex-1 space-y-4">
          <div class="flex items-center justify-between p-4 rounded-xl bg-primary/10 border border-primary/20">
            <div class="flex items-center gap-3">
              <span class="w-4 h-4 rounded-full bg-primary" />
              <span class="text-sm font-semibold text-neutral-text">直伤</span>
            </div>
            <div class="text-right">
              <p class="text-xl font-bold text-primary">
                {{ fmtCompact(agg.total_power_damage) }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ donut.p }}%
              </p>
            </div>
          </div>
          <div class="flex items-center justify-between p-4 rounded-xl bg-success/10 border border-success/20">
            <div class="flex items-center gap-3">
              <span class="w-4 h-4 rounded-full bg-success" />
              <span class="text-sm font-semibold text-neutral-text">症状</span>
            </div>
            <div class="text-right">
              <p class="text-xl font-bold text-success">
                {{ fmtCompact(agg.total_condi_damage) }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ donut.c }}%
              </p>
            </div>
          </div>
          <div class="flex items-center justify-between p-4 rounded-xl bg-secondary/10 border border-secondary/20">
            <div class="flex items-center gap-3">
              <span class="w-4 h-4 rounded-full bg-secondary" />
              <span class="text-sm font-semibold text-neutral-text">破甲</span>
            </div>
            <div class="text-right">
              <p class="text-xl font-bold text-secondary">
                {{ fmtCompact(agg.total_breakbar_damage) }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ breakbarPct }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 伤害排行表格 -->
      <div>
        <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
          <i class="pi pi-trophy text-yellow-500" /> 伤害贡献排行
        </h4>
        <DataTable
          :value="topDpsPlayers"
          :paginator="true"
          :rows="10"
          class="w-full"
          scrollable
        >
          <Column
            field="rank"
            header="排名"
            style="width: 60px"
          >
            <template #body="{ index }">
              <span
                class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                :class="rankClass(index)"
              >{{ index + 1 }}</span>
            </template>
          </Column>
          <Column
            field="character_name"
            header="玩家"
            style="min-width: 140px"
          >
            <template #body="{ data }">
              <div class="flex items-center gap-2">
                <img
                  :src="getProfessionIconUrl(data.profession)"
                  class="w-6 h-6 rounded-full"
                >
                <div>
                  <p class="text-sm font-medium">
                    {{ data.character_name || data.account }}
                  </p>
                  <p class="text-xs text-neutral-text-secondary">
                    {{ getProfessionName(data.profession) }}
                  </p>
                </div>
              </div>
            </template>
          </Column>
          <Column
            field="damage"
            header="总伤害"
            style="min-width: 120px"
          >
            <template #body="{ data }">
              <span class="text-sm font-bold text-primary">{{ fmtCompact(data.damage) }}</span>
            </template>
          </Column>
          <Column
            field="power_damage"
            header="直伤"
            style="min-width: 100px"
          >
            <template #body="{ data }">
              <span class="text-sm text-primary/80">{{ fmtCompact(data.power_damage) }}</span>
            </template>
          </Column>
          <Column
            field="condi_damage"
            header="症状"
            style="min-width: 100px"
          >
            <template #body="{ data }">
              <span class="text-sm text-success/80">{{ fmtCompact(data.condi_damage) }}</span>
            </template>
          </Column>
          <Column
            field="dps"
            header="DPS"
            style="min-width: 100px"
          >
            <template #body="{ data }">
              <span class="text-sm font-semibold text-neutral-text">{{ fmtCompact(data.dps) }}</span>
            </template>
          </Column>
          <Column
            field="damage_percent"
            header="占比"
            style="min-width: 80px"
          >
            <template #body="{ data }">
              <span class="text-sm">{{ ((data.damage / donut.total) * 100).toFixed(1) }}%</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </Dialog>

  <!-- 战斗属性详情弹框 -->
  <Dialog
    v-model:visible="showStatDetailDialog"
    :header="statDetailTitle"
    :style="{ width: '700px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
  >
    <div class="space-y-4">
      <!-- 统计摘要 -->
      <div class="flex items-center gap-4 p-3 rounded-xl bg-neutral-bg-secondary border border-neutral-border/50">
        <div class="flex items-center gap-2">
          <i class="pi pi-users text-primary" />
          <span class="text-sm text-neutral-text">共 {{ statDetailList.length }} 人</span>
        </div>
        <div
          v-if="statDetailList.length > 0"
          class="flex items-center gap-2 ml-auto"
        >
          <span class="text-xs text-neutral-text-secondary">平均值：</span>
          <span class="text-sm font-semibold text-primary">
            {{ statDetailList.length > 0 ? (statDetailList.reduce((s, p) => s + parseFloat(getStatValue(p, currentStatType).replace('%', '')), 0) / statDetailList.length).toFixed(1) : '0' }}{{ currentStatType === 'condition_cleanses' || currentStatType === 'boon_strips' || currentStatType === 'damage_taken' ? '' : '%' }}
          </span>
        </div>
      </div>

      <!-- 玩家列表 -->
      <DataTable
        :value="statDetailList"
        :paginator="true"
        :rows="10"
        class="w-full"
        scrollable
        scroll-height="400px"
      >
        <Column
          field="rank"
          header="排名"
          style="width: 60px"
        >
          <template #body="{ index }">
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
              :class="rankClass(index)"
            >{{ index + 1 }}</span>
          </template>
        </Column>
        <Column
          field="character_name"
          header="玩家"
          style="min-width: 160px"
        >
          <template #body="{ data }">
            <div
              class="flex items-center gap-2 cursor-pointer hover:text-primary transition-colors"
              @click="openPlayerDialog(data)"
            >
              <img
                :src="getProfessionIconUrl(data.profession)"
                class="w-6 h-6 rounded-full"
              >
              <div>
                <p class="text-sm font-medium">
                  {{ data.character_name || data.account }}
                </p>
                <p class="text-xs text-neutral-text-secondary">
                  {{ getProfessionName(data.profession) }}
                </p>
              </div>
            </div>
          </template>
        </Column>
        <Column
          field="account"
          header="账号"
          style="min-width: 120px"
        >
          <template #body="{ data }">
            <span class="text-xs text-neutral-text-secondary">{{ data.account }}</span>
          </template>
        </Column>
        <Column
          :field="currentStatType"
          header="数值"
          style="min-width: 120px"
        >
          <template #body="{ data }">
            <span
              class="text-sm font-semibold"
              :class="getStatValueClass(currentStatType, data)"
            >{{ getStatValue(data, currentStatType) }}</span>
          </template>
        </Column>
      </DataTable>
    </div>
  </Dialog>

  <!-- 玩家详情弹框 -->
  <Dialog
    v-model:visible="dialogVisible"
    :header="selectedPlayer ? (selectedPlayer.character_name || selectedPlayer.account) : '玩家详情'"
    :style="{ width: '900px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
  >
    <div
      v-if="selectedPlayer"
      class="space-y-5"
    >
      <!-- 玩家信息头 -->
      <div class="flex items-center gap-4 pb-4 border-b border-neutral-border">
        <img
          :src="getProfessionIconUrl(selectedPlayer.profession)"
          class="w-12 h-12 rounded-full"
        >
        <div>
          <p class="text-lg font-bold text-neutral-text">
            {{ selectedPlayer.character_name || selectedPlayer.account }}
          </p>
          <p
            v-if="selectedPlayer.account && selectedPlayer.character_name"
            class="text-sm text-neutral-text-secondary"
          >
            {{ selectedPlayer.account }}
          </p>
          <p class="text-sm text-neutral-text-secondary">
            {{ getProfessionName(selectedPlayer.profession) }}
          </p>
        </div>
        <div class="ml-auto flex gap-3 text-sm">
          <div class="text-center">
            <p class="font-bold text-primary">
              {{ fmtCompact(selectedPlayer.damage) }}
            </p><p class="text-xs text-neutral-text-secondary">
              总伤害
            </p>
          </div>
          <div class="text-center">
            <p class="font-bold text-primary">
              {{ fmtCompact(selectedPlayer.dps) }}
            </p><p class="text-xs text-neutral-text-secondary">
              DPS
            </p>
          </div>
          <div class="text-center">
            <p class="font-bold text-status-success">
              {{ selectedPlayer.score_grade || '-' }}
            </p><p class="text-xs text-neutral-text-secondary">
              评分
            </p>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div
        v-if="rotationLoading"
        class="flex items-center justify-center py-8"
      >
        <ProgressSpinner style="width: 40px; height: 40px" />
        <span class="ml-3 text-neutral-text-secondary text-sm">加载技能数据中...</span>
      </div>

      <template v-else-if="playerRotation">
        <!-- 武器配置 -->
        <div
          v-if="playerRotation.weapons?.length"
          class="pb-4 border-b border-neutral-border"
        >
          <h4 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2">
            <i class="pi pi-wrench text-primary" /> 武器配置
          </h4>
          <div class="flex items-center gap-3 flex-wrap">
            <div
              v-for="(w, idx) in playerRotation.weapons.filter((x: string) => x && x !== 'Unknown').slice(0, 4)"
              :key="idx"
              class="px-2 py-1 rounded bg-neutral-bg text-xs text-neutral-text"
            >
              {{ weaponNameMap[w] || w }}
            </div>
          </div>
        </div>

        <!-- 食物/扳手 -->
        <div
          v-if="playerRotation.consumables?.food?.length || playerRotation.consumables?.utility?.length"
          class="pb-4 border-b border-neutral-border"
        >
          <h4 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2">
            <i class="pi pi-sparkles text-status-success" /> 食物 / 扳手
          </h4>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(f, idx) in playerRotation.consumables.food"
              :key="`food-${idx}`"
              class="flex items-center gap-2 px-2 py-1 rounded bg-status-success/10 text-xs text-neutral-text"
            >
              <img
                v-if="f.icon"
                :src="f.icon"
                class="w-5 h-5 rounded"
              >
              <span>{{ f.name || '未知食物' }}</span>
            </div>
            <div
              v-for="(u, idx) in playerRotation.consumables.utility"
              :key="`util-${idx}`"
              class="flex items-center gap-2 px-2 py-1 rounded bg-primary/10 text-xs text-neutral-text"
            >
              <img
                v-if="u.icon"
                :src="u.icon"
                class="w-5 h-5 rounded"
              >
              <span>{{ u.name || '未知扳手' }}</span>
            </div>
          </div>
        </div>

        <!-- 无详细数据时统一提示 -->
        <div
          v-if="!hasPlayerDetailData"
          class="text-neutral-text-secondary text-sm text-center py-8"
        >
          <i class="pi pi-info-circle text-2xl mb-2 block" />
          <p>暂无详细战斗数据</p>
          <p class="text-xs mt-1">
            当前解析器暂未提供技能循环、武器配置等详细信息
          </p>
        </div>

        <div
          v-else
          class="grid grid-cols-1 lg:grid-cols-2 gap-5"
        >
          <!-- 技能释放次数 -->
          <div v-if="sortedSkillCasts.length > 0">
            <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
              <i class="pi pi-sort-amount-down text-primary" /> 技能释放次数
            </h4>
            <div class="max-h-[400px] overflow-auto space-y-1">
              <div
                v-for="s in sortedSkillCasts"
                :key="s.skillId"
                class="flex items-center gap-3 p-2 rounded hover:bg-neutral-bg/50"
              >
                <img
                  v-if="s.icon"
                  :src="s.icon"
                  class="w-8 h-8 rounded"
                >
                <div
                  v-else
                  class="w-8 h-8 rounded bg-neutral-bg flex items-center justify-center text-xs text-neutral-text-secondary"
                >
                  ?
                </div>
                <span class="text-sm text-neutral-text flex-1 truncate">{{ s.name }}</span>
                <span class="text-sm font-bold text-primary w-10 text-right">{{ s.count }}</span>
              </div>
            </div>
          </div>

          <!-- 技能循环 -->
          <div v-if="rotationEvents.length > 0">
            <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
              <i class="pi pi-history text-primary" /> 技能循环 (前100次)
            </h4>
            <div class="max-h-[400px] overflow-auto space-y-1">
              <div
                v-for="(e, idx) in rotationEvents"
                :key="idx"
                class="flex items-center gap-3 p-2 rounded hover:bg-neutral-bg/50"
              >
                <img
                  v-if="e.icon"
                  :src="e.icon"
                  class="w-8 h-8 rounded"
                >
                <div
                  v-else
                  class="w-8 h-8 rounded bg-neutral-bg flex items-center justify-center text-xs text-neutral-text-secondary"
                >
                  ?
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-neutral-text truncate">
                    {{ e.name }}
                  </p>
                  <p class="text-[10px] text-neutral-text-secondary">
                    {{ e.duration > 0 ? e.duration + 'ms' : '瞬发' }}
                  </p>
                </div>
                <span class="text-xs text-neutral-text-secondary w-16 text-right">{{ e.time.toFixed(1) }}s</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div
        v-else
        class="text-neutral-text-secondary text-sm text-center py-8"
      >
        <i class="pi pi-info-circle text-2xl mb-2 block" />
        <p>该日志未生成技能循环数据</p>
        <p class="text-xs mt-1">
          请重新解析日志以获取技能详情
        </p>
      </div>
    </div>
  </Dialog>

  <ConfirmDialog />
  <Toast />
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { getProfessionColor, getProfessionName, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import Button from 'primevue/button'
import TabMenu from 'primevue/tabmenu'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import ProgressSpinner from 'primevue/progressspinner'
import { logsService } from '@/services/combat/logsService'
import { eiAnalysisService, type EiAnalysisResponse, type EiAnalysisPlayer, type EiAnalysisFight, type EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import type { PlayerRotationData } from '@/services/ei/eiAnalysisService'

import { getSkillIconUrl } from '@/utils/skillIcons'

const weaponNameMap: Record<string, string> = {
  'Sword': '剑', 'Axe': '斧', 'Mace': '锤', 'Shield': '盾',
  'Greatsword': '大剑', 'Hammer': '巨锤', 'Staff': '法杖',
  'Scepter': '权杖', 'Focus': '聚能器', 'Dagger': '匕首',
  'Pistol': '手枪', 'Rifle': '步枪', 'Shortbow': '短弓',
  'Longbow': '长弓', 'Torch': '火炬', 'Warhorn': '战号',
  'Spear': '矛', 'Trident': '三叉戟', '2Hand': '双手'
}

const route = useRoute()
const toast = useToast()
const confirm = useConfirm()
const activeTab = ref(0)
const loading = ref(true)
const parsing = ref(false)
const error = ref('')
const playerSort = ref('damage')
const dialogVisible = ref(false)
const selectedPlayer = ref<EiAnalysisPlayer | null>(null)
const playerRotation = ref<PlayerRotationData | null>(null)
const rotationLoading = ref(false)
const showDetailStats = ref(false)
const showDamageDetailDialog = ref(false)
const showStatDetailDialog = ref(false)
const currentStatType = ref<'protection' | 'stability' | 'condition_cleanses' | 'boon_strips' | 'damage_taken' | 'hitRate'>('protection')
const statDetailTitle = ref('')

const logDetail = ref<Record<string, any>>({})
const summary = ref<EiAnalysisResponse | null>(null)

const tabItems = [
  { label: '战斗概览', icon: 'pi pi-chart-bar' },
  { label: '玩家 & 小队', icon: 'pi pi-users' },
]

const fightSummary = computed<EiAnalysisFight>(() => summary.value?.fight || ({} as EiAnalysisFight))
const agg = computed<EiAnalysisAggregate>(() => summary.value?.aggregate || {
  duration_sec: 0, player_count: 0, total_damage: 0, total_power_damage: 0, total_condi_damage: 0,
  total_breakbar_damage: 0, total_damage_taken: 0, total_healing: 0, total_kills: 0, total_deaths: 0,
  total_downs: 0, total_boon_strips: 0, total_condition_cleanses: 0, total_resurrects: 0, avg_dps: 0, avg_critical_rate: 0
})

const players = computed(() => summary.value?.players || [])

const kpiList = computed(() => {
  const maxDamage = 5000000 // 参考最大值
  const maxHealing = 2000000 // 参考最大值
  const maxDeaths = 50 // 参考最大值
  const maxDps = 50000 // 参考最大值
  
  return [
    { 
      icon: 'pi pi-bolt', 
      label: '总伤害', 
      value: fmtCompact(agg.value.total_damage), 
      color: 'text-primary', 
      bg: 'from-primary/20 to-primary/5',
      barColor: 'bg-primary',
      unit: '',
      percent: Math.min((agg.value.total_damage / maxDamage) * 100, 100)
    },
    { 
      icon: 'pi pi-heart', 
      label: '总治疗', 
      value: fmtCompact(agg.value.total_healing), 
      color: 'text-success', 
      bg: 'from-success/20 to-success/5',
      barColor: 'bg-success',
      unit: '',
      percent: Math.min((agg.value.total_healing / maxHealing) * 100, 100)
    },
    { 
      icon: 'pi pi-shield', 
      label: '总承伤', 
      value: fmtCompact(agg.value.total_damage_taken), 
      color: 'text-secondary', 
      bg: 'from-secondary/20 to-secondary/5',
      barColor: 'bg-secondary',
      unit: '',
      percent: Math.min((agg.value.total_damage_taken / maxDamage) * 100, 100)
    },
    { 
      icon: 'pi pi-star', 
      label: '击杀', 
      value: String(agg.value.total_kills || 0), 
      color: 'text-success', 
      bg: 'from-success/20 to-success/5',
      barColor: 'bg-success',
      unit: '次',
      percent: Math.min((agg.value.total_kills / maxDeaths) * 100, 100)
    },
    { 
      icon: 'pi pi-times-circle', 
      label: '死亡', 
      value: String(agg.value.total_deaths || 0), 
      color: 'text-error', 
      bg: 'from-error/20 to-error/5',
      barColor: 'bg-error',
      unit: '次',
      percent: Math.min((agg.value.total_deaths / maxDeaths) * 100, 100)
    },
    { 
      icon: 'pi pi-chart-line', 
      label: '平均DPS', 
      value: fmtCompact(agg.value.avg_dps), 
      color: 'text-primary', 
      bg: 'from-primary/20 to-primary/5',
      barColor: 'bg-primary',
      unit: '',
      percent: Math.min((agg.value.avg_dps / maxDps) * 100, 100)
    },
  ]
})

const donut = computed(() => {
  const total = Math.max(agg.value.total_damage, 1)
  const p = Math.round((agg.value.total_power_damage / total) * 100)
  const c = Math.round((agg.value.total_condi_damage / total) * 100)
  const b = Math.round((agg.value.total_breakbar_damage / total) * 100)
  const circ = 2 * Math.PI * 40
  return {
    total: agg.value.total_damage,
    p, c, b,
    pd: `${(p / 100) * circ} ${circ}`,
    cd: `${(c / 100) * circ} ${circ}`,
    bd: `${(b / 100) * circ} ${circ}`,
    co: -((p / 100) * circ),
    bo: -(((p + c) / 100) * circ),
  }
})

const topDpsPlayers = computed(() => {
  return [...players.value].sort((a, b) => b.dps - a.dps).slice(0, 10)
})

const commanders = computed(() => players.value.filter((p: EiAnalysisPlayer) => p.has_commander_tag))

const groups = computed(() => {
  const result: { id: number; players: EiAnalysisPlayer[] }[] = []
  for (let i = 1; i <= 15; i++) {
    const g = players.value.filter((p: EiAnalysisPlayer) => p.group_id === i)
    if (g.length) result.push({ id: i, players: g })
  }
  return result
})

const ungroupedPlayers = computed(() => players.value.filter((p: EiAnalysisPlayer) => !p.group_id))

const statAverages = computed(() => {
  const list = players.value
  if (!list.length) return { protection: 0, stability: 0, hitRate: 100 }
  const sum = (key: keyof EiAnalysisPlayer) => list.reduce((s, p) => s + (Number(p[key]) || 0), 0)
  const avgProtection = list.filter(p => p.protection_uptime > 0).reduce((s, p) => s + p.protection_uptime, 0) / list.filter(p => p.protection_uptime > 0).length || 0
  const avgStability = list.filter(p => p.stability_uptime > 0).reduce((s, p) => s + p.stability_uptime, 0) / list.filter(p => p.stability_uptime > 0).length || 0
  const hitRate = 100 - ((sum('missed') / (sum('missed') + sum('critical_rate') + sum('flanking_rate') + sum('glance_rate') + 1)) * 100) || 0
  return {
    protection: avgProtection || 0,
    stability: avgStability || 0,
    hitRate: Math.min(Math.max(hitRate, 0), 100)
  }
})

const selectedTeamId = ref<number | null>(null)
const getTeamTotalDamage = (g: { id: number; players: EiAnalysisPlayer[] }) => {
  return g.players.reduce((sum, p) => sum + (p.damage || 0), 0)
}

const getTeamAvgDps = (g: { id: number; players: EiAnalysisPlayer[] }) => {
  return g.players.length ? Math.round(g.players.reduce((sum, p) => sum + (p.dps || 0), 0) / g.players.length) : 0
}

const getTeamAvgScore = (g: { id: number; players: EiAnalysisPlayer[] }): number | undefined => {
  const scored = g.players.filter(p => p.ai_score != null)
  return scored.length ? scored.reduce((sum, p) => sum + (p.ai_score || 0), 0) / scored.length : undefined
}

const statDetailList = computed(() => {
  const list = [...players.value]
  switch (currentStatType.value) {
    case 'protection':
      return list.filter(p => p.protection_uptime > 0).sort((a, b) => b.protection_uptime - a.protection_uptime)
    case 'stability':
      return list.filter(p => p.stability_uptime > 0).sort((a, b) => b.stability_uptime - a.stability_uptime)
    case 'condition_cleanses':
      return list.sort((a, b) => b.condition_cleanses - a.condition_cleanses)
    case 'boon_strips':
      return list.sort((a, b) => b.boon_strips - a.boon_strips)
    case 'damage_taken':
      return list.sort((a, b) => b.damage_taken - a.damage_taken)
    case 'hitRate':
      return list.sort((a, b) => {
        const aRate = 100 - ((a.missed || 0) / ((a.missed || 0) + (a.critical_rate || 0) + (a.flanking_rate || 0) + (a.glance_rate || 0) + 1) * 100)
        const bRate = 100 - ((b.missed || 0) / ((b.missed || 0) + (b.critical_rate || 0) + (b.flanking_rate || 0) + (b.glance_rate || 0) + 1) * 100)
        return bRate - aRate
      })
    default:
      return list
  }
})

const getStatValue = (p: EiAnalysisPlayer, type: string) => {
  switch (type) {
    case 'protection': return p.protection_uptime.toFixed(1) + '%'
    case 'stability': return p.stability_uptime.toFixed(1) + '%'
    case 'condition_cleanses': return fmtCompact(p.condition_cleanses)
    case 'boon_strips': return fmtCompact(p.boon_strips)
    case 'damage_taken': return fmtCompact(p.damage_taken)
    case 'hitRate': {
      const rate = 100 - ((p.missed || 0) / ((p.missed || 0) + (p.critical_rate || 0) + (p.flanking_rate || 0) + (p.glance_rate || 0) + 1) * 100)
      return rate.toFixed(1) + '%'
    }
    default: return '-'
  }
}

const getStatValueClass = (type: string, p: EiAnalysisPlayer) => {
  const val = parseFloat(getStatValue(p, type).replace('%', ''))
  switch (type) {
    case 'protection':
    case 'stability':
    case 'hitRate':
      return val >= 70 ? 'text-success' : val >= 40 ? 'text-warning' : 'text-error'
    case 'condition_cleanses':
    case 'boon_strips':
      return 'text-primary'
    case 'damage_taken':
      return 'text-secondary'
    default:
      return 'text-neutral-text'
  }
}

const openStatDetailDialog = (type: 'protection' | 'stability' | 'condition_cleanses' | 'boon_strips' | 'damage_taken' | 'hitRate', title: string) => {
  currentStatType.value = type
  statDetailTitle.value = title
  showStatDetailDialog.value = true
}

const sortedPlayerList = computed(() => {
  const list = [...players.value]
  const key = playerSort.value as keyof EiAnalysisPlayer
  list.sort((a: any, b: any) => (b[key] || 0) - (a[key] || 0))
  return list
})

const hasPlayerDetailData = computed(() => {
  if (!playerRotation.value) return false
  const hasConsumables = (
    (playerRotation.value.consumables?.food?.length || 0) > 0 ||
    (playerRotation.value.consumables?.utility?.length || 0) > 0
  )
  return (
    (playerRotation.value.weapons?.length || 0) > 0 ||
    sortedSkillCasts.value.length > 0 ||
    rotationEvents.value.length > 0 ||
    hasConsumables
  )
})

const powerPct = computed(() => {
  const t = agg.value.total_damage
  return t ? Math.round((agg.value.total_power_damage / t) * 100) : 0
})
const condiPct = computed(() => {
  const t = agg.value.total_damage
  return t ? Math.round((agg.value.total_condi_damage / t) * 100) : 0
})
const breakbarPct = computed(() => {
  const t = agg.value.total_damage
  return t ? Math.round((agg.value.total_breakbar_damage / t) * 100) : 0
})

const loadData = async (sortBy?: string) => {
  const logId = Number(route.params.id)
  if (!logId) { error.value = '无效的日志ID'; loading.value = false; return }
  loading.value = true; error.value = ''
  try {
    const [logRes, sumRes] = await Promise.all([
      logsService.getLog(logId),
      eiAnalysisService.getSummary(logId, sortBy || playerSort.value)
    ])
    if (logRes.success) logDetail.value = logRes.data || {}
    if (sumRes.success && sumRes.data) summary.value = sumRes.data
    else {
      toast.add({ severity: 'warn', summary: '暂无解析数据', detail: '该日志尚未解析或解析失败', life: 3000 })
    }
  } catch (e: any) {
    error.value = e.message || '加载数据失败'
    toast.add({ severity: 'error', summary: '加载失败', detail: error.value, life: 3000 })
  } finally {
    loading.value = false
  }
}

const reparseLog = async () => {
  confirm.require({
    message: '重新解析将覆盖现有数据，是否继续？',
    header: '确认重新解析',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: '确认',
    rejectLabel: '取消',
    accept: async () => {
      const logId = Number(route.params.id)
      parsing.value = true
      try {
        const res = await logsService.parseLog(logId)
        if (res.success) {
          toast.add({ severity: 'info', summary: '重新解析', detail: '正在解析，请稍后刷新', life: 3000 })
          pollParseProgress(logId)
        } else throw new Error(res.message)
      } catch (e: any) {
        toast.add({ severity: 'error', summary: '解析失败', detail: e.message || '重新解析失败', life: 3000 })
      } finally {
        parsing.value = false
      }
    }
  })
}

const pollParseProgress = (logId: number) => {
  const iv = setInterval(async () => {
    try {
      const res = await logsService.getParseProgress(logId)
      if (res.data?.progress === 100) {
        clearInterval(iv); await loadData()
        toast.add({ severity: 'success', summary: '解析完成', detail: '数据已更新', life: 3000 })
      } else if (res.data?.stage === '错误') {
        clearInterval(iv)
        toast.add({ severity: 'error', summary: '解析失败', detail: res.data?.errors?.[0] || '解析错误', life: 3000 })
      }
    } catch { clearInterval(iv) }
  }, 2000)
}

const rankClass = (idx: number) => {
  if (idx === 0) return 'bg-yellow-500/20 text-yellow-600'
  if (idx === 1) return 'bg-gray-400/20 text-gray-500'
  if (idx === 2) return 'bg-orange-400/20 text-orange-500'
  return 'bg-neutral-bg text-neutral-text-secondary'
}

const groupColor = (id: number) => {
  const colors: Record<string, string> = {
    '0': '#6b7280', '1': '#ef4444', '2': '#f97316', '3': '#eab308', '4': '#84cc16',
    '5': '#22c55e', '6': '#06b6d4', '7': '#3b82f6', '8': '#8b5cf6', '9': '#d946ef', '10': '#f43f5e'
  }
  return colors[String(id)] || '#6b7280'
}

const scoreSeverity = (score?: string) => {
  if (!score) return 'secondary'
  const s = score.toLowerCase()
  if (s.startsWith('s')) return 'success'
  if (s.startsWith('a')) return 'info'
  if (s.startsWith('b')) return 'warn'
  return 'danger'
}

const scoreValueColor = (score?: number | null) => {
  if (score == null) return 'text-neutral-text-secondary'
  if (score >= 90) return 'text-success'
  if (score >= 80) return 'text-info'
  if (score >= 70) return 'text-warning'
  if (score >= 60) return 'text-orange-400'
  return 'text-error'
}

const fmtDuration = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return m > 0 ? `${m}分${s}秒` : `${s}秒`
}

const fmtDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const onRowClick = (event: any) => {
  const player = event.data as EiAnalysisPlayer
  if (player) {
    openPlayerDialog(player)
  }
}

const openPlayerDialog = async (player: EiAnalysisPlayer) => {
  selectedPlayer.value = player
  dialogVisible.value = true
  rotationLoading.value = true
  playerRotation.value = null
  try {
    const logId = Number(route.params.id)
    const res = await eiAnalysisService.getPlayerRotation(logId, player.account)
    if (res.success && res.data) {
      playerRotation.value = res.data
    } else {
      toast.add({ severity: 'warn', summary: '暂无数据', detail: res.message || '该玩家没有技能循环数据', life: 3000 })
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message || '获取技能数据失败', life: 3000 })
  } finally {
    rotationLoading.value = false
  }
}

const sortedSkillCasts = computed(() => {
  if (!playerRotation.value?.skill_casts) return []
  const map = playerRotation.value.skill_map || {}
  return Object.entries(playerRotation.value.skill_casts)
    .map(([skillId, count]) => {
      const name = map[skillId]?.name || `技能 #${skillId}`
      return {
        skillId,
        count,
        name,
        icon: getSkillIconUrl(name),
      }
    })
    .sort((a, b) => b.count - a.count)
})

const rotationEvents = computed(() => {
  if (!playerRotation.value?.rotation) return []
  const map = playerRotation.value.skill_map || {}
  const events: any[] = []
  playerRotation.value.rotation.forEach((rot: any) => {
    if (!rot || typeof rot !== 'object') return
    const skillId = rot.id ?? 0
    const name = map[String(skillId)]?.name || `技能 #${skillId}`
    const icon = getSkillIconUrl(name)
    ;(rot.skills || []).forEach((cast: any) => {
      events.push({
        time: (cast.castTime ?? 0) / 1000,
        skillId,
        duration: cast.duration ?? 0,
        casts: 1,
        name,
        icon,
      })
    })
  })
  return events.slice(0, 100)
})

// 监听路由参数变化，切换日志时重新加载数据
watch(() => route.params.id, () => {
  loadData()
})

// 前端纯排序，不触发后端请求
// watch(playerSort, () => { loadData(playerSort.value) })

onMounted(() => { loadData() })
</script>
