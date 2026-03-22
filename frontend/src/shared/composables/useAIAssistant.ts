import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { sendAICommand, type AIMessage, type FrontendAction } from '../api/aiAssistant'
import { extractErrorMessage } from '../api/errors'

const STORAGE_KEY = 'prescreen_ai_assistant_history'
const MAX_MESSAGES = 200 // 100 prompts × 2 (user + assistant)

function loadHistory(): AIMessage[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as AIMessage[]
  } catch { /* corrupted data */ }
  return []
}

function saveHistory(msgs: AIMessage[]): void {
  const trimmed = msgs.slice(-MAX_MESSAGES)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
}

const isOpen = ref(false)
const messages = ref<AIMessage[]>(loadHistory())
const sending = ref(false)

// Persist on every change
watch(messages, (val) => saveHistory(val), { deep: true })

export function useAIAssistant() {
  const route = useRoute()
  const router = useRouter()

  function toggle() { isOpen.value = !isOpen.value }
  function open() { isOpen.value = true }
  function close() { isOpen.value = false }

  function executeFrontendActions(actions: Array<{ tool: string; result: Record<string, unknown> }> | undefined): void {
    if (!actions) return

    for (const action of actions) {
      const fa = action.result?.frontend_action as FrontendAction | undefined
      if (!fa) continue

      if (fa.type === 'navigate' && fa.path) {
        router.push(fa.path)
      } else if (fa.type === 'clear_history') {
        clearHistory()
      }
    }
  }

  async function sendMessage(text: string) {
    if (!text.trim() || sending.value) return

    messages.value.push({
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    })
    sending.value = true

    try {
      const context: Record<string, unknown> = {
        currentPage: route.name,
        currentParams: route.params,
      }

      // Send last 10 messages as conversation history for context
      const recentHistory = messages.value.slice(-11, -1).map((m) => ({
        role: m.role,
        content: m.content,
      }))
      if (recentHistory.length > 0) {
        context.conversationHistory = recentHistory
      }

      const response = await sendAICommand(text, context)
      messages.value.push({
        role: 'assistant',
        content: response.message,
        actions: response.actions,
        timestamp: new Date().toISOString(),
      })

      // Execute frontend actions (navigate, clear history, etc.)
      executeFrontendActions(response.actions)
    } catch (err) {
      messages.value.push({
        role: 'assistant',
        content: extractErrorMessage(err),
        timestamp: new Date().toISOString(),
      })
    } finally {
      sending.value = false
    }
  }

  function clearHistory() {
    messages.value = []
    localStorage.removeItem(STORAGE_KEY)
  }

  return { isOpen, messages, sending, toggle, open, close, sendMessage, clearHistory }
}
