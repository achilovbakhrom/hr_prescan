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

const isCandidate = computed(() => authStore.user?.role === 'candidate')
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
      class="fixed inset-x-3 top-4 z-50 mx-auto flex max-h-[calc(100vh-2rem)] max-w-5xl flex-col overflow-hidden overscroll-contain rounded-2xl border border-white/80 bg-white shadow-[0_30px_90px_rgba(15,23,42,0.3)] dark:border-slate-700 dark:bg-slate-950 sm:top-8"
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
        class="grid min-h-0 flex-1 bg-slate-50 dark:bg-slate-950 lg:grid-cols-[360px_minmax(0,1fr)]"
      >
        <aside
          class="border-b border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900/80 lg:border-b-0 lg:border-r"
        >
          <p class="text-sm font-semibold text-slate-950 dark:text-white">
            {{ t('aiAssistant.tryAsking') }}
          </p>
          <p class="mt-1 text-xs leading-5 text-slate-600 dark:text-slate-300">
            {{ intro }}
          </p>
          <AIAssistantSuggestionGrid class="mt-4" :is-candidate="isCandidate" @send="sendMessage" />
        </aside>

        <main class="flex min-h-[420px] min-w-0 flex-col">
          <div
            ref="messagesContainer"
            class="min-h-0 flex-1 overflow-y-auto overscroll-contain p-4 sm:p-5"
          >
            <div
              v-if="messages.length === 0"
              class="flex h-full min-h-[260px] flex-col items-center justify-center rounded-2xl border border-dashed border-cyan-200 bg-white px-5 py-8 text-center dark:border-cyan-900 dark:bg-slate-900"
            >
              <span
                class="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200"
              >
                <i class="pi pi-bolt text-xl"></i>
              </span>
              <h3 class="mt-4 text-lg font-semibold text-slate-950 dark:text-white">
                {{ t('aiAssistant.startTitle') }}
              </h3>
              <p class="mt-2 max-w-md text-sm leading-6 text-slate-600 dark:text-slate-300">
                {{ intro }}
              </p>
            </div>

            <AIMessageList v-else :messages="messages" :sending="sending" />
          </div>

          <footer
            class="border-t border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900"
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
