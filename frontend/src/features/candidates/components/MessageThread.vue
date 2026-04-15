<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { candidateService } from '../services/candidate.service'
import type { Message } from '../types/message.types'

const { t } = useI18n()

const props = defineProps<{
  candidateId: string
}>()

const messages = ref<Message[]>([])
const newMessage = ref('')
const loading = ref(false)
const sending = ref(false)
const threadContainer = ref<HTMLElement | null>(null)

async function fetchMessages(): Promise<void> {
  loading.value = true
  try {
    messages.value = await candidateService.getMessages(props.candidateId)
    await scrollToBottom()
  } catch {
    // Silently fail
  } finally {
    loading.value = false
  }
}

async function handleSend(): Promise<void> {
  const content = newMessage.value.trim()
  if (!content || sending.value) return

  sending.value = true
  try {
    const message = await candidateService.sendMessage(props.candidateId, content)
    messages.value.push(message)
    newMessage.value = ''
    await scrollToBottom()
  } catch {
    // Silently fail
  } finally {
    sending.value = false
  }
}

async function scrollToBottom(): Promise<void> {
  await nextTick()
  if (threadContainer.value) {
    threadContainer.value.scrollTop = threadContainer.value.scrollHeight
  }
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

watch(() => props.candidateId, fetchMessages)
onMounted(fetchMessages)
</script>

<template>
  <div class="flex h-96 flex-col rounded-lg border border-gray-200">
    <div class="border-b border-gray-100 px-4 py-3">
      <h3 class="text-sm font-semibold text-gray-900">{{ t('candidates.messages') }}</h3>
    </div>

    <div ref="threadContainer" class="flex-1 space-y-3 overflow-y-auto p-4">
      <div v-if="loading" class="py-8 text-center">
        <i class="pi pi-spinner pi-spin text-gray-400"></i>
      </div>

      <div
        v-else-if="messages.length === 0"
        class="py-8 text-center text-sm text-gray-500"
      >
        {{ t('candidates.messageThread.noMessages') }}
      </div>

      <div v-for="msg in messages" :key="msg.id" class="flex flex-col gap-1">
        <div class="flex items-baseline gap-2">
          <span class="text-xs font-medium text-gray-700">
            {{ msg.senderName }}
          </span>
          <span class="text-xs text-gray-400">
            {{ formatTime(msg.createdAt) }}
          </span>
        </div>
        <p class="rounded-lg bg-gray-100 px-3 py-2 text-sm text-gray-800">
          {{ msg.content }}
        </p>
      </div>
    </div>

    <div class="flex gap-2 border-t border-gray-100 p-3">
      <InputText
        v-model="newMessage"
        :placeholder="t('candidates.messageThread.placeholder')"
        class="flex-1"
        @keyup.enter="handleSend"
      />
      <Button
        icon="pi pi-send"
        :loading="sending"
        :disabled="!newMessage.trim()"
        @click="handleSend"
      />
    </div>
  </div>
</template>
