<script setup lang="ts">
/**
 * ChatInterviewHeader — sticky top bar for the candidate chat interview.
 *
 * T13: AI Prism avatar with `accentPulse` ring when `isSpeaking` is true,
 * live/completed status indicator, minimize + close controls. Sits on top
 * of the floating chat layer.
 */
import { useI18n } from 'vue-i18n'
import AppLogo from '@/shared/components/AppLogo.vue'

defineProps<{
  vacancyTitle: string
  companyName?: string | null
  isCompleted: boolean
  isSpeaking?: boolean
}>()

const emit = defineEmits<{
  minimize: []
  close: []
}>()

const { t } = useI18n()
</script>

<template>
  <header
    class="bg-glass-float border-b border-[color:var(--color-border-glass)] px-4 py-3 backdrop-blur-md"
  >
    <div class="mx-auto flex max-w-3xl items-center justify-between">
      <div class="flex min-w-0 items-center gap-3">
        <!-- AI avatar (Prism) with pulse ring when speaking -->
        <div class="relative h-10 w-10 shrink-0">
          <span
            v-if="isSpeaking && !isCompleted"
            class="ai-pulse absolute inset-0 rounded-full bg-[color:var(--color-accent-ai-soft)]"
            aria-hidden="true"
          ></span>
          <div
            class="relative flex h-10 w-10 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)] ring-1 ring-[color:var(--color-accent-ai)]/40"
          >
            <AppLogo variant="glyph" size="sm" :linked="false" />
          </div>
        </div>

        <div class="min-w-0">
          <h1
            class="truncate text-sm font-semibold text-[color:var(--color-text-primary)] sm:text-base"
          >
            {{ vacancyTitle }}
          </h1>
          <p v-if="companyName" class="truncate text-xs text-[color:var(--color-text-muted)]">
            <i class="pi pi-building mr-1"></i>{{ companyName }}
          </p>
          <div class="flex items-center gap-1.5">
            <span
              class="h-2 w-2 rounded-full"
              :class="
                isCompleted
                  ? 'bg-[color:var(--color-text-muted)]'
                  : 'bg-[color:var(--color-success)] animate-pulse'
              "
            ></span>
            <span class="text-[11px] text-[color:var(--color-text-muted)]">
              {{
                isCompleted ? t('interviews.status.completed') : t('interviews.chat.aiInterview')
              }}
            </span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-1">
        <button
          class="flex h-9 w-9 items-center justify-center rounded-md text-[color:var(--color-text-muted)] ease-ios transition-colors hover:bg-[color:var(--color-surface-raised)] hover:text-[color:var(--color-text-primary)]"
          :title="t('interviews.chatPage.minimize') || 'Minimize'"
          @click="emit('minimize')"
        >
          <i class="pi pi-minus text-sm"></i>
        </button>
        <button
          class="flex h-9 w-9 items-center justify-center rounded-md text-[color:var(--color-text-muted)] ease-ios transition-colors hover:bg-[color:var(--color-danger)]/10 hover:text-[color:var(--color-danger)]"
          :title="t('common.close') || 'Close'"
          @click="emit('close')"
        >
          <i class="pi pi-times text-sm"></i>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
@keyframes ai-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.12);
    opacity: 0.35;
  }
}
.ai-pulse {
  animation: ai-pulse 1.6s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .ai-pulse {
    animation: none;
    opacity: 0.7;
  }
}
</style>
