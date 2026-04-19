<script setup lang="ts">
/**
 * RoomPreviewView — device check / preview before joining.
 *
 * T13: video tile stays dark (cinematic); side panel is glass. Controls
 * become floating glass pills.
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import type { InterviewDetail } from '../types/interview.types'

defineProps<{
  interview: InterviewDetail
  isMuted: boolean
  isCameraOff: boolean
  getInitials: (name: string) => string
}>()

const emit = defineEmits<{
  toggleMic: []
  toggleCamera: []
  joinRoom: []
  cancel: []
}>()

const previewVideoEl = defineModel<HTMLVideoElement | null>('previewVideoEl', { required: true })

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-1 flex-col items-center justify-center gap-6 p-6 md:flex-row md:gap-8">
    <!-- Preview video -->
    <div
      class="relative w-full max-w-xl overflow-hidden rounded-lg bg-black/80 ring-1 ring-[color:var(--color-border-glass)]"
    >
      <div class="aspect-video">
        <video
          v-show="!isCameraOff"
          ref="previewVideoEl"
          autoplay
          playsinline
          muted
          class="h-full w-full object-cover"
        ></video>
        <div v-if="isCameraOff" class="flex h-full w-full items-center justify-center">
          <div
            class="flex h-24 w-24 items-center justify-center rounded-full bg-[color:var(--color-accent-ai)] text-3xl font-medium text-white"
          >
            {{ interview.candidateName ? getInitials(interview.candidateName) : '?' }}
          </div>
        </div>
      </div>

      <!-- Preview controls: floating glass pill -->
      <GlassSurface
        level="float"
        class="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-2 !rounded-full p-2"
      >
        <button
          class="flex h-10 w-10 items-center justify-center rounded-full transition-colors"
          :class="
            isMuted
              ? 'bg-[color:var(--color-danger)] text-white'
              : 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] hover:bg-[color:var(--color-surface-sunken)]'
          "
          @click="emit('toggleMic')"
        >
          <i :class="isMuted ? 'pi pi-microphone-slash' : 'pi pi-microphone'" class="text-base"></i>
        </button>
        <button
          class="flex h-10 w-10 items-center justify-center rounded-full transition-colors"
          :class="
            isCameraOff
              ? 'bg-[color:var(--color-danger)] text-white'
              : 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] hover:bg-[color:var(--color-surface-sunken)]'
          "
          @click="emit('toggleCamera')"
        >
          <i :class="isCameraOff ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-base"></i>
        </button>
      </GlassSurface>
    </div>

    <!-- Join panel -->
    <GlassCard class="w-full max-w-xs shrink-0 text-center md:w-72">
      <h2 class="mb-1 text-xl font-semibold text-[color:var(--color-text-primary)]">
        {{ t('interviews.roomPage.readyToJoin') }}
      </h2>
      <p class="mb-6 text-sm text-[color:var(--color-text-secondary)]">
        {{ interview.vacancyTitle }}
      </p>
      <Button
        :label="t('interviews.roomPage.joinNow')"
        icon="pi pi-video"
        class="w-full"
        size="large"
        @click="emit('joinRoom')"
      />
      <button
        class="mt-3 text-sm text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]"
        @click="emit('cancel')"
      >
        {{ t('interviews.roomPage.goBack') }}
      </button>
    </GlassCard>
  </div>
</template>
