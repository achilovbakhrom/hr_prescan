<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '../stores/admin.store'

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
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <div class="flex items-center gap-3">
            <i class="pi pi-building text-2xl text-blue-500"></i>
            <div>
              <p class="text-sm text-gray-500">{{ t('admin.dashboard.totalCompanies') }}</p>
              <p class="text-2xl font-bold">
                {{ adminStore.analytics.totalCompanies }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <div class="flex items-center gap-3">
            <i class="pi pi-users text-2xl text-green-500"></i>
            <div>
              <p class="text-sm text-gray-500">{{ t('admin.dashboard.totalUsers') }}</p>
              <p class="text-2xl font-bold">
                {{ adminStore.analytics.totalUsers }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <div class="flex items-center gap-3">
            <i class="pi pi-video text-2xl text-purple-500"></i>
            <div>
              <p class="text-sm text-gray-500">{{ t('admin.dashboard.totalInterviews') }}</p>
              <p class="text-2xl font-bold">
                {{ adminStore.analytics.totalInterviews }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <div class="flex items-center gap-3">
            <i class="pi pi-credit-card text-2xl text-yellow-500"></i>
            <div>
              <p class="text-sm text-gray-500">Active Subscriptions</p>
              <p class="text-2xl font-bold">
                {{ adminStore.analytics.activeSubscriptions }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <div class="flex items-center gap-3">
            <i class="pi pi-dollar text-2xl text-emerald-500"></i>
            <div>
              <p class="text-sm text-gray-500">{{ t('admin.dashboard.monthlyRevenue') }}</p>
              <p class="text-2xl font-bold">
                ${{ adminStore.analytics.monthlyRevenue.toLocaleString() }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Placeholders -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">Revenue Trend</h2>
          <div class="flex h-48 items-center justify-center rounded bg-gray-50">
            <p class="text-gray-400">Chart placeholder</p>
          </div>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">Interview Volume</h2>
          <div class="flex h-48 items-center justify-center rounded bg-gray-50">
            <p class="text-gray-400">Chart placeholder</p>
          </div>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">Subscription Distribution</h2>
          <div class="flex h-48 items-center justify-center rounded bg-gray-50">
            <p class="text-gray-400">Chart placeholder</p>
          </div>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">User Registrations</h2>
          <div class="flex h-48 items-center justify-center rounded bg-gray-50">
            <p class="text-gray-400">Chart placeholder</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
