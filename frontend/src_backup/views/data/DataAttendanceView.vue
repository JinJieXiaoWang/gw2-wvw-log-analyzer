<template>
  <div class="space-y-6">
    <PageHeader
      title="出勤评分"
      subtitle="查看和管理 WvW 出勤评分数据"
      icon="pi pi-users"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <ScoreTipCard
      :role-label="currentRoleLabel"
      :rule-version="currentRuleVersion"
      @open-rules="openScoringRulesDialog"
    />

    <AttendanceStatCards
      :total-accounts="statCards.totalAccounts"
      :total-duration="statCards.totalDuration"
      :total-damage="statCards.totalDamage"
      :total-downed="statCards.totalDowned"
    />

    <AttendanceFilterBar
      v-model:date-range="dateRange"
      v-model:search-query="searchQuery"
      v-model:filter-map="filterMap"
      v-model:filter-profession="filterProfession"
      :filter-options="filterOptions"
      :loading="loading"
      @apply="fetchAccounts"
      @reset="resetFilters"
    />

    <AttendanceTable
      :account-list="accountList"
      :pagination="pagination"
      :loading="loading"
      @page-change="onPageChange"
      @sort="onSort"
      @detail-click="openDetail"
      @score-click="openScoreBreakdown"
    />

    <ScoreBreakdownDialog
      v-model:visible="scoreBreakdownVisible"
      :account="scoreBreakdownAccount"
      :loading="scoreBreakdownLoading"
      :data="scoreBreakdownData"
    />

    <ScoringRulesDialog
      v-model:visible="scoringRulesVisible"
      v-model:active-tab="scoringRulesActiveTab"
      :loading="scoringRulesLoading"
      :rules-data="scoringRulesData"
      :rule-version="currentRuleVersion"
      :role-type="currentRoleType"
    />

    <Toast />
  </div>
</template>

<script setup lang="ts">
import AttendanceFilterBar from '@/components/attendance/AttendanceFilterBar.vue'
import AttendanceStatCards from '@/components/attendance/AttendanceStatCards.vue'
import AttendanceTable from '@/components/attendance/AttendanceTable.vue'
import ScoreBreakdownDialog from '@/components/attendance/ScoreBreakdownDialog.vue'
import ScoreTipCard from '@/components/attendance/ScoreTipCard.vue'
import ScoringRulesDialog from '@/components/attendance/ScoringRulesDialog.vue'
import { useAttendancePage } from '@/composables/attendance/useAttendancePage'
import PageHeader from '@/layout/components/PageHeader.vue'
import Toast from 'primevue/toast'

const {
  currentRoleType,
  currentRoleLabel,
  currentRuleVersion,
  loading,
  dateRange,
  searchQuery,
  filterMap,
  filterProfession,
  filterOptions,
  accountList,
  pagination,
  currentSort,
  statCards,
  scoreBreakdownVisible,
  scoreBreakdownLoading,
  scoreBreakdownData,
  scoreBreakdownAccount,
  scoringRulesVisible,
  scoringRulesLoading,
  scoringRulesData,
  scoringRulesActiveTab,
  openScoringRulesDialog,
  openDetail,
  openScoreBreakdown,
  onPageChange,
  onSort,
  resetFilters,
  fetchAccounts
} = useAttendancePage()
</script>
