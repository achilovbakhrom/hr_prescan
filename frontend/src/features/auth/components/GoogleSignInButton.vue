<script setup lang="ts">
import { onMounted, ref } from 'vue'

const emit = defineEmits<{
  success: [credential: string]
  error: [message: string]
}>()

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string
const loading = ref(false)
const ready = ref(false)

interface GoogleCredentialResponse {
  credential: string
  select_by: string
}

interface GoogleNotification {
  isNotDisplayed: () => boolean
  isSkippedMoment: () => boolean
  getNotDisplayedReason: () => string
  getSkippedReason: () => string
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void
          prompt: (callback?: (notification: GoogleNotification) => void) => void
          renderButton: (el: HTMLElement, config: Record<string, unknown>) => void
        }
      }
    }
  }
}

function handleCredentialResponse(response: GoogleCredentialResponse): void {
  loading.value = false
  if (response.credential) {
    emit('success', response.credential)
  } else {
    emit('error', 'Google sign-in failed')
  }
}

function handleClick(): void {
  if (!window.google || loading.value) return
  loading.value = true

  // Render a hidden Google button and click it to trigger the popup flow
  // This is more reliable than prompt() which uses One Tap
  const hiddenDiv = document.createElement('div')
  hiddenDiv.style.position = 'fixed'
  hiddenDiv.style.top = '-9999px'
  hiddenDiv.style.left = '-9999px'
  document.body.appendChild(hiddenDiv)

  window.google.accounts.id.renderButton(hiddenDiv, {
    type: 'standard',
    size: 'large',
  })

  // Click the rendered button's inner element
  const btn =
    hiddenDiv.querySelector<HTMLElement>('[role="button"]') ||
    hiddenDiv.querySelector<HTMLElement>('div[style]')

  if (btn) {
    btn.click()
  } else {
    // Fallback: try One Tap prompt
    window.google.accounts.id.prompt((notification: GoogleNotification) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        loading.value = false
        emit('error', 'Google sign-in is not available. Please try another method.')
      }
    })
  }

  // Clean up hidden div after a delay
  setTimeout(() => {
    hiddenDiv.remove()
    loading.value = false
  }, 30000)
}

onMounted(() => {
  if (!clientId) return

  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.defer = true
  script.onload = () => {
    if (!window.google) return

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: handleCredentialResponse,
      ux_mode: 'popup',
    })

    ready.value = true
  }
  document.head.appendChild(script)
})
</script>

<template>
  <button
    v-if="clientId"
    type="button"
    :disabled="!ready || loading"
    class="mb-4 flex w-full items-center justify-center gap-3 rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    @click="handleClick"
  >
    <svg
      v-if="!loading"
      width="18"
      height="18"
      viewBox="0 0 48 48"
    >
      <path
        fill="#EA4335"
        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
      />
      <path
        fill="#4285F4"
        d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
      />
      <path
        fill="#FBBC05"
        d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
      />
      <path
        fill="#34A853"
        d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
      />
    </svg>
    <svg
      v-else
      class="animate-spin"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="3"
        class="opacity-25"
      />
      <path
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        class="opacity-75"
      />
    </svg>
    <span>Continue with Google</span>
  </button>
</template>
