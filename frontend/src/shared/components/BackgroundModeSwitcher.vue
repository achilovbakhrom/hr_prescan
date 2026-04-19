<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Popover from 'primevue/popover'
import { useThemeStore, type BackgroundMode } from '@/shared/stores/theme.store'

interface Mode {
  code: BackgroundMode
  label: string
  emoji: string
}

const MODES: Mode[] = [
  { code: 'off', label: 'No background', emoji: '⬜' },
  { code: 'forest', label: 'Forest', emoji: '🦊' },
  { code: 'ocean', label: 'Ocean', emoji: '🐋' },
]

const themeStore = useThemeStore()
const popover = ref()

function toggle(event: Event): void {
  popover.value.toggle(event)
}

function select(code: BackgroundMode): void {
  themeStore.setBackgroundMode(code)
  popover.value.hide()
}
</script>

<template>
  <Button
    type="button"
    icon="pi pi-palette"
    severity="secondary"
    text
    rounded
    size="small"
    class="!px-2.5"
    aria-label="Background style"
    title="Background style"
    @click="toggle"
  />
  <Popover ref="popover">
    <div class="flex flex-col gap-0.5 py-1">
      <button
        v-for="mode in MODES"
        :key="mode.code"
        type="button"
        role="option"
        :aria-selected="mode.code === themeStore.backgroundMode"
        class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
        :class="
          mode.code === themeStore.backgroundMode
            ? 'bg-blue-50 font-medium text-blue-700 dark:bg-blue-950 dark:text-blue-300'
            : 'text-gray-700 dark:text-gray-200'
        "
        @click="select(mode.code)"
      >
        <span class="text-base">{{ mode.emoji }}</span>
        <span>{{ mode.label }}</span>
        <i
          v-if="mode.code === themeStore.backgroundMode"
          class="pi pi-check ml-auto text-xs text-blue-500"
        ></i>
      </button>
    </div>
  </Popover>
</template>
