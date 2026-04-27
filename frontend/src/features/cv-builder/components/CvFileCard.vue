<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'
import type { CvFile } from '../types/cv-builder.types'

defineProps<{
  cv: CvFile
  actionLoading: string | null
}>()

const emit = defineEmits<{
  view: [cv: CvFile]
  toggleActive: [cv: CvFile]
  delete: [cv: CvFile]
}>()

const { t } = useI18n()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
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
    class="rounded-lg border p-4 shadow-glass backdrop-blur-md transition-all"
    :class="
      cv.isActive
        ? 'border-emerald-300/70 bg-emerald-50/70 dark:border-emerald-500/35 dark:bg-emerald-950/35'
        : 'border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-glass-1)] dark:border-white/10 dark:bg-slate-800/70'
    "
  >
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex min-w-0 items-start gap-3">
        <div
          class="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg"
          :class="
            cv.isActive
              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300'
              : 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)] dark:bg-white/10'
          "
        >
          <i class="pi pi-file-pdf text-lg"></i>
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex min-w-0 flex-wrap items-center gap-2">
            <p
              class="min-w-0 max-w-full truncate font-semibold text-[color:var(--color-text-primary)]"
            >
              {{ cv.name }}
            </p>
            <Tag
              v-if="cv.isActive"
              :value="t('myCvs.active')"
              severity="success"
              class="shrink-0 !text-[10px]"
            />
          </div>
          <div class="mt-2 flex flex-wrap gap-2 text-xs text-[color:var(--color-text-muted)]">
            <span
              class="inline-flex max-w-full items-center gap-1.5 rounded-md bg-[color:var(--color-surface-sunken)] px-2 py-1 dark:bg-white/10"
            >
              <i class="pi pi-file text-[10px]"></i>
              <span class="truncate">{{ templateLabel(cv.template) }}</span>
            </span>
            <span
              class="inline-flex max-w-full items-center gap-1.5 rounded-md bg-[color:var(--color-surface-sunken)] px-2 py-1 dark:bg-white/10"
            >
              <i class="pi pi-calendar text-[10px]"></i>
              <span class="truncate">{{ formatDate(cv.createdAt) }}</span>
            </span>
          </div>
        </div>
      </div>

      <div
        class="flex items-center justify-between gap-3 border-t border-[color:var(--color-border-soft)] pt-3 dark:border-white/10 sm:border-t-0 sm:pt-0"
      >
        <div class="flex items-center gap-2">
          <span
            class="max-w-28 text-right text-xs font-medium leading-tight text-[color:var(--color-text-secondary)] sm:max-w-24"
          >
            {{ cv.isActive ? t('myCvs.activeLabel') : t('myCvs.activate') }}
          </span>
          <ToggleSwitch
            :modelValue="cv.isActive"
            :disabled="actionLoading === cv.id"
            @update:modelValue="emit('toggleActive', cv)"
          />
        </div>
        <span class="h-5 w-px bg-[color:var(--color-border-soft)] dark:bg-white/10"></span>
        <Button
          v-if="cv.downloadUrl"
          icon="pi pi-eye"
          severity="secondary"
          text
          rounded
          size="small"
          v-tooltip.top="t('myCvs.view')"
          @click="emit('view', cv)"
        />
        <Button
          icon="pi pi-trash"
          severity="danger"
          text
          rounded
          size="small"
          v-tooltip.top="cv.isActive ? t('myCvs.deactivateFirst') : t('common.delete')"
          :loading="actionLoading === cv.id"
          :disabled="cv.isActive"
          @click="emit('delete', cv)"
        />
      </div>
    </div>
  </div>
</template>
