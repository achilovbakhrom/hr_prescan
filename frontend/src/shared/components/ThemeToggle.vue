<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'
import { useThemeStore } from '@/shared/stores/theme.store'

const themeStore = useThemeStore()

const icon = computed(() => {
  if (themeStore.colorScheme === 'light') return 'pi pi-sun'
  if (themeStore.colorScheme === 'dark') return 'pi pi-moon'
  return 'pi pi-desktop'
})

const label = computed(() => {
  if (themeStore.colorScheme === 'light') return 'Light theme (click for dark)'
  if (themeStore.colorScheme === 'dark') return 'Dark theme (click for system)'
  return 'System theme (click for light)'
})
</script>

<template>
  <Button
    type="button"
    :icon="icon"
    severity="secondary"
    text
    rounded
    size="small"
    class="!px-2.5"
    :aria-label="label"
    :title="label"
    @click="themeStore.cycleColorScheme"
  />
</template>
