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
import AppLogo from './AppLogo.vue'
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
  <header class="sticky top-0 z-40 px-3 pt-3 sm:px-4 lg:px-6">
    <div
      class="mx-auto flex h-16 max-w-[1600px] items-center justify-between rounded-[24px] border border-white/50 bg-white/72 px-4 shadow-[0_18px_48px_rgba(15,23,42,0.08)] backdrop-blur-2xl dark:border-white/10 dark:bg-gray-950/72 dark:shadow-black/25"
    >
      <div class="flex min-w-0 items-center gap-3">
        <Button
          icon="pi pi-bars"
          text
          severity="secondary"
          aria-label="Toggle menu"
          @click="handleMenuToggle"
        />
        <AppLogo size="sm" to="/" />
        <a
          href="/jobs"
          target="_blank"
          rel="noopener"
          class="group hidden items-center gap-2 rounded-full border border-[color:var(--color-border-glass)] bg-[linear-gradient(180deg,color-mix(in_srgb,var(--color-surface-raised)_84%,white),color-mix(in_srgb,var(--color-surface-raised)_96%,white))] px-2.5 py-1.5 text-xs font-semibold text-[color:var(--color-text-primary)] shadow-[0_10px_24px_rgba(15,23,42,0.08)] transition-all hover:-translate-y-px hover:border-[color:color-mix(in_srgb,var(--color-accent)_28%,var(--color-border-glass))] hover:shadow-[0_14px_28px_rgba(15,23,42,0.12)] dark:bg-[rgba(15,23,42,0.55)] dark:hover:bg-[rgba(15,23,42,0.72)] sm:flex"
        >
          <span
            class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)] transition-colors group-hover:bg-[color:var(--color-accent)] group-hover:text-white"
          >
            <i class="pi pi-briefcase text-[11px]"></i>
          </span>
          <span class="whitespace-nowrap">{{ t('nav.browseJobs') }}</span>
          <i
            class="pi pi-arrow-up-right text-[10px] text-[color:var(--color-text-muted)] transition-all group-hover:-translate-y-px group-hover:translate-x-px group-hover:text-[color:var(--color-text-primary)]"
          ></i>
        </a>
        <CompanySwitcher class="min-w-0" />
      </div>

      <div class="flex items-center gap-2 sm:gap-3">
        <button
          type="button"
          class="hidden items-center gap-2 rounded-2xl border border-white/70 bg-white/70 px-3 py-2 text-xs text-gray-500 transition-colors hover:bg-white dark:border-white/10 dark:bg-gray-900/70 dark:text-gray-400 dark:hover:bg-gray-900 sm:flex"
          :title="t('common.searchPlaceholder')"
          @click="showSearch = true"
        >
          <i class="pi pi-search text-[10px]"></i>
          <span class="hidden md:inline">{{ t('common.searchPlaceholder') }}</span>
          <kbd
            class="hidden rounded border border-gray-200 bg-white px-1 py-0.5 text-[9px] font-medium dark:border-gray-700 dark:bg-gray-800 md:inline"
            >⌘K</kbd
          >
        </button>
        <button
          type="button"
          class="rounded-lg p-1.5 text-gray-500 transition-colors hover:bg-white/80 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-900 dark:hover:text-gray-200 sm:hidden"
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
          class="hidden items-center gap-2 rounded-full bg-gradient-to-r from-violet-500 to-indigo-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-95 sm:flex"
          @click="aiAssistant.toggle()"
        >
          <i class="pi pi-sparkles text-[10px]"></i>
          <span>{{ t('aiAssistant.title') }}</span>
        </button>

        <ThemeToggle />
        <LanguageSwitcher />
        <NotificationBell />

        <button
          type="button"
          class="flex items-center gap-2 rounded-xl px-2 py-1 transition-colors hover:bg-white/80 dark:hover:bg-gray-900"
          aria-label="User menu"
          aria-haspopup="true"
          @click="toggleUserMenu"
        >
          <div
            class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700 dark:bg-blue-950"
          >
            {{ authStore.user?.firstName?.charAt(0) ?? ''
            }}{{ authStore.user?.lastName?.charAt(0) ?? '' }}
          </div>
          <span class="hidden text-sm font-medium text-gray-700 dark:text-gray-300 sm:inline"
            >{{ authStore.user?.firstName }} {{ authStore.user?.lastName }}</span
          >
          <i
            class="pi pi-chevron-down hidden text-xs text-gray-400 dark:text-gray-500 sm:inline"
          ></i>
        </button>

        <Menu ref="userMenu" :model="menuItems" :popup="true" />
      </div>
    </div>

    <GlobalSearchDialog v-model:visible="showSearch" />
  </header>
</template>
