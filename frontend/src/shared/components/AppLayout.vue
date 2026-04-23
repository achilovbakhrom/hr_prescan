<script setup lang="ts">
import { ref, watch } from 'vue'
import Toast from 'primevue/toast'
import AppNavbar from './AppNavbar.vue'
import AppSidebar from './AppSidebar.vue'
import MobileNav from './MobileNav.vue'
import PageShell from './PageShell.vue'

const sidebarCollapsed = ref(localStorage.getItem('sidebar_collapsed') === 'true')
const mobileNavOpen = ref(false)

function toggleDesktopSidebar(): void {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

watch(sidebarCollapsed, (val) => localStorage.setItem('sidebar_collapsed', String(val)))

function toggleMobileNav(): void {
  mobileNavOpen.value = !mobileNavOpen.value
}

function closeMobileNav(): void {
  mobileNavOpen.value = false
}
</script>

<template>
  <PageShell variant="app">
    <template #nav>
      <AppNavbar
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleDesktopSidebar"
        @toggle-mobile-nav="toggleMobileNav"
      />
    </template>

    <div class="flex flex-1">
      <div class="mx-auto flex w-full max-w-[1600px] min-w-0 gap-0 xl:px-2">
        <AppSidebar
          :collapsed="sidebarCollapsed"
          class="hidden lg:sticky lg:top-24 lg:flex lg:h-[calc(100vh-7rem)] lg:self-start"
          @toggle="toggleDesktopSidebar"
        />

        <div class="min-w-0 flex-1 lg:pl-5" id="main-content">
          <RouterView />
        </div>
      </div>
    </div>

    <MobileNav :open="mobileNavOpen" @close="closeMobileNav" />
    <Toast position="bottom-right" />
  </PageShell>
</template>
