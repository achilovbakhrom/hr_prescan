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
  <div class="flex flex-1 items-center justify-center p-4 sm:p-6">
    <GlassCard class="w-full max-w-2xl overflow-hidden !p-0">
      <div class="grid md:grid-cols-[0.9fr_1.1fr]">
        <div
          class="relative hidden min-h-80 overflow-hidden bg-black/70 ring-1 ring-white/10 md:block"
        >
          <div
            class="absolute inset-0 bg-[radial-gradient(circle_at_35%_30%,rgba(125,211,252,0.28),transparent_36%),radial-gradient(circle_at_70%_70%,rgba(167,243,208,0.18),transparent_42%)]"
          ></div>
          <div
            class="absolute inset-x-8 top-10 h-36 rounded-3xl border border-white/10 bg-white/5"
          ></div>
          <div
            class="absolute bottom-10 left-1/2 h-28 w-28 -translate-x-1/2 rounded-full bg-white/10 ring-1 ring-white/15"
          ></div>
          <div
            class="absolute bottom-24 left-1/2 flex h-16 w-16 -translate-x-1/2 items-center justify-center rounded-2xl bg-white/15 text-white shadow-2xl"
          >
            <i class="pi pi-sparkles text-2xl"></i>
          </div>
          <div class="absolute bottom-8 left-8 right-8 h-2 rounded-full bg-white/10">
            <div
              class="h-full w-2/3 rounded-full bg-gradient-to-r from-sky-300 to-emerald-200"
            ></div>
          </div>
        </div>

        <div class="p-6 text-center sm:p-8">
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
            class="mb-6 rounded-md bg-[color:var(--color-surface-raised)]/70 p-4 text-left text-sm ring-1 ring-[color:var(--color-border-soft)]"
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
            {{
              t('interviews.roomPage.cannotJoin', { status: interview.status.replace(/_/g, ' ') })
            }}
          </p>
        </div>
      </div>
    </GlassCard>
  </div>
</template>
