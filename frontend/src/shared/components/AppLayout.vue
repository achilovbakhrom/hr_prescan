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

    <div class="flex flex-1 gap-0">
      <!-- Desktop Sidebar (always rendered, collapsible) -->
      <AppSidebar
        :collapsed="sidebarCollapsed"
        class="hidden lg:flex"
        @toggle="toggleDesktopSidebar"
      />

      <!-- Main content -->
      <div class="min-w-0 flex-1" id="main-content">
        <RouterView />
      </div>
    </div>

    <!-- Mobile slide-out navigation (teleported, only on small screens) -->
    <MobileNav :open="mobileNavOpen" @close="closeMobileNav" />

    <!-- Global toast outlet -->
    <Toast position="bottom-right" />
  </PageShell>
</template>
