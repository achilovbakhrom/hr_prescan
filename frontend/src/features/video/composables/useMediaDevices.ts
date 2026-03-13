import { ref } from 'vue'
import type { MediaDeviceInfo as AppMediaDeviceInfo } from '../types/video.types'

export function useMediaDevices() {
  const cameras = ref<AppMediaDeviceInfo[]>([])
  const microphones = ref<AppMediaDeviceInfo[]>([])
  const speakers = ref<AppMediaDeviceInfo[]>([])
  const selectedCamera = ref<string>('')
  const selectedMicrophone = ref<string>('')
  const hasCameraPermission = ref(false)
  const hasMicPermission = ref(false)
  const error = ref<string | null>(null)

  async function requestPermissions(): Promise<void> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })
      hasCameraPermission.value = true
      hasMicPermission.value = true
      stream.getTracks().forEach((track) => track.stop())
      await enumerateDevices()
    } catch {
      error.value = 'Please allow camera and microphone access'
    }
  }

  async function enumerateDevices(): Promise<void> {
    const devices = await navigator.mediaDevices.enumerateDevices()

    cameras.value = devices
      .filter((d) => d.kind === 'videoinput')
      .map((d) => ({
        deviceId: d.deviceId,
        label: d.label || `Camera ${d.deviceId.slice(0, 5)}`,
        kind: 'videoinput' as const,
      }))

    microphones.value = devices
      .filter((d) => d.kind === 'audioinput')
      .map((d) => ({
        deviceId: d.deviceId,
        label: d.label || `Microphone ${d.deviceId.slice(0, 5)}`,
        kind: 'audioinput' as const,
      }))

    speakers.value = devices
      .filter((d) => d.kind === 'audiooutput')
      .map((d) => ({
        deviceId: d.deviceId,
        label: d.label || `Speaker ${d.deviceId.slice(0, 5)}`,
        kind: 'audiooutput' as const,
      }))

    if (cameras.value.length) {
      selectedCamera.value = cameras.value[0].deviceId
    }
    if (microphones.value.length) {
      selectedMicrophone.value = microphones.value[0].deviceId
    }
  }

  return {
    cameras,
    microphones,
    speakers,
    selectedCamera,
    selectedMicrophone,
    hasCameraPermission,
    hasMicPermission,
    error,
    requestPermissions,
    enumerateDevices,
  }
}
