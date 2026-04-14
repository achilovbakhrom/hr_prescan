<script setup lang="ts">
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import { useAIAssistant } from '../composables/useAIAssistant'

const { t } = useI18n()
const { isOpen, messages, sending, close, toggle, sendMessage, clearHistory } = useAIAssistant()

const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(() => messages.value.length, scrollToBottom)

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

function formatMessage(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code class="rounded bg-gray-200 px-1 text-xs">$1</code>')
    .replace(/\n/g, '<br>')
}
</script>

<template>
  <!-- Backdrop -->
  <Transition name="fade">
    <div v-if="isOpen" class="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm" @click="close"></div>
  </Transition>

  <!-- Drawer -->
  <Transition name="slide-right">
    <div
      v-if="isOpen"
      class="fixed right-0 top-0 z-50 flex h-full w-full flex-col border-l border-gray-200 bg-white shadow-2xl sm:max-w-[400px]"
    >
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
        <div class="flex items-center gap-2">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600"
          >
            <i class="pi pi-sparkles text-sm text-white"></i>
          </div>
          <div>
            <p class="text-sm font-semibold text-gray-900">
              {{ t('aiAssistant.title') }}
            </p>
            <p class="text-[10px] text-gray-400">
              {{ t('aiAssistant.subtitle') }}
            </p>
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
            v-tooltip.left="t('aiAssistant.clearHistory')"
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

      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4">
        <!-- Welcome message if empty -->
        <div
          v-if="messages.length === 0"
          class="flex flex-col items-center justify-center py-12 text-center"
        >
          <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-50">
            <i class="pi pi-sparkles text-2xl text-violet-500"></i>
          </div>
          <p class="text-sm font-medium text-gray-700">
            {{ t('aiAssistant.welcome') }}
          </p>
          <p class="mt-1 max-w-[260px] text-xs text-gray-400">
            {{ t('aiAssistant.welcomeHint') }}
          </p>
          <!-- Quick actions -->
          <div class="mt-4 flex flex-wrap justify-center gap-2">
            <button
              v-for="hint in ['List my vacancies', 'Show dashboard stats', 'Help']"
              :key="hint"
              class="rounded-full border border-gray-200 px-3 py-1.5 text-xs text-gray-600 transition-colors hover:border-violet-300 hover:bg-violet-50 hover:text-violet-700"
              @click="sendMessage(hint)"
            >
              {{ hint }}
            </button>
          </div>
        </div>

        <!-- Message list -->
        <div v-else class="space-y-3">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <!-- User message -->
            <div
              v-if="msg.role === 'user'"
              class="max-w-[85%] rounded-2xl rounded-tr-sm bg-blue-600 px-3.5 py-2.5"
            >
              <p class="whitespace-pre-wrap text-sm text-white">
                {{ msg.content }}
              </p>
            </div>
            <!-- Assistant message -->
            <div v-else class="max-w-[85%]">
              <div
                class="rounded-2xl rounded-tl-sm border border-gray-100 bg-gray-50 px-3.5 py-2.5"
              >
                <!-- eslint-disable-next-line vue/no-v-html -->
                <p
                  class="whitespace-pre-wrap text-sm text-gray-700"
                  v-html="formatMessage(msg.content)"
                ></p>
              </div>
              <!-- Action badges -->
              <div v-if="msg.actions?.length" class="mt-1.5 flex flex-wrap gap-1">
                <span
                  v-for="(action, aidx) in msg.actions"
                  :key="aidx"
                  class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700"
                >
                  <i class="pi pi-check text-[8px]"></i>
                  {{ action.tool.replace(/_/g, ' ') }}
                </span>
              </div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="sending" class="flex justify-start">
            <div class="flex gap-1 rounded-2xl bg-gray-100 px-4 py-3">
              <span
                class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400"
                style="animation-delay: 0ms"
              ></span>
              <span
                class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400"
                style="animation-delay: 150ms"
              ></span>
              <span
                class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400"
                style="animation-delay: 300ms"
              ></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="border-t border-gray-100 p-3">
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
