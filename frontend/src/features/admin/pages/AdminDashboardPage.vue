<script setup lang="ts">
import { onMounted } from 'vue'
import { useAdminStore } from '../stores/admin.store'

const adminStore = useAdminStore()

onMounted(() => adminStore.fetchAnalytics())
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Admin Dashboard</h1>

    <div v-if="adminStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="adminStore.analytics">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <p class="text-sm text-gray-500">Total Companies</p>
          <p class="mt-1 text-2xl font-bold">
            {{ adminStore.analytics.totalCompanies }}
          </p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <p class="text-sm text-gray-500">Total Users</p>
          <p class="mt-1 text-2xl font-bold">
            {{ adminStore.analytics.totalUsers }}
          </p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <p class="text-sm text-gray-500">Total Interviews</p>
          <p class="mt-1 text-2xl font-bold">
            {{ adminStore.analytics.totalInterviews }}
          </p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <p class="text-sm text-gray-500">Active Subscriptions</p>
          <p class="mt-1 text-2xl font-bold">
            {{ adminStore.analytics.activeSubscriptions }}
          </p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <p class="text-sm text-gray-500">Monthly Revenue</p>
          <p class="mt-1 text-2xl font-bold">
            ${{ adminStore.analytics.monthlyRevenue.toLocaleString() }}
          </p>
        </div>
      </div>

      <!-- Charts Placeholder -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="flex h-64 items-center justify-center rounded-lg border border-gray-200 bg-white">
          <p class="text-gray-400">Revenue Chart (coming soon)</p>
        </div>
        <div class="flex h-64 items-center justify-center rounded-lg border border-gray-200 bg-white">
          <p class="text-gray-400">User Growth Chart (coming soon)</p>
        </div>
      </div>
    </template>
  </div>
</template>
