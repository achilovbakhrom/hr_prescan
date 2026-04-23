<script setup lang="ts">
import { computed } from 'vue'
import AppSelect from '@/shared/components/AppSelect.vue'
import type { MediaDeviceInfo } from '../types/video.types'

const props = defineProps<{
  devices: MediaDeviceInfo[]
  selectedDevice: string
  label: string
}>()

const emit = defineEmits<{
  'update:selectedDevice': [value: string]
}>()

const deviceOptions = computed(() =>
  props.devices.map((device) => ({
    label: device.label,
    value: device.deviceId,
  })),
)
</script>

<template>
  <div class="space-y-1">
    <label class="block text-sm font-medium text-gray-700">{{ label }}</label>
    <AppSelect
      :model-value="selectedDevice"
      :options="deviceOptions"
      option-label="label"
      option-value="value"
      class="w-full"
      @update:model-value="emit('update:selectedDevice', String($event ?? ''))"
    />
  </div>
</template>
