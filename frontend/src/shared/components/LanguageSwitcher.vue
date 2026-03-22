<script setup lang="ts">
import { useLocale } from '../composables/useLocale'
import type { SupportedLocale } from '../composables/useLocale'
import Dropdown from 'primevue/dropdown'

const { currentLocale, localeOptions, switchLocale } = useLocale()

function handleChange(event: { value: SupportedLocale }): void {
  switchLocale(event.value)
}
</script>

<template>
  <Dropdown
    :model-value="currentLocale"
    :options="localeOptions"
    option-label="label"
    option-value="code"
    class="w-28"
    @change="handleChange"
  />
</template>
