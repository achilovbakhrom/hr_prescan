<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import NotificationBell from '@/features/notifications/components/NotificationBell.vue'
import { useNotificationPolling } from '@/features/notifications/composables/useNotificationPolling'

defineProps<{
  sidebarCollapsed: boolean
}>()

const emit = defineEmits<{
  toggleSidebar: []
}>()

const router = useRouter()
const authStore = useAuthStore()

useNotificationPolling()

async function handleLogout(): Promise<void> {
  await authStore.logout()
  await router.push({ name: ROUTE_NAMES.LOGIN })
}
</script>

<template>
  <header
    class="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4"
  >
    <div class="flex items-center gap-3">
      <Button
        icon="pi pi-bars"
        text
        severity="secondary"
        class="lg:hidden"
        @click="emit('toggleSidebar')"
      />
      <h1 class="text-xl font-bold text-gray-900">HR PreScan</h1>
    </div>

    <div class="flex items-center gap-4">
      <NotificationBell />

      <div class="flex items-center gap-2">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700"
        >
          {{ authStore.user?.firstName?.charAt(0) ?? '' }}{{ authStore.user?.lastName?.charAt(0) ?? '' }}
        </div>
        <span class="hidden text-sm font-medium text-gray-700 sm:inline">
          {{ authStore.user?.firstName }} {{ authStore.user?.lastName }}
        </span>
      </div>

      <Button
        icon="pi pi-sign-out"
        text
        severity="secondary"
        rounded
        aria-label="Logout"
        @click="handleLogout"
      />
    </div>
  </header>
</template>
