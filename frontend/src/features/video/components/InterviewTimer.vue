<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  durationMinutes: number
}>()

const elapsedSeconds = ref(0)
let intervalId: ReturnType<typeof setInterval> | null = null

const formattedTime = computed(() => {
  const minutes = Math.floor(elapsedSeconds.value / 60)
  const seconds = elapsedSeconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const durationFormatted = computed(() => {
  return `${String(props.durationMinutes).padStart(2, '0')}:00`
})

const isWarning = computed(() => {
  const limitSeconds = props.durationMinutes * 60
  return elapsedSeconds.value >= limitSeconds * 0.8
})

const isOverTime = computed(() => {
  return elapsedSeconds.value >= props.durationMinutes * 60
})

onMounted(() => {
  intervalId = setInterval(() => {
    elapsedSeconds.value++
  }, 1000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<template>
  <div
    class="flex items-center gap-1 rounded-md px-3 py-1 text-sm font-mono"
    :class="{
      'bg-gray-100 text-gray-700': !isWarning && !isOverTime,
      'bg-yellow-100 text-yellow-800': isWarning && !isOverTime,
      'bg-red-100 text-red-800': isOverTime,
    }"
  >
    <i class="pi pi-clock text-xs"></i>
    <span>{{ formattedTime }}</span>
    <span class="text-gray-400">/</span>
    <span class="text-gray-500">{{ durationFormatted }}</span>
  </div>
</template>
