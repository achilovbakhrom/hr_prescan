<script setup lang="ts">
import { useI18n } from 'vue-i18n'

type CandidateSection = 'applications' | 'base'

defineProps<{
  modelValue: CandidateSection
}>()

defineEmits<{
  'update:modelValue': [value: CandidateSection]
}>()

const { t } = useI18n()

const tabs: Array<{ key: CandidateSection; labelKey: string }> = [
  { key: 'applications', labelKey: 'nav.allCandidates' },
  { key: 'base', labelKey: 'nav.candidateBase' },
]
</script>

<template>
  <div class="inline-flex rounded-md bg-[color:var(--color-surface-sunken)] p-0.5" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
      :class="
        modelValue === tab.key
          ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
          : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
      "
      role="tab"
      :aria-selected="modelValue === tab.key"
      @click="$emit('update:modelValue', tab.key)"
    >
      {{ t(tab.labelKey) }}
    </button>
  </div>
</template>
