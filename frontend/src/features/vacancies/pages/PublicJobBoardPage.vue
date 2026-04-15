<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import { vacancyService } from '../services/vacancy.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Vacancy } from '../types/vacancy.types'
import JobSearchBar from '../components/JobSearchBar.vue'
import JobFilterSidebar from '../components/JobFilterSidebar.vue'
import JobCardList from '../components/JobCardList.vue'

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
  } catch {
    /* silent */
  } finally {
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
</script>

<template>
  <div>
    <JobSearchBar
      :search="search"
      :location="locationFilter"
      :loading="loading"
      :job-count="jobs.length"
      @update:search="search = $event"
      @update:location="locationFilter = $event"
      @submit="fetchJobs"
    />

    <div class="mx-auto max-w-6xl px-4 py-4 sm:px-6 sm:py-6">
      <div class="flex gap-6">
        <JobFilterSidebar
          :employment-type="employmentType"
          :experience-level="experienceLevel"
          :remote-only="remoteOnly"
          :salary-min="salaryMin"
          :salary-max="salaryMax"
          :active-filter-count="activeFilterCount"
          @toggle-employment="toggleEmploymentType"
          @toggle-experience="toggleExperienceLevel"
          @toggle-remote="toggleRemote"
          @update:salary-min="salaryMin = $event"
          @update:salary-max="salaryMax = $event"
          @clear-filters="clearFilters"
        />

        <div class="min-w-0 flex-1">
          <!-- Mobile filter bar -->
          <div class="mb-3 flex items-center gap-2 lg:hidden">
            <button
              class="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50"
              @click="showMobileFilters = !showMobileFilters"
            >
              <i class="pi pi-filter text-xs"></i>
              {{ t('common.filters') }}
              <span
                v-if="activeFilterCount > 0"
                class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white"
              >
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

          <JobFilterSidebar
            v-if="showMobileFilters"
            :show-mobile="true"
            :employment-type="employmentType"
            :experience-level="experienceLevel"
            :remote-only="remoteOnly"
            :salary-min="salaryMin"
            :salary-max="salaryMax"
            :active-filter-count="activeFilterCount"
            @toggle-employment="toggleEmploymentType"
            @toggle-experience="toggleExperienceLevel"
            @toggle-remote="toggleRemote"
            @update:salary-min="salaryMin = $event"
            @update:salary-max="salaryMax = $event"
            @clear-filters="clearFilters"
          />

          <JobCardList
            :jobs="jobs"
            :loading="loading"
            :active-filter-count="activeFilterCount"
            @select="navigateToDetail"
            @clear-filters="clearFilters"
          />
        </div>
      </div>
    </div>
  </div>
</template>
