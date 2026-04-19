<script setup lang="ts">
/**
 * AnalyticsStatCards — 4-up metric grid for HR analytics page.
 * Composes DashboardStatsCard for consistent glass styling.
 */
import { useI18n } from 'vue-i18n'
import DashboardStatsCard from './DashboardStatsCard.vue'

defineProps<{
  totalApplications: number
  totalInterviews: number
  completionRate: number
  averageScore: number | null
}>()

const { t } = useI18n()
</script>

<template>
  <div class="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
    <DashboardStatsCard
      icon="pi pi-users"
      icon-accent="default"
      :label="t('analytics.totalApplications')"
      :value="totalApplications"
    />
    <DashboardStatsCard
      icon="pi pi-video"
      icon-accent="ai"
      :label="t('analytics.totalInterviews')"
      :value="totalInterviews"
    />
    <DashboardStatsCard
      icon="pi pi-check-circle"
      icon-accent="success"
      :label="t('analytics.completionRate')"
      :value="`${completionRate}%`"
    />
    <DashboardStatsCard
      icon="pi pi-star"
      icon-accent="celebrate"
      :label="t('analytics.avgInterviewScore')"
      :value="averageScore !== null ? averageScore : '-'"
    />
  </div>
</template>
