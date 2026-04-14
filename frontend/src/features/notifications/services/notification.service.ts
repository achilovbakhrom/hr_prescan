import { apiClient } from '@/shared/api/client'
import type { Notification } from '../types/notification.types'

export const notificationService = {
  async getNotifications(params?: { unread?: boolean }): Promise<Notification[]> {
    const response = await apiClient.get<Notification[]>('/notifications', {
      params,
    })
    return response.data
  },

  async markAsRead(id: string): Promise<void> {
    await apiClient.patch(`/notifications/${id}/read`)
  },

  async markAllAsRead(): Promise<void> {
    await apiClient.patch('/notifications/read-all')
  },

  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<{ count: number }>('/notifications/unread-count')
    return response.data.count
  },
}
