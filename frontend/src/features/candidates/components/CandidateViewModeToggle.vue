<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  modelValue: 'kanban' | 'table'
}>()

defineEmits<{
  'update:modelValue': [value: 'kanban' | 'table']
}>()

const { t } = useI18n()
</script>

<template>
  <div class="inline-flex rounded-md bg-[color:var(--color-surface-sunken)] p-0.5" role="tablist">
    <button
      class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
      :class="
        modelValue === 'kanban'
          ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
          : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
      "
      @click="$emit('update:modelValue', 'kanban')"
    >
      <i class="pi pi-th-large mr-1.5"></i>{{ t('candidates.kanban') }}
    </button>
    <button
      class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
      :class="
        modelValue === 'table'
          ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
          : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
      "
      @click="$emit('update:modelValue', 'table')"
    >
      <i class="pi pi-list mr-1.5"></i>{{ t('candidates.table') }}
    </button>
  </div>
</template>
