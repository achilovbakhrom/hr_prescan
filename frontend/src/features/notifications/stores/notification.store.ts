import { ref } from 'vue'
import { defineStore } from 'pinia'
import { notificationService } from '../services/notification.service'
import type { Notification } from '../types/notification.types'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)

  async function fetchNotifications(unread?: boolean): Promise<void> {
    loading.value = true
    try {
      notifications.value = await notificationService.getNotifications(
        unread !== undefined ? { unread } : undefined,
      )
    } catch {
      // Silently fail — notifications are non-critical
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(id: string): Promise<void> {
    try {
      await notificationService.markAsRead(id)
      const notification = notifications.value.find((n) => n.id === id)
      if (notification && !notification.isRead) {
        notification.isRead = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch {
      // Silently fail
    }
  }

  async function markAllAsRead(): Promise<void> {
    try {
      await notificationService.markAllAsRead()
      notifications.value.forEach((n) => {
        n.isRead = true
      })
      unreadCount.value = 0
    } catch {
      // Silently fail
    }
  }

  async function fetchUnreadCount(): Promise<void> {
    try {
      unreadCount.value = await notificationService.getUnreadCount()
    } catch {
      // Silently fail
    }
  }

  return {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    fetchUnreadCount,
  }
})
