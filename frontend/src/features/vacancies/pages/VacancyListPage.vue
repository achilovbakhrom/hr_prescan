<script setup lang="ts">
/**
 * VacancyListPage — HR vacancy list.
 * DataTable (solid rows) inside a GlassSurface toolbar + glass-paginated.
 * Preserves one-directional state transitions (no archive/unarchive here).
 * Spec: docs/design/spec.md §9 Vacancies block.
 */
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import VacancyListTable from '../components/VacancyListTable.vue'
import VacancyListToolbar from '../components/VacancyListToolbar.vue'
import VacancyTableView from '../components/VacancyTableView.vue'
import { useVacancyStore } from '../stores/vacancy.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { VacancyStatus } from '../types/vacancy.types'

const { t } = useI18n()
const router = useRouter()
const vacancyStore = useVacancyStore()
const confirm = useConfirm()

type TabKey = 'active' | 'archived'
const activeTab = ref<TabKey>('active')
const viewMode = ref<'grid' | 'table'>('grid')
const statusFilter = ref<string | null>(null)
const sortOrder = ref<'newest' | 'oldest'>('newest')

const statusOptions = computed(() => [
  { label: t('vacancies.allStatuses'), value: null },
  { label: t('vacancies.status.draft'), value: 'draft' },
  { label: t('vacancies.status.published'), value: 'published' },
  { label: t('vacancies.status.paused'), value: 'paused' },
])

const sortOptions = computed<Array<{ label: string; value: 'newest' | 'oldest' }>>(() => [
  { label: t('candidates.ordering.newest'), value: 'newest' },
  { label: t('candidates.ordering.oldest'), value: 'oldest' },
])

const filteredVacancies = computed(() => {
  const list =
    activeTab.value === 'archived'
      ? vacancyStore.vacancies.filter((v) => v.status === 'archived')
      : vacancyStore.vacancies
          .filter((v) => v.status !== 'archived')
          .filter((v) => !statusFilter.value || v.status === statusFilter.value)
  const sorted = [...list].sort((a, b) => {
    const diff = new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    return sortOrder.value === 'newest' ? diff : -diff
  })
  return sorted
})

const activeCount = computed(
  () => vacancyStore.vacancies.filter((v) => v.status !== 'archived').length,
)
const archivedCount = computed(
  () => vacancyStore.vacancies.filter((v) => v.status === 'archived').length,
)

onMounted(() => {
  const saved = localStorage.getItem('vacancy_status_filter')
  statusFilter.value = saved && saved !== 'null' ? saved : null
  vacancyStore.fetchVacancies()
})

function onStatusChange(): void {
  localStorage.setItem('vacancy_status_filter', String(statusFilter.value))
}

function openDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.VACANCY_DETAIL, params: { id } })
}

function confirmDelete(event: Event, id: string, title: string): void {
  event.stopPropagation()
  confirm.require({
    message: t('vacancies.deleteConfirmMessage', { title }),
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

async function handleStatusChange(_event: Event, id: string, status: VacancyStatus): Promise<void> {
  await vacancyStore.changeStatus(id, status).catch(() => {})
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
          {{ t('vacancies.title') }}
        </h1>
        <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
          {{ t('vacancies.shown', { count: filteredVacancies.length }) }}
        </p>
      </div>
      <Button
        :label="t('vacancies.create')"
        icon="pi pi-plus"
        @click="router.push({ name: ROUTE_NAMES.VACANCY_CREATE })"
      />
    </div>

    <!-- Glass toolbar: tabs + filters -->
    <GlassSurface
      class="flex flex-col gap-2 rounded-lg p-2 sm:flex-row sm:items-center sm:gap-3"
      level="1"
    >
      <VacancyListToolbar
        v-model:active-tab="activeTab"
        v-model:view-mode="viewMode"
        v-model:status-filter="statusFilter"
        v-model:sort-order="sortOrder"
        :status-options="statusOptions"
        :sort-options="sortOptions"
        :active-count="activeCount"
        :archived-count="archivedCount"
        @status-change="onStatusChange"
      />
    </GlassSurface>

    <p
      v-if="vacancyStore.error"
      class="rounded-lg border border-[color:var(--color-danger)] bg-[color:var(--color-danger)]/10 px-4 py-2 text-sm text-[color:var(--color-danger)]"
    >
      {{ vacancyStore.error }}
    </p>

    <VacancyTableView
      v-if="viewMode === 'table'"
      :vacancies="filteredVacancies"
      :loading="vacancyStore.loading"
      @open="openDetail"
      @delete="confirmDelete"
      @status-change="handleStatusChange"
    />
    <VacancyListTable
      v-else
      :vacancies="filteredVacancies"
      :loading="vacancyStore.loading"
      @open="openDetail"
      @delete="confirmDelete"
      @status-change="handleStatusChange"
    />

    <ConfirmDialog />
  </div>
</template>
