<script setup lang="ts">
/**
 * AppSidebar — Figma app shell sidebar: logo at top, a flat nav list,
 * then company switcher + an upgrade card + the user chip pinned to the bottom.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { USER_ROLES } from '@/shared/constants/roles'
import { BILLING_ENABLED } from '@/shared/constants/billing'
import AppLogo from './AppLogo.vue'
import AppNavbarUserMenu from './AppNavbarUserMenu.vue'
import type { HRPermission, UserRole } from '@/shared/types/auth.types'

interface NavItem {
  label: string
  icon: string
  to: string
  roles: UserRole[]
  permission?: HRPermission
}

defineProps<{ collapsed: boolean }>()

const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

const isAdmin = computed(() => authStore.user?.role === 'admin')

const isTrial = computed(() => BILLING_ENABLED && authStore.user?.subscriptionStatus === 'trial')
const trialDaysLeft = computed(() => {
  const ends = authStore.user?.trialEndsAt
  if (!ends) return null
  return Math.max(0, Math.ceil((new Date(ends).getTime() - Date.now()) / 86_400_000))
})
const upgradeTitle = computed(() =>
  isTrial.value && trialDaysLeft.value != null
    ? t('trial.daysLeft', { days: trialDaysLeft.value })
    : t('nav.subscription'),
)

function hasPermission(permission?: HRPermission): boolean {
  if (!permission) return true
  const user = authStore.user
  if (!user) return false
  if (user.role === 'admin') return true
  return (user.hrPermissions || []).includes(permission)
}

const allItems = computed<NavItem[]>(() => [
  {
    label: t('nav.dashboard'),
    icon: 'pi pi-home',
    to: '/dashboard',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR, USER_ROLES.CANDIDATE],
  },
  {
    label: t('nav.vacancies'),
    icon: 'pi pi-briefcase',
    to: '/vacancies',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
    permission: 'manage_vacancies',
  },
  {
    label: t('nav.candidates'),
    icon: 'pi pi-users',
    to: '/candidates',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
    permission: 'manage_candidates',
  },
  {
    label: t('nav.interviews'),
    icon: 'pi pi-video',
    to: '/interviews',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
    permission: 'manage_interviews',
  },
  {
    label: t('nav.hrAnalytics'),
    icon: 'pi pi-chart-bar',
    to: '/analytics',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
    permission: 'view_analytics',
  },
  {
    label: t('nav.myApplications'),
    icon: 'pi pi-file',
    to: '/my-applications',
    roles: [USER_ROLES.CANDIDATE],
  },
  {
    label: t('nav.myCvs'),
    icon: 'pi pi-file-pdf',
    to: '/my-cvs',
    roles: [USER_ROLES.CANDIDATE],
  },
  {
    label: t('companies.title'),
    icon: 'pi pi-building',
    to: '/companies',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
    permission: 'manage_vacancies',
  },
  {
    label: t('nav.team'),
    icon: 'pi pi-users',
    to: '/settings/team',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
    permission: 'manage_team',
  },
  {
    label: t('nav.settings'),
    icon: 'pi pi-cog',
    to: '/profile',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR, USER_ROLES.CANDIDATE],
  },
])

const navItems = computed(() => {
  const role = authStore.currentAccessRole
  if (!role) return []
  return allItems.value.filter((i) => i.roles.includes(role) && hasPermission(i.permission))
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <aside
    class="flex h-full shrink-0 flex-col border-r border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-base)] transition-all duration-200"
    :class="collapsed ? 'w-16' : 'w-64'"
    role="navigation"
    :aria-label="t('common.aria.mainNavigation')"
  >
    <!-- Logo -->
    <div class="px-4 py-5">
      <AppLogo :variant="collapsed ? 'glyph' : 'full'" size="md" to="/dashboard" />
    </div>

    <!-- Nav -->
    <nav class="flex flex-1 flex-col gap-1 overflow-y-auto px-3 py-2">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors"
        :class="
          isActive(item.to)
            ? 'bg-[color:color-mix(in_srgb,var(--color-accent)_14%,transparent)] font-semibold text-[color:var(--color-accent)]'
            : 'text-[color:var(--color-text-secondary)] hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]'
        "
        :title="collapsed ? item.label : undefined"
      >
        <i
          :class="item.icon"
          class="shrink-0 text-base"
          :style="{ width: '20px', textAlign: 'center' }"
          aria-hidden="true"
        ></i>
        <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <!-- Bottom: upgrade card + user -->
    <div v-if="!collapsed" class="space-y-3 border-t border-[color:var(--color-border-soft)] p-3">
      <div
        v-if="isAdmin"
        class="rounded-2xl bg-[linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)] p-4 text-white shadow-[0_10px_30px_rgba(124,58,237,0.35)]"
      >
        <p class="text-sm font-semibold leading-tight">{{ upgradeTitle }}</p>
        <RouterLink
          to="/subscription"
          class="mt-3 inline-flex items-center rounded-lg bg-white/95 px-3 py-1.5 text-xs font-semibold text-[#7c3aed] transition-colors hover:bg-white"
        >
          {{ t('trial.choosePlan') }}
        </RouterLink>
      </div>

      <AppNavbarUserMenu />
    </div>
  </aside>
</template>
