<script setup lang="ts">
import { computed } from 'vue'
import type { ConnectionState } from '../types/video.types'

const props = defineProps<{
  state: ConnectionState
}>()

const config = computed(() => {
  const map: Record<ConnectionState, { label: string; color: string }> = {
    connected: { label: 'Connected', color: 'bg-green-500' },
    connecting: { label: 'Connecting...', color: 'bg-yellow-500' },
    reconnecting: { label: 'Reconnecting...', color: 'bg-yellow-500' },
    disconnected: { label: 'Disconnected', color: 'bg-red-500' },
  }
  return map[props.state]
})
</script>

<template>
  <div class="flex items-center gap-2 text-sm">
    <span
      class="inline-block h-2.5 w-2.5 rounded-full"
      :class="[
        config.color,
        state === 'connecting' || state === 'reconnecting' ? 'animate-pulse' : '',
      ]"
    ></span>
    <span class="text-gray-600">{{ config.label }}</span>
  </div>
</template>
