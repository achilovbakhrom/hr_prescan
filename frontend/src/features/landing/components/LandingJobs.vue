<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import { EMPLOYMENT_LABELS, formatSalaryRange, formatDate } from '@/features/vacancies/composables/useVacancyLabels'
import type { Vacancy } from '@/shared/types/vacancy.types'

const router = useRouter()
const { t } = useI18n()
const jobs = ref<Vacancy[]>([])
const jobsLoading = ref(false)

onMounted(async () => {
  jobsLoading.value = true
  try {
    jobs.value = await vacancyService.getPublicList({})
  } catch {
    /* silent */
  } finally {
    jobsLoading.value = false
  }
})

function goToJobDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id } })
}
</script>

<template>
  <section id="jobs" class="px-6 py-24">
    <div class="mx-auto max-w-5xl">
      <div class="scroll-animate mb-10 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <h2 class="mb-2 text-3xl font-bold tracking-tight text-gray-900">
            {{ t('landing.latestJobs') }}
          </h2>
          <p class="text-gray-500">{{ t('landing.latestJobsSubtitle') }}</p>
        </div>
        <Button
          :label="t('landing.viewAllJobs')"
          icon="pi pi-arrow-right"
          icon-pos="right"
          text
          severity="secondary"
          @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
        />
      </div>

      <!-- Loading state -->
      <div v-if="jobsLoading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
      </div>

      <!-- Jobs list -->
      <div v-else-if="jobs.length > 0" class="space-y-3">
        <div
          v-for="job in jobs.slice(0, 10)"
          :key="job.id"
          class="flex cursor-pointer items-center justify-between rounded-xl border border-gray-100 bg-white p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-gray-200 hover:shadow-lg hover:shadow-gray-100/50"
          @click="goToJobDetail(job.id)"
        >
          <div class="min-w-0 flex-1">
            <h3 class="text-base font-semibold text-gray-900">{{ job.title }}</h3>
            <div class="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
              <span v-if="job.location"><i class="pi pi-map-marker mr-1 text-xs"></i>{{ job.location }}</span>
              <span><i class="pi pi-briefcase mr-1 text-xs"></i>{{ EMPLOYMENT_LABELS[job.employmentType] }}</span>
              <Tag v-if="job.isRemote" :value="t('landing.remote')" severity="info" class="text-xs" />
            </div>
          </div>
          <div class="ml-4 flex flex-col items-end gap-1">
            <span
              v-if="formatSalaryRange(job, t) !== t('vacancies.overview.salaryNotSpecified')"
              class="text-sm font-semibold text-emerald-600"
            >
              {{ formatSalaryRange(job, t) }}
            </span>
            <span class="text-xs text-gray-400">{{ formatDate(job.createdAt) }}</span>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
        <i class="pi pi-briefcase mb-3 text-4xl text-gray-300"></i>
        <p class="text-gray-500">{{ t('landing.noJobsYet') }}</p>
        <p class="mt-1 text-sm text-gray-400">{{ t('landing.noJobsCheckBack') }}</p>
      </div>
    </div>
  </section>
</template>
