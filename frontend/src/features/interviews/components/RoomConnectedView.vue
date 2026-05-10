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
import LiveTranscriptOverlay from './LiveTranscriptOverlay.vue'
import VoiceLevelMeter from './VoiceLevelMeter.vue'
import type { LiveTranscriptLine } from '../composables/useInterviewRoom'
import type { InterviewDetail } from '../types/interview.types'

defineProps<{
  interview: InterviewDetail
  isMuted: boolean
  isCameraOff: boolean
  audioPlaybackBlocked: boolean
  hasRemoteVideo: boolean
  remoteParticipantName: string
  localAudioLevel: number
  remoteAudioLevel: number
  localIsSpeaking: boolean
  remoteIsSpeaking: boolean
  liveTranscript: LiveTranscriptLine[]
  formattedTime: string
  getInitials: (name: string) => string
}>()

const emit = defineEmits<{
  toggleMute: []
  toggleCamera: []
  enableAudio: []
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
        class="remote-stage relative flex h-full min-h-[40vh] flex-1 items-center justify-center overflow-hidden rounded-lg bg-black/85 ring-1 ring-white/10 transition duration-300"
        :class="{ 'remote-stage--speaking': remoteIsSpeaking }"
      >
        <video
          v-show="hasRemoteVideo"
          ref="remoteVideoEl"
          autoplay
          playsinline
          class="h-full w-full object-cover"
        ></video>
        <audio ref="remoteAudioEl" autoplay></audio>

        <div v-if="!hasRemoteVideo" class="flex flex-col items-center gap-4">
          <div
            class="ai-avatar relative flex h-28 w-28 items-center justify-center rounded-full bg-[color:var(--color-accent-ai)] text-3xl font-medium text-white"
            :class="{ 'ai-avatar--speaking': remoteIsSpeaking }"
          >
            <span class="ai-avatar__ring"></span>
            {{ getInitials(remoteParticipantName) }}
          </div>
          <div class="flex flex-col items-center gap-2">
            <span class="text-sm text-white/76">{{ remoteParticipantName }}</span>
            <VoiceLevelMeter :level="remoteAudioLevel" :speaking="remoteIsSpeaking" />
          </div>
        </div>

        <div
          class="absolute bottom-3 left-3 flex items-center gap-2 rounded-md bg-black/60 px-2.5 py-1 font-mono text-xs text-white backdrop-blur-sm"
        >
          <span>{{ remoteParticipantName }}</span>
          <VoiceLevelMeter :level="remoteAudioLevel" :speaking="remoteIsSpeaking" compact />
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
          class="absolute bottom-2 left-2 flex items-center gap-2 rounded-md bg-black/60 px-2 py-0.5 font-mono text-[11px] text-white backdrop-blur-sm"
        >
          <span>{{ t('interviews.roomPage.you') }}</span>
          <VoiceLevelMeter
            :level="localAudioLevel"
            :speaking="localIsSpeaking"
            :muted="isMuted"
            compact
          />
          <span
            v-if="isMuted"
            aria-hidden="true"
            class="pi pi-microphone media-icon-muted text-white"
            style="font-size: 0.65rem"
          ></span>
        </div>
      </div>
    </div>

    <LiveTranscriptOverlay :lines="liveTranscript" />

    <button
      v-if="audioPlaybackBlocked"
      class="absolute bottom-24 left-1/2 z-20 flex -translate-x-1/2 items-center gap-2 rounded-full bg-[color:var(--color-warning)] px-4 py-2 text-sm font-medium text-black shadow-glass-float transition hover:brightness-95"
      @click="emit('enableAudio')"
    >
      <i class="pi pi-volume-up text-base"></i>
      <span>{{ t('interviews.roomPage.enableAudio') }}</span>
    </button>

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
        <span
          aria-hidden="true"
          class="pi pi-microphone text-base"
          :class="{ 'media-icon-muted': isMuted }"
        ></span>
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

<style scoped>
.remote-stage::before {
  position: absolute;
  inset: -20%;
  background:
    radial-gradient(circle at 45% 38%, rgba(54, 211, 153, 0.16), transparent 28%),
    radial-gradient(circle at 55% 62%, rgba(99, 102, 241, 0.18), transparent 32%);
  content: '';
  opacity: 0.35;
  transition: opacity 220ms ease;
}

.remote-stage--speaking {
  box-shadow:
    0 0 0 1px rgba(57, 229, 140, 0.38),
    0 22px 80px rgba(57, 229, 140, 0.16);
}

.remote-stage--speaking::before {
  opacity: 0.72;
  animation: ambient-speak 1.4s ease-in-out infinite alternate;
}

.ai-avatar {
  box-shadow: 0 18px 64px rgba(99, 102, 241, 0.28);
}

.ai-avatar__ring {
  position: absolute;
  inset: -10px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  opacity: 0.8;
}

.ai-avatar--speaking .ai-avatar__ring {
  border-color: rgba(57, 229, 140, 0.72);
  animation: avatar-ring 900ms ease-out infinite;
}

.media-icon-muted {
  position: relative;
}

.media-icon-muted::after {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 1.1em;
  height: 2px;
  border-radius: 999px;
  background: currentColor;
  content: '';
  transform: translate(-50%, -50%) rotate(-45deg);
}

@keyframes ambient-speak {
  from {
    transform: scale(1);
  }
  to {
    transform: scale(1.08);
  }
}

@keyframes avatar-ring {
  from {
    opacity: 0.9;
    transform: scale(0.94);
  }
  to {
    opacity: 0;
    transform: scale(1.2);
  }
}
</style>
