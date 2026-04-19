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
import Dropdown from 'primevue/dropdown'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import VacancyListTable from '../components/VacancyListTable.vue'
import { useVacancyStore } from '../stores/vacancy.store'
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
const sortOrder = ref<'newest' | 'oldest'>('newest')

const statusOptions = computed(() => [
  { label: t('vacancies.allStatuses'), value: null },
  { label: t('vacancies.status.draft'), value: 'draft' },
  { label: t('vacancies.status.published'), value: 'published' },
  { label: t('vacancies.status.paused'), value: 'paused' },
])

const sortOptions = computed(() => [
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

onMounted(() => vacancyStore.fetchVacancies())

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
      <div
        class="inline-flex rounded-md bg-[color:var(--color-surface-sunken)] p-0.5"
        role="tablist"
      >
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="
            activeTab === 'active'
              ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
              : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
          "
          role="tab"
          :aria-selected="activeTab === 'active'"
          @click="activeTab = 'active'"
        >
          {{ t('vacancies.active') }}
          <span class="ml-1 text-xs text-[color:var(--color-text-muted)]">({{ activeCount }})</span>
        </button>
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="
            activeTab === 'archived'
              ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
              : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
          "
          role="tab"
          :aria-selected="activeTab === 'archived'"
          @click="activeTab = 'archived'"
        >
          {{ t('vacancies.status.archived') }}
          <span class="ml-1 text-xs text-[color:var(--color-text-muted)]"
            >({{ archivedCount }})</span
          >
        </button>
      </div>
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
      <Dropdown
        v-model="sortOrder"
        :options="sortOptions"
        option-label="label"
        option-value="value"
        class="w-full sm:w-40"
      />
    </GlassSurface>

    <p
      v-if="vacancyStore.error"
      class="rounded-lg border border-[color:var(--color-danger)] bg-[color:var(--color-danger)]/10 px-4 py-2 text-sm text-[color:var(--color-danger)]"
    >
      {{ vacancyStore.error }}
    </p>

    <GlassCard class="!p-0 overflow-hidden">
      <VacancyListTable
        :vacancies="filteredVacancies"
        :loading="vacancyStore.loading"
        @open="openDetail"
        @delete="confirmDelete"
        @status-change="handleStatusChange"
      />
    </GlassCard>

    <ConfirmDialog />
  </div>
</template>
