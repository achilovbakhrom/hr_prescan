<script setup lang="ts">
import type { MediaDeviceInfo } from '../types/video.types'

defineProps<{
  devices: MediaDeviceInfo[]
  selectedDevice: string
  label: string
}>()

const emit = defineEmits<{
  'update:selectedDevice': [value: string]
}>()
</script>

<template>
  <div class="space-y-1">
    <label class="block text-sm font-medium text-gray-700">{{ label }}</label>
    <select
      class="w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      :value="selectedDevice"
      @change="emit('update:selectedDevice', ($event.target as HTMLSelectElement).value)"
    >
      <option v-for="device in devices" :key="device.deviceId" :value="device.deviceId">
        {{ device.label }}
      </option>
    </select>
  </div>
</template>
