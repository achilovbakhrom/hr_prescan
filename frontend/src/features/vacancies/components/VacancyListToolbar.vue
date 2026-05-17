<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Dropdown from '@/shared/components/AppSelect.vue'

type TabKey = 'active' | 'archived'
type ViewMode = 'grid' | 'table'
type SortOrder = 'newest' | 'oldest'

interface Option {
  label: string
  value: string | null
}

defineProps<{
  activeTab: TabKey
  viewMode: ViewMode
  statusFilter: string | null
  sortOrder: SortOrder
  statusOptions: Option[]
  sortOptions: Array<{ label: string; value: SortOrder }>
  activeCount: number
  archivedCount: number
}>()

const emit = defineEmits<{
  'update:activeTab': [value: TabKey]
  'update:viewMode': [value: ViewMode]
  'update:statusFilter': [value: string | null]
  'update:sortOrder': [value: SortOrder]
  statusChange: []
}>()

const { t } = useI18n()

const tabs: Array<{ key: TabKey; labelKey: string; countKey: 'activeCount' | 'archivedCount' }> = [
  { key: 'active', labelKey: 'vacancies.active', countKey: 'activeCount' },
  { key: 'archived', labelKey: 'vacancies.status.archived', countKey: 'archivedCount' },
]

function onStatusFilterChange(value: unknown): void {
  emit('update:statusFilter', typeof value === 'string' ? value : null)
}

function onSortOrderChange(value: unknown): void {
  emit('update:sortOrder', value === 'oldest' ? 'oldest' : 'newest')
}
</script>

<template>
  <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
    <div class="inline-flex rounded-md bg-[color:var(--color-surface-sunken)] p-0.5" role="tablist">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
        :class="
          activeTab === tab.key
            ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
            : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
        "
        role="tab"
        :aria-selected="activeTab === tab.key"
        @click="emit('update:activeTab', tab.key)"
      >
        {{ t(tab.labelKey) }}
        <span class="ml-1 text-xs text-[color:var(--color-text-muted)]">
          ({{ tab.countKey === 'activeCount' ? activeCount : archivedCount }})
        </span>
      </button>
    </div>
    <Dropdown
      v-if="activeTab === 'active'"
      :model-value="statusFilter"
      :options="statusOptions"
      option-label="label"
      option-value="value"
      :placeholder="t('common.filter')"
      class="w-full sm:w-44"
      @update:model-value="onStatusFilterChange"
      @change="emit('statusChange')"
    />
    <Dropdown
      :model-value="sortOrder"
      :options="sortOptions"
      option-label="label"
      option-value="value"
      class="w-full sm:w-40"
      @update:model-value="onSortOrderChange"
    />
    <div class="inline-flex rounded-md bg-[color:var(--color-surface-sunken)] p-0.5 sm:ml-auto">
      <button
        class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
        :class="
          viewMode === 'grid'
            ? 'bg-[color:var(--color-surface-raised)] shadow-sm'
            : 'text-[color:var(--color-text-muted)]'
        "
        aria-label="Grid"
        @click="emit('update:viewMode', 'grid')"
      >
        <i class="pi pi-th-large"></i>
      </button>
      <button
        class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
        :class="
          viewMode === 'table'
            ? 'bg-[color:var(--color-surface-raised)] shadow-sm'
            : 'text-[color:var(--color-text-muted)]'
        "
        :aria-label="t('candidates.table')"
        @click="emit('update:viewMode', 'table')"
      >
        <i class="pi pi-list"></i>
      </button>
    </div>
  </div>
</template>
