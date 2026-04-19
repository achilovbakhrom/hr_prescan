<script setup lang="ts">
/**
 * LandingNav — translucent glass header, sticky at top. Adds `shadow-glass`
 * once the page has scrolled past 16px. Mobile hamburger opens a full-screen
 * glass sheet (see LandingNavMobile).
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import type { MenuItem } from 'primevue/menuitem'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import LandingNavMobile from './LandingNavMobile.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const mobileOpen = ref(false)
const scrolled = ref(false)
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

const navLinks = [
  { id: 'features', labelKey: 'landing.footer.features' },
  { id: 'how-it-works', labelKey: 'landing.howItWorks.title' },
  { id: 'pricing', labelKey: 'landing.footer.pricing' },
] as const

function toggleUserMenu(event: Event): void {
  userMenu.value?.toggle(event)
}

function scrollTo(id: string): void {
  mobileOpen.value = false
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function onScroll(): void {
  scrolled.value = window.scrollY > 16
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <nav
    class="sticky top-0 z-40 transition-shadow duration-300 ease-ios"
    :class="scrolled ? 'shadow-glass' : ''"
  >
    <div class="bg-glass-1 border-b border-glass backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <AppLogo variant="full" size="md" />

        <!-- Desktop links -->
        <div class="hidden items-center gap-1 md:flex">
          <button
            v-for="link in navLinks"
            :key="link.id"
            type="button"
            class="rounded-md px-3 py-1.5 text-sm font-medium text-[color:var(--color-text-secondary)] transition-colors duration-200 ease-ios hover:bg-[color:var(--color-surface-raised)] hover:text-[color:var(--color-text-primary)]"
            @click="scrollTo(link.id)"
          >
            {{ t(link.labelKey) }}
          </button>
        </div>

        <div class="flex items-center gap-2">
          <LanguageSwitcher class="hidden sm:inline-flex" />
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
              class="flex items-center gap-2 rounded-md px-2 py-1 transition-colors duration-200 ease-ios hover:bg-[color:var(--color-surface-raised)]"
              @click="toggleUserMenu"
            >
              <div
                class="flex h-8 w-8 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-sm font-medium text-[color:var(--color-accent)]"
              >
                {{ authStore.user?.firstName?.charAt(0) }}{{ authStore.user?.lastName?.charAt(0) }}
              </div>
              <span
                class="hidden text-sm font-medium text-[color:var(--color-text-primary)] sm:inline"
              >
                {{ authStore.user?.firstName }}
              </span>
            </button>
            <Menu ref="userMenu" :model="menuItems" :popup="true" />
          </template>
          <template v-else>
            <Button
              :label="t('nav.signIn')"
              text
              severity="secondary"
              size="small"
              class="hidden sm:flex"
              @click="router.push({ name: ROUTE_NAMES.LOGIN })"
            />
            <Button
              :label="t('landing.hero.getStarted')"
              size="small"
              class="hidden sm:flex"
              @click="router.push({ name: ROUTE_NAMES.REGISTER })"
            />
          </template>

          <!-- Mobile hamburger -->
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-md text-[color:var(--color-text-secondary)] transition-colors hover:bg-[color:var(--color-surface-raised)] md:hidden"
            aria-label="Open menu"
            @click="mobileOpen = !mobileOpen"
          >
            <i class="pi text-lg" :class="mobileOpen ? 'pi-times' : 'pi-bars'"></i>
          </button>
        </div>
      </div>
    </div>

    <LandingNavMobile :open="mobileOpen" :nav-links="navLinks" @close="mobileOpen = false" />
  </nav>
</template>
