<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AutoComplete from '@/shared/components/AppAutocomplete.vue'
import type { Vacancy } from '../types/vacancy.types'

defineProps<{
  modelValue: Vacancy | null
  vacancies: Vacancy[]
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Vacancy | null]
}>()

const { t } = useI18n()
const suggestions = ref<Vacancy[]>([])

function search(event: { query: string }, vacancies: Vacancy[]): void {
  const query = event.query.trim().toLowerCase()
  suggestions.value = vacancies.filter((vacancy) => {
    const haystack = `${vacancy.title} ${vacancy.companyName ?? ''}`.toLowerCase()
    return !query || haystack.includes(query)
  })
}

function onValueChange(value: unknown): void {
  emit('update:modelValue', value && typeof value === 'object' ? (value as Vacancy) : null)
}
</script>

<template>
  <AutoComplete
    :model-value="modelValue"
    :suggestions="suggestions"
    option-label="title"
    :placeholder="placeholder || t('vacancies.filterByVacancy', 'Filter by vacancy')"
    class="w-full sm:w-72"
    input-class="w-full"
    force-selection
    dropdown
    @complete="search($event, vacancies)"
    @update:model-value="onValueChange"
  >
    <template #option="{ option }">
      <div class="min-w-0">
        <p class="truncate text-sm font-medium text-[color:var(--color-text-primary)]">
          {{ option.title }}
        </p>
        <p v-if="option.companyName" class="truncate text-xs text-[color:var(--color-text-muted)]">
          {{ option.companyName }}
        </p>
      </div>
    </template>
  </AutoComplete>
</template>
