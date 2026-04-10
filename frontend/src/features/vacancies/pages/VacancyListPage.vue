<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyCard from '../components/VacancyCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { VacancyStatus } from '../types/vacancy.types'

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
  if (activeTab.value === 'archived') return vacancyStore.vacancies.filter(v => v.status === 'archived')
  const active = vacancyStore.vacancies.filter(v => v.status !== 'archived')
  return statusFilter.value ? active.filter(v => v.status === statusFilter.value) : active
})

const activeCount = computed(() => vacancyStore.vacancies.filter(v => v.status !== 'archived').length)
const archivedCount = computed(() => vacancyStore.vacancies.filter(v => v.status === 'archived').length)

onMounted(() => { vacancyStore.fetchVacancies() })

function onStatusChange(): void { localStorage.setItem('vacancy_status_filter', String(statusFilter.value)) }

function confirmDelete(event: Event, id: string, title: string): void {
  event.stopPropagation()
  confirm.require({
    message: `Are you sure you want to permanently delete "${title}"? This action cannot be undone.`,
    header: t('vacancies.deleteConfirmHeader'), icon: 'pi pi-trash',
    rejectLabel: t('common.cancel'), acceptLabel: t('common.delete'), acceptClass: 'p-button-danger',
    accept: async () => { await vacancyStore.deleteVacancy(id) },
  })
}

async function handleStatusChange(_event: Event, id: string, status: VacancyStatus): Promise<void> {
  await vacancyStore.changeStatus(id, status).catch(() => {})
}
</script>

<template>
  <div>
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-lg font-bold text-gray-900 md:text-xl">{{ t('vacancies.title') }}</h1>
        <p class="mt-0.5 text-sm text-gray-500">{{ t('vacancies.shown', { count: filteredVacancies.length }) }}</p>
      </div>
      <Button :label="t('vacancies.create')" icon="pi pi-plus" size="small" @click="router.push({ name: ROUTE_NAMES.VACANCY_CREATE })" />
    </div>

    <div class="mb-4 flex items-center gap-2">
      <div class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-0.5">
        <button class="rounded-md px-4 py-1.5 text-sm font-medium transition-colors" :class="activeTab === 'active' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'" @click="activeTab = 'active'">{{ t('vacancies.active') }} <span class="ml-1 text-xs text-gray-400">({{ activeCount }})</span></button>
        <button class="rounded-md px-4 py-1.5 text-sm font-medium transition-colors" :class="activeTab === 'archived' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'" @click="activeTab = 'archived'">{{ t('vacancies.status.archived') }} <span class="ml-1 text-xs text-gray-400">({{ archivedCount }})</span></button>
      </div>
      <Dropdown v-if="activeTab === 'active'" v-model="statusFilter" :options="statusOptions" option-label="label" option-value="value" :placeholder="t('common.filter')" class="w-full sm:w-44" @change="onStatusChange" />
    </div>

    <p v-if="vacancyStore.error" class="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{{ vacancyStore.error }}</p>

    <div v-if="vacancyStore.loading" class="flex items-center justify-center py-20"><i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i></div>

    <div v-else-if="filteredVacancies.length > 0" class="space-y-3">
      <VacancyCard v-for="vacancy in filteredVacancies" :key="vacancy.id" :vacancy="vacancy" @click="(id) => router.push({ name: ROUTE_NAMES.VACANCY_DETAIL, params: { id } })" @delete="confirmDelete" @status-change="handleStatusChange" />
    </div>

    <div v-else class="flex flex-col items-center rounded-xl border border-dashed border-gray-200 px-4 py-12 text-center md:py-16">
      <div class="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100"><i class="pi pi-briefcase text-2xl text-gray-400"></i></div>
      <template v-if="activeTab === 'archived'">
        <p class="mt-4 text-sm font-medium text-gray-600">{{ t('vacancies.noArchivedVacancies') }}</p>
        <p class="mt-1 text-sm text-gray-400">{{ t('vacancies.noArchivedVacanciesHint') }}</p>
      </template>
      <template v-else>
        <p class="mt-4 text-sm font-medium text-gray-600">{{ t('vacancies.noVacancies') }}</p>
        <p class="mt-1 text-sm text-gray-400">{{ t('vacancies.noVacanciesHint') }}</p>
        <Button :label="t('vacancies.create')" icon="pi pi-plus" class="mt-4" size="small" @click="router.push({ name: ROUTE_NAMES.VACANCY_CREATE })" />
      </template>
    </div>

    <ConfirmDialog />
  </div>
</template>
