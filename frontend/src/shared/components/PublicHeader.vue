<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import { ref, computed } from 'vue'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import type { MenuItem } from 'primevue/menuitem'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const userMenu = ref<InstanceType<typeof Menu> | null>(null)

const menuItems = computed<MenuItem[]>(() => [
  {
    label: t('nav.dashboard'),
    icon: 'pi pi-th-large',
    command: () => router.push({ name: ROUTE_NAMES.DASHBOARD }),
  },
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

function initials(): string {
  const f = authStore.user?.firstName?.charAt(0) ?? ''
  const l = authStore.user?.lastName?.charAt(0) ?? ''
  return (f + l).toUpperCase()
}
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-gray-100 bg-white/95 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
      <RouterLink to="/" class="flex items-center gap-2.5">
        <AppLogo size="sm" />
        <span class="text-xl font-bold tracking-tight text-gray-900">HR PreScan</span>
      </RouterLink>

      <slot name="center" />

      <div class="flex items-center gap-3">
        <LanguageSwitcher />

        <!-- Authenticated: show user menu -->
        <template v-if="authStore.isAuthenticated">
          <Button
            :label="t('nav.dashboard')"
            icon="pi pi-th-large"
            text
            severity="secondary"
            size="small"
            class="hidden sm:flex"
            @click="router.push({ name: ROUTE_NAMES.DASHBOARD })"
          />
          <button
            type="button"
            class="flex items-center gap-2 rounded-lg px-2 py-1 transition-colors hover:bg-gray-100"
            @click="toggleUserMenu"
          >
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700">
              {{ initials() }}
            </div>
            <span class="hidden text-sm font-medium text-gray-700 sm:inline">
              {{ authStore.user?.firstName }}
            </span>
            <i class="pi pi-chevron-down hidden text-xs text-gray-400 sm:inline"></i>
          </button>
          <Menu ref="userMenu" :model="menuItems" :popup="true" />
        </template>

        <!-- Not authenticated: show sign in / register -->
        <template v-else>
          <RouterLink
            :to="{ name: ROUTE_NAMES.LOGIN }"
            class="text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            {{ t('nav.signIn') }}
          </RouterLink>
          <RouterLink
            :to="{ name: ROUTE_NAMES.COMPANY_REGISTER }"
            class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            {{ t('nav.forEmployers') }}
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>
