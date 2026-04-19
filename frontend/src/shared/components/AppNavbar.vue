<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import Badge from 'primevue/badge'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { authService } from '@/features/auth/services/auth.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import NotificationBell from '@/features/notifications/components/NotificationBell.vue'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import ThemeToggle from '@/shared/components/ThemeToggle.vue'
import CompanySwitcher from './CompanySwitcher.vue'
import GlobalSearchDialog from './GlobalSearchDialog.vue'
import { useNotificationPolling } from '@/features/notifications/composables/useNotificationPolling'
import { useAIAssistant } from '@/shared/composables/useAIAssistant'
import type { MenuItem } from 'primevue/menuitem'

defineProps<{ sidebarCollapsed: boolean }>()
const emit = defineEmits<{ toggleSidebar: []; toggleMobileNav: [] }>()

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const userMenu = ref<InstanceType<typeof Menu> | null>(null)
const pendingInvitationsCount = ref(0)
const showSearch = ref(false)

useNotificationPolling()
const aiAssistant = useAIAssistant()

function onKeydown(e: KeyboardEvent): void {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    showSearch.value = true
  }
}

onMounted(async () => {
  try {
    pendingInvitationsCount.value = (await authService.getMyInvitations()).length
  } catch {
    /* silent */
  }
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})

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
function handleMenuToggle(): void {
  if (globalThis.innerWidth >= 1024) {
    emit('toggleSidebar')
  } else {
    emit('toggleMobileNav')
  }
}
</script>

<template>
  <header
    class="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 dark:border-gray-800 dark:bg-gray-950"
  >
    <div class="flex items-center gap-3">
      <Button
        icon="pi pi-bars"
        text
        severity="secondary"
        aria-label="Toggle menu"
        @click="handleMenuToggle"
      />
      <RouterLink to="/" class="text-xl font-bold text-gray-900 hover:text-blue-600"
        >PreScreen AI</RouterLink
      >
      <a
        href="/jobs"
        target="_blank"
        rel="noopener"
        class="ml-1 flex items-center gap-1.5 rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 transition-colors hover:border-blue-200 hover:bg-blue-100 sm:ml-2"
      >
        <i class="pi pi-search text-[10px]"></i>
        <span class="hidden sm:inline">{{ t('nav.browseJobs') }}</span>
        <span class="sm:hidden">{{ t('nav.jobs') }}</span>
      </a>
      <CompanySwitcher />
    </div>

    <div class="flex items-center gap-3">
      <button
        type="button"
        class="hidden items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs text-gray-500 transition-colors hover:bg-gray-100 sm:flex"
        :title="t('common.searchPlaceholder')"
        @click="showSearch = true"
      >
        <i class="pi pi-search text-[10px]"></i>
        <span class="hidden md:inline">{{ t('common.searchPlaceholder') }}</span>
        <kbd
          class="hidden rounded border border-gray-200 bg-white px-1 py-0.5 text-[9px] font-medium md:inline"
          >⌘K</kbd
        >
      </button>
      <button
        type="button"
        class="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700 sm:hidden"
        :aria-label="t('common.searchPlaceholder')"
        @click="showSearch = true"
      >
        <i class="pi pi-search"></i>
      </button>

      <Button
        v-if="pendingInvitationsCount > 0"
        icon="pi pi-envelope"
        text
        severity="info"
        size="small"
        class="relative"
        aria-label="Pending invitations"
        @click="router.push({ name: ROUTE_NAMES.PROFILE })"
      >
        <template #icon
          ><i class="pi pi-envelope"></i
          ><Badge
            :value="pendingInvitationsCount"
            severity="danger"
            class="absolute -right-1 -top-1"
        /></template>
      </Button>

      <button
        type="button"
        class="flex items-center gap-1.5 rounded-full bg-gradient-to-r from-violet-500 to-indigo-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-95"
        @click="aiAssistant.toggle()"
      >
        <i class="pi pi-sparkles text-[10px]"></i><span class="hidden sm:inline">AI</span>
      </button>

      <ThemeToggle />
      <LanguageSwitcher />
      <NotificationBell />

      <button
        type="button"
        class="flex items-center gap-2 rounded-lg px-2 py-1 transition-colors hover:bg-gray-100"
        aria-label="User menu"
        aria-haspopup="true"
        @click="toggleUserMenu"
      >
        <div
          class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700"
        >
          {{ authStore.user?.firstName?.charAt(0) ?? ''
          }}{{ authStore.user?.lastName?.charAt(0) ?? '' }}
        </div>
        <span class="hidden text-sm font-medium text-gray-700 sm:inline"
          >{{ authStore.user?.firstName }} {{ authStore.user?.lastName }}</span
        >
        <i class="pi pi-chevron-down hidden text-xs text-gray-400 sm:inline"></i>
      </button>

      <Menu ref="userMenu" :model="menuItems" :popup="true" />
    </div>

    <GlobalSearchDialog v-model:visible="showSearch" />
  </header>
</template>
