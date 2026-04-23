<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Dropdown from '@/shared/components/AppSelect.vue'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'

defineProps<{
  selectedCandidates: Application[]
}>()
const emit = defineEmits<{
  searchInput: []
  bulkAction: [event: { value: ApplicationStatus }]
}>()
const candidateViewMode = defineModel<'kanban' | 'table'>('viewMode', { required: true })
const statusFilter = defineModel<string | undefined>('statusFilter', { required: true })
const orderingFilter = defineModel<string>('orderingFilter', { required: true })
const searchQuery = defineModel<string>('searchQuery', { required: true })

const { t } = useI18n()
const candidateStore = useCandidateStore()

const statusOptions = computed(() => [
  { label: t('vacancies.allStatuses'), value: undefined },
  { label: t('candidates.status.applied'), value: 'applied' },
  { label: t('candidates.status.prescanned'), value: 'prescanned' },
  { label: t('candidates.status.interviewed'), value: 'interviewed' },
  { label: t('candidates.status.shortlisted'), value: 'shortlisted' },
  { label: t('candidates.status.hired'), value: 'hired' },
  { label: t('candidates.status.rejected'), value: 'rejected' },
  { label: t('candidates.status.expired'), value: 'expired' },
  { label: t('candidates.status.archived'), value: 'archived' },
])

const orderingOptions = computed(() => [
  { label: t('candidates.ordering.newest'), value: '-created_at' },
  { label: t('candidates.ordering.oldest'), value: 'created_at' },
  { label: t('candidates.ordering.highestScore'), value: '-match_score' },
  { label: t('candidates.ordering.lowestScore'), value: 'match_score' },
])

const bulkActionOptions = computed(() => [
  { label: t('candidates.actions.shortlist'), value: 'shortlisted' as ApplicationStatus },
  { label: t('candidates.actions.hire'), value: 'hired' as ApplicationStatus },
  { label: t('candidates.actions.reject'), value: 'rejected' as ApplicationStatus },
  { label: t('candidates.actions.archive'), value: 'archived' as ApplicationStatus },
  { label: t('candidates.actions.reset'), value: 'applied' as ApplicationStatus },
])
</script>

<template>
  <div class="flex items-center gap-2">
    <!-- View toggle -->
    <div
      class="flex shrink-0 items-center rounded-lg border border-gray-200 dark:border-gray-700 p-0.5"
    >
      <button
        class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors sm:px-3 sm:py-1.5 sm:text-sm"
        :class="
          candidateViewMode === 'kanban'
            ? 'bg-gray-900 text-white'
            : 'text-gray-500 hover:text-gray-700'
        "
        @click="candidateViewMode = 'kanban'"
      >
        <i class="pi pi-th-large sm:mr-1.5"></i
        ><span class="hidden sm:inline">{{ t('candidates.board') }}</span>
      </button>
      <button
        class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors sm:px-3 sm:py-1.5 sm:text-sm"
        :class="
          candidateViewMode === 'table'
            ? 'bg-gray-900 text-white'
            : 'text-gray-500 hover:text-gray-700'
        "
        @click="candidateViewMode = 'table'"
      >
        <i class="pi pi-list sm:mr-1.5"></i
        ><span class="hidden sm:inline">{{ t('candidates.table') }}</span>
      </button>
    </div>

    <!-- Search -->
    <IconField class="min-w-0 flex-1 sm:max-w-64">
      <InputIcon class="pi pi-search" />
      <InputText
        v-model="searchQuery"
        :placeholder="t('common.search')"
        class="w-full"
        @input="emit('searchInput')"
      />
    </IconField>

    <!-- Table-only filters -->
    <template v-if="candidateViewMode === 'table'">
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('common.status')"
        class="hidden shrink-0 sm:flex"
      />
      <Dropdown
        v-model="orderingFilter"
        :options="orderingOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('candidates.sort')"
        class="hidden shrink-0 sm:flex"
      />
    </template>

    <!-- Bulk actions -->
    <template v-if="selectedCandidates.length > 0">
      <span class="hidden shrink-0 text-xs text-gray-500 dark:text-gray-400 sm:inline">{{
        t('candidates.selected', { count: selectedCandidates.length })
      }}</span>
      <Dropdown
        :model-value="null"
        :options="bulkActionOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('candidates.bulkActions')"
        class="shrink-0"
        @change="emit('bulkAction', $event)"
      />
    </template>

    <!-- Count -->
    <span class="ml-auto shrink-0 text-xs text-gray-400">{{
      candidateStore.candidates.length
    }}</span>
  </div>
</template>
