<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { vacancyService } from '../services/vacancy.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { EMPLOYMENT_LABELS, EXPERIENCE_LABELS, formatSalaryRange } from '../composables/useVacancyLabels'
import type { Vacancy } from '../types/vacancy.types'

const { t } = useI18n()
const router = useRouter()
const jobs = ref<Vacancy[]>([])
const loading = ref(false)

// Filters
const search = ref('')
const locationFilter = ref('')
const employmentType = ref<string | null>(null)
const experienceLevel = ref<string | null>(null)
const remoteOnly = ref(false)

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
  return count
})

let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch([search, locationFilter], () => {
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
      <div class="mx-auto max-w-6xl px-6 py-8">
        <h1 class="mb-1 text-2xl font-bold text-gray-900">{{ t('jobBoard.title') }}</h1>
        <p class="mb-5 text-sm text-gray-500">{{ jobs.length }} open positions</p>

        <div class="flex gap-3">
          <IconField class="flex-1">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="search"
              class="w-full"
              :placeholder="t('jobBoard.searchPlaceholder')"
              @keyup.enter="fetchJobs"
            />
          </IconField>
          <IconField class="w-52">
            <InputIcon class="pi pi-map-marker" />
            <InputText
              v-model="locationFilter"
              class="w-full"
              :placeholder="t('jobBoard.locationPlaceholder')"
              @keyup.enter="fetchJobs"
            />
          </IconField>
          <Button :label="t('common.search')" icon="pi pi-search" :loading="loading" @click="fetchJobs" />
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="mx-auto max-w-6xl px-6 py-6">
      <div class="flex gap-6">
        <!-- Sidebar Filters -->
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
          </div>
        </aside>

        <!-- Mobile filter chips -->
        <div class="mb-4 flex flex-wrap gap-2 lg:hidden">
          <button
            class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
            :class="remoteOnly ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-600'"
            @click="toggleRemote"
          >
            {{ t('vacancies.overview.remote') }}
          </button>
          <button
            v-for="opt in employmentOptions" :key="opt.value"
            class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
            :class="employmentType === opt.value ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-600'"
            @click="toggleEmploymentType(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>

        <!-- Job Listings -->
        <div class="min-w-0 flex-1">
          <!-- Loading -->
          <div v-if="loading" class="flex items-center justify-center py-20">
            <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
          </div>

          <!-- Results -->
          <div v-else-if="jobs.length > 0" class="space-y-3">
            <div
              v-for="job in jobs" :key="job.id"
              class="group cursor-pointer rounded-xl border border-gray-100 bg-white p-5 transition-all hover:border-blue-200 hover:shadow-md"
              @click="navigateToDetail(job.id)"
            >
              <!-- Top row -->
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0 flex-1">
                  <h2 class="text-base font-semibold text-gray-900 group-hover:text-blue-600">
                    {{ job.title }}
                  </h2>
                  <p v-if="(job as Record<string, unknown>).companyName" class="mt-0.5 text-sm text-gray-500">
                    {{ (job as Record<string, unknown>).companyName }}
                  </p>
                </div>
                <span
                  v-if="formatSalaryRange(job) !== 'Not specified'"
                  class="shrink-0 rounded-lg bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700"
                >
                  {{ formatSalaryRange(job) }}
                </span>
              </div>

              <!-- Tags row -->
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <span v-if="job.location" class="flex items-center gap-1 text-sm text-gray-500">
                  <i class="pi pi-map-marker text-xs"></i>{{ job.location }}
                </span>
                <Tag v-if="job.isRemote" :value="t('vacancies.overview.remote')" severity="info" class="text-xs" />
                <span class="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                  {{ EMPLOYMENT_LABELS[job.employmentType] || job.employmentType }}
                </span>
                <span class="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                  {{ EXPERIENCE_LABELS[job.experienceLevel] || job.experienceLevel }}
                </span>
              </div>

              <!-- Description -->
              <p class="mt-2.5 line-clamp-2 text-sm leading-relaxed text-gray-500">
                {{ job.description }}
              </p>

              <!-- Skills + date -->
              <div class="mt-3 flex items-center justify-between">
                <div v-if="job.skills?.length" class="flex flex-wrap gap-1.5">
                  <span
                    v-for="skill in job.skills.slice(0, 4)" :key="skill"
                    class="rounded-md bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-600"
                  >
                    {{ skill }}
                  </span>
                  <span v-if="job.skills.length > 4" class="rounded-md bg-gray-50 px-2 py-0.5 text-xs text-gray-400">
                    +{{ job.skills.length - 4 }}
                  </span>
                </div>
                <span class="shrink-0 text-xs text-gray-400">{{ formatRelativeDate(job.createdAt) }}</span>
              </div>
            </div>
          </div>

          <!-- Empty -->
          <div v-else class="flex flex-col items-center rounded-xl border border-dashed border-gray-200 bg-white py-20 text-center">
            <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
              <i class="pi pi-search text-2xl text-gray-400"></i>
            </div>
            <p class="mt-4 font-medium text-gray-600">{{ t('jobBoard.noJobs') }}</p>
            <p class="mt-1 text-sm text-gray-400">{{ t('jobBoard.noJobsHint') }}</p>
            <Button v-if="activeFilterCount > 0" :label="t('common.clearFilters')" text size="small" class="mt-3" @click="clearFilters" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
