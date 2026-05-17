<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LiveTranscriptOverlay from './LiveTranscriptOverlay.vue'
import RoomControlBar from './RoomControlBar.vue'
import RoomParticipantTile from './RoomParticipantTile.vue'
import RoomTopBar from './RoomTopBar.vue'
import type { LiveTranscriptLine } from '../composables/useInterviewRoom'
import type { InterviewDetail } from '../types/interview.types'

const props = defineProps<{
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

const candidateInitials = computed(() =>
  props.interview.candidateName ? props.getInitials(props.interview.candidateName) : 'Y',
)
const remoteInitials = computed(() => props.getInitials(props.remoteParticipantName))
</script>

<template>
  <div class="room-shell">
    <div class="room-shell__ambient"></div>

    <div class="room-shell__top">
      <RoomTopBar
        :title="interview.vacancyTitle"
        :formatted-time="formattedTime"
        :remote-is-speaking="remoteIsSpeaking"
      />
    </div>

    <main class="room-shell__stage">
      <RoomParticipantTile
        v-model:video-el="remoteVideoEl"
        class="room-shell__remote"
        :name="remoteParticipantName"
        :initials="remoteInitials"
        :has-video="hasRemoteVideo"
        :is-speaking="remoteIsSpeaking"
        :audio-level="remoteAudioLevel"
        accent="ai"
      />

      <audio ref="remoteAudioEl" autoplay></audio>

      <RoomParticipantTile
        v-model:video-el="localVideoEl"
        class="room-shell__self"
        :name="t('interviews.roomPage.you')"
        :initials="candidateInitials"
        :has-video="!isCameraOff"
        :is-speaking="localIsSpeaking"
        :audio-level="localAudioLevel"
        :muted="isMuted"
        compact
      />
    </main>

    <LiveTranscriptOverlay :lines="liveTranscript" />

    <button v-if="audioPlaybackBlocked" class="room-shell__audio" @click="emit('enableAudio')">
      <i class="pi pi-volume-up text-base"></i>
      <span>{{ t('interviews.roomPage.enableAudio') }}</span>
    </button>

    <div class="room-shell__controls">
      <RoomControlBar
        :is-muted="isMuted"
        :is-camera-off="isCameraOff"
        @toggle-mute="emit('toggleMute')"
        @toggle-camera="emit('toggleCamera')"
        @leave="emit('leave')"
      />
    </div>
  </div>
</template>

<style>
@import './RoomConnectedView.css';
</style>
