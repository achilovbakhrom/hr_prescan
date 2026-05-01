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

import App from './App.vue'
import { router } from './router'
import { i18n, detectAndApplyLocale } from '@/shared/i18n'
import { initializeGoogleAnalytics } from '@/shared/analytics/googleAnalytics'

import '@/assets/styles/main.css'
import '@/assets/styles/primevue-overrides.css'
// Dark-mode overrides load LAST so `!important` rules win over utilities.
import '@/assets/styles/dark-mode.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
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
