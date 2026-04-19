<script setup lang="ts">
/**
 * ChatInputBar — composer for the candidate chat interview.
 *
 * T13 redesign: glass float-level surface, textarea on sunken fill.
 */
import { computed, watch } from 'vue'
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

const inIframe = computed(() => {
  try {
    return window !== window.top
  } catch {
    return true
  }
})

watch(
  () => props.isCompleted,
  (completed) => {
    if (completed && inIframe.value) {
      window.parent.postMessage({ type: 'prescan_completed' }, '*')
    }
  },
)

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value)
}
</script>

<template>
  <!-- Completed overlay -->
  <div
    v-if="isCompleted"
    class="bg-glass-float border-t border-[color:var(--color-border-glass)] px-4 py-6 backdrop-blur-md"
  >
    <div class="mx-auto max-w-3xl text-center">
      <div
        class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)]"
      >
        <i class="pi pi-check text-2xl text-[color:var(--color-accent-celebrate)]"></i>
      </div>
      <h2 class="mb-1 text-lg font-semibold text-[color:var(--color-text-primary)]">
        {{ t('interviews.chatPage.interviewComplete') }}
      </h2>
      <p class="mb-4 text-sm text-[color:var(--color-text-secondary)]">
        {{ t('interviews.chatPage.thankYouReview') }}
      </p>
      <p v-if="inIframe" class="text-sm text-[color:var(--color-text-muted)]">
        {{ t('interviews.chatPage.youCanCloseThis') }}
      </p>
      <div v-else class="flex justify-center gap-3">
        <RouterLink
          to="/register"
          class="rounded-md bg-[color:var(--color-accent)] px-5 py-2.5 text-sm font-medium text-[color:var(--color-text-on-accent)] shadow-card ease-ios transition-colors hover:brightness-95"
        >
          {{ t('interviews.chatPage.createAccount') }}
        </RouterLink>
        <RouterLink
          to="/jobs"
          class="rounded-md border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] px-5 py-2.5 text-sm font-medium text-[color:var(--color-text-primary)] ease-ios transition-colors hover:bg-[color:var(--color-surface-sunken)]"
        >
          {{ t('interviews.chatPage.browseJobs') }}
        </RouterLink>
      </div>
    </div>
  </div>

  <!-- Input area -->
  <div
    v-else
    class="bg-glass-float border-t border-[color:var(--color-border-glass)] px-4 py-3 backdrop-blur-md"
  >
    <div class="mx-auto flex max-w-3xl items-end gap-3">
      <div class="relative flex-1">
        <textarea
          :value="modelValue"
          rows="1"
          class="w-full resize-none rounded-2xl border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] px-4 py-3 pr-4 text-sm ease-ios transition-colors placeholder:text-[color:var(--color-text-muted)] focus:border-[color:var(--color-accent)] focus:bg-[color:var(--color-surface-base)] focus:outline-none focus:ring-2 focus:ring-[color:var(--color-accent-soft)]"
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
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full ease-ios transition-all"
        :class="
          canSend
            ? 'bg-[color:var(--color-accent)] text-[color:var(--color-text-on-accent)] shadow-card hover:brightness-95'
            : 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)]'
        "
        :disabled="!canSend"
        @click="emit('send')"
      >
        <i v-if="!props.sending" class="pi pi-send text-sm" style="transform: rotate(-30deg)"></i>
        <i v-else class="pi pi-spinner pi-spin text-sm"></i>
      </button>
    </div>
    <p
      class="mx-auto mt-1.5 max-w-3xl text-center text-[10px] text-[color:var(--color-text-muted)]"
    >
      {{ t('interviews.chatPage.enterHint') }}
    </p>
  </div>
</template>
