<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import CompanyLogo from '@/shared/components/CompanyLogo.vue'
import {
  EMPLOYMENT_LABELS,
  EXPERIENCE_LABELS,
  formatSalaryRange,
} from '../composables/useVacancyLabels'
import type { Vacancy } from '../types/vacancy.types'

defineProps<{
  jobs: Vacancy[]
  loading: boolean
  activeFilterCount: number
}>()

const emit = defineEmits<{
  select: [id: string]
  clearFilters: []
}>()

const { t } = useI18n()

function stripHtml(html: string): string {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

function getCompanyName(job: Vacancy): string {
  return job.companyName ?? ''
}

function formatRelativeDate(dateStr: string): string {
  const d = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}
</script>

<template>
  <!-- Loading -->
  <div v-if="loading" class="flex items-center justify-center py-20">
    <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
  </div>

  <!-- Results -->
  <div v-else-if="jobs.length > 0" class="space-y-3">
    <div
      v-for="job in jobs"
      :key="job.id"
      class="group cursor-pointer rounded-xl border border-gray-100 bg-white p-4 transition-all hover:border-blue-200 hover:shadow-md sm:p-5"
      @click="emit('select', job.id)"
    >
      <!-- Top row -->
      <div class="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
        <div class="flex min-w-0 flex-1 items-start gap-3">
          <CompanyLogo
            v-if="getCompanyName(job)"
            :logo="job.companyLogo"
            :name="getCompanyName(job)"
            size="md"
          />
          <div class="min-w-0 flex-1">
            <h2 class="text-base font-semibold text-gray-900 group-hover:text-blue-600">
              {{ job.title }}
            </h2>
            <p v-if="getCompanyName(job)" class="mt-0.5 text-sm text-gray-500">
              {{ getCompanyName(job) }}
            </p>
          </div>
        </div>
        <span
          v-if="formatSalaryRange(job, t) !== t('vacancies.overview.salaryNotSpecified')"
          class="self-start rounded-lg bg-emerald-50 px-2.5 py-0.5 text-sm font-semibold text-emerald-700 sm:shrink-0 sm:px-3 sm:py-1"
        >
          {{ formatSalaryRange(job, t) }}
        </span>
      </div>

      <!-- Tags row -->
      <div class="mt-2 flex flex-wrap items-center gap-1.5 sm:mt-3 sm:gap-2">
        <span v-if="job.location" class="flex items-center gap-1 text-xs text-gray-500 sm:text-sm">
          <i class="pi pi-map-marker text-[10px] sm:text-xs"></i>{{ job.location }}
        </span>
        <Tag
          v-if="job.isRemote"
          :value="t('vacancies.overview.remote')"
          severity="info"
          class="!text-[10px] sm:!text-xs"
        />
        <span
          class="rounded-md bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 sm:px-2 sm:text-xs"
        >
          {{ EMPLOYMENT_LABELS[job.employmentType] || job.employmentType }}
        </span>
        <span
          class="rounded-md bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 sm:px-2 sm:text-xs"
        >
          {{ EXPERIENCE_LABELS[job.experienceLevel] || job.experienceLevel }}
        </span>
      </div>

      <!-- Description -->
      <p class="mt-2 line-clamp-2 text-xs leading-relaxed text-gray-500 sm:mt-2.5 sm:text-sm">
        {{ stripHtml(job.description) }}
      </p>

      <!-- Skills + date -->
      <div class="mt-2 flex flex-col gap-2 sm:mt-3 sm:flex-row sm:items-center sm:justify-between">
        <div v-if="job.skills?.length" class="flex flex-wrap gap-1 sm:gap-1.5">
          <span
            v-for="skill in job.skills.slice(0, 3)"
            :key="skill"
            class="rounded-md bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-600 sm:px-2 sm:text-xs"
          >
            {{ skill }}
          </span>
          <span
            v-if="job.skills.length > 3"
            class="rounded-md bg-gray-50 px-1.5 py-0.5 text-[10px] text-gray-400 sm:px-2 sm:text-xs"
          >
            +{{ job.skills.length - 3 }}
          </span>
        </div>
        <span class="shrink-0 text-[10px] text-gray-400 sm:text-xs">{{
          formatRelativeDate(job.createdAt)
        }}</span>
      </div>
    </div>
  </div>

  <!-- Empty -->
  <div
    v-else
    class="flex flex-col items-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center sm:py-20"
  >
    <div
      class="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 sm:h-16 sm:w-16"
    >
      <i class="pi pi-search text-xl text-gray-400 sm:text-2xl"></i>
    </div>
    <p class="mt-3 text-sm font-medium text-gray-600 sm:mt-4">{{ t('jobBoard.noJobs') }}</p>
    <p class="mt-1 text-xs text-gray-400 sm:text-sm">{{ t('jobBoard.noJobsHint') }}</p>
    <Button
      v-if="activeFilterCount > 0"
      :label="t('common.clearFilters')"
      text
      size="small"
      class="mt-3"
      @click="emit('clearFilters')"
    />
  </div>
</template>
