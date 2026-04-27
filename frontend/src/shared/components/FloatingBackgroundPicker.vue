<script setup lang="ts">
/**
 * FloatingBackgroundPicker — fixed bottom-right control that lets users pick
 * one of the available animated backgrounds.
 * Dark mode was removed — theme-cycle button is gone.
 *
 * Replaces the legacy BackgroundModeSwitcher.vue popover.
 * Spec: docs/design/spec.md §5, §10.
 *
 * Keyboard:
 *   - `?` or `Alt+B` toggles open
 *   - `Esc` closes
 *   - Arrow keys navigate thumbs when open
 *   - `Enter` / `Space` on a thumb selects it
 */
import { nextTick, ref } from 'vue'
import { useThemeStore, type BackgroundMode } from '@/shared/stores/theme.store'
import { useBackgroundPickerKeys } from '@/shared/composables/useBackgroundPickerKeys'
import GlassSurface from './GlassSurface.vue'
import BackgroundThumb from './BackgroundThumb.vue'
import './FloatingBackgroundPicker.css'

interface ThumbDef {
  code: Exclude<BackgroundMode, 'off'>
  label: string
}

const THUMBS: readonly ThumbDef[] = [
  { code: 'mesh', label: 'Mesh' },
  { code: 'constellation', label: 'Constellation' },
  { code: 'vellum', label: 'Sheets' },
  { code: 'aurora', label: 'Aurora' },
  { code: 'waves', label: 'Flow' },
  { code: 'ocean', label: 'Ocean' },
  { code: 'rays', label: 'Planes' },
]

const themeStore = useThemeStore()
const open = ref(false)
const rootRef = ref<HTMLElement | null>(null)
const thumbRefs = ref<HTMLButtonElement[]>([])

function setThumbRef(el: Element | null, index: number): void {
  if (el instanceof HTMLButtonElement) thumbRefs.value[index] = el
}

function toggleOpen(): void {
  open.value = !open.value
  if (open.value) {
    void nextTick(() => {
      const selectedIdx = THUMBS.findIndex((t) => t.code === themeStore.backgroundMode)
      const idx = selectedIdx >= 0 ? selectedIdx : 0
      thumbRefs.value[idx]?.focus()
    })
  }
}

function close(): void {
  open.value = false
}

function selectThumb(code: BackgroundMode): void {
  themeStore.setBackgroundMode(code)
}

function onThumbKeydown(event: KeyboardEvent, index: number): void {
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    event.preventDefault()
    const next = (index + 1) % THUMBS.length
    thumbRefs.value[next]?.focus()
  } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    event.preventDefault()
    const prev = (index - 1 + THUMBS.length) % THUMBS.length
    thumbRefs.value[prev]?.focus()
  } else if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    selectThumb(THUMBS[index].code)
  }
}

useBackgroundPickerKeys({ rootRef, isOpen: open, toggle: toggleOpen, close })
</script>

<template>
  <div
    ref="rootRef"
    class="fixed bottom-4 right-4 z-50 flex items-center gap-2"
    role="toolbar"
    aria-label="Background picker"
  >
    <Transition name="picker">
      <GlassSurface
        v-if="open"
        level="float"
        class="flex items-center gap-2 rounded-full p-1.5 min-h-[44px]"
      >
        <div
          role="radiogroup"
          aria-label="Background variant"
          class="grid grid-cols-2 gap-1.5 md:flex md:flex-row md:gap-1.5"
        >
          <button
            v-for="(thumb, index) in THUMBS"
            :key="thumb.code"
            :ref="(el) => setThumbRef(el as Element | null, index)"
            type="button"
            role="radio"
            :aria-checked="themeStore.backgroundMode === thumb.code"
            :aria-label="thumb.label"
            :title="thumb.label"
            class="fbp-thumb"
            :class="{ 'fbp-thumb--selected': themeStore.backgroundMode === thumb.code }"
            @click="selectThumb(thumb.code)"
            @keydown="onThumbKeydown($event, index)"
          >
            <BackgroundThumb :kind="thumb.code" />
          </button>
        </div>
      </GlassSurface>
    </Transition>

    <button
      type="button"
      class="fbp-trigger bg-glass-float border-glass shadow-glass-float"
      :aria-expanded="open"
      aria-haspopup="true"
      aria-label="Background picker"
      title="Background (? or Alt+B)"
      @click="toggleOpen"
    >
      <i class="pi pi-palette" />
    </button>
  </div>
</template>
