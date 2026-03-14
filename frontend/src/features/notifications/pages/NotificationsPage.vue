<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notification.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Notification, NotificationType } from '../types/notification.types'

const router = useRouter()
const notificationStore = useNotificationStore()
const filterMode = ref<'all' | 'unread'>('all')

const filteredNotifications = computed(() => {
  if (filterMode.value === 'unread') {
    return notificationStore.notifications.filter((n) => !n.isRead)
  }
  return notificationStore.notifications
})

const typeIcons: Record<NotificationType, string> = {
  application_received: 'pi pi-user-plus',
  interview_scheduled: 'pi pi-calendar',
  interview_completed: 'pi pi-check-circle',
  interview_reminder: 'pi pi-clock',
  status_changed: 'pi pi-sync',
  invitation_received: 'pi pi-envelope',
  system: 'pi pi-info-circle',
}

function getIcon(type: NotificationType): string {
  return typeIcons[type] ?? 'pi pi-bell'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

async function handleMarkAsRead(notification: Notification): Promise<void> {
  await notificationStore.markAsRead(notification.id)
}

async function handleMarkAllAsRead(): Promise<void> {
  await notificationStore.markAllAsRead()
}

async function handleClick(notification: Notification): Promise<void> {
  await notificationStore.markAsRead(notification.id)

  if (
    notification.type === 'application_received' &&
    notification.data.candidateId
  ) {
    await router.push({
      name: ROUTE_NAMES.CANDIDATE_DETAIL,
      params: { id: notification.data.candidateId },
    })
  } else if (
    notification.type === 'interview_scheduled' &&
    notification.data.interviewId
  ) {
    await router.push({
      name: ROUTE_NAMES.INTERVIEW_DETAIL,
      params: { id: notification.data.interviewId },
    })
  }
}

onMounted(() => notificationStore.fetchNotifications())
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Notifications</h1>
      <Button
        v-if="notificationStore.unreadCount > 0"
        label="Mark all as read"
        icon="pi pi-check"
        size="small"
        outlined
        @click="handleMarkAllAsRead"
      />
    </div>

    <div class="flex gap-2">
      <Button
        label="All"
        :outlined="filterMode !== 'all'"
        size="small"
        @click="filterMode = 'all'"
      />
      <Button
        label="Unread"
        :outlined="filterMode !== 'unread'"
        size="small"
        @click="filterMode = 'unread'"
      />
    </div>

    <div v-if="notificationStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <div
      v-else-if="filteredNotifications.length === 0"
      class="py-12 text-center text-gray-500"
    >
      <i class="pi pi-bell-slash mb-2 text-3xl"></i>
      <p>No notifications</p>
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="notification in filteredNotifications"
        :key="notification.id"
        class="flex cursor-pointer items-start gap-3 rounded-lg border border-gray-200 p-4 transition hover:bg-gray-50"
        :class="{ 'border-blue-200 bg-blue-50': !notification.isRead }"
        @click="handleClick(notification)"
      >
        <i :class="getIcon(notification.type)" class="mt-0.5 text-lg text-gray-400"></i>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-medium text-gray-900">
            {{ notification.title }}
          </p>
          <p class="mt-1 text-sm text-gray-600">
            {{ notification.message }}
          </p>
          <p class="mt-1 text-xs text-gray-400">
            {{ formatDate(notification.createdAt) }}
          </p>
        </div>
        <Button
          v-if="!notification.isRead"
          icon="pi pi-check"
          text
          rounded
          size="small"
          aria-label="Mark as read"
          @click.stop="handleMarkAsRead(notification)"
        />
      </div>
    </div>
  </div>
</template>
