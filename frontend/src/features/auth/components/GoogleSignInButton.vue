<script setup lang="ts">
import { onMounted, ref } from 'vue'

const emit = defineEmits<{
  success: [credential: string]
  error: [message: string]
}>()

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string
const buttonContainer = ref<HTMLElement | null>(null)

interface GoogleCredentialResponse {
  credential: string
  select_by: string
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void
          renderButton: (el: HTMLElement, config: Record<string, unknown>) => void
        }
      }
    }
  }
}

function handleCredentialResponse(response: GoogleCredentialResponse): void {
  if (response.credential) {
    emit('success', response.credential)
  } else {
    emit('error', 'Google sign-in failed')
  }
}

function renderGoogleButton(): void {
  if (!window.google || !buttonContainer.value) return

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleCredentialResponse,
    ux_mode: 'popup',
  })

  // Render Google's own button visibly — GSI's origin check requires the
  // iframe to be in a visible, sized element. Any hidden/off-screen hack
  // gets 403'd.
  window.google.accounts.id.renderButton(buttonContainer.value, {
    type: 'standard',
    theme: 'outline',
    size: 'large',
    text: 'signin_with',
    shape: 'rectangular',
    logo_alignment: 'left',
    width: buttonContainer.value.clientWidth || 320,
  })
}

onMounted(() => {
  if (!clientId) return

  // If the GSI script has already been loaded by another mount, reuse it.
  if (window.google?.accounts?.id) {
    renderGoogleButton()
    return
  }

  const existing = document.querySelector<HTMLScriptElement>(
    'script[src="https://accounts.google.com/gsi/client"]',
  )
  if (existing) {
    existing.addEventListener('load', renderGoogleButton, { once: true })
    return
  }

  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.defer = true
  script.onload = renderGoogleButton
  document.head.appendChild(script)
})
</script>

<template>
  <div v-if="clientId" class="mb-4 flex w-full justify-center">
    <div ref="buttonContainer" class="w-full"></div>
  </div>
</template>
