<script setup lang="ts">
/**
 * NotificationRow — solid list row inside the glass notifications container.
 * Unread state gets a subtle accent tint + dot; read state is muted.
 */
import { computed } from 'vue'
import Button from 'primevue/button'
import type { Notification, NotificationType } from '../types/notification.types'

const props = defineProps<{
  notification: Notification
}>()

defineEmits<{
  click: []
  markRead: []
}>()

const typeIcons: Record<NotificationType, string> = {
  application_received: 'pi pi-user-plus',
  interview_scheduled: 'pi pi-calendar',
  interview_completed: 'pi pi-check-circle',
  interview_reminder: 'pi pi-clock',
  status_changed: 'pi pi-sync',
  invitation_received: 'pi pi-envelope',
  system: 'pi pi-info-circle',
}

const icon = computed(() => typeIcons[props.notification.type] ?? 'pi pi-bell')

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}
</script>

<template>
  <li
    class="notif-row flex cursor-pointer items-start gap-3 px-4 py-3.5 transition-colors hover:bg-[color:var(--color-accent-soft)]"
    :class="{ 'notif-row--unread': !notification.isRead }"
    @click="$emit('click')"
  >
    <span
      class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
      :class="
        !notification.isRead
          ? 'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
          : 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)]'
      "
    >
      <i :class="icon" class="text-sm"></i>
    </span>
    <div class="min-w-0 flex-1">
      <div class="flex items-center gap-2">
        <p class="truncate text-sm font-semibold text-[color:var(--color-text-primary)]">
          {{ notification.title }}
        </p>
        <span
          v-if="!notification.isRead"
          class="h-2 w-2 shrink-0 rounded-full bg-[color:var(--color-accent)]"
          aria-label="unread"
        />
      </div>
      <p class="mt-1 text-sm text-[color:var(--color-text-secondary)]">
        {{ notification.message }}
      </p>
      <p class="mt-1 text-xs text-[color:var(--color-text-muted)]">
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
      @click.stop="$emit('markRead')"
    />
  </li>
</template>

<style scoped>
.notif-row--unread {
  background: color-mix(in srgb, var(--color-accent-soft) 35%, transparent);
}
</style>
