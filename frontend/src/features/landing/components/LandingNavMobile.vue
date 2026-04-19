<script setup lang="ts">
/**
 * LandingNavMobile — the full-screen glass overlay opened by the hamburger.
 * Split out from LandingNav so each file stays under the 200-line limit.
 */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import ThemeToggle from '@/shared/components/ThemeToggle.vue'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'

interface NavLink {
  id: string
  labelKey: string
}

defineProps<{
  open: boolean
  navLinks: readonly NavLink[]
}>()

const emit = defineEmits<{
  close: []
}>()

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

function scrollTo(id: string): void {
  emit('close')
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function goToRoute(name: string): void {
  router.push({ name })
  emit('close')
}

async function handleLogout(): Promise<void> {
  await authStore.logout()
  emit('close')
  await router.push({ name: ROUTE_NAMES.LOGIN })
}
</script>

<template>
  <Transition
    enter-active-class="transition-opacity duration-200 ease-ios"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-150 ease-ios"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="open"
      class="bg-glass-float fixed inset-0 top-[60px] z-30 md:hidden"
      @click.self="emit('close')"
    >
      <div class="flex flex-col gap-1 px-6 py-6">
        <button
          v-for="link in navLinks"
          :key="link.id"
          type="button"
          class="rounded-md px-4 py-3 text-left text-base font-medium text-[color:var(--color-text-primary)] transition-colors hover:bg-[color:var(--color-surface-raised)]"
          @click="scrollTo(link.id)"
        >
          {{ t(link.labelKey) }}
        </button>
        <div class="my-3 border-t border-[color:var(--color-border-soft)]"></div>
        <template v-if="!authStore.isAuthenticated">
          <Button
            :label="t('nav.signIn')"
            text
            severity="secondary"
            class="justify-start"
            @click="goToRoute(ROUTE_NAMES.LOGIN)"
          />
        </template>
        <template v-else>
          <Button
            :label="t('nav.dashboard')"
            icon="pi pi-th-large"
            @click="goToRoute(ROUTE_NAMES.DASHBOARD)"
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
        <div class="my-3 border-t border-[color:var(--color-border-soft)]"></div>
        <div class="flex items-center justify-end gap-2 px-2 py-2">
          <LanguageSwitcher />
          <ThemeToggle />
        </div>
      </div>
    </div>
  </Transition>
</template>
