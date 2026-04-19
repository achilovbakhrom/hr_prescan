<script setup lang="ts">
/**
 * RecommendedVacancies — card listing jobs the candidate should consider.
 * Glass card chrome, solid rows, tap → job detail.
 */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { RecommendedVacancy } from '../types/dashboard.types'

defineProps<{ vacancies: RecommendedVacancy[] }>()

const router = useRouter()
const { t } = useI18n()

function formatEmploymentType(type: string): string {
  const map: Record<string, string> = {
    full_time: t('vacancies.employment.fullTime'),
    part_time: t('vacancies.employment.partTime'),
    contract: t('vacancies.employment.contract'),
    internship: t('vacancies.employment.internship'),
  }
  return map[type] || type
}
</script>

<template>
  <GlassCard class="lg:col-span-2">
    <template #header>
      <div class="flex items-center justify-between">
        <h2
          class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('dashboard.candidate.recommendedJobs') }}
        </h2>
        <Button
          :label="t('common.viewAll')"
          text
          size="small"
          severity="secondary"
          @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
        />
      </div>
    </template>

    <div v-if="vacancies.length > 0" class="flex flex-col gap-2">
      <div
        v-for="vacancy in vacancies"
        :key="vacancy.id"
        class="flex cursor-pointer items-center justify-between rounded-[--radius-sm] bg-[color:var(--color-surface-raised)] px-4 py-3 transition-colors hover:bg-[color:var(--color-surface-sunken)]"
        @click="router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id: vacancy.id } })"
      >
        <div class="flex items-center gap-3">
          <div
            class="flex h-9 w-9 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-xs font-semibold text-[color:var(--color-accent)]"
          >
            {{ vacancy.companyName?.charAt(0) ?? '?' }}
          </div>
          <div>
            <p class="text-sm font-medium text-[color:var(--color-text-primary)]">
              {{ vacancy.title }}
            </p>
            <p class="text-xs text-[color:var(--color-text-muted)]">
              {{ vacancy.companyName }}
            </p>
          </div>
        </div>
        <div class="text-right">
          <p class="text-sm font-medium text-[color:var(--color-text-secondary)]">
            {{ vacancy.isRemote ? t('vacancies.overview.remote') : vacancy.location }}
          </p>
          <p class="font-mono text-xs text-[color:var(--color-text-muted)]">
            {{ formatEmploymentType(vacancy.employmentType) }}
          </p>
        </div>
      </div>
    </div>

    <div
      v-else
      class="flex flex-col items-center py-8 text-center text-[color:var(--color-text-muted)]"
    >
      <i class="pi pi-briefcase mb-2 text-2xl"></i>
      <p class="text-sm">{{ t('dashboard.candidate.noRecommendations') }}</p>
      <p class="text-xs">{{ t('dashboard.candidate.noRecommendationsHint') }}</p>
    </div>
  </GlassCard>
</template>
