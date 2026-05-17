<script setup lang="ts">
/**
 * RoomPreviewView — device check / preview before joining.
 *
 * T13: video tile stays dark (cinematic); side panel is glass. Controls
 * become floating glass pills.
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import AppSelect from '@/shared/components/AppSelect.vue'
import type { InterviewDetail } from '../types/interview.types'
import type { MediaDeviceInfo } from '@/features/video/types/video.types'

defineProps<{
  interview: InterviewDetail
  isMuted: boolean
  isCameraOff: boolean
  audioDevices: MediaDeviceInfo[]
  videoDevices: MediaDeviceInfo[]
  selectedAudioDeviceId: string
  selectedVideoDeviceId: string
  deviceError: string | null
  hasRequiredDevices: boolean
  getInitials: (name: string) => string
}>()

const emit = defineEmits<{
  toggleMic: []
  toggleCamera: []
  selectAudioDevice: [deviceId: string]
  selectVideoDevice: [deviceId: string]
  joinRoom: []
  cancel: []
}>()

const previewVideoEl = defineModel<HTMLVideoElement | null>('previewVideoEl', { required: true })

const { t } = useI18n()
</script>

<template>
  <div class="room-preview">
    <div class="room-preview__video">
      <div class="room-preview__frame">
        <video
          v-show="!isCameraOff"
          ref="previewVideoEl"
          autoplay
          playsinline
          muted
          class="h-full w-full object-cover"
        ></video>
        <div v-if="isCameraOff" class="room-preview__avatar-wrap">
          <div class="room-preview__avatar">
            {{ interview.candidateName ? getInitials(interview.candidateName) : '?' }}
          </div>
        </div>
      </div>

      <GlassSurface level="float" class="room-preview__controls flex gap-2 !rounded-full p-2">
        <button
          class="flex h-10 w-10 items-center justify-center rounded-full transition-colors"
          :class="
            isMuted
              ? 'bg-[color:var(--color-danger)] text-white'
              : 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] hover:bg-[color:var(--color-surface-sunken)]'
          "
          @click="emit('toggleMic')"
        >
          <span
            aria-hidden="true"
            class="pi pi-microphone text-base"
            :class="{ 'media-icon-muted': isMuted }"
          ></span>
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

    <aside class="room-preview__panel">
      <h2 class="mb-1 text-xl font-semibold text-white">
        {{ t('interviews.roomPage.readyToJoin') }}
      </h2>
      <p class="mb-6 text-sm text-white/68">
        {{ interview.vacancyTitle }}
      </p>
      <div class="mb-4 space-y-3 text-left">
        <div class="room-preview__field">
          <label class="mb-1 block text-xs font-semibold text-white/58">
            {{ t('interviews.preCheck.camera') }}
          </label>
          <AppSelect
            :model-value="selectedVideoDeviceId"
            :options="videoDevices"
            option-label="label"
            option-value="deviceId"
            class="w-full"
            :disabled="!videoDevices.length"
            @update:model-value="emit('selectVideoDevice', String($event ?? ''))"
          />
        </div>
        <div class="room-preview__field">
          <label class="mb-1 block text-xs font-semibold text-white/58">
            {{ t('interviews.preCheck.microphone') }}
          </label>
          <AppSelect
            :model-value="selectedAudioDeviceId"
            :options="audioDevices"
            option-label="label"
            option-value="deviceId"
            class="w-full"
            :disabled="!audioDevices.length"
            @update:model-value="emit('selectAudioDevice', String($event ?? ''))"
          />
        </div>
      </div>
      <p
        v-if="deviceError"
        class="mb-4 rounded-md border border-[color:var(--color-warning)]/40 bg-[color:var(--color-warning)]/10 px-3 py-2 text-left text-xs text-[color:var(--color-warning)]"
      >
        {{ deviceError }}
      </p>
      <Button
        :label="t('interviews.roomPage.joinNow')"
        icon="pi pi-video"
        class="w-full"
        size="large"
        :disabled="!hasRequiredDevices"
        @click="emit('joinRoom')"
      />
      <button class="mt-3 w-full text-sm text-white/58 hover:text-white" @click="emit('cancel')">
        {{ t('interviews.roomPage.goBack') }}
      </button>
    </aside>
  </div>
</template>

<style scoped>
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
</style>

<style>
@import './RoomPreviewView.css';
</style>
