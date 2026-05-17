<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import ProgressBar from 'primevue/progressbar'
import GlassCard from '@/shared/components/GlassCard.vue'
import type { VacancyPerformance } from '../types/analytics.types'

defineProps<{
  vacancies: VacancyPerformance[]
}>()

const { t } = useI18n()

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
  <GlassCard>
    <template #header>
      <h2
        class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('analytics.vacancyPerformance') }}
      </h2>
    </template>
    <div v-if="vacancies.length > 0" class="overflow-x-auto">
      <DataTable :value="vacancies" :rows="5" class="min-w-[820px] text-sm" striped-rows>
        <Column field="title" :header="t('analytics.table.vacancy')" class="max-w-[200px] truncate">
          <template #body="{ data }">
            <span class="font-medium text-[color:var(--color-text-primary)]" :title="data.title">{{
              data.title
            }}</span>
          </template>
        </Column>
        <Column field="appCount" :header="t('analytics.table.applications')" style="width: 100px">
          <template #body="{ data }">
            <span class="font-mono font-semibold text-[color:var(--color-text-secondary)]">
              {{ data.appCount }}
            </span>
          </template>
        </Column>
        <Column
          field="interviewedCount"
          :header="t('analytics.funnel.interviewed')"
          style="width: 100px"
        >
          <template #body="{ data }">
            <span class="font-mono font-semibold text-[color:var(--color-text-secondary)]">
              {{ data.interviewedCount }}
            </span>
          </template>
        </Column>
        <Column field="hiredCount" :header="t('analytics.funnel.hired')" style="width: 90px">
          <template #body="{ data }">
            <span class="font-mono font-semibold text-[color:var(--color-text-secondary)]">
              {{ data.hiredCount }}
            </span>
          </template>
        </Column>
        <Column field="hireRate" :header="`${t('analytics.funnel.hired')} %`" style="width: 90px">
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
              <span class="font-mono text-sm text-[color:var(--color-text-secondary)]">
                {{ formatScore(data.avgScore) }}
              </span>
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
</template>
