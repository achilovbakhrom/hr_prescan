<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

const COOKIE_CONSENT_KEY = 'hr_prescan_cookie_consent'

type ConsentState = 'accepted' | 'declined' | null

const { t } = useI18n()
const visible = ref(false)

onMounted(() => {
  const stored = localStorage.getItem(COOKIE_CONSENT_KEY) as ConsentState
  if (!stored) {
    // Slight delay so it doesn't flash on first paint
    setTimeout(() => {
      visible.value = true
    }, 1500)
  }
})

function accept(): void {
  localStorage.setItem(COOKIE_CONSENT_KEY, 'accepted')
  visible.value = false
}

function decline(): void {
  localStorage.setItem(COOKIE_CONSENT_KEY, 'declined')
  visible.value = false
}
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-500 ease-out"
    enter-from-class="translate-y-full opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition-all duration-300 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-full opacity-0"
  >
    <div
      v-if="visible"
      class="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-2xl"
      role="dialog"
      aria-modal="false"
      aria-label="Cookie consent"
      aria-live="polite"
    >
      <div
        class="mx-auto flex max-w-7xl flex-col items-start justify-between gap-4 px-6 py-5 sm:flex-row sm:items-center"
      >
        <div class="flex-1">
          <p class="text-sm leading-relaxed text-gray-700">
            {{ t('cookies.message') }}
            <RouterLink
              to="/privacy"
              class="ml-1 font-medium text-blue-600 dark:text-blue-400 hover:underline"
              @click="visible = false"
            >
              {{ t('cookies.learnMore') }}
            </RouterLink>
          </p>
        </div>
        <div class="flex shrink-0 items-center gap-3">
          <Button
            :label="t('cookies.decline')"
            text
            severity="secondary"
            size="small"
            @click="decline"
          />
          <Button :label="t('cookies.accept')" size="small" @click="accept" />
        </div>
      </div>
    </div>
  </Transition>
</template>
