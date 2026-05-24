<script setup lang="ts">
import { ref, nextTick, watch, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import AIAssistantDialogHeader from './AIAssistantDialogHeader.vue'
import AIMessageList from './AIMessageList.vue'
import AIAssistantSuggestionGrid from './AIAssistantSuggestionGrid.vue'
import { useAIAssistant } from '../composables/useAIAssistant'
import { useAuthStore } from '@/features/auth/stores/auth.store'

const { t } = useI18n()
const authStore = useAuthStore()
const { isOpen, messages, sending, close, sendMessage, clearHistory } = useAIAssistant()

const isCandidate = computed(() => authStore.currentAccessRole === 'candidate')
const title = computed(() =>
  isCandidate.value ? t('aiAssistant.candidateTitle') : t('aiAssistant.hrTitle'),
)
const subtitle = computed(() =>
  isCandidate.value ? t('aiAssistant.candidateSubtitle') : t('aiAssistant.hrSubtitle'),
)
const intro = computed(() =>
  isCandidate.value ? t('aiAssistant.startHintCandidate') : t('aiAssistant.startHint'),
)

const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
let pageScrollLocked = false
let previousBodyOverflow = ''
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value)
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  })
}

watch(() => messages.value.length, scrollToBottom)
watch(isOpen, (open) => {
  if (open) scrollToBottom()
  setPageScrollLocked(open)
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
  if (e.key === 'Escape' && isOpen.value) close()
}

function setPageScrollLocked(locked: boolean): void {
  if (typeof document === 'undefined') return
  if (locked && !pageScrollLocked) {
    previousBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    pageScrollLocked = true
  }
  if (!locked && pageScrollLocked) {
    document.body.style.overflow = previousBodyOverflow
    pageScrollLocked = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
  setPageScrollLocked(isOpen.value)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
  setPageScrollLocked(false)
})
</script>

<template>
  <Transition name="ai-dialog-fade">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40 bg-slate-950/45 backdrop-blur-sm"
      @click="close"
    ></div>
  </Transition>

  <Transition name="ai-dialog-scale">
    <section
      v-if="isOpen"
      role="dialog"
      aria-modal="true"
      :aria-label="title"
      class="fixed inset-0 z-50 flex h-[100dvh] max-h-[100dvh] flex-col overflow-hidden overscroll-contain bg-white shadow-[0_30px_90px_rgba(15,23,42,0.3)] dark:bg-slate-950 sm:inset-x-3 sm:top-8 sm:mx-auto sm:h-auto sm:max-h-[calc(100dvh-4rem)] sm:max-w-5xl sm:rounded-2xl sm:border sm:border-white/80 sm:dark:border-slate-700"
      @wheel.stop
      @touchmove.stop
    >
      <AIAssistantDialogHeader
        :title="title"
        :subtitle="subtitle"
        @clear="clearHistory"
        @close="close"
      />

      <div
        class="flex min-h-0 flex-1 flex-col bg-slate-50 dark:bg-slate-950 lg:grid lg:grid-cols-[360px_minmax(0,1fr)]"
      >
        <aside
          class="max-h-[32dvh] shrink-0 overflow-y-auto border-b border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900/80 sm:p-4 lg:max-h-none lg:border-b-0 lg:border-r"
        >
          <p class="text-sm font-semibold text-slate-950 dark:text-white">
            {{ isCandidate ? t('aiAssistant.candidateTitle') : t('aiAssistant.tryAsking') }}
          </p>
          <p class="mt-1 hidden text-xs leading-5 text-slate-600 dark:text-slate-300 sm:block">
            {{ intro }}
          </p>
          <AIAssistantSuggestionGrid
            class="mt-3 sm:mt-4"
            :is-candidate="isCandidate"
            @send="sendMessage"
          />
        </aside>

        <main class="flex min-h-0 min-w-0 flex-1 flex-col lg:min-h-[420px]">
          <div
            ref="messagesContainer"
            class="min-h-0 flex-1 overflow-y-auto overscroll-contain p-3 sm:p-5"
          >
            <div
              v-if="messages.length === 0"
              class="flex h-full min-h-[190px] flex-col items-center justify-center rounded-2xl border border-dashed border-cyan-200 bg-white px-4 py-6 text-center dark:border-cyan-900 dark:bg-slate-900 sm:min-h-[260px] sm:px-5 sm:py-8"
            >
              <span
                class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200 sm:h-14 sm:w-14"
              >
                <i class="pi pi-bolt text-base sm:text-xl"></i>
              </span>
              <h3
                class="mt-3 text-base font-semibold text-slate-950 dark:text-white sm:mt-4 sm:text-lg"
              >
                {{ t('aiAssistant.startTitle') }}
              </h3>
              <p
                class="mt-2 max-w-md text-xs leading-5 text-slate-600 dark:text-slate-300 sm:text-sm sm:leading-6"
              >
                {{ intro }}
              </p>
            </div>

            <AIMessageList v-else :messages="messages" :sending="sending" />
          </div>

          <footer
            class="shrink-0 border-t border-slate-200 bg-white p-2.5 pb-[max(0.625rem,env(safe-area-inset-bottom))] dark:border-slate-800 dark:bg-slate-900 sm:p-3"
          >
            <div class="flex gap-2">
              <Textarea
                v-model="inputText"
                :placeholder="t('aiAssistant.placeholder')"
                class="min-w-0 flex-1"
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
          </footer>
        </main>
      </div>
    </section>
  </Transition>
</template>

<style scoped>
.ai-dialog-fade-enter-active,
.ai-dialog-fade-leave-active,
.ai-dialog-scale-enter-active,
.ai-dialog-scale-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}
.ai-dialog-fade-enter-from,
.ai-dialog-fade-leave-to,
.ai-dialog-scale-enter-from,
.ai-dialog-scale-leave-to {
  opacity: 0;
}
.ai-dialog-scale-enter-from,
.ai-dialog-scale-leave-to {
  transform: translateY(12px) scale(0.98);
}
</style>
