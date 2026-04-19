<script setup lang="ts">
/**
 * AdminDashboardPage — system-wide overview.
 * Denser treatment: compact tiles, minimal glass.
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '../stores/admin.store'
import AdminPageHeader from '../components/AdminPageHeader.vue'
import AdminStatTile from '../components/AdminStatTile.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'

const { t } = useI18n()
const adminStore = useAdminStore()

onMounted(() => adminStore.fetchAnalytics())
</script>

<template>
  <div class="mx-auto w-full max-w-7xl">
    <AdminPageHeader :eyebrow="t('admin.title')" :title="t('admin.title')" />

    <div v-if="adminStore.loading" class="py-10 text-center">
      <i class="pi pi-spinner pi-spin text-2xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else-if="adminStore.analytics">
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <AdminStatTile
          icon="pi pi-building"
          :label="t('admin.dashboard.totalCompanies')"
          :value="adminStore.analytics.totalCompanies"
        />
        <AdminStatTile
          icon="pi pi-users"
          accent="success"
          :label="t('admin.dashboard.totalUsers')"
          :value="adminStore.analytics.totalUsers"
        />
        <AdminStatTile
          icon="pi pi-video"
          accent="ai"
          :label="t('admin.dashboard.totalInterviews')"
          :value="adminStore.analytics.totalInterviews"
        />
        <AdminStatTile
          icon="pi pi-credit-card"
          accent="warning"
          :label="t('admin.analytics.activeSubscriptions')"
          :value="adminStore.analytics.activeSubscriptions"
        />
        <AdminStatTile
          icon="pi pi-dollar"
          accent="celebrate"
          :label="t('admin.dashboard.monthlyRevenue')"
          :value="`$${adminStore.analytics.monthlyRevenue.toLocaleString()}`"
        />
      </div>

      <!-- Charts placeholder -->
      <div class="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <GlassSurface level="1" class="flex h-56 items-center justify-center px-4">
          <p class="font-mono text-xs text-[color:var(--color-text-muted)]">
            {{ t('admin.analytics.revenueChartSoon') }}
          </p>
        </GlassSurface>
        <GlassSurface level="1" class="flex h-56 items-center justify-center px-4">
          <p class="font-mono text-xs text-[color:var(--color-text-muted)]">
            {{ t('admin.analytics.userGrowthChartSoon') }}
          </p>
        </GlassSurface>
      </div>
    </template>
  </div>
</template>
