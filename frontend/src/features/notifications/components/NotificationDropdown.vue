<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useNotificationStore } from '../stores/notification.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Notification, NotificationType } from '../types/notification.types'

const emit = defineEmits<{
  close: []
}>()

const { t } = useI18n()

const router = useRouter()
const notificationStore = useNotificationStore()
const dropdownEl = ref<HTMLElement | null>(null)

const recentNotifications = computed(() => notificationStore.notifications.slice(0, 10))

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

function formatTimeAgo(dateStr: string): string {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diffMs = now - then
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return 'Just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  const diffDay = Math.floor(diffHr / 24)
  return `${diffDay}d ago`
}

async function handleNotificationClick(notification: Notification): Promise<void> {
  await notificationStore.markAsRead(notification.id)
  emit('close')

  if (notification.type === 'application_received' && notification.data.candidateId) {
    await router.push({
      name: ROUTE_NAMES.CANDIDATE_DETAIL,
      params: { id: notification.data.candidateId },
    })
  } else if (notification.type === 'interview_scheduled' && notification.data.interviewId) {
    await router.push({
      name: ROUTE_NAMES.INTERVIEW_DETAIL,
      params: { id: notification.data.interviewId },
    })
  } else if (notification.type === 'status_changed' && notification.data.applicationId) {
    await router.push({
      name: ROUTE_NAMES.MY_APPLICATION_DETAIL,
      params: { id: notification.data.applicationId },
    })
  }
}

async function handleMarkAllAsRead(): Promise<void> {
  await notificationStore.markAllAsRead()
}

function handleViewAll(): void {
  emit('close')
  router.push({ name: ROUTE_NAMES.NOTIFICATIONS })
}

function handleClickOutside(event: MouseEvent): void {
  if (dropdownEl.value && !dropdownEl.value.contains(event.target as Node)) {
    emit('close')
  }
}

onMounted(() => {
  notificationStore.fetchNotifications()
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<template>
  <div
    ref="dropdownEl"
    class="absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg"
  >
    <div class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 px-4 py-3">
      <span class="text-sm font-semibold text-gray-900">{{ t('notifications.title') }}</span>
      <button
        v-if="notificationStore.unreadCount > 0"
        class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800"
        @click="handleMarkAllAsRead"
      >
        {{ t('notifications.markAllRead') }}
      </button>
    </div>

    <div class="max-h-96 overflow-y-auto">
      <div
        v-if="recentNotifications.length === 0"
        class="px-4 py-8 text-center text-sm text-gray-500"
      >
        {{ t('notifications.noNotifications') }}
      </div>

      <button
        v-for="notification in recentNotifications"
        :key="notification.id"
        class="flex w-full items-start gap-3 px-4 py-3 text-left transition hover:bg-gray-50"
        :class="{ 'bg-blue-50': !notification.isRead }"
        @click="handleNotificationClick(notification)"
      >
        <i :class="getIcon(notification.type)" class="mt-0.5 text-gray-400"></i>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-gray-900">
            {{ notification.title }}
          </p>
          <p class="truncate text-xs text-gray-500">
            {{ notification.message }}
          </p>
          <p class="mt-1 text-xs text-gray-400">
            {{ formatTimeAgo(notification.createdAt) }}
          </p>
        </div>
        <span
          v-if="!notification.isRead"
          class="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-blue-500"
        ></span>
      </button>
    </div>

    <div class="border-t border-gray-100 dark:border-gray-800 px-4 py-2">
      <Button
        :label="t('common.viewAll')"
        text
        size="small"
        class="w-full"
        @click="handleViewAll"
      />
    </div>
  </div>
</template>
