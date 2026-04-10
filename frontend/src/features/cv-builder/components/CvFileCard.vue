<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'
import type { CvFile } from '../types/cv-builder.types'

const { t } = useI18n()

defineProps<{
  cv: CvFile
  actionLoading: string | null
}>()

const emit = defineEmits<{
  view: [cv: CvFile]
  toggleActive: [cv: CvFile]
  delete: [cv: CvFile]
}>()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function templateLabel(template: string): string {
  const map: Record<string, string> = {
    classic: t('myCvs.templates.classic'),
    modern: t('myCvs.templates.modern'),
    minimal: t('myCvs.templates.minimal'),
  }
  return map[template] || template
}
</script>

<template>
  <div
    class="rounded-xl border bg-white p-4 transition-all"
    :class="cv.isActive ? 'border-green-200 bg-green-50/20' : 'border-gray-200'"
  >
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg" :class="cv.isActive ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'">
          <i class="pi pi-file-pdf text-lg"></i>
        </div>
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <p class="truncate font-medium text-gray-900">{{ cv.name }}</p>
            <Tag v-if="cv.isActive" :value="t('myCvs.active')" severity="success" class="!text-[10px]" />
          </div>
          <div class="flex flex-wrap items-center gap-2 text-xs text-gray-500">
            <span>{{ templateLabel(cv.template) }}</span>
            <span>&middot;</span>
            <span>{{ formatDate(cv.createdAt) }}</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">{{ cv.isActive ? t('myCvs.active') : t('myCvs.inactive') }}</span>
          <ToggleSwitch :modelValue="cv.isActive" :disabled="actionLoading === cv.id" @update:modelValue="emit('toggleActive', cv)" />
        </div>
        <span class="h-5 w-px bg-gray-200"></span>
        <Button v-if="cv.downloadUrl" icon="pi pi-eye" severity="secondary" text rounded size="small" v-tooltip.top="t('myCvs.view')" @click="emit('view', cv)" />
        <Button icon="pi pi-trash" severity="danger" text rounded size="small" v-tooltip.top="cv.isActive ? t('myCvs.deactivateFirst') : t('common.delete')" :loading="actionLoading === cv.id" :disabled="cv.isActive" @click="emit('delete', cv)" />
      </div>
    </div>
  </div>
</template>
