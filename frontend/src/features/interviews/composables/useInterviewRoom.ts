import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
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

export type ConnectionState = 'idle' | 'preview' | 'connecting' | 'connected' | 'error' | 'ended'
const LIVEKIT_URL = import.meta.env.VITE_LIVEKIT_URL as string | undefined

export function useInterviewRoom(token: () => string) {
  const router = useRouter()
  const interview = ref<InterviewDetail | null>(null)
  const loading = ref(true)
  const fetchError = ref<string | null>(null)
  const connectionState = ref<ConnectionState>('idle')
  const errorMessage = ref<string | null>(null)
  const previewVideoEl = ref<HTMLVideoElement | null>(null)
  const localVideoEl = ref<HTMLVideoElement | null>(null)
  const remoteVideoEl = ref<HTMLVideoElement | null>(null)
  const remoteAudioEl = ref<HTMLAudioElement | null>(null)
  const isMuted = ref(false)
  const isCameraOff = ref(false)
  const elapsedTime = ref(0)
  const hasRemoteVideo = ref(false)
  const remoteParticipantName = ref('AI Interviewer')
  const previewStream = ref<MediaStream | null>(null)
  let timerInterval: ReturnType<typeof setInterval> | null = null
  let room: Room | null = null

  const formattedTime = computed(() => {
    const m = Math.floor(elapsedTime.value / 60),
      s = elapsedTime.value % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  })
  const canJoin = computed(
    () => interview.value?.status === 'pending' || interview.value?.status === 'in_progress',
  )
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

  async function startPreview(): Promise<void> {
    connectionState.value = 'preview'
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      previewStream.value = stream
      await nextTick()
      if (previewVideoEl.value) previewVideoEl.value.srcObject = stream
    } catch {
      errorMessage.value = 'Could not access camera or microphone. Please check your permissions.'
      connectionState.value = 'error'
    }
  }
  function stopPreview(): void {
    previewStream.value?.getTracks().forEach((t) => t.stop())
    previewStream.value = null
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
  function cancelPreview(): void {
    stopPreview()
    connectionState.value = 'idle'
  }

  function handleTrackSubscribed(
    track: RemoteTrack,
    _pub: RemoteTrackPublication,
    participant: RemoteParticipant,
  ): void {
    remoteParticipantName.value = participant.name || participant.identity || 'AI Interviewer'
    if (track.kind === Track.Kind.Video) {
      hasRemoteVideo.value = true
      if (remoteVideoEl.value) track.attach(remoteVideoEl.value)
    }
    if (track.kind === Track.Kind.Audio && remoteAudioEl.value) track.attach(remoteAudioEl.value)
  }
  function handleTrackUnsubscribed(track: RemoteTrack): void {
    if (track.kind === Track.Kind.Video) hasRemoteVideo.value = false
    track.detach()
  }
  function handleParticipantConnected(p: RemoteParticipant): void {
    remoteParticipantName.value = p.name || p.identity || 'AI Interviewer'
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
      if (interview.value.status === 'pending')
        interview.value = await interviewService.startInterview(token())
      room = new Room()
      room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed)
      room.on(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed)
      room.on(RoomEvent.ParticipantConnected, handleParticipantConnected)
      room.on(RoomEvent.Disconnected, handleDisconnected)
      await room.connect(LIVEKIT_URL, interview.value.candidateToken)
      await room.localParticipant.enableCameraAndMicrophone()
      if (isMuted.value) await room.localParticipant.setMicrophoneEnabled(false)
      if (isCameraOff.value) await room.localParticipant.setCameraEnabled(false)
      await nextTick()
      room.localParticipant.videoTrackPublications.forEach((pub: LocalTrackPublication) => {
        if (pub.track && localVideoEl.value) pub.track.attach(localVideoEl.value)
      })
      room.remoteParticipants.forEach((p) => {
        remoteParticipantName.value = p.name || p.identity || 'AI Interviewer'
        p.trackPublications.forEach((pub) => {
          if (pub.track)
            handleTrackSubscribed(pub.track as RemoteTrack, pub as RemoteTrackPublication, p)
        })
      })
      connectionState.value = 'connected'
      startTimer()
    } catch (err: unknown) {
      errorMessage.value = `Connection failed: ${err instanceof Error ? err.message : 'Failed to connect'}`
      connectionState.value = 'error'
    }
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

  onMounted(async () => {
    try {
      const data = await interviewService.getInterviewByToken(token())
      interview.value = data
      if (data.status === 'completed')
        fetchError.value = 'This interview has already been completed.'
      else if (data.status === 'expired') fetchError.value = 'This interview link has expired.'
      else if (data.status === 'cancelled') fetchError.value = 'This vacancy has been closed.'
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

  return {
    interview,
    loading,
    fetchError,
    connectionState,
    errorMessage,
    previewVideoEl,
    localVideoEl,
    remoteVideoEl,
    remoteAudioEl,
    isMuted,
    isCameraOff,
    hasRemoteVideo,
    remoteParticipantName,
    formattedTime,
    canJoin,
    getInitials,
    startPreview,
    stopPreview,
    cancelPreview,
    togglePreviewMic,
    togglePreviewCamera,
    joinRoom,
    toggleMute,
    toggleCamera,
    leaveInterview,
    router,
  }
}
