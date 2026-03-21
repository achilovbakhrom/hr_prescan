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
  { label: 'Closed', value: 'closed' },
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
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-gray-900">Vacancies</h1>
        <p class="mt-0.5 text-sm text-gray-500">{{ vacancyStore.vacancies.length }} total</p>
      </div>
      <Button label="New Vacancy" icon="pi pi-plus" size="small" @click="navigateToCreate" />
    </div>

    <!-- Filters -->
    <div class="mb-4 flex items-center gap-3">
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        placeholder="Filter by status"
        class="w-44"
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
        class="flex cursor-pointer items-center justify-between rounded-xl border border-gray-100 bg-white px-5 py-4 transition-all hover:border-gray-200 hover:shadow-sm"
        @click="navigateToDetail(vacancy.id)"
      >
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-3">
            <h3 class="text-sm font-semibold text-gray-900">{{ vacancy.title }}</h3>
            <VacancyStatusBadge :status="vacancy.status" />
          </div>
          <div class="mt-1.5 flex items-center gap-4 text-xs text-gray-500">
            <span v-if="vacancy.location"><i class="pi pi-map-marker mr-1"></i>{{ vacancy.location }}</span>
            <span v-if="vacancy.isRemote" class="text-blue-600">Remote</span>
            <span><i class="pi pi-calendar mr-1"></i>{{ formatDate(vacancy.createdAt) }}</span>
          </div>
        </div>
        <div class="ml-4 flex items-center gap-4 text-right">
          <div class="flex items-center gap-1.5 rounded-lg bg-blue-50 px-2.5 py-1.5">
            <i class="pi pi-users text-xs text-blue-500"></i>
            <span class="text-sm font-semibold text-blue-700">{{ (vacancy as Record<string, unknown>).candidatesTotal ?? 0 }}</span>
            <span class="text-xs text-blue-400">applied</span>
          </div>
          <div class="flex items-center gap-1.5 rounded-lg bg-emerald-50 px-2.5 py-1.5">
            <i class="pi pi-check text-xs text-emerald-500"></i>
            <span class="text-sm font-semibold text-emerald-700">{{ (vacancy as Record<string, unknown>).candidatesInterviewed ?? 0 }}</span>
            <span class="text-xs text-emerald-400">interviewed</span>
          </div>
          <div class="flex items-center gap-1.5 rounded-lg bg-violet-50 px-2.5 py-1.5">
            <i class="pi pi-star text-xs text-violet-500"></i>
            <span class="text-sm font-semibold text-violet-700">{{ (vacancy as Record<string, unknown>).candidatesShortlisted ?? 0 }}</span>
            <span class="text-xs text-violet-400">shortlisted</span>
          </div>
          <i class="pi pi-chevron-right text-sm text-gray-300"></i>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center rounded-xl border border-dashed border-gray-200 py-16 text-center">
      <div class="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100">
        <i class="pi pi-briefcase text-2xl text-gray-400"></i>
      </div>
      <p class="mt-4 text-sm font-medium text-gray-600">No vacancies yet</p>
      <p class="mt-1 text-sm text-gray-400">Create your first vacancy to start receiving applications</p>
      <Button label="Create Vacancy" icon="pi pi-plus" class="mt-4" size="small" @click="navigateToCreate" />
    </div>
  </div>
</template>
