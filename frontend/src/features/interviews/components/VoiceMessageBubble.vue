<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

const { t } = useI18n()

const props = defineProps<{
  audioUrl: string
  duration: number
  transcript: string
}>()

const isPlaying = ref(false)
const currentTime = ref(0)
const showTranscript = ref(false)
const loadError = ref(false)
let audio: HTMLAudioElement | null = null

function createAudio(url: string): void {
  if (audio) {
    audio.pause()
    audio = null
  }
  if (!url) return

  loadError.value = false
  audio = new Audio(url)
  audio.addEventListener('timeupdate', () => {
    currentTime.value = audio!.currentTime
  })
  audio.addEventListener('ended', () => {
    isPlaying.value = false
    currentTime.value = 0
  })
  audio.addEventListener('error', () => {
    loadError.value = true
    isPlaying.value = false
  })
}

// Create audio when URL is available; recreate if URL changes
watch(() => props.audioUrl, (url) => {
  if (url) {
    createAudio(url)
  }
}, { immediate: true })

function togglePlay(): void {
  if (!audio || !props.audioUrl) return
  if (isPlaying.value) {
    audio.pause()
    isPlaying.value = false
  } else {
    audio.play().catch(() => {
      loadError.value = true
    })
    isPlaying.value = true
  }
}

function formatTime(sec: number): string {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

onBeforeUnmount(() => {
  if (audio) {
    audio.pause()
    audio = null
  }
})
</script>

<template>
  <div class="space-y-1.5">
    <div v-if="loadError" class="flex items-center gap-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-500">
      <i class="pi pi-exclamation-circle"></i> {{ t('interviews.chat.audioUnavailable') }}
    </div>
    <div v-else class="flex items-center gap-2 rounded-lg bg-gray-100 px-3 py-2">
      <button
        type="button"
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white text-blue-500 shadow-sm transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
        :disabled="!audioUrl"
        @click="togglePlay"
      >
        <i class="pi" :class="isPlaying ? 'pi-pause' : 'pi-play'" style="font-size: 0.75rem"></i>
      </button>
      <!-- Progress bar -->
      <div class="flex-1">
        <div class="h-1.5 rounded-full bg-gray-300">
          <div
            class="h-1.5 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-150"
            :style="{ width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%' }"
          ></div>
        </div>
      </div>
      <span class="font-mono text-xs text-gray-500">
        {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
      </span>
    </div>
    <button
      class="flex items-center gap-1 text-xs text-blue-500 transition-colors hover:text-blue-700"
      @click="showTranscript = !showTranscript"
    >
      <i class="pi text-[10px]" :class="showTranscript ? 'pi-chevron-down' : 'pi-chevron-right'"></i>
      {{ showTranscript ? t('interviews.chat.hideTranscript') : t('interviews.chat.showTranscript') }}
    </button>
    <div v-if="showTranscript" class="rounded-lg bg-white/10 p-2">
      <p class="text-sm italic text-gray-600">{{ transcript }}</p>
    </div>
  </div>
</template>
