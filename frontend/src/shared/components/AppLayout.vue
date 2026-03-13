<script setup lang="ts">
import { ref } from 'vue'
import AppNavbar from './AppNavbar.vue'
import AppSidebar from './AppSidebar.vue'

const sidebarCollapsed = ref(false)

function toggleSidebar(): void {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function closeSidebar(): void {
  sidebarCollapsed.value = true
}
</script>

<template>
  <div class="flex h-screen flex-col">
    <AppNavbar
      :sidebar-collapsed="sidebarCollapsed"
      @toggle-sidebar="toggleSidebar"
    />

    <div class="flex flex-1 overflow-hidden">
      <!-- Mobile overlay -->
      <div
        v-if="!sidebarCollapsed"
        class="fixed inset-0 z-20 bg-black/50 lg:hidden"
        @click="closeSidebar"
      ></div>

      <!-- Sidebar -->
      <div
        class="z-30 lg:relative lg:z-auto"
        :class="!sidebarCollapsed ? 'fixed inset-y-16 left-0 lg:static' : ''"
      >
        <AppSidebar :collapsed="sidebarCollapsed" @close="closeSidebar" />
      </div>

      <!-- Main content -->
      <main class="flex-1 overflow-y-auto bg-gray-50">
        <RouterView />
      </main>
    </div>
  </div>
</template>
