<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { USER_ROLES } from '@/shared/constants/roles'
import { useAIAssistant } from '@/shared/composables/useAIAssistant'
import type { HRPermission, UserRole } from '@/shared/types/auth.types'

interface NavItem {
  label: string
  icon: string
  to: string
  roles: UserRole[]
  permission?: HRPermission
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
const { t } = useI18n()
const aiAssistant = useAIAssistant()

function hasPermission(permission?: HRPermission): boolean {
  if (!permission) return true
  const user = authStore.user
  if (!user) return false
  if (user.role === 'admin') return true
  return (user.hrPermissions || []).includes(permission)
}

const sections = computed<NavSection[]>(() => [
  {
    items: [
      {
        label: t('nav.dashboard'),
        icon: 'pi pi-home',
        to: '/dashboard',
        roles: [USER_ROLES.ADMIN, USER_ROLES.HR, USER_ROLES.CANDIDATE],
      },
    ],
  },
  {
    title: t('vacancies.title'),
    items: [
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
    ],
  },
  {
    title: t('candidates.title'),
    items: [
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
    ],
  },
  {
    title: t('nav.settings'),
    items: [
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
    ],
  },
])

const filteredSections = computed(() => {
  const userRole = authStore.user?.role
  if (!userRole) return []
  return sections.value
    .map((section) => ({
      ...section,
      items: section.items.filter(
        (item) => item.roles.includes(userRole) && hasPermission(item.permission),
      ),
    }))
    .filter((section) => section.items.length > 0)
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <aside
    class="flex h-full shrink-0 flex-col border-r border-gray-100 bg-white transition-all duration-200 dark:border-gray-800 dark:bg-gray-950"
    :class="collapsed ? 'w-16' : 'w-60'"
    role="navigation"
    aria-label="Main navigation"
  >
    <nav class="flex flex-1 flex-col gap-0.5 overflow-y-auto px-2 py-3">
      <template v-for="(section, sIdx) in filteredSections" :key="sIdx">
        <!-- Section divider -->
        <div v-if="section.title && !collapsed && sIdx > 0" class="mb-1 mt-3 px-3">
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
                  : 'text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900'
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

    <!-- AI Assistant button -->
    <div class="border-t border-gray-100 dark:border-gray-800 px-2 py-3">
      <button
        type="button"
        class="flex w-full items-center gap-3 rounded-xl bg-gradient-to-r from-violet-500 to-indigo-600 px-3 py-2.5 text-[13px] font-medium text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-[0.98]"
        :class="collapsed ? 'justify-center' : ''"
        :title="collapsed ? t('aiAssistant.title') : undefined"
        @click="aiAssistant.toggle()"
      >
        <i
          class="pi pi-sparkles shrink-0 text-sm"
          :style="{ width: '18px', textAlign: 'center' }"
          aria-hidden="true"
        ></i>
        <span v-if="!collapsed" class="truncate">{{ t('aiAssistant.title') }}</span>
      </button>
    </div>
  </aside>
</template>
