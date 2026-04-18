<script setup lang="ts">
import { useI18n } from 'vue-i18n'
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
  <div class="flex flex-1 flex-col">
    <!-- Top bar -->
    <header class="flex items-center justify-between px-4 py-2">
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-white">{{ interview.vacancyTitle }}</span>
        <span class="rounded bg-[#3c4043] px-2 py-0.5 text-xs text-gray-300">{{
          t('interviews.roomPage.aiInterview')
        }}</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="font-mono text-sm text-gray-400">{{ formattedTime }}</span>
        <span class="flex items-center gap-1.5 text-xs text-green-400">
          <span class="h-1.5 w-1.5 rounded-full bg-green-400"></span>
          {{ t('interviews.roomPage.connected') }}
        </span>
      </div>
    </header>

    <!-- Video grid -->
    <div class="flex flex-1 items-center justify-center gap-3 px-3 pb-3">
      <!-- Remote participant (main/large) -->
      <div
        class="relative flex h-full flex-1 items-center justify-center overflow-hidden rounded-xl bg-[#303134]"
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
            class="flex h-24 w-24 items-center justify-center rounded-full bg-purple-600 text-3xl font-medium text-white"
          >
            {{ getInitials(remoteParticipantName) }}
          </div>
          <span class="text-sm text-gray-400">{{ remoteParticipantName }}</span>
        </div>

        <div
          v-if="hasRemoteVideo"
          class="absolute bottom-3 left-3 flex items-center gap-2 rounded-md bg-black/60 px-2.5 py-1 backdrop-blur-sm"
        >
          <span class="text-sm text-white">{{ remoteParticipantName }}</span>
        </div>
      </div>

      <!-- Local participant (side/small) -->
      <div class="relative h-48 w-64 shrink-0 overflow-hidden rounded-xl bg-[#303134]">
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
            class="flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-lg font-medium text-white"
          >
            {{ interview.candidateName ? getInitials(interview.candidateName) : 'Y' }}
          </div>
        </div>
        <div
          class="absolute bottom-2 left-2 flex items-center gap-1.5 rounded-md bg-black/60 px-2 py-0.5 text-xs text-white backdrop-blur-sm"
        >
          <span>{{ t('interviews.roomPage.you') }}</span>
          <i
            v-if="isMuted"
            class="pi pi-microphone-slash text-red-400"
            style="font-size: 0.65rem"
          ></i>
        </div>
      </div>
    </div>

    <!-- Bottom control bar -->
    <div class="flex items-center justify-center bg-[#202124] px-4 py-3">
      <div class="flex items-center gap-3">
        <button
          class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
          :class="isMuted ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'"
          :title="isMuted ? t('interviews.roomPage.unmute') : t('interviews.roomPage.mute')"
          @click="emit('toggleMute')"
        >
          <i :class="isMuted ? 'pi pi-microphone-slash' : 'pi pi-microphone'" class="text-lg"></i>
        </button>

        <button
          class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
          :class="
            isCameraOff ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'
          "
          :title="
            isCameraOff
              ? t('interviews.roomPage.turnOnCamera')
              : t('interviews.roomPage.turnOffCamera')
          "
          @click="emit('toggleCamera')"
        >
          <i :class="isCameraOff ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-lg"></i>
        </button>

        <button
          class="ml-4 flex h-12 w-28 items-center justify-center gap-2 rounded-full bg-red-500 text-white transition-colors hover:bg-red-600"
          :title="t('interviews.roomPage.leaveInterview')"
          @click="emit('leave')"
        >
          <i class="pi pi-phone text-lg" style="transform: rotate(135deg)"></i>
          <span class="text-sm font-medium">{{ t('interviews.roomPage.leave') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
