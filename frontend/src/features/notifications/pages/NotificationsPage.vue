<script setup lang="ts">
/**
 * NotificationsPage — HR notifications inbox.
 * Glass list container wrapping solid rows (data legibility rule).
 * Spec: docs/design/spec.md §9 Settings+Notifications block.
 */
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import NotificationRow from '../components/NotificationRow.vue'
import { useNotificationStore } from '../stores/notification.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Notification } from '../types/notification.types'

const { t } = useI18n()
const router = useRouter()
const notificationStore = useNotificationStore()
const filterMode = ref<'all' | 'unread'>('all')

const filteredNotifications = computed(() => {
  if (filterMode.value === 'unread') {
    return notificationStore.notifications.filter((n) => !n.isRead)
  }
  return notificationStore.notifications
})

async function handleMarkAllAsRead(): Promise<void> {
  await notificationStore.markAllAsRead()
}

async function handleMarkAsRead(notification: Notification): Promise<void> {
  await notificationStore.markAsRead(notification.id)
}

async function handleClick(notification: Notification): Promise<void> {
  await notificationStore.markAsRead(notification.id)
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
  }
}

onMounted(() => notificationStore.fetchNotifications())
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
          {{ t('notifications.title') }}
        </h1>
        <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
          {{ notificationStore.unreadCount }} {{ t('common.unread', 'unread') }}
        </p>
      </div>
      <Button
        v-if="notificationStore.unreadCount > 0"
        :label="t('notifications.markAllRead')"
        icon="pi pi-check"
        size="small"
        outlined
        @click="handleMarkAllAsRead"
      />
    </div>

    <div class="flex gap-2">
      <Button
        :label="t('common.all')"
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

    <GlassCard class="!p-0">
      <div v-if="notificationStore.loading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
      </div>
      <div
        v-else-if="filteredNotifications.length === 0"
        class="py-12 text-center text-[color:var(--color-text-muted)]"
      >
        <i class="pi pi-bell-slash mb-2 text-3xl"></i>
        <p>{{ t('notifications.noNotifications') }}</p>
      </div>
      <ul v-else class="divide-y divide-[color:var(--color-border-soft)]">
        <NotificationRow
          v-for="notification in filteredNotifications"
          :key="notification.id"
          :notification="notification"
          @click="handleClick(notification)"
          @mark-read="handleMarkAsRead(notification)"
        />
      </ul>
    </GlassCard>
  </div>
</template>
