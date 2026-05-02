<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  isMicEnabled: boolean
  isCameraEnabled: boolean
}>()

const emit = defineEmits<{
  toggleMic: []
  toggleCamera: []
  leave: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex items-center justify-center gap-4">
    <button
      class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
      :class="
        isMicEnabled
          ? 'bg-gray-700 text-white hover:bg-gray-600'
          : 'bg-red-600 text-white hover:bg-red-500'
      "
      :title="isMicEnabled ? t('interviews.roomPage.mute') : t('interviews.roomPage.unmute')"
      @click="emit('toggleMic')"
    >
      <i class="pi text-lg" :class="isMicEnabled ? 'pi-microphone' : 'pi-microphone-slash'"></i>
    </button>

    <button
      class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
      :class="
        isCameraEnabled
          ? 'bg-gray-700 text-white hover:bg-gray-600'
          : 'bg-red-600 text-white hover:bg-red-500'
      "
      :title="
        isCameraEnabled
          ? t('interviews.roomPage.turnOffCamera')
          : t('interviews.roomPage.turnOnCamera')
      "
      @click="emit('toggleCamera')"
    >
      <i class="pi text-lg" :class="isCameraEnabled ? 'pi-video' : 'pi-video-slash'"></i>
    </button>

    <button
      class="flex h-12 w-12 items-center justify-center rounded-full bg-red-600 text-white transition-colors hover:bg-red-500"
      :title="t('interviews.roomPage.leaveInterview')"
      @click="emit('leave')"
    >
      <i class="pi pi-phone text-lg" style="transform: rotate(135deg)"></i>
    </button>
  </div>
</template>
