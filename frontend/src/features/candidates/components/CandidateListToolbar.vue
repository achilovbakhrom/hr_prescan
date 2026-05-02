<script setup lang="ts">
/**
 * CandidateListToolbar — glass chrome row with search + sort + filter.
 * Extracted from CandidateListPage to respect the 200-line file cap.
 */
import { useI18n } from 'vue-i18n'
import Dropdown from '@/shared/components/AppSelect.vue'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import GlassSurface from '@/shared/components/GlassSurface.vue'

interface Option {
  label: string
  value: string | undefined
}

defineProps<{
  search: string
  statusFilter: string | undefined
  orderingFilter: string
  statusOptions: Option[]
  orderingOptions: Option[]
  showFilters: boolean
}>()

defineEmits<{
  'update:search': [value: string]
  'update:statusFilter': [value: string | undefined]
  'update:orderingFilter': [value: string]
  searchInput: []
}>()

const { t } = useI18n()
</script>

<template>
  <GlassSurface class="flex flex-wrap items-center gap-3 rounded-lg p-3" level="1">
    <IconField class="w-full sm:w-64">
      <InputIcon class="pi pi-search" />
      <InputText
        :model-value="search"
        :placeholder="t('candidates.search')"
        class="w-full"
        @update:model-value="$emit('update:search', String($event ?? ''))"
        @input="$emit('searchInput')"
      />
    </IconField>
    <template v-if="showFilters">
      <Dropdown
        :model-value="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('candidates.filterByStatus')"
        class="w-full sm:w-48"
        @update:model-value="$emit('update:statusFilter', $event)"
      />
      <Dropdown
        :model-value="orderingFilter"
        :options="orderingOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('candidates.sortBy')"
        class="w-full sm:w-48"
        @update:model-value="$emit('update:orderingFilter', String($event))"
      />
    </template>
  </GlassSurface>
</template>
