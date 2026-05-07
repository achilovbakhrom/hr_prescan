<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import Button from 'primevue/button'
import JobSearchBar from '../components/JobSearchBar.vue'
import JobFilterSidebar from '../components/JobFilterSidebar.vue'
import JobCardList from '../components/JobCardList.vue'
import { usePublicJobSearch } from '../composables/usePublicJobSearch'

const { t } = useI18n()
const router = useRouter()
const showMobileFilters = ref(false)
const loadMoreTrigger = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

const {
  jobs,
  loading,
  loadingMore,
  hasMore,
  jobCount,
  search,
  locationFilter,
  employmentType,
  experienceLevel,
  remoteOnly,
  salaryMin,
  salaryMax,
  activeFilterCount,
  fetchJobs,
  loadMore,
  toggleEmploymentType,
  toggleExperienceLevel,
  toggleRemote,
  clearFilters,
} = usePublicJobSearch()

onMounted(() => {
  void fetchJobs()
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry?.isIntersecting) void loadMore()
    },
    { rootMargin: '320px' },
  )
  if (loadMoreTrigger.value) observer.observe(loadMoreTrigger.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

function navigateToDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id } })
}
</script>

<template>
  <div class="public-job-board relative">
    <JobSearchBar
      :search="search"
      :location="locationFilter"
      :loading="loading"
      :job-count="jobCount"
      @update:search="search = $event"
      @update:location="locationFilter = $event"
      @submit="fetchJobs"
    />

    <div class="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
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
              class="bg-glass-1 border-glass shadow-glass flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium text-[color:var(--color-text-secondary)] ease-ios transition-colors hover:text-[color:var(--color-text-primary)]"
              @click="showMobileFilters = !showMobileFilters"
            >
              <i class="pi pi-filter text-xs"></i>
              {{ t('common.filters') }}
              <span
                v-if="activeFilterCount > 0"
                class="flex h-5 w-5 items-center justify-center rounded-full bg-[color:var(--color-accent)] font-mono text-[10px] font-bold text-[color:var(--color-text-on-accent)]"
              >
                {{ activeFilterCount }}
              </span>
            </button>
            <button
              v-if="activeFilterCount > 0"
              class="text-xs text-[color:var(--color-accent)] hover:underline"
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
            :loading="loading && jobs.length === 0"
            :active-filter-count="activeFilterCount"
            @select="navigateToDetail"
            @clear-filters="clearFilters"
          />

          <div ref="loadMoreTrigger" class="flex min-h-16 items-center justify-center py-5">
            <i
              v-if="loadingMore"
              class="pi pi-spinner pi-spin text-xl text-[color:var(--color-text-muted)]"
            ></i>
            <Button
              v-else-if="hasMore"
              :label="t('common.showMore')"
              icon="pi pi-chevron-down"
              text
              size="small"
              @click="loadMore"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
