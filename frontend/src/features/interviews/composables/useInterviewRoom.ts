import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Room,
  RoomEvent,
  Track,
  type Participant,
  type RemoteTrack,
  type RemoteTrackPublication,
  type RemoteParticipant,
  type LocalTrackPublication,
  type TrackPublication,
  type TranscriptionSegment,
} from 'livekit-client'
import { interviewService } from '../services/interview.service'
import { useInterviewDevices } from './useInterviewDevices'
import type { InterviewDetail } from '../types/interview.types'

export type ConnectionState = 'idle' | 'preview' | 'connecting' | 'connected' | 'error' | 'ended'
export interface LiveTranscriptLine {
  id: string
  speaker: string
  text: string
  final: boolean
  receivedAt: number
}

const LIVEKIT_URL = import.meta.env.VITE_LIVEKIT_URL as string | undefined
const AUDIO_SPEAKING_THRESHOLD = 0.015

function normalizeAudioLevel(level: number | undefined): number {
  const raw = Math.max(0, level ?? 0)
  return Math.min(1, raw * 8)
}

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
  const elapsedTime = ref(0)
  const hasRemoteVideo = ref(false)
  const audioPlaybackBlocked = ref(false)
  const remoteParticipantName = ref('AI Interviewer')
  const localAudioLevel = ref(0)
  const remoteAudioLevel = ref(0)
  const localIsSpeaking = ref(false)
  const remoteIsSpeaking = ref(false)
  const liveTranscript = ref<LiveTranscriptLine[]>([])
  const devices = useInterviewDevices(previewVideoEl)
  let timerInterval: ReturnType<typeof setInterval> | null = null
  let volumeInterval: ReturnType<typeof setInterval> | null = null
  let statusPollInterval: ReturnType<typeof setInterval> | null = null
  let room: Room | null = null
  const transcriptById = new Map<string, LiveTranscriptLine>()

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
    await nextTick()
    await devices.startPreview()
  }
  function cancelPreview(): void {
    devices.stopPreview()
    connectionState.value = 'idle'
  }

  async function enableRoomAudio(): Promise<void> {
    if (!room) return
    try {
      await room.startAudio()
      await remoteAudioEl.value?.play()
      audioPlaybackBlocked.value = false
    } catch {
      audioPlaybackBlocked.value = true
    }
  }

  function attachLocalVideoPublication(publication: LocalTrackPublication): void {
    if (publication.kind !== Track.Kind.Video || !publication.track || !localVideoEl.value) return
    publication.track.attach(localVideoEl.value)
    void localVideoEl.value.play()
  }

  function attachLocalVideoTracks(): void {
    if (!room) return
    room.localParticipant.videoTrackPublications.forEach(attachLocalVideoPublication)
  }

  function detachLocalVideo(): void {
    if (localVideoEl.value) localVideoEl.value.srcObject = null
  }

  function attachRemoteTrack(track: RemoteTrack, participant: RemoteParticipant): void {
    remoteParticipantName.value = participant.name || participant.identity || 'AI Interviewer'
    if (track.kind === Track.Kind.Video) {
      hasRemoteVideo.value = true
      if (remoteVideoEl.value) track.attach(remoteVideoEl.value)
    }
    if (track.kind === Track.Kind.Audio && remoteAudioEl.value) {
      track.attach(remoteAudioEl.value)
      remoteAudioEl.value.autoplay = true
      void enableRoomAudio()
    }
  }

  function handleTrackSubscribed(
    track: RemoteTrack,
    _pub: RemoteTrackPublication,
    participant: RemoteParticipant,
  ): void {
    attachRemoteTrack(track, participant)
  }

  function handleTrackUnsubscribed(track: RemoteTrack): void {
    if (track.kind === Track.Kind.Video) hasRemoteVideo.value = false
    track.detach()
  }

  function attachExistingRemoteTracks(): void {
    if (!room) return
    hasRemoteVideo.value = false
    room.remoteParticipants.forEach((participant) => {
      remoteParticipantName.value =
        participant.name || participant.identity || remoteParticipantName.value
      participant.trackPublications.forEach((publication) => {
        if (publication.track) attachRemoteTrack(publication.track as RemoteTrack, participant)
      })
    })
  }

  function handleParticipantConnected(p: RemoteParticipant): void {
    remoteParticipantName.value = p.name || p.identity || 'AI Interviewer'
  }

  function finishRoom(): void {
    disconnect()
    connectionState.value = 'ended'
  }

  function handleParticipantDisconnected(p: RemoteParticipant): void {
    remoteParticipantName.value = p.name || p.identity || remoteParticipantName.value
    if (connectionState.value === 'connected') finishRoom()
  }

  function updateAudioLevels(): void {
    if (!room) return
    const localRawLevel = room.localParticipant.audioLevel || 0
    localAudioLevel.value = normalizeAudioLevel(localRawLevel)
    localIsSpeaking.value =
      room.localParticipant.isSpeaking || localRawLevel > AUDIO_SPEAKING_THRESHOLD
    let loudestRemote = 0
    let remoteSpeaking = false
    room.remoteParticipants.forEach((participant) => {
      const remoteRawLevel = participant.audioLevel || 0
      loudestRemote = Math.max(loudestRemote, remoteRawLevel)
      const participantSpeaking =
        participant.isSpeaking || remoteRawLevel > AUDIO_SPEAKING_THRESHOLD
      remoteSpeaking = remoteSpeaking || participantSpeaking
      if (participantSpeaking) {
        remoteParticipantName.value = participant.name || participant.identity || 'AI Interviewer'
      }
    })
    remoteAudioLevel.value = normalizeAudioLevel(loudestRemote)
    remoteIsSpeaking.value = remoteSpeaking
  }

  function startVolumeMeter(): void {
    stopVolumeMeter()
    updateAudioLevels()
    volumeInterval = setInterval(updateAudioLevels, 120)
  }

  function stopVolumeMeter(): void {
    if (volumeInterval) {
      clearInterval(volumeInterval)
      volumeInterval = null
    }
    localAudioLevel.value = 0
    remoteAudioLevel.value = 0
    localIsSpeaking.value = false
    remoteIsSpeaking.value = false
  }

  function stopStatusPolling(): void {
    if (statusPollInterval) {
      clearInterval(statusPollInterval)
      statusPollInterval = null
    }
  }

  async function refreshInterviewStatus(): Promise<void> {
    try {
      const latest = await interviewService.getInterviewByToken(token())
      interview.value = { ...interview.value, ...latest } as InterviewDetail
      if (['completed', 'cancelled', 'expired'].includes(latest.status)) {
        finishRoom()
      }
    } catch {
      // Keep the LiveKit room active during short API/network interruptions.
    }
  }

  function startStatusPolling(): void {
    stopStatusPolling()
    statusPollInterval = setInterval(() => void refreshInterviewStatus(), 3000)
  }

  function handleTranscriptionReceived(
    segments: TranscriptionSegment[],
    participant?: Participant,
    _publication?: TrackPublication,
  ): void {
    for (const segment of segments) {
      if (!segment.text.trim()) continue
      const speaker = participant?.isLocal
        ? 'You'
        : participant?.name || participant?.identity || 'AI Interviewer'
      transcriptById.set(segment.id, {
        id: segment.id,
        speaker,
        text: segment.text,
        final: segment.final,
        receivedAt: segment.lastReceivedTime || Date.now(),
      })
    }
    liveTranscript.value = Array.from(transcriptById.values())
      .sort((a, b) => a.receivedAt - b.receivedAt)
      .slice(-5)
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
    stopVolumeMeter()
    stopStatusPolling()
  }
  function disconnect(): void {
    if (room) {
      room.disconnect()
      room = null
    }
    detachLocalVideo()
    hasRemoteVideo.value = false
    audioPlaybackBlocked.value = false
    transcriptById.clear()
    liveTranscript.value = []
    stopTimer()
    stopVolumeMeter()
    stopStatusPolling()
  }

  async function joinRoom(): Promise<void> {
    devices.stopPreview()
    if (!LIVEKIT_URL) {
      errorMessage.value = 'LiveKit server URL is not configured.'
      connectionState.value = 'error'
      return
    }
    connectionState.value = 'connecting'
    errorMessage.value = null
    try {
      interview.value = await interviewService.getRoomJoinInfo(token())
      if (!interview.value.candidateToken) {
        throw new Error('No interview token available. Please try again.')
      }
      room = new Room()
      room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed)
      room.on(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed)
      room.on(RoomEvent.LocalTrackPublished, attachLocalVideoPublication)
      room.on(RoomEvent.LocalTrackUnpublished, detachLocalVideo)
      room.on(RoomEvent.AudioPlaybackStatusChanged, () => {
        audioPlaybackBlocked.value = !room?.canPlaybackAudio
      })
      room.on(RoomEvent.ParticipantConnected, handleParticipantConnected)
      room.on(RoomEvent.ParticipantDisconnected, handleParticipantDisconnected)
      room.on(RoomEvent.Disconnected, handleDisconnected)
      room.on(RoomEvent.ActiveSpeakersChanged, updateAudioLevels)
      room.on(RoomEvent.TranscriptionReceived, handleTranscriptionReceived)
      await room.connect(LIVEKIT_URL, interview.value.candidateToken)
      await enableRoomAudio()
      await devices.publishLocalMedia(room.localParticipant)
      connectionState.value = 'connected'
      await nextTick()
      attachLocalVideoTracks()
      attachExistingRemoteTracks()
      await enableRoomAudio()
      startTimer()
      startVolumeMeter()
      startStatusPolling()
    } catch (err: unknown) {
      errorMessage.value = `Connection failed: ${err instanceof Error ? err.message : 'Failed to connect'}`
      connectionState.value = 'error'
    }
  }
  function toggleMute(): void {
    if (!room) return
    devices.isMuted.value = !devices.isMuted.value
    room.localParticipant.setMicrophoneEnabled(!devices.isMuted.value)
  }
  async function toggleCamera(): Promise<void> {
    if (!room) return
    const shouldEnable = devices.isCameraOff.value
    if (!shouldEnable) {
      await room.localParticipant.setCameraEnabled(false)
      devices.isCameraOff.value = true
      detachLocalVideo()
      return
    }

    try {
      const publication = await room.localParticipant.setCameraEnabled(
        true,
        devices.liveKitVideoOptions(),
      )
      devices.isCameraOff.value = false
      await nextTick()
      if (publication) attachLocalVideoPublication(publication)
      attachLocalVideoTracks()
    } catch {
      devices.isCameraOff.value = true
      detachLocalVideo()
    }
  }
  function leaveInterview(): void {
    finishRoom()
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
    devices.stopPreview()
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
    isMuted: devices.isMuted,
    isCameraOff: devices.isCameraOff,
    audioPlaybackBlocked,
    audioDevices: devices.audioDevices,
    videoDevices: devices.videoDevices,
    selectedAudioDeviceId: devices.selectedAudioDeviceId,
    selectedVideoDeviceId: devices.selectedVideoDeviceId,
    deviceError: devices.deviceError,
    hasRequiredDevices: devices.hasRequiredDevices,
    hasRemoteVideo,
    remoteParticipantName,
    localAudioLevel,
    remoteAudioLevel,
    localIsSpeaking,
    remoteIsSpeaking,
    liveTranscript,
    formattedTime,
    canJoin,
    getInitials,
    startPreview,
    stopPreview: devices.stopPreview,
    cancelPreview,
    togglePreviewMic: devices.togglePreviewMic,
    togglePreviewCamera: devices.togglePreviewCamera,
    selectAudioDevice: devices.selectAudioDevice,
    selectVideoDevice: devices.selectVideoDevice,
    joinRoom,
    toggleMute,
    toggleCamera,
    enableRoomAudio,
    leaveInterview,
    router,
  }
}
