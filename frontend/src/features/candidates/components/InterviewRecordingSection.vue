<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  recordingUrl: string
}>()

const { t } = useI18n()
const mediaRef = ref<HTMLMediaElement | null>(null)

const isVideo = computed(() => {
  const url = props.recordingUrl.toLowerCase()
  return url.endsWith('.mp4') || url.endsWith('.webm') || url.endsWith('.mkv')
})

function seekTo(seconds: number): void {
  if (!mediaRef.value || !Number.isFinite(seconds)) return
  mediaRef.value.currentTime = Math.max(0, seconds)
  void mediaRef.value.play().catch(() => {})
}

defineExpose({ seekTo })
</script>

<template>
  <div class="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <div class="mb-3 flex items-center gap-2 text-sm font-medium text-gray-700">
      <i class="pi pi-video text-[color:var(--color-accent)]"></i>
      {{ t('interviews.recording') }}
    </div>
    <video
      v-if="isVideo"
      ref="mediaRef"
      :src="recordingUrl"
      controls
      class="w-full rounded-lg"
      preload="metadata"
    />
    <audio v-else ref="mediaRef" :src="recordingUrl" controls class="w-full" preload="metadata" />
  </div>
</template>
