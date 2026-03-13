<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  deviceId: string
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const stream = ref<MediaStream | null>(null)

async function startPreview(): Promise<void> {
  stopPreview()

  try {
    const constraints: MediaStreamConstraints = {
      video: props.deviceId
        ? { deviceId: { exact: props.deviceId } }
        : true,
      audio: false,
    }
    stream.value = await navigator.mediaDevices.getUserMedia(constraints)

    if (videoRef.value) {
      videoRef.value.srcObject = stream.value
    }
  } catch {
    // Permission not granted or device unavailable
  }
}

function stopPreview(): void {
  if (stream.value) {
    stream.value.getTracks().forEach((track) => track.stop())
    stream.value = null
  }
}

watch(() => props.deviceId, startPreview)
onMounted(startPreview)
onUnmounted(stopPreview)
</script>

<template>
  <div class="overflow-hidden rounded-lg bg-gray-900">
    <video
      ref="videoRef"
      autoplay
      playsinline
      muted
      class="h-full w-full object-cover"
    />
  </div>
</template>
