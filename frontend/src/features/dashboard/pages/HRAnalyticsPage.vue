<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressBar from 'primevue/progressbar'
import { useAnalyticsStore } from '../stores/analytics.store'
import GlassCard from '@/shared/components/GlassCard.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
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

function numericValue(value: number | string | null | undefined): number | null {
  if (value === null || value === undefined || value === '') return null
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

function formatScore(score: number | string | null): string {
  const numeric = numericValue(score)
  if (numeric === null) return '-'
  return numeric.toFixed(1)
}

function formatPercent(value: number | string | null | undefined): string {
  const numeric = numericValue(value)
  if (numeric === null) return '-'
  return `${Math.round(numeric)}%`
}

function progressValue(value: number | string | null | undefined): number {
  return Math.round(numericValue(value) ?? 0)
}
</script>

<template>
  <div class="mx-auto w-full max-w-[1440px]">
    <!-- Sticky glass toolbar -->
    <GlassSurface
      level="1"
      class="sticky top-4 z-10 mb-6 flex items-center justify-between gap-4 px-5 py-3"
    >
      <div class="min-w-0">
        <p
          class="font-mono text-[11px] uppercase tracking-[0.18em] text-[color:var(--color-text-muted)]"
        >
          {{ t('analytics.title') }}
        </p>
        <h1
          class="truncate text-xl font-semibold text-[color:var(--color-text-primary)] sm:text-2xl"
        >
          {{ t('analytics.subtitle') }}
        </h1>
      </div>
    </GlassSurface>

    <div v-if="analyticsStore.loading" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>
    <GlassCard v-else-if="analyticsStore.error" class="border-[color:var(--color-danger)]">
      <div class="flex flex-col items-center py-6 text-center text-[color:var(--color-danger)]">
        <i class="pi pi-exclamation-triangle mb-2 text-2xl"></i>
        <p class="text-sm">{{ analyticsStore.error }}</p>
      </div>
    </GlassCard>

    <template v-else-if="analyticsStore.analytics">
      <AnalyticsStatCards
        :total-applications="funnel?.total ?? 0"
        :total-interviews="insights?.total ?? 0"
        :completion-rate="insights?.completionRate ?? 0"
        :average-score="insights?.averageScore ?? null"
      />

      <div class="grid gap-6 lg:grid-cols-2">
        <HiringFunnel :funnel="funnel ?? null" />

        <GlassCard>
          <template #header>
            <h2
              class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
            >
              {{ t('analytics.vacancyPerformance') }}
            </h2>
          </template>
          <div v-if="vacancyPerformance.length > 0" class="overflow-x-auto">
            <DataTable
              :value="vacancyPerformance"
              :rows="5"
              class="min-w-[820px] text-sm"
              striped-rows
            >
              <Column
                field="title"
                :header="t('analytics.table.vacancy')"
                class="max-w-[200px] truncate"
              >
                <template #body="{ data }">
                  <span
                    class="font-medium text-[color:var(--color-text-primary)]"
                    :title="data.title"
                    >{{ data.title }}</span
                  >
                </template>
              </Column>
              <Column
                field="appCount"
                :header="t('analytics.table.applications')"
                style="width: 100px"
              >
                <template #body="{ data }">
                  <span class="font-mono font-semibold text-[color:var(--color-text-secondary)]">{{
                    data.appCount
                  }}</span>
                </template>
              </Column>
              <Column
                field="interviewedCount"
                :header="t('analytics.funnel.interviewed')"
                style="width: 100px"
              >
                <template #body="{ data }">
                  <span class="font-mono font-semibold text-[color:var(--color-text-secondary)]">{{
                    data.interviewedCount
                  }}</span>
                </template>
              </Column>
              <Column field="hiredCount" :header="t('analytics.funnel.hired')" style="width: 90px">
                <template #body="{ data }">
                  <span class="font-mono font-semibold text-[color:var(--color-text-secondary)]">{{
                    data.hiredCount
                  }}</span>
                </template>
              </Column>
              <Column
                field="hireRate"
                :header="`${t('analytics.funnel.hired')} %`"
                style="width: 90px"
              >
                <template #body="{ data }">
                  <span class="font-mono text-sm text-[color:var(--color-text-secondary)]">
                    {{ formatPercent(data.hireRate) }}
                  </span>
                </template>
              </Column>
              <Column
                field="rejectionRate"
                :header="`${t('analytics.funnel.rejected')} %`"
                style="width: 90px"
              >
                <template #body="{ data }">
                  <span class="font-mono text-sm text-[color:var(--color-text-secondary)]">
                    {{ formatPercent(data.rejectionRate) }}
                  </span>
                </template>
              </Column>
              <Column field="avgScore" :header="t('analytics.table.avgScore')" style="width: 140px">
                <template #body="{ data }">
                  <div class="flex items-center gap-2">
                    <ProgressBar
                      v-if="data.avgScore !== null"
                      :value="progressValue(data.avgScore)"
                      :show-value="false"
                      style="width: 60px; height: 6px"
                    />
                    <span class="font-mono text-sm text-[color:var(--color-text-secondary)]">{{
                      formatScore(data.avgScore)
                    }}</span>
                  </div>
                </template>
              </Column>
            </DataTable>
          </div>
          <div
            v-else
            class="flex flex-col items-center py-8 text-center text-[color:var(--color-text-muted)]"
          >
            <i class="pi pi-briefcase mb-2 text-2xl"></i>
            <p class="text-sm">{{ t('analytics.noVacancies') }}</p>
          </div>
        </GlassCard>
      </div>
    </template>
  </div>
</template>
