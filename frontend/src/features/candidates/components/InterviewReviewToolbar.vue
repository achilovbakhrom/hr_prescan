<script setup lang="ts">
import { useI18n } from 'vue-i18n'

type Section = 'conversation' | 'recording' | 'scores'

defineProps<{
  activeSection: Section
  conversationCount: number
  hasRecording: boolean
}>()

const emit = defineEmits<{
  'update:activeSection': [value: Section]
  export: [format: 'doc' | 'txt']
}>()

const { t } = useI18n()

function tabClass(isActive: boolean): string {
  return isActive
    ? 'bg-[color:var(--color-accent)] text-white'
    : 'bg-gray-100 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
}
</script>

<template>
  <div class="mb-4 flex flex-wrap items-center gap-2">
    <button
      class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
      :class="tabClass(activeSection === 'scores')"
      @click="emit('update:activeSection', 'scores')"
    >
      {{ t('interviews.scores') }}
    </button>
    <button
      class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
      :class="tabClass(activeSection === 'conversation')"
      @click="emit('update:activeSection', 'conversation')"
    >
      {{ t('interviews.conversation') }} ({{ conversationCount }} {{ t('interviews.messages') }})
    </button>
    <button
      v-if="hasRecording"
      class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
      :class="tabClass(activeSection === 'recording')"
      @click="emit('update:activeSection', 'recording')"
    >
      {{ t('interviews.recording') }}
    </button>
    <span class="min-w-0 flex-1"></span>
    <button
      class="rounded-lg px-3 py-2 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-100"
      type="button"
      @click="emit('export', 'txt')"
    >
      <i class="pi pi-download mr-1"></i>TXT
    </button>
    <button
      class="rounded-lg px-3 py-2 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-100"
      type="button"
      @click="emit('export', 'doc')"
    >
      <i class="pi pi-file-word mr-1"></i>DOC
    </button>
  </div>
</template>
