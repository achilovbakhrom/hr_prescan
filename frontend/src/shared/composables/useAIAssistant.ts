import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { sendAICommand, type AIMessage, type FrontendAction } from '../api/aiAssistant'
import { extractErrorMessage } from '../api/errors'
import { useAuthStore } from '@/features/auth/stores/auth.store'

const STORAGE_KEY_PREFIX = 'prescreen_ai_assistant_history'
const MAX_MESSAGES = 200 // 100 prompts × 2 (user + assistant)
const CONTEXT_HISTORY_MESSAGES = 10
const CONTEXT_HISTORY_MESSAGE_CHARS = 1200

function getStorageKey(role: string): string {
  return `${STORAGE_KEY_PREFIX}_${role}`
}

function loadHistory(role: string): AIMessage[] {
  try {
    const raw = localStorage.getItem(getStorageKey(role))
    if (raw) return JSON.parse(raw) as AIMessage[]
  } catch {
    /* corrupted data */
  }
  return []
}

function saveHistory(msgs: AIMessage[], role: string): void {
  const trimmed = msgs.slice(-MAX_MESSAGES)
  localStorage.setItem(getStorageKey(role), JSON.stringify(trimmed))
}

function trimContextContent(content: string): string {
  if (content.length <= CONTEXT_HISTORY_MESSAGE_CHARS) return content
  return `${content.slice(0, CONTEXT_HISTORY_MESSAGE_CHARS)}...`
}

const isOpen = ref(false)
const messages = ref<AIMessage[]>([])
const sending = ref(false)
let skipSave = false
let activeRole = ''

// Persist on every change
watch(
  messages,
  (val) => {
    if (skipSave) {
      skipSave = false
      return
    }
    if (activeRole) saveHistory(val, activeRole)
  },
  { deep: true },
)

export function useAIAssistant() {
  const route = useRoute()
  const router = useRouter()
  const authStore = useAuthStore()

  // Load role-specific chat history when role changes
  const role = authStore.user?.role || 'hr'
  if (role !== activeRole) {
    activeRole = role
    skipSave = true
    messages.value = loadHistory(role)
  }

  function toggle() {
    isOpen.value = !isOpen.value
  }
  function open() {
    isOpen.value = true
  }
  function close() {
    isOpen.value = false
  }

  function executeFrontendActions(
    actions: Array<{ tool: string; result: Record<string, unknown> }> | undefined,
  ): void {
    if (!actions) return

    for (const action of actions) {
      // Check both camelCase (after axios interceptor) and snake_case (raw)
      const fa = (action.result?.frontendAction || action.result?.frontend_action) as
        | FrontendAction
        | undefined
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

      // Send recent history, but cap each item so pasted vacancy text does not
      // make every later assistant request oversized.
      const recentHistory = messages.value.slice(-(CONTEXT_HISTORY_MESSAGES + 1), -1).map((m) => ({
        role: m.role,
        content: trimContextContent(m.content),
      }))
      if (recentHistory.length > 0) {
        context.conversationHistory = recentHistory
      }

      const userRole = authStore.user?.role
      const response = await sendAICommand(text, context, userRole)
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
    skipSave = true
    messages.value.splice(0, messages.value.length)
    localStorage.removeItem(getStorageKey(activeRole))
  }

  return { isOpen, messages, sending, toggle, open, close, sendMessage, clearHistory }
}
