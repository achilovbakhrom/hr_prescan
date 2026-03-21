<script setup lang="ts">
import { ref, watch } from 'vue'
import AppNavbar from './AppNavbar.vue'
import AppSidebar from './AppSidebar.vue'
import MobileNav from './MobileNav.vue'

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
  <div class="flex h-screen flex-col">
    <AppNavbar
      :sidebar-collapsed="sidebarCollapsed"
      @toggle-sidebar="toggleDesktopSidebar"
      @toggle-mobile-nav="toggleMobileNav"
    />

    <div class="flex flex-1 overflow-hidden">
      <!-- Desktop Sidebar (always rendered, collapsible) -->
      <AppSidebar
        :collapsed="sidebarCollapsed"
        class="hidden lg:flex"
        @toggle="toggleDesktopSidebar"
      />

      <!-- Main content -->
      <main class="flex-1 overflow-y-auto bg-gray-50 p-3 sm:p-5 lg:p-8" id="main-content">
        <RouterView />
      </main>
    </div>

    <!-- Mobile slide-out navigation (teleported, only on small screens) -->
    <MobileNav :open="mobileNavOpen" @close="closeMobileNav" />
  </div>
</template>
