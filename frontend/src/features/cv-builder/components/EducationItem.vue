<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { Education } from '../types/cv-builder.types'

defineProps<{
  education: Education
}>()

const emit = defineEmits<{
  edit: [edu: Education]
  delete: [id: string]
}>()

const { t } = useI18n()

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
        <h3 class="font-semibold text-gray-900">{{ education.degree }}</h3>
        <p class="text-sm text-gray-600">{{ education.institution }}</p>
        <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
          <span v-if="education.educationLevel">{{ education.educationLevel.name }}</span>
          <span v-if="education.fieldOfStudy">{{ education.fieldOfStudy }}</span>
        </div>
        <p class="mt-1 text-xs text-gray-500">
          {{ formatDisplayDate(education.startDate) }}
          <template v-if="education.endDate"
            >&mdash; {{ formatDisplayDate(education.endDate) }}</template
          >
        </p>
        <p v-if="education.description" class="mt-2 text-sm text-gray-600">
          {{ education.description }}
        </p>
      </div>
      <div class="ml-3 flex shrink-0 gap-1">
        <Button
          icon="pi pi-pencil"
          severity="secondary"
          text
          rounded
          size="small"
          @click="emit('edit', education)"
          :aria-label="t('common.edit')"
        />
        <Button
          icon="pi pi-trash"
          severity="danger"
          text
          rounded
          size="small"
          @click="emit('delete', education.id)"
          :aria-label="t('common.delete')"
        />
      </div>
    </div>
  </div>
</template>
