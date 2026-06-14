<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Menu from 'primevue/menu'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { MenuItem } from 'primevue/menuitem'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const userMenu = ref<InstanceType<typeof Menu> | null>(null)

const menuItems = computed<MenuItem[]>(() => [
  {
    label: t('nav.profile'),
    icon: 'pi pi-user',
    command: () => router.push({ name: ROUTE_NAMES.PROFILE }),
  },
  { separator: true },
  {
    label: t('nav.logout'),
    icon: 'pi pi-sign-out',
    command: async () => {
      await authStore.logout()
      await router.push({ name: ROUTE_NAMES.LOGIN })
    },
  },
])

function toggleUserMenu(event: Event): void {
  userMenu.value?.toggle(event)
}
</script>

<template>
  <button
    type="button"
    class="flex items-center gap-2 rounded-xl px-2 py-1 transition-colors hover:bg-white/80 dark:hover:bg-gray-900"
    :aria-label="t('common.aria.userMenu')"
    aria-haspopup="true"
    @click="toggleUserMenu"
  >
    <div
      class="flex h-8 w-8 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-sm font-medium text-[color:var(--color-accent)]"
    >
      {{ authStore.user?.firstName?.charAt(0) ?? ''
      }}{{ authStore.user?.lastName?.charAt(0) ?? '' }}
    </div>
    <span class="hidden text-sm font-medium text-gray-700 dark:text-gray-300 sm:inline">
      {{ authStore.user?.firstName }} {{ authStore.user?.lastName }}
    </span>
    <i class="pi pi-chevron-down hidden text-xs text-gray-400 dark:text-gray-500 sm:inline"></i>
  </button>

  <Menu ref="userMenu" :model="menuItems" :popup="true" />
</template>
