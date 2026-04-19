<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { InterviewDetail } from '../types/interview.types'
import VideoPreview from '@/features/video/components/VideoPreview.vue'
import MediaControls from '@/features/video/components/MediaControls.vue'
import ConnectionStatus from '@/features/video/components/ConnectionStatus.vue'
import InterviewTimer from '@/features/video/components/InterviewTimer.vue'
import { useLiveKit } from '@/features/video/composables/useLiveKit'

const props = defineProps<{
  interview: InterviewDetail
  livekitUrl: string
}>()

const emit = defineEmits<{
  end: []
}>()

const { t } = useI18n()

const showLeaveDialog = ref(false)

const {
  connectionState,
  isMicEnabled,
  isCameraEnabled,
  error: livekitError,
  connect,
  disconnect,
  toggleMic,
  toggleCamera,
} = useLiveKit()

onMounted(async () => {
  await connect({
    url: props.livekitUrl,
    token: props.interview.candidateToken,
    roomName: props.interview.livekitRoomName,
  })
})

function handleLeaveRequest(): void {
  showLeaveDialog.value = true
}

function cancelLeave(): void {
  showLeaveDialog.value = false
}

async function confirmLeave(): Promise<void> {
  showLeaveDialog.value = false
  await disconnect()
  emit('end')
}
</script>

<template>
  <div class="space-y-4">
    <!-- Top Bar -->
    <div class="flex items-center justify-between rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm">
      <div class="flex items-center gap-4">
        <ConnectionStatus :state="connectionState" />
        <InterviewTimer :duration-minutes="interview.durationMinutes" />
      </div>
      <h2 class="text-sm font-medium text-gray-600">
        {{ interview.vacancyTitle }}
      </h2>
    </div>

    <p v-if="livekitError" class="text-sm text-red-600">
      {{ livekitError }}
    </p>

    <!-- Video Area -->
    <div class="relative min-h-[400px] rounded-lg bg-gray-900 p-8">
      <!-- AI agent indicator (center) -->
      <div class="flex h-full items-center justify-center">
        <div class="text-center">
          <div
            class="mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-full bg-gray-700"
          >
            <i class="pi pi-user text-4xl text-gray-400"></i>
          </div>
          <p class="text-sm text-gray-400">{{ t('interviews.inInterview.aiInterviewer') }}</p>
          <p v-if="connectionState === 'connecting'" class="mt-2 text-xs text-gray-500">
            {{ t('interviews.inInterview.connecting') }}
          </p>
        </div>
      </div>

      <!-- Local video (small corner) -->
      <div
        class="absolute bottom-4 right-4 h-32 w-44 overflow-hidden rounded-lg border-2 border-gray-600 shadow-lg"
      >
        <VideoPreview device-id="" />
      </div>
    </div>

    <!-- Controls -->
    <div class="rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm">
      <MediaControls
        :is-mic-enabled="isMicEnabled"
        :is-camera-enabled="isCameraEnabled"
        @toggle-mic="toggleMic"
        @toggle-camera="toggleCamera"
        @leave="handleLeaveRequest"
      />
    </div>

    <!-- Leave Confirmation Dialog -->
    <div
      v-if="showLeaveDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    >
      <div class="mx-4 w-full max-w-sm rounded-lg bg-white dark:bg-gray-800 p-6 shadow-xl">
        <h3 class="mb-2 text-lg font-semibold text-gray-900">
          {{ t('interviews.inInterview.leaveTitle') }}
        </h3>
        <p class="mb-6 text-sm text-gray-600">
          {{ t('interviews.inInterview.leaveMessage') }}
        </p>
        <div class="flex justify-end gap-3">
          <button
            class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100"
            @click="cancelLeave"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            class="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500"
            @click="confirmLeave"
          >
            {{ t('interviews.inInterview.leaveButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
