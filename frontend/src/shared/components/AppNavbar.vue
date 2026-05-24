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
import CompanySwitcher from './CompanySwitcher.vue'
import AccountModeSwitcher from './AccountModeSwitcher.vue'
import GlobalSearchDialog from './GlobalSearchDialog.vue'
import AppLogo from './AppLogo.vue'
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
const showModeContext = computed(() => Boolean(authStore.user))
const showResponsiveContext = computed(() => showCompanyContext.value || showModeContext.value)

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
  if (globalThis.innerWidth >= 1024) {
    emit('toggleSidebar')
  } else {
    emit('toggleMobileNav')
  }
}
</script>

<template>
  <header class="sticky top-0 z-40 px-2 pt-2 sm:px-4 lg:px-6">
    <div
      class="mx-auto max-w-[1760px] rounded-2xl border border-white/50 bg-white/78 p-2 shadow-[0_18px_48px_rgba(15,23,42,0.08)] backdrop-blur-2xl dark:border-white/10 dark:bg-gray-950/78 dark:shadow-black/25 sm:p-3 lg:rounded-[24px]"
    >
      <div class="flex min-h-11 items-center justify-between gap-2">
        <div class="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
          <Button
            icon="pi pi-bars"
            text
            severity="secondary"
            class="!h-9 !w-9 shrink-0 !p-0 sm:!h-10 sm:!w-10"
            :aria-label="t('common.aria.toggleMenu')"
            @click="handleMenuToggle"
          />
          <span class="shrink-0 sm:hidden">
            <AppLogo size="sm" to="/" variant="glyph" />
          </span>
          <span class="hidden shrink-0 sm:inline-flex">
            <AppLogo size="sm" to="/" />
          </span>
          <a
            href="/jobs"
            target="_blank"
            rel="noopener"
            class="group hidden cursor-pointer items-center gap-2 rounded-full border border-[color:var(--color-border-glass)] bg-[linear-gradient(180deg,color-mix(in_srgb,var(--color-surface-raised)_84%,white),color-mix(in_srgb,var(--color-surface-raised)_96%,white))] px-2.5 py-1.5 text-xs font-semibold text-[color:var(--color-text-primary)] shadow-[0_10px_24px_rgba(15,23,42,0.08)] transition-all hover:-translate-y-px hover:border-[color:color-mix(in_srgb,var(--color-accent)_28%,var(--color-border-glass))] hover:shadow-[0_14px_28px_rgba(15,23,42,0.12)] dark:bg-[rgba(15,23,42,0.55)] dark:hover:bg-[rgba(15,23,42,0.72)] 2xl:flex"
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
          <div
            v-if="showResponsiveContext"
            class="hidden min-w-0 flex-1 items-center gap-2 lg:flex"
          >
            <CompanySwitcher v-if="showCompanyContext" class="min-w-0" />
            <AccountModeSwitcher v-if="showModeContext" class="min-w-0" />
          </div>
        </div>

        <div class="flex shrink-0 items-center gap-1 sm:gap-2">
          <button
            v-if="canUseGlobalSearch"
            type="button"
            class="hidden items-center gap-2 rounded-2xl border border-white/70 bg-white/70 px-3 py-2 text-xs text-gray-500 transition-colors hover:bg-white dark:border-white/10 dark:bg-gray-900/70 dark:text-gray-400 dark:hover:bg-gray-900 sm:flex"
            :title="t('common.searchPlaceholder')"
            @click="showSearch = true"
          >
            <i class="pi pi-search text-[10px]"></i>
            <span class="hidden 2xl:inline">{{ t('common.searchPlaceholder') }}</span>
            <kbd
              class="hidden rounded border border-gray-200 bg-white px-1 py-0.5 text-[9px] font-medium dark:border-gray-700 dark:bg-gray-800 2xl:inline"
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
          <AppNavbarUserMenu />
        </div>
      </div>

      <div
        v-if="showResponsiveContext"
        class="mt-2 flex min-w-0 flex-wrap items-center gap-2 border-t border-[color:var(--color-border-glass)] pt-2 lg:hidden"
      >
        <CompanySwitcher v-if="showCompanyContext" class="min-w-0 flex-1" />
        <AccountModeSwitcher v-if="showModeContext" class="min-w-0 flex-1 sm:flex-none" />
      </div>
    </div>

    <GlobalSearchDialog v-if="canUseGlobalSearch" v-model:visible="showSearch" />
  </header>
</template>
