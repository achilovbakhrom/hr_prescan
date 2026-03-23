<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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
      <p class="mb-3 text-sm font-medium text-gray-700">{{ t('interviews.recordingPlayer.title') }}</p>
      <video
        v-if="isVideo"
        :src="recordingUrl"
        controls
        class="w-full rounded-lg"
        preload="metadata"
      >
        {{ t('interviews.recordingPlayer.videoUnsupported') }}
      </video>
      <audio
        v-else
        :src="recordingUrl"
        controls
        class="w-full"
        preload="metadata"
      >
        {{ t('interviews.recordingPlayer.audioUnsupported') }}
      </audio>
    </template>
    <div v-else class="py-4 text-center">
      <i class="pi pi-volume-off mb-2 text-3xl text-gray-300"></i>
      <p class="text-sm text-gray-500">{{ t('interviews.recordingPlayer.noRecording') }}</p>
    </div>
  </div>
</template>
