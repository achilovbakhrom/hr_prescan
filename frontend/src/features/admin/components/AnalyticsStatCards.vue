<script setup lang="ts">
/**
 * AnalyticsStatCards (admin) — compact stat tiles for admin analytics.
 * Composes AdminStatTile for consistent dense glass treatment.
 */
import { useI18n } from 'vue-i18n'
import AdminStatTile from './AdminStatTile.vue'
import type { PlatformAnalytics } from '../types/admin.types'

defineProps<{
  analytics: PlatformAnalytics
}>()

const { t } = useI18n()
</script>

<template>
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
    <AdminStatTile
      icon="pi pi-building"
      :label="t('admin.dashboard.totalCompanies')"
      :value="analytics.totalCompanies"
    />
    <AdminStatTile
      icon="pi pi-users"
      accent="success"
      :label="t('admin.dashboard.totalUsers')"
      :value="analytics.totalUsers"
    />
    <AdminStatTile
      icon="pi pi-video"
      accent="ai"
      :label="t('admin.dashboard.totalInterviews')"
      :value="analytics.totalInterviews"
    />
    <AdminStatTile
      icon="pi pi-credit-card"
      accent="warning"
      :label="t('admin.analytics.activeSubscriptions')"
      :value="analytics.activeSubscriptions"
    />
    <AdminStatTile
      icon="pi pi-dollar"
      accent="celebrate"
      :label="t('admin.dashboard.monthlyRevenue')"
      :value="`$${(analytics.estimatedMonthlyRevenue || analytics.monthlyRevenue || 0).toLocaleString()}`"
    />
  </div>
</template>
