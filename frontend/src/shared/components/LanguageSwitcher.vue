<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Popover from 'primevue/popover'
import { useLocale } from '../composables/useLocale'
import type { SupportedLocale } from '../composables/useLocale'

const { currentLocale, currentLocaleOption, localeOptions, switchLocale } = useLocale()
const popover = ref()

function toggle(event: Event): void {
  popover.value.toggle(event)
}

function selectLocale(code: SupportedLocale): void {
  switchLocale(code)
  popover.value.hide()
}
</script>

<template>
  <Button
    type="button"
    :label="currentLocaleOption?.code.toUpperCase()"
    icon="pi pi-globe"
    severity="secondary"
    text
    rounded
    size="small"
    class="!gap-1 !px-2.5"
    aria-label="Select language"
    aria-haspopup="true"
    @click="toggle"
  />
  <Popover ref="popover">
    <div class="flex flex-col gap-0.5 py-1">
      <button
        v-for="option in localeOptions"
        :key="option.code"
        type="button"
        role="option"
        :aria-selected="option.code === currentLocale"
        class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-gray-100"
        :class="
          option.code === currentLocale ? 'bg-blue-50 font-medium text-blue-700' : 'text-gray-700'
        "
        @click="selectLocale(option.code)"
      >
        <span class="text-base">{{ option.flag }}</span>
        <span>{{ option.label }}</span>
        <i
          v-if="option.code === currentLocale"
          class="pi pi-check ml-auto text-xs text-blue-500"
        ></i>
      </button>
    </div>
  </Popover>
</template>
