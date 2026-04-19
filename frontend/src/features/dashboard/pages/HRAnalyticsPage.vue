<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressBar from 'primevue/progressbar'
import { useAnalyticsStore } from '../stores/analytics.store'
import AnalyticsStatCards from '../components/AnalyticsStatCards.vue'
import HiringFunnel from '../components/HiringFunnel.vue'

const { t } = useI18n()
const analyticsStore = useAnalyticsStore()

onMounted(() => {
  analyticsStore.fetchAnalytics()
})

const funnel = computed(() => analyticsStore.analytics?.funnel)
const vacancyPerformance = computed(() => analyticsStore.analytics?.vacancyPerformance ?? [])
const insights = computed(() => analyticsStore.analytics?.interviewInsights)

function formatScore(score: number | null): string {
  if (score === null || score === undefined) return '-'
  return score.toFixed(1)
}
</script>

<template>
  <div>
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">{{ t('analytics.title') }}</h1>
      <p class="mt-1 text-sm text-gray-500">{{ t('analytics.subtitle') }}</p>
    </div>

    <div v-if="analyticsStore.loading" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
    </div>
    <div
      v-else-if="analyticsStore.error"
      class="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 p-6 text-center"
    >
      <i class="pi pi-exclamation-triangle mb-2 text-2xl text-red-400"></i>
      <p class="text-sm text-red-600">{{ analyticsStore.error }}</p>
    </div>

    <template v-else-if="analyticsStore.analytics">
      <AnalyticsStatCards
        :total-applications="funnel?.total ?? 0"
        :total-interviews="insights?.total ?? 0"
        :completion-rate="insights?.completionRate ?? 0"
        :average-score="insights?.averageScore ?? null"
      />

      <div class="grid gap-6 lg:grid-cols-2">
        <HiringFunnel :funnel="funnel ?? null" />

        <div class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-6">
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
              <template #body="{ data }"
                ><span class="font-medium text-gray-900" :title="data.title">{{
                  data.title
                }}</span></template
              >
            </Column>
            <Column
              field="appCount"
              :header="t('analytics.table.applications')"
              style="width: 100px"
            >
              <template #body="{ data }"
                ><span class="font-semibold text-gray-700">{{ data.appCount }}</span></template
              >
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
