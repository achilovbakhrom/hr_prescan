<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { InterviewDetail } from '../types/interview.types'

defineProps<{
  interview: InterviewDetail
  isMuted: boolean
  isCameraOff: boolean
  getInitials: (name: string) => string
}>()

const emit = defineEmits<{
  toggleMic: []
  toggleCamera: []
  joinRoom: []
  cancel: []
}>()

const previewVideoEl = defineModel<HTMLVideoElement | null>('previewVideoEl', { required: true })

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-1 items-center justify-center gap-8 p-6">
    <!-- Preview video -->
    <div class="relative w-full max-w-xl overflow-hidden rounded-2xl bg-[#303134]">
      <div class="aspect-video">
        <video
          v-show="!isCameraOff"
          ref="previewVideoEl"
          autoplay
          playsinline
          muted
          class="h-full w-full object-cover"
        ></video>
        <div v-if="isCameraOff" class="flex h-full w-full items-center justify-center">
          <div
            class="flex h-24 w-24 items-center justify-center rounded-full bg-blue-600 text-3xl font-medium text-white"
          >
            {{ interview.candidateName ? getInitials(interview.candidateName) : '?' }}
          </div>
        </div>
      </div>

      <!-- Preview controls overlay -->
      <div class="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-3">
        <button
          class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
          :class="isMuted ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'"
          @click="emit('toggleMic')"
        >
          <i :class="isMuted ? 'pi pi-microphone-slash' : 'pi pi-microphone'" class="text-lg"></i>
        </button>
        <button
          class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
          :class="
            isCameraOff ? 'bg-red-500 text-white' : 'bg-[#3c4043] text-white hover:bg-[#4a4d50]'
          "
          @click="emit('toggleCamera')"
        >
          <i :class="isCameraOff ? 'pi pi-eye-slash' : 'pi pi-eye'" class="text-lg"></i>
        </button>
      </div>
    </div>

    <!-- Join panel -->
    <div class="w-72 shrink-0 text-center">
      <h2 class="mb-1 text-xl font-medium text-white">
        {{ t('interviews.roomPage.readyToJoin') }}
      </h2>
      <p class="mb-6 text-sm text-gray-400">{{ interview.vacancyTitle }}</p>
      <Button
        :label="t('interviews.roomPage.joinNow')"
        icon="pi pi-video"
        class="w-full"
        size="large"
        @click="emit('joinRoom')"
      />
      <button class="mt-3 text-sm text-gray-400 hover:text-white" @click="emit('cancel')">
        {{ t('interviews.roomPage.goBack') }}
      </button>
    </div>
  </div>
</template>
