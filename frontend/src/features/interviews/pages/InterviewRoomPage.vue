<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import {
  Room,
  RoomEvent,
  Track,
  type RemoteTrack,
  type RemoteTrackPublication,
  type RemoteParticipant,
  type LocalTrackPublication,
} from 'livekit-client'
import { interviewService } from '../services/interview.service'
import type { InterviewDetail } from '../types/interview.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const token = computed(() => route.params.token as string)
const interview = ref<InterviewDetail | null>(null)
const loading = ref(true)
const fetchError = ref<string | null>(null)

type ConnectionState = 'idle' | 'preview' | 'connecting' | 'connected' | 'error' | 'ended'
const connectionState = ref<ConnectionState>('idle')
const errorMessage = ref<string | null>(null)

// Video elements
const previewVideoEl = ref<HTMLVideoElement | null>(null)
const localVideoEl = ref<HTMLVideoElement | null>(null)
const remoteVideoEl = ref<HTMLVideoElement | null>(null)
const remoteAudioEl = ref<HTMLAudioElement | null>(null)

// State
const isMuted = ref(false)
const isCameraOff = ref(false)
const elapsedTime = ref(0)
const hasRemoteVideo = ref(false)
const remoteParticipantName = ref('AI Interviewer')
const previewStream = ref<MediaStream | null>(null)

let timerInterval: ReturnType<typeof setInterval> | null = null
let room: Room | null = null

const LIVEKIT_URL = import.meta.env.VITE_LIVEKIT_URL as string | undefined

