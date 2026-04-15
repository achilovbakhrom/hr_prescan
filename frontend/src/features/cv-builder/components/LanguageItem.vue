<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import type { LanguageEntry } from '../types/cv-builder.types'

defineProps<{
  entry: LanguageEntry
}>()

const emit = defineEmits<{
  edit: [entry: LanguageEntry]
  delete: [id: string]
}>()

const { t, locale } = useI18n()

function getLocalizedName(lang: { name: string; nameRu: string; nameUz: string }): string {
  if (locale.value === 'ru' && lang.nameRu) return lang.nameRu
  if (locale.value === 'uz' && lang.nameUz) return lang.nameUz
  return lang.name
}

const proficiencyOptions = [
  { label: t('cvBuilder.proficiencies.beginner'), value: 'beginner' },
  { label: t('cvBuilder.proficiencies.elementary'), value: 'elementary' },
  { label: t('cvBuilder.proficiencies.intermediate'), value: 'intermediate' },
  { label: t('cvBuilder.proficiencies.upperIntermediate'), value: 'upper_intermediate' },
  { label: t('cvBuilder.proficiencies.advanced'), value: 'advanced' },
  { label: t('cvBuilder.proficiencies.native'), value: 'native' },
]

function getProficiencyLabel(value: string): string {
  return proficiencyOptions.find((o) => o.value === value)?.label ?? value
}

function getProficiencySeverity(value: string): 'success' | 'info' | 'warn' | 'secondary' {
  if (value === 'native' || value === 'advanced') return 'success'
  if (value === 'upper_intermediate' || value === 'intermediate') return 'info'
  if (value === 'elementary') return 'warn'
  return 'secondary'
}
</script>

<template>
  <div class="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-3">
    <div class="flex items-center gap-3">
      <span class="font-medium text-gray-900">{{ getLocalizedName(entry.language) }}</span>
      <Tag
        :value="getProficiencyLabel(entry.proficiency)"
        :severity="getProficiencySeverity(entry.proficiency)"
      />
    </div>
    <div class="flex gap-1">
      <Button
        icon="pi pi-pencil"
        severity="secondary"
        text
        rounded
        size="small"
        @click="emit('edit', entry)"
        :aria-label="t('common.edit')"
      />
      <Button
        icon="pi pi-trash"
        severity="danger"
        text
        rounded
        size="small"
        @click="emit('delete', entry.id)"
        :aria-label="t('common.delete')"
      />
    </div>
  </div>
</template>
