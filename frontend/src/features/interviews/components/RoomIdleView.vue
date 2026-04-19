<script setup lang="ts">
/**
 * RoomIdleView — pre-device-check entry screen for the video room.
 *
 * T13: glass card on top of the cinematic dark video canvas. Prism glyph
 * replaces the old video icon for brand consistency.
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import type { InterviewDetail } from '../types/interview.types'

defineProps<{
  interview: InterviewDetail
  canJoin: boolean
}>()

const emit = defineEmits<{
  startPreview: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-1 items-center justify-center p-6">
    <GlassCard class="w-full max-w-md text-center">
      <div class="mb-4 flex justify-center">
        <AppLogo variant="glyph" size="lg" :linked="false" />
      </div>
      <h2 class="mb-1 text-xl font-semibold text-[color:var(--color-text-primary)]">
        {{ t('interviews.roomPage.aiVideoInterview') }}
      </h2>
      <p class="mb-1 text-sm text-[color:var(--color-text-secondary)]">
        {{ interview.vacancyTitle }}
      </p>
      <p class="mb-5 font-mono text-xs text-[color:var(--color-text-muted)]">
        {{ interview.durationMinutes }} min
      </p>

      <div
        class="bg-glass-2 mb-6 rounded-md border border-[color:var(--color-border-soft)] p-4 text-left text-sm"
      >
        <p class="mb-2 font-medium text-[color:var(--color-text-primary)]">
          {{ t('interviews.roomPage.beforeYouJoin') }}
        </p>
        <ul class="space-y-1.5 text-[color:var(--color-text-secondary)]">
          <li class="flex items-start gap-2">
            <i class="pi pi-wifi mt-0.5 text-xs text-[color:var(--color-success)]"></i>
            {{ t('interviews.roomPage.stableConnection') }}
          </li>
          <li class="flex items-start gap-2">
            <i class="pi pi-volume-up mt-0.5 text-xs text-[color:var(--color-success)]"></i>
            {{ t('interviews.roomPage.quietRoom') }}
          </li>
          <li class="flex items-start gap-2">
            <i class="pi pi-camera mt-0.5 text-xs text-[color:var(--color-success)]"></i>
            {{ t('interviews.roomPage.allowCameraMic') }}
          </li>
          <li class="flex items-start gap-2">
            <i class="pi pi-user mt-0.5 text-xs text-[color:var(--color-success)]"></i>
            {{ t('interviews.roomPage.faceVisible') }}
          </li>
        </ul>
      </div>

      <Button
        v-if="canJoin"
        :label="t('interviews.roomPage.checkDevicesJoin')"
        icon="pi pi-arrow-right"
        icon-pos="right"
        class="w-full"
        size="large"
        @click="emit('startPreview')"
      />
      <p v-else class="text-sm text-[color:var(--color-warning)]">
        {{ t('interviews.roomPage.cannotJoin', { status: interview.status.replace(/_/g, ' ') }) }}
      </p>
    </GlassCard>
  </div>
</template>
