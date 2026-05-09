import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { vacancyService } from '../services/vacancy.service'
import type { Vacancy } from '../types/vacancy.types'

const PAGE_SIZE = 20

export function usePublicJobSearch() {
  const jobs = ref<Vacancy[]>([])
  const loading = ref(false)
  const loadingMore = ref(false)
  const total = ref(0)
  const page = ref(0)

  const search = ref('')
  const locationFilter = ref('')
  const employmentType = ref<string | null>(null)
  const experienceLevel = ref<string | null>(null)
  const remoteOnly = ref(false)
  const salaryMin = ref<number | null>(null)
  const salaryMax = ref<number | null>(null)

  let searchTimeout: ReturnType<typeof setTimeout> | null = null
  let requestToken = 0
  let activeController: AbortController | null = null

  const hasMore = computed(() => jobs.value.length < total.value)
  const jobCount = computed(() => total.value || jobs.value.length)
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

  watch([search, locationFilter, salaryMin, salaryMax], () => {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => void fetchJobs(), 400)
  })

  onBeforeUnmount(() => {
    if (searchTimeout) clearTimeout(searchTimeout)
    activeController?.abort()
  })

  async function fetchJobs(): Promise<void> {
    if (searchTimeout) {
      clearTimeout(searchTimeout)
      searchTimeout = null
    }
    const token = ++requestToken
    activeController?.abort()
    const controller = new AbortController()
    activeController = controller
    loading.value = true
    page.value = 0
    try {
      const response = await vacancyService.getPublicListPage(
        {
          ...filters(),
          page: 1,
          pageSize: PAGE_SIZE,
        },
        controller.signal,
      )
      if (token !== requestToken) return
      jobs.value = response.results
      total.value = response.count
      page.value = 1
    } catch (error) {
      if (isCanceledRequest(error)) return
      if (token !== requestToken) return
      jobs.value = []
      total.value = 0
    } finally {
      if (activeController === controller) activeController = null
      if (token === requestToken) loading.value = false
    }
  }

  async function loadMore(): Promise<void> {
    if (loading.value || loadingMore.value || !hasMore.value) return
    const token = requestToken
    const controller = new AbortController()
    activeController = controller
    loadingMore.value = true
    try {
      const nextPage = page.value + 1
      const response = await vacancyService.getPublicListPage(
        {
          ...filters(),
          page: nextPage,
          pageSize: PAGE_SIZE,
        },
        controller.signal,
      )
      if (token !== requestToken) return
      jobs.value = [...jobs.value, ...response.results]
      total.value = response.count
      page.value = nextPage
    } catch (error) {
      if (!isCanceledRequest(error)) throw error
    } finally {
      if (activeController === controller) activeController = null
      loadingMore.value = false
    }
  }

  function toggleEmploymentType(value: string): void {
    employmentType.value = employmentType.value === value ? null : value
    void fetchJobs()
  }

  function toggleExperienceLevel(value: string): void {
    experienceLevel.value = experienceLevel.value === value ? null : value
    void fetchJobs()
  }

  function toggleRemote(): void {
    remoteOnly.value = !remoteOnly.value
    void fetchJobs()
  }

  function clearFilters(): void {
    search.value = ''
    locationFilter.value = ''
    employmentType.value = null
    experienceLevel.value = null
    remoteOnly.value = false
    salaryMin.value = null
    salaryMax.value = null
    void fetchJobs()
  }

  function filters() {
    return {
      search: search.value || undefined,
      location: locationFilter.value || undefined,
      isRemote: remoteOnly.value ? true : undefined,
      employmentType: employmentType.value ?? undefined,
      experienceLevel: experienceLevel.value ?? undefined,
      salaryMin: salaryMin.value ?? undefined,
      salaryMax: salaryMax.value ?? undefined,
    }
  }

  function isCanceledRequest(error: unknown): boolean {
    return (
      typeof error === 'object' &&
      error !== null &&
      'code' in error &&
      (error as { code?: unknown }).code === 'ERR_CANCELED'
    )
  }

  return {
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
  }
}
