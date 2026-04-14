<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import { useNotificationStore } from '../stores/notification.store'
import NotificationDropdown from './NotificationDropdown.vue'

const { t } = useI18n()
const notificationStore = useNotificationStore()
const showDropdown = ref(false)

function toggleDropdown(): void {
  showDropdown.value = !showDropdown.value
}

function closeDropdown(): void {
  showDropdown.value = false
}
</script>

<template>
  <div class="relative">
    <Button
      icon="pi pi-bell"
      text
      severity="secondary"
      rounded
      :aria-label="t('notifications.title')"
      @click="toggleDropdown"
    />
    <Badge
      v-if="notificationStore.unreadCount > 0"
      :value="notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount"
      severity="danger"
      class="absolute -right-1 -top-1 pointer-events-none"
    />
    <NotificationDropdown
      v-if="showDropdown"
      @close="closeDropdown"
    />
  </div>
</template>
