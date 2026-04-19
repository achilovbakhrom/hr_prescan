<script setup lang="ts">
import { ref, nextTick, watch, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import AIMessageList from './AIMessageList.vue'
import { useAIAssistant } from '../composables/useAIAssistant'
import { useAuthStore } from '@/features/auth/stores/auth.store'

const { t } = useI18n()
const authStore = useAuthStore()
const { isOpen, messages, sending, close, toggle, sendMessage, clearHistory } = useAIAssistant()

const isCandidate = computed(() => authStore.user?.role === 'candidate')
const quickHints = computed(() =>
  isCandidate.value
    ? [
        t('aiAssistant.hints.searchJobs'),
        t('aiAssistant.hints.improveCv'),
        t('aiAssistant.hints.myApplications'),
      ]
    : [
        t('aiAssistant.hints.listVacancies'),
        t('aiAssistant.hints.dashboardStats'),
        t('aiAssistant.hints.help'),
      ],
)

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
      class="fixed right-0 top-0 z-50 flex h-full w-full flex-col border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-2xl sm:max-w-[400px]"
    >
      <div
        class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 px-4 py-3"
      >
        <div class="flex items-center gap-2">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600"
          >
            <i class="pi pi-sparkles text-sm text-white"></i>
          </div>
          <div>
            <p class="text-sm font-semibold text-gray-900">{{ t('aiAssistant.title') }}</p>
            <p class="text-[10px] text-gray-400">{{ t('aiAssistant.subtitle') }}</p>
          </div>
        </div>
        <div class="flex items-center gap-1">
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
          />
        </div>
      </div>

      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4">
        <div
          v-if="messages.length === 0"
          class="flex flex-col items-center justify-center py-12 text-center"
        >
          <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-50">
            <i class="pi pi-sparkles text-2xl text-violet-500"></i>
          </div>
          <p class="text-sm font-medium text-gray-700">{{ t('aiAssistant.welcome') }}</p>
          <p class="mt-1 max-w-[260px] text-xs text-gray-400">
            {{ isCandidate ? t('aiAssistant.welcomeHintCandidate') : t('aiAssistant.welcomeHint') }}
          </p>
          <div class="mt-4 flex flex-wrap justify-center gap-2">
            <button
              v-for="hint in quickHints"
              :key="hint"
              class="rounded-full border border-gray-200 dark:border-gray-700 px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 transition-colors hover:border-violet-300 hover:bg-violet-50 hover:text-violet-700"
              @click="sendMessage(hint)"
            >
              {{ hint }}
            </button>
          </div>
        </div>

        <AIMessageList v-else :messages="messages" :sending="sending" />
      </div>

      <div class="border-t border-gray-100 dark:border-gray-800 p-3">
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
        <p class="mt-1.5 text-center text-[10px] text-gray-300">Ctrl+K / Cmd+K</p>
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
