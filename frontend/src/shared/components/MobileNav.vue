<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { USER_ROLES } from '@/shared/constants/roles'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import type { UserRole } from '@/shared/types/auth.types'

interface NavItem {
  label: string
  icon: string
  to: string
  roles: UserRole[]
}

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

const navItems = computed<NavItem[]>(() => [
  {
    label: t('nav.dashboard'),
    icon: 'pi pi-home',
    to: '/dashboard',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR, USER_ROLES.CANDIDATE],
  },
  {
    label: t('nav.admin'),
    icon: 'pi pi-shield',
    to: '/admin',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: t('nav.companies'),
    icon: 'pi pi-building',
    to: '/admin/companies',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: t('nav.users'),
    icon: 'pi pi-users',
    to: '/admin/users',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: t('nav.analytics'),
    icon: 'pi pi-chart-bar',
    to: '/admin/analytics',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: t('nav.plans'),
    icon: 'pi pi-list',
    to: '/admin/plans',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: t('nav.vacancies'),
    icon: 'pi pi-briefcase',
    to: '/vacancies',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
  },
  {
    label: t('nav.interviews'),
    icon: 'pi pi-calendar',
    to: '/interviews',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
  },
  {
    label: t('nav.team'),
    icon: 'pi pi-users',
    to: '/settings/team',
    roles: [USER_ROLES.ADMIN],
  },
  {
    label: t('settings.company.title'),
    icon: 'pi pi-cog',
    to: '/settings/company',
    roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
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
  {
    label: t('nav.browseJobs'),
    icon: 'pi pi-search',
    to: '/jobs',
    roles: [USER_ROLES.CANDIDATE],
  },
])

const filteredItems = computed(() => {
  const userRole = authStore.user?.role
  if (!userRole) return []
  return navItems.value.filter((item) => item.roles.includes(userRole))
})

function isActive(path: string): boolean {
  if (path === '/admin') {
    return route.path === '/admin'
  }
  return route.path === path || route.path.startsWith(path + '/')
}

// Close drawer on route change
watch(
  () => route.path,
  () => {
    if (props.open) {
      emit('close')
    }
  },
)
</script>

<template>
  <Teleport to="body">
    <!-- Backdrop overlay -->
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-40 bg-black/50 lg:hidden"
        aria-hidden="true"
        @click="emit('close')"
      ></div>
    </Transition>

    <!-- Slide-out drawer -->
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="-translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition-transform duration-300 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="-translate-x-full"
    >
      <div
        v-if="open"
        class="fixed inset-y-0 left-0 z-50 flex w-[80vw] max-w-72 flex-col bg-white shadow-xl lg:hidden"
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
      >
        <!-- Drawer header -->
        <div class="flex h-16 items-center justify-between border-b border-gray-200 px-4">
          <div class="flex items-center gap-2">
            <AppLogo size="sm" />
            <span class="text-lg font-bold text-gray-900">PreScreen AI</span>
          </div>
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700"
            aria-label="Close navigation menu"
            @click="emit('close')"
          >
            <i class="pi pi-times text-base"></i>
          </button>
        </div>

        <!-- Navigation items -->
        <nav class="flex-1 overflow-y-auto px-3 py-4" role="navigation" aria-label="Mobile menu">
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

        <!-- Language switcher -->
        <div class="border-t border-gray-200 px-4 py-3">
          <LanguageSwitcher />
        </div>

        <!-- User info footer -->
        <div v-if="authStore.user" class="border-t border-gray-200 px-4 py-3">
          <div class="flex items-center gap-3">
            <div
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700"
            >
              {{ authStore.user.firstName?.charAt(0) ?? ''
              }}{{ authStore.user.lastName?.charAt(0) ?? '' }}
            </div>
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-gray-900">
                {{ authStore.user.firstName }} {{ authStore.user.lastName }}
              </p>
              <p class="truncate text-xs text-gray-500">
                {{ authStore.user.email }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
