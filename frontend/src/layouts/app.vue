<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import Toast from 'primevue/toast'
import AppNavbar from '@/shared/components/AppNavbar.vue'
import AppSidebar from '@/shared/components/AppSidebar.vue'
import MobileNav from '@/shared/components/MobileNav.vue'
import PageShell from '@/shared/components/PageShell.vue'
import { useAuthStore } from '@/features/auth/stores/auth.store'

const sidebarCollapsed = ref(false)
const mobileNavOpen = ref(false)
const appReady = ref(false)
const authStore = useAuthStore()

onMounted(async () => {
  try {
    if (authStore.tokens && !authStore.user) await authStore.initAuth()
    sidebarCollapsed.value = localStorage.getItem('sidebar_collapsed') === 'true'
  } finally {
    appReady.value = true
  }
})

function toggleDesktopSidebar(): void {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

watch(sidebarCollapsed, (val) => {
  if (import.meta.client) localStorage.setItem('sidebar_collapsed', String(val))
})

function toggleMobileNav(): void {
  mobileNavOpen.value = !mobileNavOpen.value
}

function closeMobileNav(): void {
  mobileNavOpen.value = false
}
</script>

<template>
  <PageShell variant="app">
    <div v-if="appReady" class="flex min-h-screen w-full">
      <!-- Full-height sidebar (Figma: logo at top, flush left) -->
      <AppSidebar
        :collapsed="sidebarCollapsed"
        class="hidden shrink-0 self-start lg:sticky lg:top-0 lg:flex lg:h-screen"
        @toggle="toggleDesktopSidebar"
      />

      <!-- Content column: topbar + page -->
      <div class="flex min-w-0 flex-1 flex-col">
        <AppNavbar
          :sidebar-collapsed="sidebarCollapsed"
          @toggle-sidebar="toggleDesktopSidebar"
          @toggle-mobile-nav="toggleMobileNav"
        />
        <main id="main-content" class="w-full flex-1 px-4 py-5 sm:px-6 lg:px-8">
          <slot />
        </main>
      </div>
    </div>

    <div v-else class="flex min-h-[60vh] items-center justify-center">
      <i class="pi pi-spinner pi-spin text-2xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <MobileNav v-if="appReady" :open="mobileNavOpen" @close="closeMobileNav" />
    <Toast position="bottom-right" />
  </PageShell>
</template>
