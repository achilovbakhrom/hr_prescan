<script setup lang="ts">
import { ref } from 'vue'
import AppNavbar from './AppNavbar.vue'
import AppSidebar from './AppSidebar.vue'
import MobileNav from './MobileNav.vue'

const sidebarCollapsed = ref(false)
const mobileNavOpen = ref(false)

function toggleSidebar(): void {
  // On mobile, toggle the mobile drawer; on desktop, collapse the sidebar
  if (window.innerWidth < 1024) {
    mobileNavOpen.value = !mobileNavOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

function closeSidebar(): void {
  sidebarCollapsed.value = true
}

function closeMobileNav(): void {
  mobileNavOpen.value = false
}
</script>

<template>
  <div class="flex h-screen flex-col">
    <AppNavbar
      :sidebar-collapsed="sidebarCollapsed"
      @toggle-sidebar="toggleSidebar"
    />

    <div class="flex flex-1 overflow-hidden">
      <!-- Desktop overlay (collapsed sidebar backdrop) -->
      <div
        v-if="!sidebarCollapsed"
        class="fixed inset-0 z-20 bg-black/50 lg:hidden"
        @click="closeSidebar"
      ></div>

      <!-- Desktop Sidebar -->
      <div
        class="hidden lg:relative lg:z-auto lg:flex"
        :class="!sidebarCollapsed ? 'lg:static' : ''"
      >
        <AppSidebar :collapsed="sidebarCollapsed" @close="closeSidebar" />
      </div>

      <!-- Main content -->
      <main class="flex-1 overflow-y-auto bg-gray-50" id="main-content">
        <RouterView />
      </main>
    </div>

    <!-- Mobile slide-out navigation -->
    <MobileNav :open="mobileNavOpen" @close="closeMobileNav" />
  </div>
</template>
