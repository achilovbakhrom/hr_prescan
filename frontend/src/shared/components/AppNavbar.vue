<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { authService } from '@/features/auth/services/auth.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'
import NotificationBell from '@/features/notifications/components/NotificationBell.vue'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import ThemeToggle from '@/shared/components/ThemeToggle.vue'
import GlobalSearchDialog from './GlobalSearchDialog.vue'
import AppLogo from './AppLogo.vue'
import CompanySwitcher from './CompanySwitcher.vue'
import AccountModeSwitcher from './AccountModeSwitcher.vue'
import AIAssistantEntryButton from './AIAssistantEntryButton.vue'
import AppNavbarUserMenu from './AppNavbarUserMenu.vue'
import { useNotificationPolling } from '@/features/notifications/composables/useNotificationPolling'
import { useAIAssistant } from '@/shared/composables/useAIAssistant'

defineProps<{ sidebarCollapsed: boolean }>()
const emit = defineEmits<{ toggleSidebar: []; toggleMobileNav: [] }>()

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const pendingInvitationsCount = ref(0)
const showSearch = ref(false)
const canUseGlobalSearch = computed(
  () =>
    Boolean(authStore.user?.company) &&
    authStore.activeMode === 'hr' &&
    (authStore.currentAccessRole === USER_ROLES.ADMIN ||
      authStore.currentAccessRole === USER_ROLES.HR),
)
const showCompanyContext = computed(
  () =>
    authStore.activeMode === 'hr' &&
    (authStore.companies.length > 0 || Boolean(authStore.user?.company)),
)

watch(canUseGlobalSearch, (allowed) => {
  if (!allowed) showSearch.value = false
})

useNotificationPolling()
const aiAssistant = useAIAssistant()

function onKeydown(e: KeyboardEvent): void {
  if (canUseGlobalSearch.value && (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
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

function handleMenuToggle(): void {
  emit('toggleMobileNav')
}
</script>

<template>
  <header
    class="sticky top-0 z-30 border-b border-[color:var(--color-border-soft)] bg-[color:color-mix(in_srgb,var(--color-surface-base)_85%,transparent)] backdrop-blur-xl"
  >
    <div class="flex h-16 items-center justify-between gap-2 px-4 sm:px-6 lg:px-8">
      <!-- Left: mobile menu + logo (logo lives in the sidebar on desktop) -->
      <div class="flex min-w-0 items-center gap-2 sm:gap-3 lg:hidden">
        <Button
          icon="pi pi-bars"
          text
          severity="secondary"
          class="!h-9 !w-9 shrink-0 !p-0 sm:!h-10 sm:!w-10"
          :aria-label="t('common.aria.toggleMenu')"
          @click="handleMenuToggle"
        />
        <AppLogo size="sm" to="/dashboard" />
      </div>

      <!-- Desktop left: company picker + account/mode switcher -->
      <div class="hidden min-w-0 items-center gap-2 lg:flex">
        <CompanySwitcher v-if="showCompanyContext" class="min-w-0" />
        <AccountModeSwitcher v-if="authStore.user" class="min-w-0" />
      </div>

      <!-- Right: search + assistant + theme/lang + bell + user -->
      <div class="flex shrink-0 items-center gap-1 sm:gap-2">
        <button
          v-if="canUseGlobalSearch"
          type="button"
          class="hidden items-center gap-2 rounded-2xl border border-white/70 bg-white/70 px-3 py-2 text-xs text-gray-500 transition-colors hover:bg-white dark:border-white/10 dark:bg-gray-900/70 dark:text-gray-400 dark:hover:bg-gray-900 sm:flex"
          :title="t('common.searchPlaceholder')"
          @click="showSearch = true"
        >
          <i class="pi pi-search text-[10px]"></i>
          <span class="hidden xl:inline">{{ t('common.searchPlaceholder') }}</span>
          <kbd
            class="hidden rounded border border-gray-200 bg-white px-1 py-0.5 text-[9px] font-medium dark:border-gray-700 dark:bg-gray-800 xl:inline"
            >⌘K</kbd
          >
        </button>
        <button
          v-if="canUseGlobalSearch"
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
          :aria-label="t('settings.profile.invitations')"
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

        <AIAssistantEntryButton @click="aiAssistant.open()" />

        <span class="hidden sm:inline-flex">
          <ThemeToggle />
        </span>
        <span class="hidden sm:inline-flex">
          <LanguageSwitcher />
        </span>
        <NotificationBell />
        <span class="lg:hidden">
          <AppNavbarUserMenu />
        </span>
      </div>
    </div>

    <GlobalSearchDialog v-if="canUseGlobalSearch" v-model:visible="showSearch" />
  </header>
</template>
