import { i18n, detectAndApplyLocale } from '@/shared/i18n'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(i18n)
  if (import.meta.client) void detectAndApplyLocale()
})
