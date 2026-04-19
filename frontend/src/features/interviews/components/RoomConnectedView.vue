<script setup lang="ts">
/**
 * RoomConnectedView — live interview (candidate side).
 *
 * T13 redesign: large video tile, floating glass control pill at bottom,
 * glass top status strip. Kept cinematic-dark — video rooms read best on
 * near-black.
 */
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import type { InterviewDetail } from '../types/interview.types'

defineProps<{
  interview: InterviewDetail
  isMuted: boolean
  isCameraOff: boolean
  hasRemoteVideo: boolean
  remoteParticipantName: string
  formattedTime: string
  getInitials: (name: string) => string
}>()

const emit = defineEmits<{
  toggleMute: []
  toggleCamera: []
  leave: []
}>()

const localVideoEl = defineModel<HTMLVideoElement | null>('localVideoEl', { required: true })
const remoteVideoEl = defineModel<HTMLVideoElement | null>('remoteVideoEl', { required: true })
const remoteAudioEl = defineModel<HTMLAudioElement | null>('remoteAudioEl', { required: true })

const { t } = useI18n()
</script>

<template>
  <div class="relative flex flex-1 flex-col">
    <!-- Top glass strip -->
    <GlassSurface
      level="float"
      class="z-10 flex items-center justify-between px-4 py-2 !rounded-none"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-[color:var(--color-text-primary)]">
          {{ interview.vacancyTitle }}
        </span>
        <span
          class="rounded-md bg-[color:var(--color-accent-ai-soft)] px-2 py-0.5 text-[11px] font-medium text-[color:var(--color-accent-ai)]"
        >
          {{ t('interviews.roomPage.aiInterview') }}
        </span>
      </div>
      <div class="flex items-center gap-3">
        <span class="font-mono text-sm text-[color:var(--color-text-secondary)]">
          {{ formattedTime }}
        </span>
        <span
          class="flex items-center gap-1.5 text-xs font-medium text-[color:var(--color-success)]"
        >
          <span class="h-1.5 w-1.5 rounded-full bg-[color:var(--color-success)]"></span>
          {{ t('interviews.roomPage.connected') }}
        </span>
      </div>
    </GlassSurface>

    <!-- Video grid -->
    <div class="flex flex-1 flex-col items-center justify-center gap-3 px-3 pb-24 pt-3 md:flex-row">
      <!-- Remote participant -->
      <div
        class="relative flex h-full min-h-[40vh] flex-1 items-center justify-center overflow-hidden rounded-lg bg-black/80 ring-1 ring-[color:var(--color-border-glass)]"
      >
        <video
          v-show="hasRemoteVideo"
          ref="remoteVideoEl"
          autoplay
          playsinline
          class="h-full w-full object-cover"
        ></video>
        <audio ref="remoteAudioEl" autoplay></audio>

        <div v-if="!hasRemoteVideo" class="flex flex-col items-center gap-3">
          <div
            class="flex h-24 w-24 items-center justify-center rounded-full bg-[color:var(--color-accent-ai)] text-3xl font-medium text-white"
          >
            {{ getInitials(remoteParticipantName) }}
          </div>
          <span class="text-sm text-[color:var(--color-text-secondary)]">
            {{ remoteParticipantName }}
          </span>
        </div>

        <div
          v-if="hasRemoteVideo"
          class="absolute bottom-3 left-3 rounded-md bg-black/60 px-2.5 py-1 font-mono text-xs text-white backdrop-blur-sm"
        >
          {{ remoteParticipantName }}
        </div>
      </div>

      <!-- Local -->
      <div
        class="relative h-36 w-52 shrink-0 overflow-hidden rounded-lg bg-black/80 ring-1 ring-[color:var(--color-border-glass)] md:h-48 md:w-64"
      >
        <video
          v-show="!isCameraOff"
          ref="localVideoEl"
          autoplay
          playsinline
          muted
          class="h-full w-full object-cover"
        ></video>
        <div v-if="isCameraOff" class="flex h-full w-full items-center justify-center">
          <div
            class="flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent)] text-lg font-medium text-white"
          >
            {{ interview.candidateName ? getInitials(interview.candidateName) : 'Y' }}
          </div>
        </div>
        <div
          class="absolute bottom-2 left-2 flex items-center gap-1.5 rounded-md bg-black/60 px-2 py-0.5 font-mono text-[11px] text-white backdrop-blur-sm"
        >
          <span>{{ t('interviews.roomPage.you') }}</span>
          <i
            v-if="isMuted"
            class="pi pi-microphone-slash text-[color:var(--color-danger)]"
            style="font-size: 0.65rem"
          ></i>
        </div>
      </div>
    </div>

    <!-- Bottom floating control pill -->
    <GlassSurface
      level="float"
      class="pointer-events-auto absolute bottom-4 left-1/2 z-20 flex -translate-x-1/2 gap-2 !rounded-full p-2 shadow-glass-float"
    >
      <button
        class="flex h-11 w-11 items-center justify-center rounded-full transition-colors"
        :class="
          isMuted
            ? 'bg-[color:var(--color-danger)] text-white'
            : 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] hover:bg-[color:var(--color-surface-sunken)]'
        "
        :title="isMuted ? t('interviews.roomPage.unmute') : t('interviews.roomPage.mute')"
        @click="emit('toggleMute')"
      >
        <i :class="isMuted ? 'pi pi-microphone-slash' : 'pi pi-microphone'" class="text-base"></i>
      </button>

      <button
        class="flex h-11 w-11 items-center justify-center rounded-full transition-colors"
        :class="
          isCameraOff
            ? 'bg-[color:var(--color-danger)] text-white'
            : 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] hover:bg-[color:var(--color-surface-sunken)]'
        "
        :title="
          isCameraOff
            ? t('interviews.roomPage.turnOnCamera')
            : t('interviews.roomPage.turnOffCamera')
        "
        @click="emit('toggleCamera')"
      >
        <i :class="isCameraOff ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-base"></i>
      </button>

      <button
        class="ml-2 flex h-11 items-center gap-2 rounded-full bg-[color:var(--color-danger)] px-4 text-white transition-colors hover:brightness-90"
        :title="t('interviews.roomPage.leaveInterview')"
        @click="emit('leave')"
      >
        <i class="pi pi-phone text-base" style="transform: rotate(135deg)"></i>
        <span class="text-sm font-medium">{{ t('interviews.roomPage.leave') }}</span>
      </button>
    </GlassSurface>
  </div>
</template>
