<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'
import { useThemeStore } from '@/shared/stores/theme.store'

const themeStore = useThemeStore()

const icon = computed(() => (themeStore.resolvedDark ? 'pi pi-sun' : 'pi pi-moon'))
const label = computed(() =>
  themeStore.resolvedDark ? 'Switch to light theme' : 'Switch to dark theme',
)
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
