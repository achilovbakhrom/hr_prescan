<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import Message from 'primevue/message'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import type { CvChatMessage } from '../types/cv-builder.types'

const { t } = useI18n()
const store = useCvBuilderStore()

const visible = ref(false)
const messages = ref<CvChatMessage[]>([])
const userInput = ref('')
const thinking = ref(false)
const ready = ref(false)
const generating = ref(false)
const errorMessage = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const chatContainer = ref<HTMLElement | null>(null)

async function scrollToBottom(): Promise<void> {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

async function open(): Promise<void> {
  messages.value = []
  userInput.value = ''
  thinking.value = false
  ready.value = false
  generating.value = false
  errorMessage.value = null
  successMessage.value = null
  visible.value = true

  // Get AI's first message (greeting)
  thinking.value = true
  try {
    const result = await store.cvAiChat([])
    messages.value.push({ role: 'assistant', content: result.message })
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    thinking.value = false
  }
  scrollToBottom()
}

async function sendMessage(): Promise<void> {
  const text = userInput.value.trim()
  if (!text || thinking.value) return

  messages.value.push({ role: 'user', content: text })
  userInput.value = ''
  errorMessage.value = null
  thinking.value = true
  scrollToBottom()

  try {
    const result = await store.cvAiChat(messages.value)
    messages.value.push({ role: 'assistant', content: result.message })
    if (result.status === 'ready') {
      ready.value = true
    }
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    thinking.value = false
  }
  scrollToBottom()
}

async function handleGenerate(): Promise<void> {
  generating.value = true
  errorMessage.value = null
  try {
    await store.cvAiGenerate(messages.value)
    successMessage.value = t('cvBuilder.aiGenerate.success')
    setTimeout(() => { visible.value = false }, 1500)
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    generating.value = false
  }
}

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

defineExpose({ open })
</script>

<template>
  <Button
    :label="t('cvBuilder.aiGenerate.button')"
    icon="pi pi-sparkles"
    size="small"
    @click="open"
  />

  <Dialog
    v-model:visible="visible"
    :header="t('cvBuilder.aiGenerate.title')"
    modal
    :style="{ width: '600px' }"
    :breakpoints="{ '640px': '95vw' }"
    :closable="!generating"
    class="!p-0"
    :pt="{ content: { class: '!p-0' } }"
  >
    <div class="flex h-[65vh] max-h-[500px] flex-col">
      <!-- Chat messages -->
      <div
        ref="chatContainer"
        class="flex-1 space-y-3 overflow-y-auto p-4"
      >
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="flex"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
            :class="msg.role === 'user'
              ? 'rounded-br-md bg-blue-600 text-white'
              : 'rounded-bl-md bg-gray-100 text-gray-800'"
          >
            {{ msg.content }}
          </div>
        </div>

        <!-- Thinking indicator -->
        <div v-if="thinking" class="flex justify-start">
          <div class="rounded-2xl rounded-bl-md bg-gray-100 px-4 py-2.5">
            <div class="flex gap-1">
              <span class="h-2 w-2 animate-bounce rounded-full bg-gray-400" style="animation-delay: 0ms"></span>
              <span class="h-2 w-2 animate-bounce rounded-full bg-gray-400" style="animation-delay: 150ms"></span>
              <span class="h-2 w-2 animate-bounce rounded-full bg-gray-400" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>

        <!-- Generating overlay -->
        <div v-if="generating" class="flex flex-col items-center gap-2 py-4">
          <i class="pi pi-spinner pi-spin text-2xl text-blue-500"></i>
          <p class="text-xs font-medium text-gray-500">{{ t('cvBuilder.aiGenerate.generating') }}</p>
        </div>

        <!-- Success -->
        <Message v-if="successMessage" severity="success" class="!mt-2">{{ successMessage }}</Message>
        <Message v-if="errorMessage" severity="error" class="!mt-2">{{ errorMessage }}</Message>
      </div>

      <!-- Generate button (when ready) -->
      <div v-if="ready && !generating && !successMessage" class="border-t border-gray-100 px-4 py-3">
        <Button
          :label="t('cvBuilder.aiGenerate.generate')"
          icon="pi pi-sparkles"
          class="w-full"
          :loading="generating"
          @click="handleGenerate"
        />
      </div>

      <!-- Input area -->
      <div v-if="!ready && !generating && !successMessage" class="border-t border-gray-100 p-3">
        <div class="flex items-end gap-2">
          <Textarea
            v-model="userInput"
            class="flex-1"
            :placeholder="t('cvBuilder.aiGenerate.inputPlaceholder')"
            :disabled="thinking"
            autoResize
            rows="1"
            :style="{ maxHeight: '6rem' }"
            @keydown="handleKeydown"
          />
          <Button
            icon="pi pi-send"
            class="shrink-0"
            :disabled="!userInput.trim() || thinking"
            @click="sendMessage"
          />
        </div>
      </div>
    </div>
  </Dialog>
</template>
