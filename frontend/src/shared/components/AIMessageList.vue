<script setup lang="ts">
import { sanitizeHtml } from '@/shared/utils/sanitize'

defineProps<{
  messages: Array<{
    role: 'user' | 'assistant'
    content: string
    actions?: Array<{ tool: string }>
  }>
  sending: boolean
}>()

function formatMessage(text: string): string {
  const formatted = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code class="rounded bg-gray-200 px-1 text-xs">$1</code>')
    .replace(/\n/g, '<br>')
  return sanitizeHtml(formatted)
}
</script>

<template>
  <div class="space-y-3">
    <div
      v-for="(msg, idx) in messages"
      :key="idx"
      class="flex"
      :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
    >
      <div
        v-if="msg.role === 'user'"
        class="max-w-[85%] rounded-2xl rounded-tr-sm bg-blue-600 px-3.5 py-2.5"
      >
        <p class="whitespace-pre-wrap text-sm text-white">{{ msg.content }}</p>
      </div>
      <div v-else class="max-w-[85%]">
        <div class="rounded-2xl rounded-tl-sm border border-gray-100 bg-gray-50 px-3.5 py-2.5">
          <!-- eslint-disable-next-line vue/no-v-html -->
          <p
            class="whitespace-pre-wrap text-sm text-gray-700"
            v-html="formatMessage(msg.content)"
          ></p>
        </div>
        <div v-if="msg.actions?.length" class="mt-1.5 flex flex-wrap gap-1">
          <span
            v-for="(action, aidx) in msg.actions"
            :key="aidx"
            class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700"
          >
            <i class="pi pi-check text-[8px]"></i>{{ action.tool.replace(/_/g, ' ') }}
          </span>
        </div>
      </div>
    </div>

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
</template>
