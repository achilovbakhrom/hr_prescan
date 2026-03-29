<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { InterviewDetail } from '../types/interview.types'

defineProps<{
  interview: InterviewDetail
  canJoin: boolean
}>()

const emit = defineEmits<{
  startPreview: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-1 items-center justify-center p-6">
    <div class="w-full max-w-md rounded-2xl bg-[#303134] p-8 text-center shadow-2xl">
      <div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-blue-500/20">
        <i class="pi pi-video text-3xl text-blue-400"></i>
      </div>
      <h2 class="mb-1 text-xl font-medium text-white">{{ t('interviews.roomPage.aiVideoInterview') }}</h2>
      <p class="mb-1 text-sm text-gray-400">{{ interview.vacancyTitle }}</p>
      <p class="mb-6 text-xs text-gray-500">{{ interview.durationMinutes }} min</p>

      <div class="mb-6 rounded-xl bg-[#3c4043] p-4 text-left text-sm text-gray-300">
        <p class="mb-2 font-medium text-white">{{ t('interviews.roomPage.beforeYouJoin') }}</p>
        <ul class="space-y-1.5 text-gray-400">
          <li class="flex items-start gap-2"><i class="pi pi-wifi mt-0.5 text-xs text-green-400"></i> {{ t('interviews.roomPage.stableConnection') }}</li>
          <li class="flex items-start gap-2"><i class="pi pi-volume-up mt-0.5 text-xs text-green-400"></i> {{ t('interviews.roomPage.quietRoom') }}</li>
          <li class="flex items-start gap-2"><i class="pi pi-camera mt-0.5 text-xs text-green-400"></i> {{ t('interviews.roomPage.allowCameraMic') }}</li>
          <li class="flex items-start gap-2"><i class="pi pi-user mt-0.5 text-xs text-green-400"></i> {{ t('interviews.roomPage.faceVisible') }}</li>
        </ul>
      </div>

      <Button
        v-if="canJoin"
        :label="t('interviews.roomPage.checkDevicesJoin')"
        icon="pi pi-arrow-right"
        icon-pos="right"
        class="w-full"
        size="large"
        @click="emit('startPreview')"
      />
      <p v-else class="text-sm text-yellow-400">
        {{ t('interviews.roomPage.cannotJoin', { status: interview.status.replace(/_/g, ' ') }) }}
      </p>
    </div>
  </div>
</template>
