<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import type { MenuItem } from 'primevue/menuitem'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import ThemeToggle from '@/shared/components/ThemeToggle.vue'
import BackgroundModeSwitcher from '@/shared/components/BackgroundModeSwitcher.vue'
import AppLogo from '@/shared/components/AppLogo.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const mobileOpen = ref(false)
const userMenu = ref<InstanceType<typeof Menu> | null>(null)

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

function scrollTo(id: string): void {
  mobileOpen.value = false
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function goToRoute(name: string): void {
  router.push({ name })
  mobileOpen.value = false
}

async function handleLogout(): Promise<void> {
  await authStore.logout()
  mobileOpen.value = false
  await router.push({ name: ROUTE_NAMES.LOGIN })
}

const navLinks = [
  { id: 'features', labelKey: 'landing.footer.features' },
  { id: 'how-it-works', labelKey: 'landing.howItWorks.title' },
  { id: 'jobs', labelKey: 'landing.latestJobs' },
  { id: 'pricing', labelKey: 'landing.footer.pricing' },
]
</script>

<template>
  <nav class="sticky top-0 z-50 border-b border-gray-100 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-2.5">
        <AppLogo size="sm" />
        <span class="text-xl font-bold tracking-tight text-gray-900">PreScreen AI</span>
      </RouterLink>

      <!-- Desktop nav links -->
      <div class="hidden items-center gap-8 md:flex">
        <button
          v-for="link in navLinks"
          :key="link.id"
          type="button"
          class="text-sm font-medium text-gray-500 dark:text-gray-400 transition-colors hover:text-gray-900"
          @click="scrollTo(link.id)"
        >
          {{ t(link.labelKey) }}
        </button>
      </div>

      <!-- Right side -->
      <div class="flex items-center gap-2">
        <BackgroundModeSwitcher />
        <ThemeToggle />
        <LanguageSwitcher />
        <template v-if="authStore.isAuthenticated">
          <Button
            :label="t('nav.dashboard')"
            icon="pi pi-th-large"
            text
            severity="secondary"
            size="small"
            class="hidden sm:flex"
            @click="router.push({ name: ROUTE_NAMES.DASHBOARD })"
          />
          <button
            type="button"
            class="flex items-center gap-2 rounded-lg px-2 py-1 transition-colors hover:bg-gray-100"
            @click="toggleUserMenu"
          >
            <div
              class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-950 text-sm font-medium text-blue-700"
            >
              {{ authStore.user?.firstName?.charAt(0) }}{{ authStore.user?.lastName?.charAt(0) }}
            </div>
            <span class="hidden text-sm font-medium text-gray-700 dark:text-gray-300 sm:inline">
              {{ authStore.user?.firstName }}
            </span>
            <i class="pi pi-chevron-down hidden text-xs text-gray-400 dark:text-gray-500 sm:inline"></i>
          </button>
          <Menu ref="userMenu" :model="menuItems" :popup="true" />
        </template>
        <template v-else>
          <Button
            :label="t('nav.signIn')"
            text
            severity="secondary"
            class="hidden sm:flex"
            @click="router.push({ name: ROUTE_NAMES.LOGIN })"
          />
          <Button
            :label="t('landing.hero.getStarted')"
            size="small"
            @click="router.push({ name: ROUTE_NAMES.REGISTER })"
          />
        </template>
        <!-- Mobile hamburger -->
        <button
          type="button"
          class="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 dark:text-gray-400 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 md:hidden"
          aria-label="Open menu"
          @click="mobileOpen = !mobileOpen"
        >
          <i class="pi text-lg" :class="mobileOpen ? 'pi-times' : 'pi-bars'"></i>
        </button>
      </div>
    </div>

    <!-- Mobile drawer -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="max-h-0 opacity-0"
      enter-to-class="max-h-96 opacity-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="max-h-96 opacity-100"
      leave-to-class="max-h-0 opacity-0"
    >
      <div v-if="mobileOpen" class="overflow-hidden border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 md:hidden">
        <div class="flex flex-col gap-1 px-6 py-4">
          <button
            v-for="link in navLinks"
            :key="link.id"
            type="button"
            class="rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-600 dark:text-gray-400 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900"
            @click="scrollTo(link.id)"
          >
            {{ t(link.labelKey) }}
          </button>
          <div class="my-2 border-t border-gray-100"></div>
          <template v-if="!authStore.isAuthenticated">
            <Button
              :label="t('nav.signIn')"
              text
              severity="secondary"
              class="justify-start"
              @click="goToRoute(ROUTE_NAMES.LOGIN)"
            />
            <Button
              :label="t('landing.hero.getStarted')"
              @click="goToRoute(ROUTE_NAMES.REGISTER)"
            />
          </template>
          <template v-else>
            <Button
              :label="t('nav.dashboard')"
              icon="pi pi-th-large"
              @click="goToRoute(ROUTE_NAMES.DASHBOARD)"
            />
            <Button
              :label="t('nav.profile')"
              icon="pi pi-user"
              text
              severity="secondary"
              class="justify-start"
              @click="goToRoute(ROUTE_NAMES.PROFILE)"
            />
            <Button
              :label="t('nav.logout')"
              icon="pi pi-sign-out"
              text
              severity="secondary"
              class="justify-start"
              @click="handleLogout"
            />
          </template>
        </div>
      </div>
    </Transition>
  </nav>
</template>
