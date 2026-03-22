import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { sendAICommand, type AIMessage } from '../api/aiAssistant'
import { extractErrorMessage } from '../api/errors'

const isOpen = ref(false)
const messages = ref<AIMessage[]>([])
const sending = ref(false)

export function useAIAssistant() {
  const route = useRoute()

  function toggle() {
    isOpen.value = !isOpen.value
  }
  function open() {
    isOpen.value = true
  }
  function close() {
    isOpen.value = false
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
      const context = {
        currentPage: route.name,
        currentParams: route.params,
      }
      const response = await sendAICommand(text, context)
      messages.value.push({
        role: 'assistant',
        content: response.message,
        actions: response.actions,
        timestamp: new Date().toISOString(),
      })
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
  }

  return {
    isOpen,
    messages,
    sending,
    toggle,
    open,
    close,
    sendMessage,
    clearHistory,
  }
}
