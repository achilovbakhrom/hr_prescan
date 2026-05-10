import { computed, nextTick, ref, type Ref } from 'vue'
import type { AudioCaptureOptions, LocalParticipant, VideoCaptureOptions } from 'livekit-client'
import type { MediaDeviceInfo as AppMediaDeviceInfo } from '@/features/video/types/video.types'

type DeviceKind = 'audioinput' | 'videoinput'

export function useInterviewDevices(previewVideoEl: Ref<HTMLVideoElement | null>) {
  const previewStream = ref<MediaStream | null>(null)
  const audioDevices = ref<AppMediaDeviceInfo[]>([])
  const videoDevices = ref<AppMediaDeviceInfo[]>([])
  const selectedAudioDeviceId = ref('')
  const selectedVideoDeviceId = ref('')
  const deviceError = ref<string | null>(null)
  const isMuted = ref(false)
  const isCameraOff = ref(false)

  const hasPreviewAudio = computed(() => Boolean(previewStream.value?.getAudioTracks().length))
  const hasRequiredDevices = computed(() => hasPreviewAudio.value)

  function mapDevice(device: globalThis.MediaDeviceInfo, index: number): AppMediaDeviceInfo {
    const fallback =
      device.kind === 'audioinput' ? `Microphone ${index + 1}` : `Camera ${index + 1}`
    return {
      deviceId: device.deviceId,
      label: device.label || fallback,
      kind: device.kind as DeviceKind,
    }
  }

  async function enumerateDevices(): Promise<void> {
    if (!navigator.mediaDevices?.enumerateDevices) return
    const devices = await navigator.mediaDevices.enumerateDevices()
    audioDevices.value = devices.filter((d) => d.kind === 'audioinput').map(mapDevice)
    videoDevices.value = devices.filter((d) => d.kind === 'videoinput').map(mapDevice)
    if (!selectedAudioDeviceId.value && audioDevices.value[0]) {
      selectedAudioDeviceId.value = audioDevices.value[0].deviceId
    }
    if (!selectedVideoDeviceId.value && videoDevices.value[0]) {
      selectedVideoDeviceId.value = videoDevices.value[0].deviceId
    }
  }

  function nativeAudioOptions(): MediaTrackConstraints {
    return {
      ...(selectedAudioDeviceId.value ? { deviceId: { exact: selectedAudioDeviceId.value } } : {}),
      echoCancellation: true,
      noiseSuppression: true,
    }
  }

  function nativeVideoOptions(): MediaTrackConstraints {
    return {
      ...(selectedVideoDeviceId.value ? { deviceId: { exact: selectedVideoDeviceId.value } } : {}),
      width: { ideal: 1280 },
      height: { ideal: 720 },
    }
  }

  function liveKitAudioOptions(): AudioCaptureOptions {
    return {
      ...(selectedAudioDeviceId.value ? { deviceId: { exact: selectedAudioDeviceId.value } } : {}),
      echoCancellation: true,
      noiseSuppression: true,
    }
  }

  function liveKitVideoOptions(): VideoCaptureOptions {
    return {
      ...(selectedVideoDeviceId.value ? { deviceId: { exact: selectedVideoDeviceId.value } } : {}),
    }
  }

  function explainMediaError(kind: 'camera' | 'microphone', err: unknown): string {
    const name = err instanceof DOMException ? err.name : ''
    if (name === 'NotAllowedError' || name === 'SecurityError') {
      return `${kind === 'camera' ? 'Camera' : 'Microphone'} permission is blocked. Allow access in your browser settings and try again.`
    }
    if (name === 'NotFoundError' || name === 'OverconstrainedError') {
      return `No working ${kind} was found. Select another device and try again.`
    }
    if (kind === 'microphone') {
      return 'Microphone could not be started. If you use AirPods, reconnect them or choose the built-in microphone.'
    }
    return 'Camera could not be started. You can still join with microphone only, or close other apps using the camera and try again.'
  }

  async function requestTrack(kind: 'audio' | 'video'): Promise<MediaStreamTrack | null> {
    try {
      const constraints =
        kind === 'audio' ? { audio: nativeAudioOptions() } : { video: nativeVideoOptions() }
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      return stream.getTracks()[0] ?? null
    } catch (err) {
      const message = explainMediaError(kind === 'audio' ? 'microphone' : 'camera', err)
      deviceError.value = deviceError.value ? `${deviceError.value} ${message}` : message
      return null
    }
  }

  function stopPreview(): void {
    previewStream.value?.getTracks().forEach((track) => track.stop())
    previewStream.value = null
    if (previewVideoEl.value) previewVideoEl.value.srcObject = null
  }

  async function startPreview(): Promise<void> {
    deviceError.value = null
    if (!navigator.mediaDevices?.getUserMedia) {
      deviceError.value = 'Your browser does not support camera and microphone access.'
      return
    }

    stopPreview()
    await enumerateDevices()
    const [videoTrack, audioTrack] = await Promise.all([
      requestTrack('video'),
      requestTrack('audio'),
    ])
    const stream = new MediaStream()
    if (videoTrack) stream.addTrack(videoTrack)
    if (audioTrack) stream.addTrack(audioTrack)
    previewStream.value = stream
    isCameraOff.value = !videoTrack || isCameraOff.value
    isMuted.value = !audioTrack || isMuted.value
    stream.getVideoTracks().forEach((track) => {
      track.enabled = !isCameraOff.value
    })
    stream.getAudioTracks().forEach((track) => {
      track.enabled = !isMuted.value
    })
    await enumerateDevices()
    await nextTick()
    if (previewVideoEl.value) previewVideoEl.value.srcObject = stream
  }

  async function selectAudioDevice(deviceId: string): Promise<void> {
    selectedAudioDeviceId.value = deviceId
    isMuted.value = false
    await startPreview()
  }

  async function selectVideoDevice(deviceId: string): Promise<void> {
    selectedVideoDeviceId.value = deviceId
    isCameraOff.value = false
    await startPreview()
  }

  function togglePreviewMic(): void {
    if (!previewStream.value?.getAudioTracks().length) return
    isMuted.value = !isMuted.value
    previewStream.value.getAudioTracks().forEach((track) => {
      track.enabled = !isMuted.value
    })
  }

  function togglePreviewCamera(): void {
    if (!previewStream.value?.getVideoTracks().length) return
    isCameraOff.value = !isCameraOff.value
    previewStream.value.getVideoTracks().forEach((track) => {
      track.enabled = !isCameraOff.value
    })
  }

  async function publishLocalMedia(participant: LocalParticipant): Promise<void> {
    await participant.setMicrophoneEnabled(true, liveKitAudioOptions())
    if (!isCameraOff.value) {
      try {
        await participant.setCameraEnabled(true, liveKitVideoOptions())
      } catch {
        isCameraOff.value = true
      }
    }
    if (isMuted.value) await participant.setMicrophoneEnabled(false)
  }

  return {
    audioDevices,
    videoDevices,
    selectedAudioDeviceId,
    selectedVideoDeviceId,
    deviceError,
    isMuted,
    isCameraOff,
    hasRequiredDevices,
    startPreview,
    stopPreview,
    togglePreviewMic,
    togglePreviewCamera,
    selectAudioDevice,
    selectVideoDevice,
    publishLocalMedia,
  }
}
