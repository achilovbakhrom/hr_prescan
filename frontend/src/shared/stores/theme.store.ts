import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

export type ColorScheme = 'light' | 'dark' | 'system'
export type BackgroundMode = 'off' | 'aurora' | 'mesh' | 'constellation' | 'vellum'

const SCHEME_KEY = 'hr_prescan_color_scheme'
const BG_KEY = 'hr_prescan_bg_mode'

const VALID_BG_MODES: readonly BackgroundMode[] = [
  'off',
  'aurora',
  'mesh',
  'constellation',
  'vellum',
]

function readScheme(): ColorScheme {
  const v = localStorage.getItem(SCHEME_KEY)
  return v === 'light' || v === 'dark' || v === 'system' ? v : 'system'
}

function readBackground(): BackgroundMode {
  const v = localStorage.getItem(BG_KEY)
  if (v === null) return 'aurora'
  if ((VALID_BG_MODES as readonly string[]).includes(v)) return v as BackgroundMode
  // Legacy value (e.g. 'forest', 'ocean') or garbage — migrate to 'aurora'
  // and persist so the next read is clean.
  localStorage.setItem(BG_KEY, 'aurora')
  return 'aurora'
}

function systemPrefersDark(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export const useThemeStore = defineStore('theme', () => {
  const colorScheme = ref<ColorScheme>(readScheme())
  const backgroundMode = ref<BackgroundMode>(readBackground())

  const resolvedDark = computed(
    () => colorScheme.value === 'dark' || (colorScheme.value === 'system' && systemPrefersDark()),
  )

  function applyDarkClass(): void {
    document.documentElement.classList.toggle('dark', resolvedDark.value)
  }

  function setColorScheme(scheme: ColorScheme): void {
    colorScheme.value = scheme
    localStorage.setItem(SCHEME_KEY, scheme)
    applyDarkClass()
  }

  function cycleColorScheme(): void {
    const order: ColorScheme[] = ['light', 'dark', 'system']
    const next = order[(order.indexOf(colorScheme.value) + 1) % order.length]
    setColorScheme(next)
  }

  function setBackgroundMode(mode: BackgroundMode): void {
    backgroundMode.value = mode
    localStorage.setItem(BG_KEY, mode)
  }

  // React to OS-level color-scheme changes while the user is on "system".
  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  mq.addEventListener('change', () => {
    if (colorScheme.value === 'system') applyDarkClass()
  })

  watch(resolvedDark, applyDarkClass, { immediate: true })

  return {
    colorScheme,
    backgroundMode,
    resolvedDark,
    setColorScheme,
    cycleColorScheme,
    setBackgroundMode,
  }
})
