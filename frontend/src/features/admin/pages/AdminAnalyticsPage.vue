<script setup lang="ts">
/**
 * AdminAnalyticsPage — system-wide analytics (denser treatment).
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '../stores/admin.store'
import AnalyticsStatCards from '../components/AnalyticsStatCards.vue'
import AnalyticsCharts from '../components/AnalyticsCharts.vue'
import AdminPageHeader from '../components/AdminPageHeader.vue'

const { t } = useI18n()
const adminStore = useAdminStore()

onMounted(() => adminStore.fetchAnalytics())
</script>

<template>
  <div class="mx-auto w-full max-w-7xl">
    <AdminPageHeader :eyebrow="t('admin.title')" :title="t('nav.analytics')" />

    <div v-if="adminStore.loading" class="py-10 text-center">
      <i class="pi pi-spinner pi-spin text-2xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else-if="adminStore.analytics">
      <AnalyticsStatCards :analytics="adminStore.analytics" />
      <div class="mt-4">
        <AnalyticsCharts :analytics="adminStore.analytics" />
      </div>
    </template>
  </div>
</template>
