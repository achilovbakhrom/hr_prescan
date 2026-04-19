<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { InterviewDetail } from '../types/interview.types'

const props = defineProps<{
  interview: InterviewDetail
}>()
const emit = defineEmits<{
  join: []
}>()
const { t } = useI18n()
import VideoPreview from '@/features/video/components/VideoPreview.vue'
import DeviceSelector from '@/features/video/components/DeviceSelector.vue'
import { useMediaDevices } from '@/features/video/composables/useMediaDevices'

const {
  cameras,
  microphones,
  selectedCamera,
  selectedMicrophone,
  hasCameraPermission,
  hasMicPermission,
  error: mediaError,
  requestPermissions,
} = useMediaDevices()

const devicesReady = computed(() => {
  return hasCameraPermission.value && hasMicPermission.value
})

const canJoin = computed(() => {
  return (
    devicesReady.value &&
    (props.interview.status === 'pending' || props.interview.status === 'in_progress')
  )
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  requestPermissions()
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">{{ t('interviews.preCheck.prepareTitle') }}</h1>

    <!-- Interview Info -->
    <div
      class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6"
    >
      <dl class="space-y-3 text-sm">
        <div class="flex justify-between">
          <dt class="text-gray-500">{{ t('interviews.preCheck.position') }}</dt>
          <dd class="font-medium">{{ interview.vacancyTitle }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">{{ t('interviews.preCheck.scheduled') }}</dt>
          <dd class="font-medium">{{ formatDate(interview.createdAt) }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">{{ t('interviews.preCheck.duration') }}</dt>
          <dd class="font-medium">
            {{ t('interviews.preCheck.durationMinutes', { minutes: interview.durationMinutes }) }}
          </dd>
        </div>
      </dl>
    </div>

    <!-- Camera Preview + Device Selection -->
    <div
      class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6"
    >
      <h2 class="mb-4 text-lg font-semibold text-gray-800">
        {{ t('interviews.preCheck.title') }}
      </h2>

      <p v-if="mediaError" class="mb-4 text-sm text-red-600">
        {{ mediaError }}
      </p>

      <div v-if="devicesReady" class="space-y-4">
        <div class="aspect-video w-full max-w-md">
          <VideoPreview :device-id="selectedCamera" />
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <DeviceSelector
            :devices="cameras"
            :selected-device="selectedCamera"
            :label="t('interviews.preCheck.camera')"
            @update:selected-device="selectedCamera = $event"
          />
          <DeviceSelector
            :devices="microphones"
            :selected-device="selectedMicrophone"
            :label="t('interviews.preCheck.microphone')"
            @update:selected-device="selectedMicrophone = $event"
          />
        </div>
      </div>

      <div v-else class="py-8 text-center">
        <i class="pi pi-video mb-3 text-4xl text-gray-300"></i>
        <p class="mb-4 text-sm text-gray-500">
          {{ t('interviews.preCheck.allowCameraAccess') }}
        </p>
        <Button
          :label="t('interviews.preCheck.allowCameraMic')"
          icon="pi pi-shield"
          severity="secondary"
          @click="requestPermissions"
        />
      </div>
    </div>

    <!-- Instructions -->
    <div
      class="rounded-lg border border-blue-100 dark:border-blue-900 bg-blue-50 dark:bg-blue-950 p-6"
    >
      <h3 class="mb-3 text-sm font-semibold text-blue-800">
        {{ t('interviews.preCheck.beforeYouJoin') }}
      </h3>
      <ul class="list-inside list-disc space-y-1 text-sm text-blue-700">
        <li>{{ t('interviews.preCheck.stableConnection') }}</li>
        <li>{{ t('interviews.preCheck.quietRoom') }}</li>
        <li>{{ t('interviews.preCheck.faceVisible') }}</li>
        <li>{{ t('interviews.preCheck.aiConducted') }}</li>
        <li>{{ t('interviews.preCheck.speakClearly') }}</li>
      </ul>
    </div>

    <!-- Join Button -->
    <Button
      :label="t('interviews.preCheck.join')"
      icon="pi pi-video"
      class="w-full"
      size="large"
      :disabled="!canJoin"
      @click="emit('join')"
    />
  </div>
</template>
