<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyStatusBadge from '../components/VacancyStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()
const vacancyStore = useVacancyStore()
const confirm = useConfirm()

type TabKey = 'active' | 'archived'
const activeTab = ref<TabKey>('active')

const saved = localStorage.getItem('vacancy_status_filter')
const statusFilter = ref<string | null>(saved && saved !== 'null' ? saved : null)
const statusOptions = computed(() => [
  { label: t('vacancies.allStatuses'), value: null },
  { label: t('vacancies.status.draft'), value: 'draft' },
  { label: t('vacancies.status.published'), value: 'published' },
  { label: t('vacancies.status.paused'), value: 'paused' },
])

const filteredVacancies = computed(() => {
  if (activeTab.value === 'archived') {
    return vacancyStore.vacancies.filter(v => v.status === 'archived')
  }
  const active = vacancyStore.vacancies.filter(v => v.status !== 'archived')
  if (statusFilter.value) {
    return active.filter(v => v.status === statusFilter.value)
  }
  return active
})

const activeCount = computed(() => vacancyStore.vacancies.filter(v => v.status !== 'archived').length)
const archivedCount = computed(() => vacancyStore.vacancies.filter(v => v.status === 'archived').length)

onMounted(() => {
  vacancyStore.fetchVacancies()
})

function switchTab(tab: TabKey): void {
  activeTab.value = tab
}

function onStatusChange(): void {
  localStorage.setItem('vacancy_status_filter', String(statusFilter.value))
}

function navigateToCreate(): void {
  router.push({ name: ROUTE_NAMES.VACANCY_CREATE })
}

function navigateToDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.VACANCY_DETAIL, params: { id } })
}

function confirmDelete(event: Event, id: string, title: string): void {
  event.stopPropagation()
  confirm.require({
    message: `Are you sure you want to permanently delete "${title}"? This action cannot be undone.`,
    header: t('vacancies.deleteConfirmHeader'),
    icon: 'pi pi-trash',
    rejectLabel: t('common.cancel'),
    acceptLabel: t('common.delete'),
    acceptClass: 'p-button-danger',
    accept: async () => {
      await vacancyStore.deleteVacancy(id)
    },
  })
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
        <h1 class="text-lg font-bold text-gray-900 md:text-xl">{{ t('vacancies.title') }}</h1>
        <p class="mt-0.5 text-sm text-gray-500">{{ filteredVacancies.length }} shown</p>
      </div>
      <Button :label="t('vacancies.create')" icon="pi pi-plus" size="small" @click="navigateToCreate" />
    </div>

    <!-- Tabs -->
    <div class="mb-4 flex items-center gap-2">
      <div class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-0.5">
        <button
          class="rounded-md px-4 py-1.5 text-sm font-medium transition-colors"
          :class="activeTab === 'active' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          @click="switchTab('active')"
        >
          {{ t('vacancies.active') }}
          <span class="ml-1 text-xs text-gray-400">({{ activeCount }})</span>
        </button>
        <button
          class="rounded-md px-4 py-1.5 text-sm font-medium transition-colors"
          :class="activeTab === 'archived' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          @click="switchTab('archived')"
        >
          {{ t('vacancies.status.archived') }}
          <span class="ml-1 text-xs text-gray-400">({{ archivedCount }})</span>
        </button>
      </div>

      <!-- Status filter (only for Active tab) -->
      <Dropdown
        v-if="activeTab === 'active'"
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('common.filter')"
        class="w-full sm:w-44"
        @change="onStatusChange"
      />
    </div>

    <!-- Loading -->
    <div v-if="vacancyStore.loading" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
    </div>

    <!-- Vacancy Cards -->
    <div v-else-if="filteredVacancies.length > 0" class="space-y-3">
      <div
        v-for="vacancy in filteredVacancies"
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
            <p v-if="(vacancy as any).employerName" class="mt-0.5 text-xs text-gray-500">
              <i class="pi pi-building mr-1"></i>{{ (vacancy as any).employerName }}
            </p>
            <div class="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
              <span v-if="vacancy.location"><i class="pi pi-map-marker mr-1"></i>{{ vacancy.location }}</span>
              <span v-if="vacancy.isRemote" class="text-blue-600">{{ t('vacancies.overview.remote') }}</span>
              <span><i class="pi pi-calendar mr-1"></i>{{ formatDate(vacancy.createdAt) }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <!-- Delete button for archived vacancies -->
            <Button
              v-if="activeTab === 'archived'"
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              @click="confirmDelete($event, vacancy.id, vacancy.title)"
            />
            <i class="pi pi-chevron-right mt-1 hidden text-sm text-gray-300 sm:block"></i>
          </div>
        </div>

        <!-- Stats row -->
        <div class="mt-3 flex flex-wrap gap-2">
          <div class="flex items-center gap-1.5 rounded-lg bg-blue-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
            <i class="pi pi-users text-xs text-blue-500"></i>
            <span class="text-xs font-semibold text-blue-700 sm:text-sm">{{ vacancy.candidatesTotal ?? 0 }}</span>
            <span class="text-[10px] text-blue-400 sm:text-xs">{{ t('vacancies.applied') }}</span>
          </div>
          <div class="flex items-center gap-1.5 rounded-lg bg-emerald-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
            <i class="pi pi-check text-xs text-emerald-500"></i>
            <span class="text-xs font-semibold text-emerald-700 sm:text-sm">{{ vacancy.candidatesInterviewed ?? 0 }}</span>
            <span class="text-[10px] text-emerald-400 sm:text-xs">{{ t('vacancies.interviewed') }}</span>
          </div>
          <div class="flex items-center gap-1.5 rounded-lg bg-violet-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
            <i class="pi pi-star text-xs text-violet-500"></i>
            <span class="text-xs font-semibold text-violet-700 sm:text-sm">{{ vacancy.candidatesShortlisted ?? 0 }}</span>
            <span class="text-[10px] text-violet-400 sm:text-xs">{{ t('vacancies.shortlisted') }}</span>
          </div>
          <div v-if="vacancy.status === 'archived' && (vacancy.candidatesHired ?? 0) > 0" class="flex items-center gap-1.5 rounded-lg bg-amber-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
            <i class="pi pi-verified text-xs text-amber-500"></i>
            <span class="text-xs font-semibold text-amber-700 sm:text-sm">{{ vacancy.candidatesHired }}</span>
            <span class="text-[10px] text-amber-400 sm:text-xs">{{ t('vacancies.hired') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center rounded-xl border border-dashed border-gray-200 px-4 py-12 text-center md:py-16">
      <div class="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100">
        <i class="pi pi-briefcase text-2xl text-gray-400"></i>
      </div>
      <template v-if="activeTab === 'archived'">
        <p class="mt-4 text-sm font-medium text-gray-600">{{ t('vacancies.noArchivedVacancies') }}</p>
        <p class="mt-1 text-sm text-gray-400">Archived vacancies will appear here</p>
      </template>
      <template v-else>
        <p class="mt-4 text-sm font-medium text-gray-600">{{ t('vacancies.noVacancies') }}</p>
        <p class="mt-1 text-sm text-gray-400">{{ t('vacancies.noVacanciesHint') }}</p>
        <Button :label="t('vacancies.create')" icon="pi pi-plus" class="mt-4" size="small" @click="navigateToCreate" />
      </template>
    </div>

    <ConfirmDialog />
  </div>
</template>
