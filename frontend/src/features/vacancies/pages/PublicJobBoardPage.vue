<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { vacancyService } from '../services/vacancy.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { EMPLOYMENT_LABELS, EXPERIENCE_LABELS, formatSalaryRange } from '../composables/useVacancyLabels'
import type { Vacancy } from '../types/vacancy.types'

function stripHtml(html: string): string {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

const { t } = useI18n()
const router = useRouter()
const jobs = ref<Vacancy[]>([])
const loading = ref(false)
const showMobileFilters = ref(false)

// Filters
const search = ref('')
const locationFilter = ref('')
const employmentType = ref<string | null>(null)
const experienceLevel = ref<string | null>(null)
const remoteOnly = ref(false)
const salaryMin = ref<number | null>(null)
const salaryMax = ref<number | null>(null)

const employmentOptions = computed(() => [
  { value: 'full_time', label: t('vacancies.employment.fullTime'), icon: 'pi pi-clock' },
  { value: 'part_time', label: t('vacancies.employment.partTime'), icon: 'pi pi-hourglass' },
  { value: 'contract', label: t('vacancies.employment.contract'), icon: 'pi pi-file' },
  { value: 'internship', label: t('vacancies.employment.internship'), icon: 'pi pi-graduation-cap' },
])

const experienceOptions = computed(() => [
  { value: 'junior', label: t('vacancies.experience.junior') },
  { value: 'middle', label: t('vacancies.experience.middle') },
  { value: 'senior', label: t('vacancies.experience.senior') },
  { value: 'lead', label: t('vacancies.experience.lead') },
  { value: 'director', label: t('vacancies.experience.director') },
])

const activeFilterCount = computed(() => {
  let count = 0
  if (search.value) count++
  if (locationFilter.value) count++
  if (employmentType.value) count++
  if (experienceLevel.value) count++
  if (remoteOnly.value) count++
  if (salaryMin.value !== null) count++
  if (salaryMax.value !== null) count++
  return count
})

let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch([search, locationFilter, salaryMin, salaryMax], () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchJobs, 400)
})

onMounted(() => fetchJobs())

async function fetchJobs(): Promise<void> {
  loading.value = true
  try {
    jobs.value = await vacancyService.getPublicList({
      search: search.value || undefined,
      location: locationFilter.value || undefined,
      isRemote: remoteOnly.value ? true : undefined,
      employmentType: employmentType.value ?? undefined,
      experienceLevel: experienceLevel.value ?? undefined,
      salaryMin: salaryMin.value ?? undefined,
      salaryMax: salaryMax.value ?? undefined,
    })
  } catch { /* silent */ } finally {
    loading.value = false
  }
}

function toggleEmploymentType(value: string): void {
  employmentType.value = employmentType.value === value ? null : value
  fetchJobs()
}

function toggleExperienceLevel(value: string): void {
  experienceLevel.value = experienceLevel.value === value ? null : value
  fetchJobs()
}

function toggleRemote(): void {
  remoteOnly.value = !remoteOnly.value
  fetchJobs()
}

function clearFilters(): void {
  search.value = ''
  locationFilter.value = ''
  employmentType.value = null
  experienceLevel.value = null
  remoteOnly.value = false
  salaryMin.value = null
  salaryMax.value = null
  fetchJobs()
}

function navigateToDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id } })
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
  <div>
    <!-- Search Hero -->
    <div class="border-b border-gray-100 bg-white">
      <div class="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <h1 class="mb-1 text-xl font-bold text-gray-900 sm:text-2xl">{{ t('jobBoard.title') }}</h1>
        <p class="mb-4 text-sm text-gray-500 sm:mb-5">{{ t('jobBoard.openPositions', { count: jobs.length }) }}</p>

        <!-- Search inputs — stacked on mobile, row on sm+ -->
        <div class="flex flex-col gap-2 sm:flex-row sm:gap-3">
          <IconField class="flex-1">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="search"
              class="w-full"
              :placeholder="t('jobBoard.searchPlaceholder')"
              @keyup.enter="fetchJobs"
            />
          </IconField>
          <div class="flex gap-2">
            <IconField class="flex-1 sm:w-48 sm:flex-initial">
              <InputIcon class="pi pi-map-marker" />
              <InputText
                v-model="locationFilter"
                class="w-full"
                :placeholder="t('jobBoard.locationPlaceholder')"
                @keyup.enter="fetchJobs"
              />
            </IconField>
            <span class="shrink-0 sm:hidden">
              <Button icon="pi pi-search" :loading="loading" @click="fetchJobs" />
            </span>
            <span class="hidden shrink-0 sm:inline-flex">
              <Button :label="t('common.search')" icon="pi pi-search" :loading="loading" @click="fetchJobs" />
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="mx-auto max-w-6xl px-4 py-4 sm:px-6 sm:py-6">
      <div class="flex gap-6">
        <!-- Sidebar Filters (desktop) -->
        <aside class="hidden w-56 shrink-0 lg:block">
          <div class="sticky top-4 space-y-6">
            <!-- Active filters -->
            <div v-if="activeFilterCount > 0" class="flex items-center justify-between">
              <span class="text-xs font-medium text-gray-500">{{ activeFilterCount }} {{ t('jobBoard.activeFilters') }}</span>
              <button class="text-xs text-blue-600 hover:underline" @click="clearFilters">{{ t('jobBoard.clearAll') }}</button>
            </div>

            <!-- Remote toggle -->
            <div>
              <button
                class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
                :class="remoteOnly ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100'"
                @click="toggleRemote"
              >
                <i class="pi pi-globe text-sm"></i>
                {{ t('jobBoard.remoteOnly') }}
              </button>
            </div>

            <!-- Employment Type -->
            <div>
              <h3 class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('vacancies.form.employmentType') }}</h3>
              <div class="space-y-1">
                <button
                  v-for="opt in employmentOptions" :key="opt.value"
                  class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors"
                  :class="employmentType === opt.value ? 'bg-blue-50 font-medium text-blue-700' : 'text-gray-600 hover:bg-gray-100'"
                  @click="toggleEmploymentType(opt.value)"
                >
                  <i :class="opt.icon" class="text-xs"></i>
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Experience Level -->
            <div>
              <h3 class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('vacancies.form.experienceLevel') }}</h3>
              <div class="space-y-1">
                <button
                  v-for="opt in experienceOptions" :key="opt.value"
                  class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors"
                  :class="experienceLevel === opt.value ? 'bg-blue-50 font-medium text-blue-700' : 'text-gray-600 hover:bg-gray-100'"
                  @click="toggleExperienceLevel(opt.value)"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Salary Range -->
            <div>
              <h3 class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('jobBoard.salaryRange') }}</h3>
              <div class="space-y-2">
                <InputNumber
                  v-model="salaryMin"
                  :placeholder="t('jobBoard.minSalary')"
                  :min="0"
                  mode="decimal"
                  :use-grouping="true"
                  class="w-full"
                  input-class="w-full text-sm"
                />
                <InputNumber
                  v-model="salaryMax"
                  :placeholder="t('jobBoard.maxSalary')"
                  :min="0"
                  mode="decimal"
                  :use-grouping="true"
                  class="w-full"
                  input-class="w-full text-sm"
                />
              </div>
            </div>
          </div>
        </aside>

        <!-- Job Listings column -->
        <div class="min-w-0 flex-1">
          <!-- Mobile filter bar -->
          <div class="mb-3 flex items-center gap-2 lg:hidden">
            <button
              class="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50"
              @click="showMobileFilters = !showMobileFilters"
            >
              <i class="pi pi-filter text-xs"></i>
              {{ t('common.filters') }}
              <span v-if="activeFilterCount > 0" class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white">
                {{ activeFilterCount }}
              </span>
            </button>
            <button
              v-if="activeFilterCount > 0"
              class="text-xs text-blue-600 hover:underline"
              @click="clearFilters"
            >
              {{ t('jobBoard.clearAll') }}
            </button>
          </div>

          <!-- Mobile filter drawer -->
          <div
            v-if="showMobileFilters"
            class="mb-4 space-y-4 rounded-xl border border-gray-200 bg-white p-4 lg:hidden"
          >
            <!-- Remote -->
            <button
              class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
              :class="remoteOnly ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100'"
              @click="toggleRemote"
            >
              <i class="pi pi-globe text-sm"></i>
              {{ t('jobBoard.remoteOnly') }}
            </button>

            <!-- Employment chips -->
            <div>
              <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('vacancies.form.employmentType') }}</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="opt in employmentOptions" :key="opt.value"
                  class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
                  :class="employmentType === opt.value ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-600'"
                  @click="toggleEmploymentType(opt.value)"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Experience chips -->
            <div>
              <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('vacancies.form.experienceLevel') }}</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="opt in experienceOptions" :key="opt.value"
                  class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
                  :class="experienceLevel === opt.value ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-600'"
                  @click="toggleExperienceLevel(opt.value)"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Salary -->
            <div>
              <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('jobBoard.salaryRange') }}</p>
              <div class="flex gap-2">
                <InputNumber
                  v-model="salaryMin"
                  :placeholder="t('jobBoard.minSalary')"
                  :min="0"
                  mode="decimal"
                  :use-grouping="true"
                  class="flex-1"
                  input-class="w-full text-sm"
                />
                <InputNumber
                  v-model="salaryMax"
                  :placeholder="t('jobBoard.maxSalary')"
                  :min="0"
                  mode="decimal"
                  :use-grouping="true"
                  class="flex-1"
                  input-class="w-full text-sm"
                />
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="loading" class="flex items-center justify-center py-20">
            <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
          </div>

          <!-- Results -->
          <div v-else-if="jobs.length > 0" class="space-y-3">
            <div
              v-for="job in jobs" :key="job.id"
              class="group cursor-pointer rounded-xl border border-gray-100 bg-white p-4 transition-all hover:border-blue-200 hover:shadow-md sm:p-5"
              @click="navigateToDetail(job.id)"
            >
              <!-- Top row -->
              <div class="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
                <div class="min-w-0 flex-1">
                  <h2 class="text-base font-semibold text-gray-900 group-hover:text-blue-600">
                    {{ job.title }}
                  </h2>
                  <p v-if="(job as Record<string, unknown>).employerName || (job as Record<string, unknown>).companyName" class="mt-0.5 text-sm text-gray-500">
                    <i class="pi pi-building mr-1 text-xs"></i>{{ (job as Record<string, unknown>).employerName || (job as Record<string, unknown>).companyName }}
                  </p>
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
                <Tag v-if="job.isRemote" :value="t('vacancies.overview.remote')" severity="info" class="!text-[10px] sm:!text-xs" />
                <span class="rounded-md bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 sm:px-2 sm:text-xs">
                  {{ EMPLOYMENT_LABELS[job.employmentType] || job.employmentType }}
                </span>
                <span class="rounded-md bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 sm:px-2 sm:text-xs">
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
                    v-for="skill in job.skills.slice(0, 3)" :key="skill"
                    class="rounded-md bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-600 sm:px-2 sm:text-xs"
                  >
                    {{ skill }}
                  </span>
                  <span v-if="job.skills.length > 3" class="rounded-md bg-gray-50 px-1.5 py-0.5 text-[10px] text-gray-400 sm:px-2 sm:text-xs">
                    +{{ job.skills.length - 3 }}
                  </span>
                </div>
                <span class="shrink-0 text-[10px] text-gray-400 sm:text-xs">{{ formatRelativeDate(job.createdAt) }}</span>
              </div>
            </div>
          </div>

          <!-- Empty -->
          <div v-else class="flex flex-col items-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center sm:py-20">
            <div class="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 sm:h-16 sm:w-16">
              <i class="pi pi-search text-xl text-gray-400 sm:text-2xl"></i>
            </div>
            <p class="mt-3 text-sm font-medium text-gray-600 sm:mt-4">{{ t('jobBoard.noJobs') }}</p>
            <p class="mt-1 text-xs text-gray-400 sm:text-sm">{{ t('jobBoard.noJobsHint') }}</p>
            <Button v-if="activeFilterCount > 0" :label="t('common.clearFilters')" text size="small" class="mt-3" @click="clearFilters" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
