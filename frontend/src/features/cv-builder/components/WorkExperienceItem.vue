<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { WorkExperience } from '../types/cv-builder.types'

defineProps<{
  experience: WorkExperience
}>()

const emit = defineEmits<{
  edit: [exp: WorkExperience]
  delete: [id: string]
}>()

const { t } = useI18n()

const employmentTypeOptions = [
  { label: t('cvBuilder.employmentTypes.fullTime'), value: 'full_time' },
  { label: t('cvBuilder.employmentTypes.partTime'), value: 'part_time' },
  { label: t('cvBuilder.employmentTypes.contract'), value: 'contract' },
  { label: t('cvBuilder.employmentTypes.internship'), value: 'internship' },
]

function getEmploymentLabel(value: string): string {
  const opt = employmentTypeOptions.find((o) => o.value === value)
  return opt?.label ?? value
}

function formatDisplayDate(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short' })
}
</script>

<template>
  <div class="rounded-lg border border-gray-200 p-4">
    <div class="flex items-start justify-between">
      <div class="min-w-0 flex-1">
        <h3 class="font-semibold text-gray-900">{{ experience.position }}</h3>
        <p class="text-sm text-gray-600">{{ experience.companyName }}</p>
        <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
          <span v-if="experience.employmentType">{{ getEmploymentLabel(experience.employmentType) }}</span>
          <span v-if="experience.location">{{ experience.location }}</span>
        </div>
        <p class="mt-1 text-xs text-gray-500">
          {{ formatDisplayDate(experience.startDate) }}
          &mdash;
          {{ experience.isCurrent ? t('cvBuilder.experience.present') : formatDisplayDate(experience.endDate) }}
        </p>
        <p v-if="experience.description" class="mt-2 text-sm text-gray-600">{{ experience.description }}</p>
      </div>
      <div class="ml-3 flex shrink-0 gap-1">
        <Button
          icon="pi pi-pencil"
          severity="secondary"
          text
          rounded
          size="small"
          @click="emit('edit', experience)"
          :aria-label="t('common.edit')"
        />
        <Button
          icon="pi pi-trash"
          severity="danger"
          text
          rounded
          size="small"
          @click="emit('delete', experience.id)"
          :aria-label="t('common.delete')"
        />
      </div>
    </div>
  </div>
</template>
