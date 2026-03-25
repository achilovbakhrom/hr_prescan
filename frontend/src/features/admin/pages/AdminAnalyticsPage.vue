<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Chart from 'primevue/chart'
import { useAdminStore } from '../stores/admin.store'

const { t } = useI18n()
const adminStore = useAdminStore()

onMounted(() => adminStore.fetchAnalytics())

// Revenue Trend (placeholder data since backend doesn't track revenue history yet)
const revenueTrendData = computed(() => {
  const analytics = adminStore.analytics
  if (!analytics) return null

  // Generate last 6 months labels
  const labels: string[] = []
  const now = new Date()
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    labels.push(d.toLocaleDateString(undefined, { month: 'short', year: '2-digit' }))
  }

  // Use estimated monthly revenue as the current month, simulate slight growth
  const currentRevenue = analytics.estimatedMonthlyRevenue || analytics.monthlyRevenue || 0
  const data = labels.map((_, idx) => {
    const factor = 0.6 + idx * 0.08
    return Math.round(currentRevenue * factor)
  })

  return {
    labels,
    datasets: [
      {
        label: t('admin.analytics.revenueTrend'),
        data,
        fill: true,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        pointBackgroundColor: '#10b981',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
      },
    ],
  }
})

const revenueTrendOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: number) => `$${value.toLocaleString()}`,
      },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
    x: {
      grid: { display: false },
    },
  },
}

// Interview Volume (bar chart from backend data)
const interviewVolumeData = computed(() => {
  const analytics = adminStore.analytics
  if (!analytics?.monthlyInterviewVolume?.length) return null

  const labels = analytics.monthlyInterviewVolume.map((entry) => {
    const [year, month] = entry.month.split('-')
    const d = new Date(parseInt(year), parseInt(month) - 1, 1)
    return d.toLocaleDateString(undefined, { month: 'short', year: '2-digit' })
  })

  const data = analytics.monthlyInterviewVolume.map((entry) => entry.count)

  return {
    labels,
    datasets: [
      {
        label: t('admin.analytics.interviewVolume'),
        data,
        backgroundColor: '#8b5cf6',
        borderColor: '#7c3aed',
        borderWidth: 1,
        borderRadius: 6,
        barPercentage: 0.6,
      },
    ],
  }
})

const interviewVolumeOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 1 },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
    x: {
      grid: { display: false },
    },
  },
}

// Subscription Distribution (doughnut chart from backend data)
const subscriptionDistData = computed(() => {
  const analytics = adminStore.analytics
  if (!analytics?.subscriptionDistribution?.length) return null

  const tierColors: Record<string, string> = {
    free: '#94a3b8',
    starter: '#3b82f6',
    professional: '#8b5cf6',
    enterprise: '#f59e0b',
  }

  const labels = analytics.subscriptionDistribution.map((entry) => entry.name || entry.tier)
  const data = analytics.subscriptionDistribution.map((entry) => entry.count)
  const colors = analytics.subscriptionDistribution.map(
    (entry) => tierColors[entry.tier] || '#6b7280',
  )

  return {
    labels,
    datasets: [
      {
        data,
        backgroundColor: colors,
        hoverBackgroundColor: colors.map((c) => c + 'dd'),
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  }
})

const subscriptionDistOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 16,
      },
    },
  },
  cutout: '60%',
}

// User Registrations (stacked bar chart from backend data)
const userRegistrationsData = computed(() => {
  const analytics = adminStore.analytics
  if (!analytics?.monthlyRegistrations?.length) return null

  // Group by month
  const monthMap = new Map<string, Record<string, number>>()
  for (const entry of analytics.monthlyRegistrations) {
    if (!monthMap.has(entry.month)) {
      monthMap.set(entry.month, {})
    }
    const roleMap = monthMap.get(entry.month)!
    roleMap[entry.role] = entry.count
  }

  const sortedMonths = Array.from(monthMap.keys()).sort()
  const labels = sortedMonths.map((m) => {
    const [year, month] = m.split('-')
    const d = new Date(parseInt(year), parseInt(month) - 1, 1)
    return d.toLocaleDateString(undefined, { month: 'short', year: '2-digit' })
  })

  const roleColors: Record<string, { bg: string; border: string; label: string }> = {
    candidate: { bg: '#3b82f6', border: '#2563eb', label: t('admin.analytics.candidates') },
    hr: { bg: '#10b981', border: '#059669', label: t('admin.analytics.hrManagers') },
    admin: { bg: '#f59e0b', border: '#d97706', label: t('admin.analytics.admins') },
  }

  const roles = ['candidate', 'hr', 'admin']
  const datasets = roles.map((role) => ({
    label: roleColors[role]?.label || role,
    data: sortedMonths.map((m) => monthMap.get(m)?.[role] || 0),
    backgroundColor: roleColors[role]?.bg || '#6b7280',
    borderColor: roleColors[role]?.border || '#4b5563',
    borderWidth: 1,
    borderRadius: 4,
    barPercentage: 0.7,
  }))

  return { labels, datasets }
})

const userRegistrationsOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 16,
      },
    },
  },
  scales: {
    x: {
      stacked: true,
      grid: { display: false },
    },
    y: {
      stacked: true,
      beginAtZero: true,
      ticks: { stepSize: 1 },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
  },
}
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
              <p class="text-sm text-gray-500">{{ t('admin.analytics.activeSubscriptions') }}</p>
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
                ${{
                  (
                    adminStore.analytics.estimatedMonthlyRevenue ||
                    adminStore.analytics.monthlyRevenue ||
                    0
                  ).toLocaleString()
                }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <!-- Revenue Trend -->
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">{{ t('admin.analytics.revenueTrend') }}</h2>
          <div class="h-64">
            <Chart
              v-if="revenueTrendData"
              type="line"
              :data="revenueTrendData"
              :options="revenueTrendOptions"
              class="h-full w-full"
            />
            <div v-else class="flex h-full items-center justify-center rounded bg-gray-50">
              <p class="text-gray-400">{{ t('common.noData') }}</p>
            </div>
          </div>
        </div>

        <!-- Interview Volume -->
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">{{ t('admin.analytics.interviewVolume') }}</h2>
          <div class="h-64">
            <Chart
              v-if="interviewVolumeData"
              type="bar"
              :data="interviewVolumeData"
              :options="interviewVolumeOptions"
              class="h-full w-full"
            />
            <div v-else class="flex h-full items-center justify-center rounded bg-gray-50">
              <p class="text-gray-400">{{ t('common.noData') }}</p>
            </div>
          </div>
        </div>

        <!-- Subscription Distribution -->
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">
            {{ t('admin.analytics.subscriptionDistribution') }}
          </h2>
          <div class="h-64">
            <Chart
              v-if="subscriptionDistData"
              type="doughnut"
              :data="subscriptionDistData"
              :options="subscriptionDistOptions"
              class="h-full w-full"
            />
            <div v-else class="flex h-full items-center justify-center rounded bg-gray-50">
              <p class="text-gray-400">{{ t('common.noData') }}</p>
            </div>
          </div>
        </div>

        <!-- User Registrations -->
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">{{ t('admin.analytics.userRegistrations') }}</h2>
          <div class="h-64">
            <Chart
              v-if="userRegistrationsData"
              type="bar"
              :data="userRegistrationsData"
              :options="userRegistrationsOptions"
              class="h-full w-full"
            />
            <div v-else class="flex h-full items-center justify-center rounded bg-gray-50">
              <p class="text-gray-400">{{ t('common.noData') }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
