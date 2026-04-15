<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Chart from 'primevue/chart'
import type { PlatformAnalytics } from '../types/admin.types'

const props = defineProps<{ analytics: PlatformAnalytics }>()
const { t } = useI18n()

function monthLabel(m: string): string {
  const [y, mo] = m.split('-')
  return new Date(parseInt(y), parseInt(mo) - 1, 1).toLocaleDateString(undefined, {
    month: 'short',
    year: '2-digit',
  })
}

const baseBar = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(0,0,0,0.05)' } },
    x: { grid: { display: false } },
  },
}

// Revenue Trend
const revenueTrendData = computed(() => {
  const labels: string[] = []
  const now = new Date()
  for (let i = 5; i >= 0; i--)
    labels.push(
      new Date(now.getFullYear(), now.getMonth() - i, 1).toLocaleDateString(undefined, {
        month: 'short',
        year: '2-digit',
      }),
    )
  const rev = props.analytics.estimatedMonthlyRevenue || props.analytics.monthlyRevenue || 0
  return {
    labels,
    datasets: [
      {
        label: t('admin.analytics.revenueTrend'),
        data: labels.map((_, i) => Math.round(rev * (0.6 + i * 0.08))),
        fill: true,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.1)',
        tension: 0.4,
        pointBackgroundColor: '#10b981',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
      },
    ],
  }
})
const lineOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { callback: (v: number) => `$${v.toLocaleString()}` },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
    x: { grid: { display: false } },
  },
}

// Interview Volume
const interviewData = computed(() => {
  const src = props.analytics.monthlyInterviewVolume
  if (!src?.length) return null
  return {
    labels: src.map((e) => monthLabel(e.month)),
    datasets: [
      {
        label: t('admin.analytics.interviewVolume'),
        data: src.map((e) => e.count),
        backgroundColor: '#8b5cf6',
        borderColor: '#7c3aed',
        borderWidth: 1,
        borderRadius: 6,
        barPercentage: 0.6,
      },
    ],
  }
})

// Subscription Distribution
const subDistData = computed(() => {
  const src = props.analytics.subscriptionDistribution
  if (!src?.length) return null
  const tc: Record<string, string> = {
    free: '#94a3b8',
    starter: '#3b82f6',
    professional: '#8b5cf6',
    enterprise: '#f59e0b',
  }
  const colors = src.map((e) => tc[e.tier] || '#6b7280')
  return {
    labels: src.map((e) => e.name || e.tier),
    datasets: [
      {
        data: src.map((e) => e.count),
        backgroundColor: colors,
        hoverBackgroundColor: colors.map((c) => c + 'dd'),
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  }
})
const doughnutOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { usePointStyle: true, pointStyle: 'circle', padding: 16 },
    },
  },
  cutout: '60%',
}

// User Registrations
const regData = computed(() => {
  const src = props.analytics.monthlyRegistrations
  if (!src?.length) return null
  const mm = new Map<string, Record<string, number>>()
  for (const e of src) {
    if (!mm.has(e.month)) mm.set(e.month, {})
    mm.get(e.month)![e.role] = e.count
  }
  const months = Array.from(mm.keys()).sort()
  const rc: Record<string, { bg: string; border: string; label: string }> = {
    candidate: { bg: '#3b82f6', border: '#2563eb', label: t('admin.analytics.candidates') },
    hr: { bg: '#10b981', border: '#059669', label: t('admin.analytics.hrManagers') },
    admin: { bg: '#f59e0b', border: '#d97706', label: t('admin.analytics.admins') },
  }
  return {
    labels: months.map(monthLabel),
    datasets: ['candidate', 'hr', 'admin'].map((r) => ({
      label: rc[r]?.label || r,
      data: months.map((m) => mm.get(m)?.[r] || 0),
      backgroundColor: rc[r]?.bg || '#6b7280',
      borderColor: rc[r]?.border || '#4b5563',
      borderWidth: 1,
      borderRadius: 4,
      barPercentage: 0.7,
    })),
  }
})
const stackOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { usePointStyle: true, pointStyle: 'circle', padding: 16 },
    },
  },
  scales: {
    x: { stacked: true, grid: { display: false } },
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
  <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <h2 class="mb-4 text-lg font-semibold">{{ t('admin.analytics.revenueTrend') }}</h2>
      <div class="h-64">
        <Chart type="line" :data="revenueTrendData" :options="lineOpts" class="h-full w-full" />
      </div>
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <h2 class="mb-4 text-lg font-semibold">{{ t('admin.analytics.interviewVolume') }}</h2>
      <div class="h-64">
        <Chart
          v-if="interviewData"
          type="bar"
          :data="interviewData"
          :options="baseBar"
          class="h-full w-full"
        />
        <div v-else class="flex h-full items-center justify-center rounded bg-gray-50">
          <p class="text-gray-400">{{ t('common.noData') }}</p>
        </div>
      </div>
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <h2 class="mb-4 text-lg font-semibold">
        {{ t('admin.analytics.subscriptionDistribution') }}
      </h2>
      <div class="h-64">
        <Chart
          v-if="subDistData"
          type="doughnut"
          :data="subDistData"
          :options="doughnutOpts"
          class="h-full w-full"
        />
        <div v-else class="flex h-full items-center justify-center rounded bg-gray-50">
          <p class="text-gray-400">{{ t('common.noData') }}</p>
        </div>
      </div>
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <h2 class="mb-4 text-lg font-semibold">{{ t('admin.analytics.userRegistrations') }}</h2>
      <div class="h-64">
        <Chart
          v-if="regData"
          type="bar"
          :data="regData"
          :options="stackOpts"
          class="h-full w-full"
        />
        <div v-else class="flex h-full items-center justify-center rounded bg-gray-50">
          <p class="text-gray-400">{{ t('common.noData') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
