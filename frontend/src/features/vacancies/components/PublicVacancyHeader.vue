<script setup lang="ts">
/**
 * PublicVacancyHeader — the glass header block on PublicVacancyDetailPage.
 *
 * Extracted to keep the page under 200 lines.
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import GlassCard from '@/shared/components/GlassCard.vue'
import {
  EMPLOYMENT_LABELS,
  EXPERIENCE_LABELS,
  formatSalaryRange,
  formatDate,
} from '../composables/useVacancyLabels'
import type { Vacancy } from '../types/vacancy.types'
import type { Company } from '@/features/companies/types/company.types'

interface VacancyWithCompany extends Vacancy {
  company?: Company
  companyName?: string | null
}

defineProps<{
  vacancy: VacancyWithCompany
}>()

const emit = defineEmits<{
  apply: []
}>()

const { t } = useI18n()

function shouldShowExternalLink(vacancy: VacancyWithCompany): boolean {
  return (
    vacancy.contentSource === 'parsed' &&
    vacancy.canApply === false &&
    vacancy.hasContactInfo !== true &&
    !!vacancy.externalUrl
  )
}
</script>

<template>
  <GlassCard class="mb-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div class="min-w-0 flex-1">
        <h1 class="text-2xl font-semibold text-[color:var(--color-text-primary)] sm:text-3xl">
          {{ vacancy.title }}
        </h1>
        <p
          v-if="vacancy.company?.name || vacancy.companyName"
          class="mt-1 text-sm text-[color:var(--color-text-secondary)] sm:text-base"
        >
          <i class="pi pi-building mr-1"></i>
          {{ vacancy.company?.name || vacancy.companyName }}
        </p>
        <div
          class="mt-3 flex flex-wrap items-center gap-2 text-xs text-[color:var(--color-text-muted)] sm:gap-3 sm:text-sm"
        >
          <span v-if="vacancy.location" class="inline-flex items-center gap-1">
            <i class="pi pi-map-marker text-[10px]"></i>{{ vacancy.location }}
          </span>
          <Tag
            v-if="vacancy.isRemote"
            :value="t('vacancies.overview.remote')"
            severity="info"
            class="!text-[10px] sm:!text-xs"
          />
          <span class="inline-flex items-center gap-1">
            <i class="pi pi-briefcase text-[10px]"></i>
            {{ EMPLOYMENT_LABELS[vacancy.employmentType] || vacancy.employmentType }}
          </span>
          <span class="inline-flex items-center gap-1">
            <i class="pi pi-star text-[10px]"></i>
            {{ EXPERIENCE_LABELS[vacancy.experienceLevel] || vacancy.experienceLevel }}
          </span>
          <span class="inline-flex items-center gap-1">
            <i class="pi pi-calendar text-[10px]"></i>
            <span class="font-mono">{{ formatDate(vacancy.createdAt) }}</span>
          </span>
        </div>

        <p
          v-if="formatSalaryRange(vacancy, t) !== t('vacancies.overview.salaryNotSpecified')"
          class="mt-3 inline-flex items-center rounded-md bg-[color:var(--color-accent-celebrate-soft)] px-2.5 py-1 font-mono text-sm font-semibold text-[color:var(--color-accent-celebrate)]"
        >
          {{ formatSalaryRange(vacancy, t) }}
        </p>
      </div>

      <div class="hidden sm:block">
        <Button
          v-if="vacancy.canApply !== false"
          :label="t('jobBoard.apply')"
          icon="pi pi-send"
          size="large"
          @click="emit('apply')"
        />
        <a
          v-else-if="shouldShowExternalLink(vacancy)"
          :href="vacancy.externalUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 rounded-md bg-[color:var(--color-accent)] px-4 py-3 text-sm font-semibold text-white shadow-sm ease-ios transition-colors hover:bg-[color:var(--color-accent-hover)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--color-border-ring)]"
        >
          <i class="pi pi-external-link text-xs"></i>
          {{ t('jobBoard.openSource') }}
        </a>
      </div>
    </div>

    <div
      v-if="vacancy.skills.length > 0"
      class="mt-5 flex flex-wrap gap-1.5 border-t border-[color:var(--color-border-soft)] pt-4 sm:gap-2"
    >
      <Tag v-for="skill in vacancy.skills" :key="skill" :value="skill" severity="secondary" />
    </div>
  </GlassCard>
</template>
