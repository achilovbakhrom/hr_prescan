<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressBar from 'primevue/progressbar'
import { useAnalyticsStore } from '../stores/analytics.store'

const { t } = useI18n()
const analyticsStore = useAnalyticsStore()

onMounted(() => {
  analyticsStore.fetchAnalytics()
})

const funnel = computed(() => analyticsStore.analytics?.funnel)
const vacancyPerformance = computed(() => analyticsStore.analytics?.vacancyPerformance ?? [])
const insights = computed(() => analyticsStore.analytics?.interviewInsights)

const funnelSteps = computed(() => {
  if (!funnel.value) return []
  const total = funnel.value.total || 1
  return [
    {
      key: 'applied',
      label: t('analytics.funnel.applied'),
      count: funnel.value.applied,
      pct: Math.round((funnel.value.applied / total) * 100),
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-700',
    },
    {
      key: 'prescanned',
      label: t('analytics.funnel.prescanned'),
      count: funnel.value.prescanned,
      pct: Math.round((funnel.value.prescanned / total) * 100),
      color: 'bg-cyan-500',
      bgColor: 'bg-cyan-50',
      textColor: 'text-cyan-700',
    },
    {
      key: 'interviewed',
      label: t('analytics.funnel.interviewed'),
      count: funnel.value.interviewed,
      pct: Math.round((funnel.value.interviewed / total) * 100),
      color: 'bg-violet-500',
      bgColor: 'bg-violet-50',
      textColor: 'text-violet-700',
    },
    {
      key: 'shortlisted',
      label: t('analytics.funnel.shortlisted'),
      count: funnel.value.shortlisted,
      pct: Math.round((funnel.value.shortlisted / total) * 100),
      color: 'bg-amber-500',
      bgColor: 'bg-amber-50',
      textColor: 'text-amber-700',
    },
    {
      key: 'hired',
      label: t('analytics.funnel.hired'),
      count: funnel.value.hired,
      pct: Math.round((funnel.value.hired / total) * 100),
      color: 'bg-emerald-500',
      bgColor: 'bg-emerald-50',
      textColor: 'text-emerald-700',
    },
    {
      key: 'rejected',
      label: t('analytics.funnel.rejected'),
      count: funnel.value.rejected,
      pct: Math.round((funnel.value.rejected / total) * 100),
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
      textColor: 'text-red-700',
    },
  ]
})

function formatScore(score: number | null): string {
  if (score === null || score === undefined) return '-'
  return score.toFixed(1)
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t('analytics.title') }}
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        {{ t('analytics.subtitle') }}
      </p>
    </div>

    <!-- Loading -->
    <div v-if="analyticsStore.loading" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
    </div>

    <!-- Error -->
    <div
      v-else-if="analyticsStore.error"
      class="rounded-xl border border-red-200 bg-red-50 p-6 text-center"
    >
      <i class="pi pi-exclamation-triangle mb-2 text-2xl text-red-400"></i>
      <p class="text-sm text-red-600">{{ analyticsStore.error }}</p>
    </div>

    <!-- Content -->
    <template v-else-if="analyticsStore.analytics">
      <!-- Interview Insights — Stat Cards -->
      <div class="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
              <i class="pi pi-users text-lg text-blue-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ funnel?.total ?? 0 }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.totalApplications') }}</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50">
              <i class="pi pi-video text-lg text-violet-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ insights?.total ?? 0 }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.totalInterviews') }}</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
              <i class="pi pi-check-circle text-lg text-emerald-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ insights?.completionRate ?? 0 }}%</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.completionRate') }}</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
              <i class="pi pi-star text-lg text-amber-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">
              {{ insights?.averageScore !== null ? insights?.averageScore : '-' }}
            </span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.avgInterviewScore') }}</p>
        </div>
      </div>

      <div class="grid gap-6 lg:grid-cols-2">
        <!-- Hiring Funnel -->
        <div class="rounded-xl border border-gray-100 bg-white p-6">
          <h2 class="mb-5 text-sm font-semibold uppercase tracking-wider text-gray-400">
            {{ t('analytics.hiringFunnel') }}
          </h2>

          <div v-if="funnel && funnel.total > 0" class="space-y-4">
            <div v-for="step in funnelSteps" :key="step.key" class="space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">{{ step.label }}</span>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-semibold text-gray-900">{{ step.count }}</span>
                  <span class="text-xs text-gray-400">({{ step.pct }}%)</span>
                </div>
              </div>
              <div class="h-2.5 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="step.color"
                  :style="{ width: `${Math.max(step.pct, 2)}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div v-else class="flex flex-col items-center py-8 text-center">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
              <i class="pi pi-chart-bar text-xl text-gray-400"></i>
            </div>
            <p class="mt-3 text-sm text-gray-500">{{ t('analytics.noData') }}</p>
          </div>
        </div>

        <!-- Vacancy Performance -->
        <div class="rounded-xl border border-gray-100 bg-white p-6">
          <h2 class="mb-5 text-sm font-semibold uppercase tracking-wider text-gray-400">
            {{ t('analytics.vacancyPerformance') }}
          </h2>

          <DataTable
            v-if="vacancyPerformance.length > 0"
            :value="vacancyPerformance"
            :rows="5"
            class="text-sm"
            striped-rows
          >
            <Column
              field="title"
              :header="t('analytics.table.vacancy')"
              class="max-w-[200px] truncate"
            >
              <template #body="{ data }">
                <span class="font-medium text-gray-900" :title="data.title">{{ data.title }}</span>
              </template>
            </Column>
            <Column field="appCount" :header="t('analytics.table.applications')" style="width: 100px">
              <template #body="{ data }">
                <span class="font-semibold text-gray-700">{{ data.appCount }}</span>
              </template>
            </Column>
            <Column field="avgScore" :header="t('analytics.table.avgScore')" style="width: 120px">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <ProgressBar
                    v-if="data.avgScore !== null"
                    :value="Math.round(data.avgScore)"
                    :show-value="false"
                    style="width: 60px; height: 6px"
                  />
                  <span class="text-sm text-gray-600">{{ formatScore(data.avgScore) }}</span>
                </div>
              </template>
            </Column>
          </DataTable>

          <div v-else class="flex flex-col items-center py-8 text-center">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
              <i class="pi pi-briefcase text-xl text-gray-400"></i>
            </div>
            <p class="mt-3 text-sm text-gray-500">{{ t('analytics.noVacancies') }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
