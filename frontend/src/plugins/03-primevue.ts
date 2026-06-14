import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import Aura from '@primevue/themes/aura'
import { definePreset } from '@primevue/themes'

// PreScreen AI brand preset — violet primary (Figma redesign) instead of Aura's
// default emerald. Light buttons use primary.500/600, dark uses primary.400.
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

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PrimeVue, {
    theme: {
      preset: PreScreenPreset,
      options: {
        darkModeSelector: '.dark',
      },
    },
  })
  nuxtApp.vueApp.use(ConfirmationService)
  nuxtApp.vueApp.use(ToastService)
})
