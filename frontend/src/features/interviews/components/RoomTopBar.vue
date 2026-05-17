<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'

defineProps<{
  title: string
  formattedTime: string
  remoteIsSpeaking: boolean
}>()

const { t } = useI18n()
</script>

<template>
  <GlassSurface level="float" class="room-topbar flex items-center justify-between gap-3 px-4 py-2">
    <div class="min-w-0">
      <p class="truncate text-sm font-semibold text-[color:var(--color-text-primary)]">
        {{ title }}
      </p>
      <p class="text-xs text-[color:var(--color-text-muted)]">
        {{ t('interviews.roomPage.aiInterview') }}
      </p>
    </div>

    <div class="flex shrink-0 items-center gap-2 sm:gap-3">
      <span
        class="hidden items-center gap-1.5 rounded-full bg-[color:var(--color-success)]/12 px-2.5 py-1 text-xs font-semibold text-[color:var(--color-success)] sm:inline-flex"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-[color:var(--color-success)]"></span>
        {{
          remoteIsSpeaking
            ? t('interviews.roomPage.aiInterview')
            : t('interviews.roomPage.connected')
        }}
      </span>
      <span
        class="rounded-full bg-[color:var(--color-surface-raised)] px-3 py-1 font-mono text-sm font-semibold text-[color:var(--color-text-primary)]"
      >
        {{ formattedTime }}
      </span>
    </div>
  </GlassSurface>
</template>
