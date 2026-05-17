<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CandidateViewModeToggle from './CandidateViewModeToggle.vue'

defineProps<{
  isAllCandidates: boolean
  count: number
  viewMode: 'kanban' | 'table'
  showViewToggle: boolean
}>()

defineEmits<{
  back: []
  'update:viewMode': [value: 'kanban' | 'table']
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <div class="flex items-center gap-3">
      <button
        v-if="!isAllCandidates"
        class="rounded-lg p-1.5 text-[color:var(--color-text-muted)] transition-colors hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]"
        @click="$emit('back')"
      >
        <i class="pi pi-arrow-left"></i>
      </button>
      <div>
        <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
          {{ isAllCandidates ? t('nav.allCandidates') : t('candidates.pipeline') }}
        </h1>
        <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
          {{ count }} {{ t('nav.candidates').toLowerCase() }}
        </p>
      </div>
    </div>
    <CandidateViewModeToggle
      v-if="showViewToggle"
      :model-value="viewMode"
      @update:model-value="$emit('update:viewMode', $event)"
    />
  </div>
</template>
