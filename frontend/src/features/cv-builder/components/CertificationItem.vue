<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { Certification } from '../types/cv-builder.types'

const { t } = useI18n()

defineProps<{
  certification: Certification
}>()

const emit = defineEmits<{
  edit: [cert: Certification]
  delete: [id: string]
}>()

function formatDisplayDate(dateStr: string | null): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short' })
}
</script>

<template>
  <div class="rounded-lg border border-gray-200 p-4">
    <div class="flex items-start justify-between">
      <div class="min-w-0 flex-1">
        <h3 class="font-semibold text-gray-900">{{ certification.name }}</h3>
        <p class="text-sm text-gray-600">{{ certification.issuingOrganization }}</p>
        <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
          <span v-if="certification.issueDate">{{ t('cvBuilder.certifications.issued') }}: {{ formatDisplayDate(certification.issueDate) }}</span>
          <span v-if="certification.expiryDate">{{ t('cvBuilder.certifications.expires') }}: {{ formatDisplayDate(certification.expiryDate) }}</span>
        </div>
        <a v-if="certification.credentialUrl" :href="certification.credentialUrl" target="_blank" rel="noopener noreferrer" class="mt-1 inline-flex items-center gap-1 text-xs text-blue-600 hover:underline">
          <i class="pi pi-external-link text-xs"></i>{{ t('cvBuilder.certifications.viewCredential') }}
        </a>
      </div>
      <div class="ml-3 flex shrink-0 gap-1">
        <Button icon="pi pi-pencil" severity="secondary" text rounded size="small" @click="emit('edit', certification)" :aria-label="t('common.edit')" />
        <Button icon="pi pi-trash" severity="danger" text rounded size="small" @click="emit('delete', certification.id)" :aria-label="t('common.delete')" />
      </div>
    </div>
  </div>
</template>
