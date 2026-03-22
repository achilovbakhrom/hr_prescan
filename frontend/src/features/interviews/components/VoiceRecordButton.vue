<script setup lang="ts">
import { useAudioRecorder } from '../composables/useAudioRecorder'
import Button from 'primevue/button'

const emit = defineEmits<{ recorded: [blob: Blob, duration: number] }>()

defineProps<{
  disabled?: boolean
}>()

const { isRecording, duration, error, startRecording, stopRecording, cancelRecording } =
  useAudioRecorder()

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

async function handleStop(): Promise<void> {
  const blob = await stopRecording()
  if (blob) {
    emit('recorded', blob, duration.value)
  }
}
</script>

<template>
  <!-- Idle: mic button -->
  <Button
    v-if="!isRecording"
    type="button"
    icon="pi pi-microphone"
    severity="secondary"
    rounded
    text
    :disabled="disabled"
    class="transition-all hover:scale-110 hover:!text-blue-500"
    v-tooltip.top="'Send voice message'"
    @click="startRecording"
  />

  <!-- Recording: timer + stop + cancel -->
  <div v-else class="flex items-center gap-2">
    <span class="flex items-center gap-1.5 text-sm text-red-600">
      <span class="relative flex h-2 w-2">
        <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
        <span class="relative inline-flex h-2 w-2 animate-pulse rounded-full bg-red-500"></span>
      </span>
      <span class="font-mono tracking-wider">{{ formatDuration(duration) }}</span>
    </span>
    <Button
      type="button"
      icon="pi pi-stop-circle"
      severity="danger"
      rounded
      text
      size="small"
      class="transition-all hover:scale-110 active:scale-95"
      @click="handleStop"
    />
    <Button
      type="button"
      icon="pi pi-times"
      severity="secondary"
      rounded
      text
      size="small"
      class="transition-all hover:scale-110 active:scale-95"
      @click="cancelRecording"
    />
  </div>

  <small v-if="error" class="text-xs text-red-500">{{ error }}</small>
</template>
