<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import VoiceRecordButton from './VoiceRecordButton.vue'

const props = defineProps<{
  modelValue: string
  sending: boolean
  sendingVoice: boolean
  canSend: boolean
  isCompleted: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  send: []
  keydown: [event: KeyboardEvent]
  voiceRecorded: [blob: Blob, duration: number]
}>()

const { t } = useI18n()

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value)
}
</script>

<template>
  <!-- Completed overlay -->
  <div v-if="isCompleted" class="border-t border-gray-200 bg-white px-4 py-6">
    <div class="mx-auto max-w-3xl text-center">
      <div
        class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-green-100"
      >
        <i class="pi pi-check text-2xl text-green-600"></i>
      </div>
      <h2 class="mb-1 text-lg font-semibold text-gray-900">
        {{ t('interviews.chatPage.interviewComplete') }}
      </h2>
      <p class="mb-4 text-sm text-gray-500">{{ t('interviews.chatPage.thankYouReview') }}</p>
      <div class="flex justify-center gap-3">
        <RouterLink
          to="/register"
          class="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          {{ t('interviews.chatPage.createAccount') }}
        </RouterLink>
        <RouterLink
          to="/jobs"
          class="rounded-xl border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
        >
          {{ t('interviews.chatPage.browseJobs') }}
        </RouterLink>
      </div>
    </div>
  </div>

  <!-- Input area -->
  <div v-else class="border-t border-gray-200 bg-white px-4 py-3">
    <div class="mx-auto flex max-w-3xl items-end gap-3">
      <div class="relative flex-1">
        <textarea
          :value="modelValue"
          rows="1"
          class="w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 pr-4 text-sm transition-colors placeholder:text-gray-400 focus:border-blue-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
          :placeholder="t('interviews.chat.placeholder')"
          :disabled="props.sending || props.sendingVoice"
          @input="onInput"
          @keydown="emit('keydown', $event)"
        ></textarea>
      </div>
      <VoiceRecordButton
        v-if="!modelValue.trim()"
        :disabled="props.sending || props.sendingVoice || props.isCompleted"
        @recorded="(blob: Blob, dur: number) => emit('voiceRecorded', blob, dur)"
      />
      <button
        v-else
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full transition-all"
        :class="
          canSend
            ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700 hover:shadow-lg'
            : 'bg-gray-200 text-gray-400'
        "
        :disabled="!canSend"
        @click="emit('send')"
      >
        <i v-if="!props.sending" class="pi pi-send text-sm" style="transform: rotate(-30deg)"></i>
        <i v-else class="pi pi-spinner pi-spin text-sm"></i>
      </button>
    </div>
    <p class="mx-auto mt-1.5 max-w-3xl text-center text-[10px] text-gray-400">
      {{ t('interviews.chatPage.enterHint') }}
    </p>
  </div>
</template>
