<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyStatusBadge from '../components/VacancyStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const vacancyStore = useVacancyStore()

const saved = localStorage.getItem('vacancy_status_filter')
const statusFilter = ref<string | null>(saved && saved !== 'null' ? saved : null)
const statusOptions = [
  { label: 'All Statuses', value: null },
  { label: 'Draft', value: 'draft' },
  { label: 'Published', value: 'published' },
  { label: 'Paused', value: 'paused' },
  { label: 'Archived', value: 'archived' },
]

onMounted(() => {
  const params = statusFilter.value ? { status: statusFilter.value } : undefined
  vacancyStore.fetchVacancies(params)
})

function onStatusChange(): void {
  localStorage.setItem('vacancy_status_filter', String(statusFilter.value))
  const params = statusFilter.value ? { status: statusFilter.value } : undefined
  vacancyStore.fetchVacancies(params)
}

function navigateToCreate(): void {
  router.push({ name: ROUTE_NAMES.VACANCY_CREATE })
}

function navigateToDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.VACANCY_DETAIL, params: { id } })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-lg font-bold text-gray-900 md:text-xl">Vacancies</h1>
        <p class="mt-0.5 text-sm text-gray-500">{{ vacancyStore.vacancies.length }} total</p>
      </div>
      <Button label="New Vacancy" icon="pi pi-plus" size="small" @click="navigateToCreate" />
    </div>

    <!-- Filters -->
    <div class="mb-4">
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        placeholder="Filter by status"
        class="w-full sm:w-44"
        @change="onStatusChange"
      />
    </div>

    <!-- Loading -->
    <div v-if="vacancyStore.loading" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
    </div>

    <!-- Vacancy Cards -->
    <div v-else-if="vacancyStore.vacancies.length > 0" class="space-y-3">
      <div
        v-for="vacancy in vacancyStore.vacancies"
        :key="vacancy.id"
        class="cursor-pointer rounded-xl border border-gray-100 bg-white px-4 py-3 transition-all hover:border-gray-200 hover:shadow-sm md:px-5 md:py-4"
        @click="navigateToDetail(vacancy.id)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <h3 class="text-sm font-semibold text-gray-900">{{ vacancy.title }}</h3>
              <VacancyStatusBadge :status="vacancy.status" />
            </div>
            <div class="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
              <span v-if="vacancy.location"><i class="pi pi-map-marker mr-1"></i>{{ vacancy.location }}</span>
              <span v-if="vacancy.isRemote" class="text-blue-600">Remote</span>
              <span><i class="pi pi-calendar mr-1"></i>{{ formatDate(vacancy.createdAt) }}</span>
            </div>
          </div>
          <i class="pi pi-chevron-right mt-1 hidden text-sm text-gray-300 sm:block"></i>
        </div>

        <!-- Stats row -->
        <div class="mt-3 flex flex-wrap gap-2">
          <div class="flex items-center gap-1.5 rounded-lg bg-blue-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
            <i class="pi pi-users text-xs text-blue-500"></i>
            <span class="text-xs font-semibold text-blue-700 sm:text-sm">{{ (vacancy as Record<string, unknown>).candidatesTotal ?? 0 }}</span>
            <span class="text-[10px] text-blue-400 sm:text-xs">applied</span>
          </div>
          <div class="flex items-center gap-1.5 rounded-lg bg-emerald-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
            <i class="pi pi-check text-xs text-emerald-500"></i>
            <span class="text-xs font-semibold text-emerald-700 sm:text-sm">{{ (vacancy as Record<string, unknown>).candidatesInterviewed ?? 0 }}</span>
            <span class="text-[10px] text-emerald-400 sm:text-xs">interviewed</span>
          </div>
          <div class="flex items-center gap-1.5 rounded-lg bg-violet-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
            <i class="pi pi-star text-xs text-violet-500"></i>
            <span class="text-xs font-semibold text-violet-700 sm:text-sm">{{ (vacancy as Record<string, unknown>).candidatesShortlisted ?? 0 }}</span>
            <span class="text-[10px] text-violet-400 sm:text-xs">shortlisted</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center rounded-xl border border-dashed border-gray-200 px-4 py-12 text-center md:py-16">
      <div class="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100">
        <i class="pi pi-briefcase text-2xl text-gray-400"></i>
      </div>
      <p class="mt-4 text-sm font-medium text-gray-600">No vacancies yet</p>
      <p class="mt-1 text-sm text-gray-400">Create your first vacancy to start receiving applications</p>
      <Button label="Create Vacancy" icon="pi pi-plus" class="mt-4" size="small" @click="navigateToCreate" />
    </div>
  </div>
</template>