const formattedTime = computed(() => {
  const mins = Math.floor(elapsedTime.value / 60)
  const secs = elapsedTime.value % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

const canJoin = computed(() => {
  if (!interview.value) return false
  return interview.value.status === 'pending' || interview.value.status === 'in_progress'
})

onMounted(async () => {
  try {
    const data = await interviewService.getInterviewByToken(token.value)
    interview.value = data

    if (data.status === 'completed') {
      fetchError.value = 'This interview has already been completed.'
    } else if (data.status === 'expired') {
      fetchError.value = 'This interview link has expired.'
    } else if (data.status === 'cancelled') {
      fetchError.value = 'This vacancy has been closed.'
    }
  } catch (err: unknown) {
    const axiosErr = err as { response?: { data?: { detail?: string; message?: string } } }
    fetchError.value =
      axiosErr.response?.data?.detail ??
      axiosErr.response?.data?.message ??
      'Failed to load interview.'
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  stopPreview()
  disconnect()
})

// --- Preview ---
async function startPreview(): Promise<void> {
  connectionState.value = 'preview'
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    previewStream.value = stream
    await nextTick()
    if (previewVideoEl.value) {
      previewVideoEl.value.srcObject = stream
    }
  } catch {
    errorMessage.value = 'Could not access camera or microphone. Please check your permissions.'
    connectionState.value = 'error'
  }
}

function stopPreview(): void {
  if (previewStream.value) {
    previewStream.value.getTracks().forEach((t) => t.stop())
    previewStream.value = null
  }
}

function togglePreviewMic(): void {
  if (!previewStream.value) return
  isMuted.value = !isMuted.value
  previewStream.value.getAudioTracks().forEach((t) => {
    t.enabled = !isMuted.value
  })
}

function togglePreviewCamera(): void {
  if (!previewStream.value) return
  isCameraOff.value = !isCameraOff.value
  previewStream.value.getVideoTracks().forEach((t) => {
    t.enabled = !isCameraOff.value
  })
}

// --- Room connection ---
async function joinRoom(): Promise<void> {
  stopPreview()

  if (!LIVEKIT_URL) {
    errorMessage.value = 'LiveKit server URL is not configured.'
    connectionState.value = 'error'
    return
  }
  if (!interview.value?.candidateToken) {
    errorMessage.value = 'No interview token available. Please try again.'
    connectionState.value = 'error'
    return
  }

  connectionState.value = 'connecting'
  errorMessage.value = null

  try {
    // Start the interview if still pending
    if (interview.value.status === 'pending') {
      const started = await interviewService.startInterview(token.value)
      interview.value = started
    }

    room = new Room()

    room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed)
    room.on(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed)
    room.on(RoomEvent.ParticipantConnected, handleParticipantConnected)
    room.on(RoomEvent.Disconnected, handleDisconnected)

    await room.connect(LIVEKIT_URL, interview.value.candidateToken)
    await room.localParticipant.enableCameraAndMicrophone()

    // Apply pre-join toggle states
    if (isMuted.value) {
      await room.localParticipant.setMicrophoneEnabled(false)
    }
    if (isCameraOff.value) {
      await room.localParticipant.setCameraEnabled(false)
    }

    // Attach local video
    await nextTick()
    room.localParticipant.videoTrackPublications.forEach((pub: LocalTrackPublication) => {
      if (pub.track && localVideoEl.value) {
        pub.track.attach(localVideoEl.value)
      }
    })

    // Check existing remote participants
    room.remoteParticipants.forEach((p) => {
      remoteParticipantName.value = p.name || p.identity || 'AI Interviewer'
      p.trackPublications.forEach((pub) => {
        if (pub.track) {
          handleTrackSubscribed(pub.track as RemoteTrack, pub as RemoteTrackPublication, p)
        }
      })
    })

    connectionState.value = 'connected'
    startTimer()
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Failed to connect'
    errorMessage.value = `Connection failed: ${msg}`
    connectionState.value = 'error'
  }
}

function handleTrackSubscribed(
  track: RemoteTrack,
  _publication: RemoteTrackPublication,
  participant: RemoteParticipant,
): void {
  remoteParticipantName.value = participant.name || participant.identity || 'AI Interviewer'
  if (track.kind === Track.Kind.Video) {
    hasRemoteVideo.value = true
    if (remoteVideoEl.value) track.attach(remoteVideoEl.value)
  }
  if (track.kind === Track.Kind.Audio) {
    if (remoteAudioEl.value) track.attach(remoteAudioEl.value)
  }
}

function handleTrackUnsubscribed(track: RemoteTrack): void {
  if (track.kind === Track.Kind.Video) hasRemoteVideo.value = false
  track.detach()
}

function handleParticipantConnected(participant: RemoteParticipant): void {
  remoteParticipantName.value = participant.name || participant.identity || 'AI Interviewer'
}

function handleDisconnected(): void {
  connectionState.value = 'ended'
  stopTimer()
}

function disconnect(): void {
  if (room) {
    room.disconnect()
    room = null
  }
  stopTimer()
}

function toggleMute(): void {
  if (!room) return
  isMuted.value = !isMuted.value
  room.localParticipant.setMicrophoneEnabled(!isMuted.value)
}

function toggleCamera(): void {
  if (!room) return
  isCameraOff.value = !isCameraOff.value
  room.localParticipant.setCameraEnabled(!isCameraOff.value)
}

function leaveInterview(): void {
  disconnect()
  connectionState.value = 'ended'
}

function startTimer(): void {
  elapsedTime.value = 0
  timerInterval = setInterval(() => {
    elapsedTime.value++
  }, 1000)
}

function stopTimer(): void {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function getInitials(name: string): string {
  return (
    name
      .split(' ')
      .map((n) => n.charAt(0))
      .slice(0, 2)
      .join('')
      .toUpperCase() || '?'
  )
}
</script>

<template>
  <div class="flex h-screen flex-col bg-[#202124]">
    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <i class="pi pi-spinner pi-spin text-4xl text-gray-400"></i>
    </div>

    <!-- Fetch error -->
    <div v-else-if="fetchError" class="flex flex-1 items-center justify-center p-8">
      <div class="max-w-md text-center">
        <i class="pi pi-exclamation-triangle mb-4 text-5xl text-red-400"></i>
        <p class="mb-4 text-white">{{ fetchError }}</p>
        <Button :label="t('errors.goBack')" severity="secondary" @click="router.back()" />
      </div>
    </div>

    <!-- Main states -->
    <template v-else-if="interview">
      <!-- ======= IDLE — Welcome card ======= -->
      <div v-if="connectionState === 'idle'" class="flex flex-1 items-center justify-center p-6">
        <div class="w-full max-w-md rounded-2xl bg-[#303134] p-8 text-center shadow-2xl">
          <div
            class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-blue-500/20"
          >
            <i class="pi pi-video text-3xl text-blue-400"></i>
          </div>
          <h2 class="mb-1 text-xl font-medium text-white">AI Video Interview</h2>
          <p class="mb-1 text-sm text-gray-400">{{ interview.vacancyTitle }}</p>
          <p class="mb-6 text-xs text-gray-500">{{ interview.durationMinutes }} min</p>

          <div class="mb-6 rounded-xl bg-[#3c4043] p-4 text-left text-sm text-gray-300">
            <p class="mb-2 font-medium text-white">Before you join:</p>
            <ul class="space-y-1.5 text-gray-400">
              <li class="flex items-start gap-2">
                <i class="pi pi-wifi mt-0.5 text-xs text-green-400"></i> Stable internet connection
              </li>
              <li class="flex items-start gap-2">
                <i class="pi pi-volume-up mt-0.5 text-xs text-green-400"></i> Quiet, well-lit room
              </li>
              <li class="flex items-start gap-2">
                <i class="pi pi-camera mt-0.5 text-xs text-green-400"></i> Allow camera & microphone
              </li>
              <li class="flex items-start gap-2">
                <i class="pi pi-user mt-0.5 text-xs text-green-400"></i> Keep your face visible
              </li>
            </ul>
          </div>

          <Button
            v-if="canJoin"
            label="Check devices & join"
            icon="pi pi-arrow-right"
            icon-pos="right"
            class="w-full"
            size="large"
            @click="startPreview"
          />
          <p v-else class="text-sm text-yellow-400">
            Interview is {{ interview.status.replace(/_/g, ' ') }}. Cannot join.
          </p>
        </div>
      </div>

      <!-- ======= PREVIEW — Camera/mic check (Google Meet style) ======= -->
      <div
        v-else-if="connectionState === 'preview'"
        class="flex flex-1 items-center justify-center gap-8 p-6"
      >
        <!-- Preview video -->
        <div class="relative w-full max-w-xl overflow-hidden rounded-2xl bg-[#303134]">
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
                class="flex h-24 w-24 items-center justify-center rounded-full bg-blue-600 text-3xl font-medium text-white"
              >
                {{ interview.candidateName ? getInitials(interview.candidateName) : '?' }}
              </div>
            </div>
          </div>

          <!-- Preview controls overlay -->
          <div class="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-3">
            <button
              class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
              :class="
                isMuted ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'
              "
              @click="togglePreviewMic"
            >
              <i
                :class="isMuted ? 'pi pi-microphone-slash' : 'pi pi-microphone'"
                class="text-lg"
              ></i>
            </button>
            <button
              class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
              :class="
                isCameraOff ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'
              "
              @click="togglePreviewCamera"
            >
              <i :class="isCameraOff ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-lg"></i>
            </button>
          </div>
        </div>

        <!-- Join panel -->
        <div class="w-72 shrink-0 text-center">
          <h2 class="mb-1 text-xl font-medium text-white">Ready to join?</h2>
          <p class="mb-6 text-sm text-gray-400">{{ interview.vacancyTitle }}</p>
          <Button
            label="Join now"
            icon="pi pi-video"
            class="w-full"
            size="large"
            @click="joinRoom"
          />
          <button
            class="mt-3 text-sm text-gray-400 hover:text-white"
            @click="
              stopPreview()
              connectionState = 'idle'
            "
          >
            Go back
          </button>
        </div>
      </div>

      <!-- ======= CONNECTING ======= -->
      <div
        v-else-if="connectionState === 'connecting'"
        class="flex flex-1 items-center justify-center"
      >
        <div class="text-center">
          <i class="pi pi-spinner pi-spin mb-4 text-5xl text-blue-400"></i>
          <p class="text-lg text-white">Joining interview...</p>
        </div>
      </div>

      <!-- ======= ERROR ======= -->
      <div
        v-else-if="connectionState === 'error'"
        class="flex flex-1 items-center justify-center p-8"
      >
        <div class="w-full max-w-md rounded-2xl bg-[#303134] p-8 text-center shadow-2xl">
          <div
            class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-500/20"
          >
            <i class="pi pi-exclamation-triangle text-2xl text-red-400"></i>
          </div>
          <h2 class="mb-2 text-lg font-medium text-white">Something went wrong</h2>
          <p class="mb-6 text-sm text-gray-400">{{ errorMessage }}</p>
          <div class="flex justify-center gap-3">
            <Button
              :label="t('errors.goBack')"
              severity="secondary"
              outlined
              @click="connectionState = 'idle'"
            />
            <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" @click="startPreview" />
          </div>
        </div>
      </div>

      <!-- ======= CONNECTED — Video room (Google Meet layout) ======= -->
      <div v-else-if="connectionState === 'connected'" class="flex flex-1 flex-col">
        <!-- Top bar -->
        <header class="flex items-center justify-between px-4 py-2">
          <div class="flex items-center gap-3">
            <span class="text-sm font-medium text-white">{{ interview.vacancyTitle }}</span>
            <span class="rounded bg-[#3c4043] px-2 py-0.5 text-xs text-gray-300">AI Interview</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="font-mono text-sm text-gray-400">{{ formattedTime }}</span>
            <span class="flex items-center gap-1.5 text-xs text-green-400">
              <span class="h-1.5 w-1.5 rounded-full bg-green-400"></span>
              Connected
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

            <!-- Avatar fallback when no remote video -->
            <div v-if="!hasRemoteVideo" class="flex flex-col items-center gap-3">
              <div
                class="flex h-24 w-24 items-center justify-center rounded-full bg-purple-600 text-3xl font-medium text-white"
              >
                {{ getInitials(remoteParticipantName) }}
              </div>
              <span class="text-sm text-gray-400">{{ remoteParticipantName }}</span>
            </div>

            <!-- Name label -->
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
              <span>You</span>
              <i
                v-if="isMuted"
                class="pi pi-microphone-slash text-red-400"
                style="font-size: 0.65rem"
              ></i>
            </div>
          </div>
        </div>

        <!-- Bottom control bar (Google Meet style) -->
        <div class="flex items-center justify-center bg-[#202124] px-4 py-3">
          <div class="flex items-center gap-3">
            <!-- Mic -->
            <button
              class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
              :class="
                isMuted ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'
              "
              :title="isMuted ? 'Unmute' : 'Mute'"
              @click="toggleMute"
            >
              <i
                :class="isMuted ? 'pi pi-microphone-slash' : 'pi pi-microphone'"
                class="text-lg"
              ></i>
            </button>

            <!-- Camera -->
            <button
              class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
              :class="
                isCameraOff ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'
              "
              :title="isCameraOff ? 'Turn on camera' : 'Turn off camera'"
              @click="toggleCamera"
            >
              <i :class="isCameraOff ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-lg"></i>
            </button>

            <!-- Leave -->
            <button
              class="ml-4 flex h-12 w-28 items-center justify-center gap-2 rounded-full bg-red-500 text-white transition-colors hover:bg-red-600"
              title="Leave interview"
              @click="leaveInterview"
            >
              <i class="pi pi-phone text-lg" style="transform: rotate(135deg)"></i>
              <span class="text-sm font-medium">Leave</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ======= ENDED ======= -->
      <div
        v-else-if="connectionState === 'ended'"
        class="flex flex-1 items-center justify-center p-8"
      >
        <div class="w-full max-w-md rounded-2xl bg-[#303134] p-8 text-center shadow-2xl">
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20"
          >
            <i class="pi pi-check text-3xl text-green-400"></i>
          </div>
          <h2 class="mb-2 text-xl font-medium text-white">
            {{ t('interviews.status.completed') }}
          </h2>
          <p class="mb-1 text-gray-400">Duration: {{ formattedTime }}</p>
          <p class="mb-6 text-sm text-gray-500">
            Thank you! Your responses are being reviewed by our AI. You'll receive results shortly.
          </p>
          <Button
            :label="t('errors.goHome')"
            icon="pi pi-home"
            class="w-full"
            @click="router.push('/')"
          />
        </div>
      </div>
    </template>
  </div>
</template>
