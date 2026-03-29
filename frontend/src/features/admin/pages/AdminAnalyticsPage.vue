<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '../stores/admin.store'
import AnalyticsStatCards from '../components/AnalyticsStatCards.vue'
import AnalyticsCharts from '../components/AnalyticsCharts.vue'

const { t } = useI18n()
const adminStore = useAdminStore()

onMounted(() => adminStore.fetchAnalytics())
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">{{ t('nav.analytics') }}</h1>

    <div v-if="adminStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="adminStore.analytics">
      <AnalyticsStatCards :analytics="adminStore.analytics" />
      <AnalyticsCharts :analytics="adminStore.analytics" />
    </template>
  </div>
</template>
