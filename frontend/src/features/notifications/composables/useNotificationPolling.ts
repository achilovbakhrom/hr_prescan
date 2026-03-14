import { onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '../stores/notification.store'

const POLL_INTERVAL_MS = 30_000

export function useNotificationPolling(): void {
  const notificationStore = useNotificationStore()
  let intervalId: ReturnType<typeof setInterval> | null = null

  onMounted(() => {
    notificationStore.fetchUnreadCount()
    intervalId = setInterval(() => {
      notificationStore.fetchUnreadCount()
    }, POLL_INTERVAL_MS)
  })

  onUnmounted(() => {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  })
}
