<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  recordingUrl: string | null
}>()

const isVideo = computed(() => {
  if (!props.recordingUrl) return false
  const url = props.recordingUrl.toLowerCase()
  return url.endsWith('.mp4') || url.endsWith('.webm') || url.endsWith('.mkv')
})
</script>

<template>
  <div class="rounded-lg border border-gray-200 p-6">
    <template v-if="recordingUrl">
      <p class="mb-3 text-sm font-medium text-gray-700">Interview Recording</p>
      <video
        v-if="isVideo"
        :src="recordingUrl"
        controls
        class="w-full rounded-lg"
        preload="metadata"
      >
        Your browser does not support the video element.
      </video>
      <audio
        v-else
        :src="recordingUrl"
        controls
        class="w-full"
        preload="metadata"
      >
        Your browser does not support the audio element.
      </audio>
    </template>
    <div v-else class="py-4 text-center">
      <i class="pi pi-volume-off mb-2 text-3xl text-gray-300"></i>
      <p class="text-sm text-gray-500">No recording available.</p>
    </div>
  </div>
</template>
