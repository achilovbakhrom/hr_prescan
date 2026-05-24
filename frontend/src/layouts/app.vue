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
    <template v-if="appReady" #nav>
      <AppNavbar
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleDesktopSidebar"
        @toggle-mobile-nav="toggleMobileNav"
      />
    </template>

    <div v-if="appReady" class="flex flex-1">
      <div class="mx-auto flex w-full max-w-[1760px] min-w-0 gap-0 xl:px-2">
        <AppSidebar
          :collapsed="sidebarCollapsed"
          class="hidden lg:sticky lg:top-24 lg:flex lg:h-[calc(100vh-7rem)] lg:self-start"
          @toggle="toggleDesktopSidebar"
        />

        <div class="min-w-0 flex-1 lg:pl-5" id="main-content">
          <slot />
        </div>
      </div>
    </div>

    <div v-else class="flex min-h-[60vh] items-center justify-center">
      <i class="pi pi-spinner pi-spin text-2xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <MobileNav v-if="appReady" :open="mobileNavOpen" @close="closeMobileNav" />
    <Toast position="bottom-right" />
  </PageShell>
</template>
