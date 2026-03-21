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

interface NavSection {
  title?: string
  items: NavItem[]
}

defineProps<{
  collapsed: boolean
}>()

const route = useRoute()
const authStore = useAuthStore()

const sections: NavSection[] = [
  {
    items: [
      { label: 'Dashboard', icon: 'pi pi-home', to: '/dashboard', roles: [USER_ROLES.ADMIN, USER_ROLES.HR, USER_ROLES.CANDIDATE] },
    ],
  },
  {
    title: 'Recruitment',
    items: [
      { label: 'Vacancies', icon: 'pi pi-briefcase', to: '/vacancies', roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
      { label: 'Interviews', icon: 'pi pi-video', to: '/interviews', roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
    ],
  },
  {
    title: 'Candidate',
    items: [
      { label: 'Browse Jobs', icon: 'pi pi-search', to: '/jobs', roles: [USER_ROLES.CANDIDATE] },
      { label: 'My Applications', icon: 'pi pi-file', to: '/my-applications', roles: [USER_ROLES.CANDIDATE] },
    ],
  },
  {
    title: 'Platform',
    items: [
      { label: 'Admin', icon: 'pi pi-shield', to: '/admin', roles: [USER_ROLES.ADMIN] },
      { label: 'Companies', icon: 'pi pi-building', to: '/admin/companies', roles: [USER_ROLES.ADMIN] },
      { label: 'Users', icon: 'pi pi-users', to: '/admin/users', roles: [USER_ROLES.ADMIN] },
      { label: 'Plans', icon: 'pi pi-list', to: '/admin/plans', roles: [USER_ROLES.ADMIN] },
      { label: 'Analytics', icon: 'pi pi-chart-bar', to: '/admin/analytics', roles: [USER_ROLES.ADMIN] },
    ],
  },
  {
    title: 'Settings',
    items: [
      { label: 'Company', icon: 'pi pi-cog', to: '/settings/company', roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
      { label: 'Team', icon: 'pi pi-users', to: '/settings/team', roles: [USER_ROLES.ADMIN] },
      { label: 'Subscription', icon: 'pi pi-credit-card', to: '/subscription', roles: [USER_ROLES.ADMIN] },
    ],
  },
]

const filteredSections = computed(() => {
  const userRole = authStore.user?.role
  if (!userRole) return []
  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => item.roles.includes(userRole)),
    }))
    .filter((section) => section.items.length > 0)
})

function isActive(path: string): boolean {
  if (path === '/admin') return route.path === '/admin'
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <aside
    class="flex h-full shrink-0 flex-col border-r border-gray-100 bg-white transition-all duration-200"
    :class="collapsed ? 'w-16' : 'w-60'"
    role="navigation"
    aria-label="Main navigation"
  >
    <nav class="flex flex-1 flex-col gap-0.5 overflow-y-auto px-2 py-3">
      <template v-for="(section, sIdx) in filteredSections" :key="sIdx">
        <!-- Section divider -->
        <div
          v-if="section.title && !collapsed && sIdx > 0"
          class="mb-1 mt-3 px-3"
        >
          <span class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">
            {{ section.title }}
          </span>
        </div>
        <div v-else-if="sIdx > 0 && collapsed" class="my-2 border-t border-gray-100"></div>

        <ul class="flex flex-col gap-0.5" role="list">
          <li v-for="item in section.items" :key="item.to" role="listitem">
            <RouterLink
              :to="item.to"
              class="flex items-center gap-3 rounded-lg px-3 py-2 text-[13px] font-medium transition-colors"
              :class="
                isActive(item.to)
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              "
              :title="collapsed ? item.label : undefined"
              :aria-current="isActive(item.to) ? 'page' : undefined"
            >
              <i
                :class="item.icon"
                class="shrink-0 text-sm"
                :style="{ width: '18px', textAlign: 'center' }"
                aria-hidden="true"
              ></i>
              <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
            </RouterLink>
          </li>
        </ul>
      </template>
    </nav>
  </aside>
</template>
