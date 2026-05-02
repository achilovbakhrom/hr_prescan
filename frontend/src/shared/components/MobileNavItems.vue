<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { USER_ROLES } from '@/shared/constants/roles'
import type { HRPermission, UserRole } from '@/shared/types/auth.types'

interface NavItem {
  label: string
  icon: string
  to: string
  roles: UserRole[]
  permission?: HRPermission
}

const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

function hasPermission(permission?: HRPermission): boolean {
  if (!permission) return true
  const user = authStore.user
  if (!user) return false
  if (user.role === 'admin') return true
  return (user.hrPermissions || []).includes(permission)
}

const navItems = computed<NavItem[]>(() => [
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
    label: t('nav.allCandidates'),
    icon: 'pi pi-users',
    to: '/candidates',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
    permission: 'manage_candidates',
  },
  {
    label: t('nav.interviews'),
    icon: 'pi pi-calendar',
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
    label: t('nav.subscription'),
    icon: 'pi pi-credit-card',
    to: '/subscription',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: t('nav.myApplications'),
    icon: 'pi pi-file',
    to: '/my-applications',
    roles: [USER_ROLES.CANDIDATE],
  },
  { label: t('nav.myCvs'), icon: 'pi pi-file-pdf', to: '/my-cvs', roles: [USER_ROLES.CANDIDATE] },
])

const filteredItems = computed(() => {
  const userRole = authStore.user?.role
  if (!userRole) return []
  return navItems.value.filter(
    (item) => item.roles.includes(userRole) && hasPermission(item.permission),
  )
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <nav
    class="flex-1 overflow-y-auto px-3 py-4"
    role="navigation"
    :aria-label="t('common.aria.mobileMenu')"
  >
    <ul class="flex flex-col gap-1" role="list">
      <li v-for="item in filteredItems" :key="item.to" role="listitem">
        <RouterLink
          :to="item.to"
          class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
          :class="
            isActive(item.to) ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
          "
          :aria-current="isActive(item.to) ? 'page' : undefined"
        >
          <i :class="item.icon" class="text-base"></i>
          <span>{{ item.label }}</span>
        </RouterLink>
      </li>
    </ul>
  </nav>
</template>
