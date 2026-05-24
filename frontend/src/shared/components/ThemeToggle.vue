<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useThemeStore } from '@/shared/stores/theme.store'

const themeStore = useThemeStore()
const { t } = useI18n()

const icon = computed(() => (themeStore.resolvedDark ? 'pi pi-sun' : 'pi pi-moon'))
const label = computed(() => t('settings.theme'))
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
