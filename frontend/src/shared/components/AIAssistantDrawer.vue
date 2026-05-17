<script setup lang="ts">
import { ref, nextTick, watch, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import AIMessageList from './AIMessageList.vue'
import AIAssistantSuggestionGrid from './AIAssistantSuggestionGrid.vue'
import { useAIAssistant } from '../composables/useAIAssistant'
import { useAuthStore } from '@/features/auth/stores/auth.store'

const { t } = useI18n()
const authStore = useAuthStore()
const { isOpen, messages, sending, close, toggle, sendMessage, clearHistory } = useAIAssistant()

const isCandidate = computed(() => authStore.user?.role === 'candidate')

const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value)
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  })
}
watch(() => messages.value.length, scrollToBottom)
watch(isOpen, (open) => {
  if (open) scrollToBottom()
})

async function handleSend() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  await sendMessage(text)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
function handleGlobalKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    toggle()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <Transition name="fade">
    <div v-if="isOpen" class="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm" @click="close"></div>
  </Transition>

  <Transition name="slide-right">
    <div
      v-if="isOpen"
      class="fixed right-0 top-0 z-50 flex h-full w-full flex-col border-l border-[color:var(--color-border-soft)] bg-[color:var(--color-surface)] shadow-2xl sm:max-w-[440px]"
    >
      <div
        class="border-b border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] px-4 py-4"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex min-w-0 items-start gap-3">
            <div
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
            >
              <i class="pi pi-comments text-base"></i>
            </div>
            <div class="min-w-0">
              <p class="text-base font-semibold text-[color:var(--color-text-primary)]">
                {{ isCandidate ? t('aiAssistant.candidateTitle') : t('aiAssistant.hrTitle') }}
              </p>
              <p class="mt-0.5 text-xs leading-5 text-[color:var(--color-text-secondary)]">
                {{ isCandidate ? t('aiAssistant.candidateSubtitle') : t('aiAssistant.hrSubtitle') }}
              </p>
            </div>
          </div>
          <div class="flex shrink-0 items-center gap-1">
            <Button
              type="button"
              icon="pi pi-trash"
              severity="secondary"
              text
              rounded
              size="small"
              @click="clearHistory"
              :title="t('aiAssistant.clearHistory')"
            />
            <Button
              type="button"
              icon="pi pi-times"
              severity="secondary"
              text
              rounded
              size="small"
              @click="close"
              :aria-label="t('common.close')"
            />
          </div>
        </div>
      </div>

      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4">
        <div v-if="messages.length === 0" class="flex flex-col gap-4 py-2">
          <div
            class="rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] p-4"
          >
            <p class="text-sm font-semibold text-[color:var(--color-text-primary)]">
              {{ t('aiAssistant.startTitle') }}
            </p>
            <p class="mt-1 text-sm leading-6 text-[color:var(--color-text-secondary)]">
              {{ isCandidate ? t('aiAssistant.startHintCandidate') : t('aiAssistant.startHint') }}
            </p>
          </div>
          <AIAssistantSuggestionGrid :is-candidate="isCandidate" @send="sendMessage" />
        </div>

        <AIMessageList v-else :messages="messages" :sending="sending" />
      </div>

      <div
        class="border-t border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] p-3"
      >
        <div class="flex gap-2">
          <Textarea
            v-model="inputText"
            :placeholder="t('aiAssistant.placeholder')"
            class="flex-1"
            rows="1"
            auto-resize
            :disabled="sending"
            @keydown="handleKeydown"
          />
          <Button
            type="button"
            icon="pi pi-send"
            :loading="sending"
            :disabled="!inputText.trim()"
            class="self-end"
            @click="handleSend"
          />
        </div>
        <p class="mt-1.5 text-center text-[10px] text-[color:var(--color-text-muted)]">
          {{ t('aiAssistant.shortcutHint') }}
        </p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.25s ease;
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
