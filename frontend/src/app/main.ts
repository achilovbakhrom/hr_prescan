import '@fontsource/geist-sans/400.css'
import '@fontsource/geist-sans/500.css'
import '@fontsource/geist-sans/600.css'
import '@fontsource/geist-sans/700.css'
import '@fontsource/geist-mono/400.css'
import '@fontsource/geist-mono/500.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import Aura from '@primevue/themes/aura'
import { definePreset } from '@primevue/themes'

import App from './App.vue'
import { router } from './router'
import { i18n, detectAndApplyLocale } from '@/shared/i18n'
import { initializeGoogleAnalytics } from '@/shared/analytics/googleAnalytics'

import '@/assets/styles/main.css'
import '@/assets/styles/primevue-overrides.css'
// Dark-mode overrides load LAST so `!important` rules win over utilities.
import '@/assets/styles/dark-mode.css'

// PreScreen AI brand preset — violet primary (Figma redesign) instead of Aura's emerald.
const PreScreenPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#f5f3ff',
      100: '#ede9fe',
      200: '#ddd6fe',
      300: '#c4b5fd',
      400: '#a78bfa',
      500: '#8b5cf6',
      600: '#7c3aed',
      700: '#6d28d9',
      800: '#5b21b6',
      900: '#4c1d95',
      950: '#2e1065',
    },
  },
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(PrimeVue, {
  theme: {
    preset: PreScreenPreset,
    options: {
      darkModeSelector: '.dark',
    },
  },
})
app.use(ConfirmationService)
app.use(ToastService)

initializeGoogleAnalytics(router)

app.mount('#app')

void detectAndApplyLocale()
