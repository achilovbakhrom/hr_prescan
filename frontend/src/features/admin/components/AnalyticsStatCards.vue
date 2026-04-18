<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { PlatformAnalytics } from '../types/admin.types'

defineProps<{
  analytics: PlatformAnalytics
}>()

const { t } = useI18n()
</script>

<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="flex items-center gap-3">
        <i class="pi pi-building text-2xl text-blue-500"></i>
        <div>
          <p class="text-sm text-gray-500">{{ t('admin.dashboard.totalCompanies') }}</p>
          <p class="text-2xl font-bold">{{ analytics.totalCompanies }}</p>
        </div>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="flex items-center gap-3">
        <i class="pi pi-users text-2xl text-green-500"></i>
        <div>
          <p class="text-sm text-gray-500">{{ t('admin.dashboard.totalUsers') }}</p>
          <p class="text-2xl font-bold">{{ analytics.totalUsers }}</p>
        </div>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="flex items-center gap-3">
        <i class="pi pi-video text-2xl text-purple-500"></i>
        <div>
          <p class="text-sm text-gray-500">{{ t('admin.dashboard.totalInterviews') }}</p>
          <p class="text-2xl font-bold">{{ analytics.totalInterviews }}</p>
        </div>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="flex items-center gap-3">
        <i class="pi pi-credit-card text-2xl text-yellow-500"></i>
        <div>
          <p class="text-sm text-gray-500">{{ t('admin.analytics.activeSubscriptions') }}</p>
          <p class="text-2xl font-bold">{{ analytics.activeSubscriptions }}</p>
        </div>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="flex items-center gap-3">
        <i class="pi pi-dollar text-2xl text-emerald-500"></i>
        <div>
          <p class="text-sm text-gray-500">{{ t('admin.dashboard.monthlyRevenue') }}</p>
          <p class="text-2xl font-bold">
            ${{
              (analytics.estimatedMonthlyRevenue || analytics.monthlyRevenue || 0).toLocaleString()
            }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
