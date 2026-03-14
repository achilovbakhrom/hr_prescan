<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { USER_ROLES } from '@/shared/constants/roles'
import type { UserRole } from '@/features/auth/types/auth.types'

interface NavItem {
  label: string
  icon: string
  to: string
  roles: UserRole[]
}

defineProps<{
  collapsed: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const route = useRoute()
const authStore = useAuthStore()

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    to: '/dashboard',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR, USER_ROLES.CANDIDATE],
  },
  {
    label: 'Admin Dashboard',
    icon: 'pi pi-shield',
    to: '/admin',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: 'Companies',
    icon: 'pi pi-building',
    to: '/admin/companies',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: 'Users',
    icon: 'pi pi-users',
    to: '/admin/users',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: 'Analytics',
    icon: 'pi pi-chart-bar',
    to: '/admin/analytics',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: 'Plans',
    icon: 'pi pi-list',
    to: '/admin/plans',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: 'Vacancies',
    icon: 'pi pi-briefcase',
    to: '/vacancies',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
  },
  {
    label: 'Candidates',
    icon: 'pi pi-user',
    to: '/candidates',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
  },
  {
    label: 'Interviews',
    icon: 'pi pi-calendar',
    to: '/interviews',
    roles: [USER_ROLES.HR],
  },
  {
    label: 'Team',
    icon: 'pi pi-users',
    to: '/team',
    roles: [USER_ROLES.HR],
  },
  {
    label: 'Subscription',
    icon: 'pi pi-credit-card',
    to: '/subscription',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: 'My Applications',
    icon: 'pi pi-file',
    to: '/my-applications',
    roles: [USER_ROLES.CANDIDATE],
  },
  {
    label: 'Browse Jobs',
    icon: 'pi pi-search',
    to: '/jobs',
    roles: [USER_ROLES.CANDIDATE],
  },
]

const filteredItems = computed(() => {
  const userRole = authStore.user?.role
  if (!userRole) return []
  return navItems.filter((item) => item.roles.includes(userRole))
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleNav(): void {
  emit('close')
}
</script>

<template>
  <aside
    class="flex h-full flex-col border-r border-gray-200 bg-white transition-all duration-300"
    :class="collapsed ? 'w-0 overflow-hidden lg:w-16' : 'w-64'"
  >
    <nav class="mt-4 flex flex-col gap-1 px-2">
      <RouterLink
        v-for="item in filteredItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
        :class="
          isActive(item.to)
            ? 'bg-blue-50 text-blue-700'
            : 'text-gray-700 hover:bg-gray-100'
        "
        @click="handleNav"
      >
        <i :class="item.icon" class="text-base"></i>
        <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>
