import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

// Two-state color scheme. `system` was dropped — users toggle explicitly.
export type ColorScheme = 'light' | 'dark'
export type BackgroundMode =
  | 'off'
  | 'mesh'
  | 'constellation'
  | 'vellum'
  | 'aurora'
  | 'waves'
  | 'ocean'
  | 'rays'
  | 'catgarden'

const SCHEME_KEY = 'hr_prescan_color_scheme'
const BG_KEY = 'hr_prescan_bg_mode'
const DEFAULT_BACKGROUND_MODE: BackgroundMode = 'catgarden'

const VALID_BG_MODES: readonly BackgroundMode[] = [
  'off',
  'mesh',
  'constellation',
  'vellum',
  'aurora',
  'waves',
  'ocean',
  'rays',
  'catgarden',
]

function readScheme(): ColorScheme {
  if (typeof localStorage === 'undefined') return 'light'
  const v = localStorage.getItem(SCHEME_KEY)
  return v === 'dark' ? 'dark' : 'light'
}

function readBackground(): BackgroundMode {
  if (typeof localStorage === 'undefined') return DEFAULT_BACKGROUND_MODE
  const v = localStorage.getItem(BG_KEY)
  if (v === null) return DEFAULT_BACKGROUND_MODE
  if ((VALID_BG_MODES as readonly string[]).includes(v)) return v as BackgroundMode
  localStorage.setItem(BG_KEY, DEFAULT_BACKGROUND_MODE)
  return DEFAULT_BACKGROUND_MODE
}

export const useThemeStore = defineStore('theme', () => {
  const colorScheme = ref<ColorScheme>('light')
  const backgroundMode = ref<BackgroundMode>(DEFAULT_BACKGROUND_MODE)
  const resolvedDark = computed(() => colorScheme.value === 'dark')

  function applyDarkClass(): void {
    if (typeof document === 'undefined') return
    document.documentElement.classList.toggle('dark', resolvedDark.value)
  }

  function setColorScheme(scheme: ColorScheme): void {
    colorScheme.value = scheme
    if (typeof localStorage !== 'undefined') localStorage.setItem(SCHEME_KEY, scheme)
    applyDarkClass()
  }

  function cycleColorScheme(): void {
    setColorScheme(colorScheme.value === 'dark' ? 'light' : 'dark')
  }

  function setBackgroundMode(mode: BackgroundMode): void {
    backgroundMode.value = mode
    if (typeof localStorage !== 'undefined') localStorage.setItem(BG_KEY, mode)
  }

  function hydratePreferences(): void {
    if (typeof localStorage === 'undefined') return
    colorScheme.value = readScheme()
    backgroundMode.value = readBackground()
    applyDarkClass()
  }

  watch(resolvedDark, applyDarkClass, { immediate: true })

  return {
    colorScheme,
    backgroundMode,
    resolvedDark,
    setColorScheme,
    cycleColorScheme,
    setBackgroundMode,
    hydratePreferences,
  }
})
