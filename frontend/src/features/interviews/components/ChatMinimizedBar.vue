<script setup lang="ts">
/**
 * ChatMinimizedBar — collapsed chat footer when the candidate minimises
 * the conversation. Tap anywhere on it to restore.
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassSurface from '@/shared/components/GlassSurface.vue'

defineProps<{
  vacancyTitle: string
  companyName?: string | null
  messageCount: number
}>()

const emit = defineEmits<{
  restore: []
  close: []
}>()

const { t } = useI18n()
</script>

<template>
  <GlassSurface
    level="float"
    class="fixed bottom-0 left-0 right-0 z-50 cursor-pointer px-4 py-3 !rounded-none"
    @click="emit('restore')"
  >
    <div class="mx-auto flex max-w-3xl items-center justify-between">
      <div class="flex items-center gap-3">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)]"
        >
          <i class="pi pi-sparkles text-sm text-[color:var(--color-accent-ai)]"></i>
        </div>
        <div>
          <p class="text-sm font-medium text-[color:var(--color-text-primary)]">
            {{ vacancyTitle }}
          </p>
          <p v-if="companyName" class="text-xs text-[color:var(--color-text-muted)]">
            <i class="pi pi-building mr-0.5"></i>{{ companyName }}
          </p>
          <p class="text-xs text-[color:var(--color-text-muted)]">
            {{ t('interviews.chatPage.inProgress') }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span
          v-if="messageCount"
          class="flex h-5 w-5 items-center justify-center rounded-full bg-[color:var(--color-accent)] font-mono text-[10px] font-bold text-[color:var(--color-text-on-accent)]"
        >
          {{ messageCount }}
        </span>
        <i class="pi pi-chevron-up text-[color:var(--color-text-muted)]"></i>
        <Button
          icon="pi pi-times"
          severity="secondary"
          text
          rounded
          size="small"
          title="Close"
          @click.stop="emit('close')"
        />
      </div>
    </div>
  </GlassSurface>
</template>
