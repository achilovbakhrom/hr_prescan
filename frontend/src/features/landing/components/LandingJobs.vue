<script setup lang="ts">
/**
 * LandingJobs — "Featured Vacancies" showcase. Pulls public vacancies from
 * the existing vacancyService. Each card is solid (data ≠ chrome per the
 * glass rule), but the section header + CTA remain glass-friendly.
 *
 * TEMPORARILY UNMOUNTED (T10 fix pass, 2026-04-19). This section rendered
 * an empty-state because there is no public /api/public/vacancies endpoint
 * yet — the empty state broke the visual rhythm of the landing page. The
 * component is intentionally left in place so it can be re-imported into
 * LandingPage.vue once real public jobs exist. Do NOT git-delete this file.
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import {
  EMPLOYMENT_LABELS,
  formatSalaryRange,
  formatDate,
} from '@/features/vacancies/composables/useVacancyLabels'
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
    /* silent — section degrades to empty state */
  } finally {
    jobsLoading.value = false
  }
})

function goToJobDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id } })
}

function getCompanyName(job: Vacancy): string | undefined {
  return job.companyName ?? undefined
}
</script>

<template>
  <section id="jobs" class="px-4 py-20 sm:px-6 sm:py-24">
    <div class="mx-auto max-w-6xl">
      <!-- Section header -->
      <div
        class="scroll-animate mb-10 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-end"
      >
        <div>
          <h2
            class="mb-2 text-4xl font-semibold tracking-tight text-[color:var(--color-text-primary)] lg:text-5xl"
          >
            {{ t('landing.latestJobs') }}
          </h2>
          <p class="text-base text-[color:var(--color-text-secondary)]">
            {{ t('landing.latestJobsSubtitle') }}
          </p>
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

      <!-- Loading -->
      <div v-if="jobsLoading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
      </div>

      <!-- Job grid (solid cards — glass rule: data stays solid) -->
      <div v-else-if="jobs.length > 0" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <button
          v-for="(job, idx) in jobs.slice(0, 6)"
          :key="job.id"
          type="button"
          class="job-card scroll-animate flex cursor-pointer flex-col gap-3 rounded-[--radius-md] border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-base)] p-5 text-left transition-all duration-300 ease-ios hover:-translate-y-0.5 hover:border-[color:var(--color-accent)] hover:shadow-card focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--color-border-ring)]"
          :class="`scroll-animate-delay-${(idx % 4) + 1}`"
          @click="goToJobDetail(job.id)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <h3 class="truncate text-base font-semibold text-[color:var(--color-text-primary)]">
                {{ job.title }}
              </h3>
              <p
                v-if="getCompanyName(job)"
                class="mt-0.5 truncate text-sm text-[color:var(--color-text-secondary)]"
              >
                <i class="pi pi-building mr-1 text-[10px]"></i>{{ getCompanyName(job) }}
              </p>
            </div>
            <Tag
              v-if="job.isRemote"
              :value="t('landing.remote')"
              severity="info"
              class="shrink-0 text-xs"
            />
          </div>

          <div
            class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[color:var(--color-text-muted)]"
          >
            <span v-if="job.location"
              ><i class="pi pi-map-marker mr-1 text-[10px]"></i>{{ job.location }}</span
            >
            <span
              ><i class="pi pi-briefcase mr-1 text-[10px]"></i
              >{{ EMPLOYMENT_LABELS[job.employmentType] }}</span
            >
          </div>

          <div
            class="mt-auto flex items-center justify-between border-t border-[color:var(--color-border-soft)] pt-3"
          >
            <span
              v-if="formatSalaryRange(job, t) !== t('vacancies.overview.salaryNotSpecified')"
              class="text-sm font-semibold text-[color:var(--color-success)]"
            >
              {{ formatSalaryRange(job, t) }}
            </span>
            <span v-else class="text-xs text-[color:var(--color-text-muted)]">—</span>
            <span class="font-mono text-xs text-[color:var(--color-text-muted)]">
              {{ formatDate(job.createdAt) }}
            </span>
          </div>
        </button>
      </div>

      <!-- Empty state -->
      <div v-else class="bg-glass-1 border-glass rounded-[--radius-lg] py-16 text-center">
        <i class="pi pi-briefcase mb-3 text-4xl text-[color:var(--color-text-muted)]"></i>
        <p class="text-[color:var(--color-text-primary)]">{{ t('landing.noJobsYet') }}</p>
        <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">
          {{ t('landing.noJobsCheckBack') }}
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  .job-card {
    transition:
      border-color 180ms linear,
      box-shadow 180ms linear;
  }
  .job-card:hover {
    transform: none;
  }
}
</style>
