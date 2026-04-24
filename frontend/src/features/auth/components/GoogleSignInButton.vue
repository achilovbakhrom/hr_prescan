<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const emit = defineEmits<{
  success: [credential: string]
  error: [message: string]
}>()

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string
const buttonContainer = ref<HTMLElement | null>(null)
const { t } = useI18n()
const darkMode = ref(isDarkMode())
let themeObserver: MutationObserver | null = null

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

function isDarkMode(): boolean {
  return document.documentElement.classList.contains('dark')
}

function renderGoogleButton(): void {
  if (!window.google || !buttonContainer.value) return

  buttonContainer.value.replaceChildren()

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleCredentialResponse,
    ux_mode: 'popup',
  })

  // Keep Google's iframe mounted as the real click target. The visible
  // surface is custom below because the iframe's logo tile cannot be styled.
  window.google.accounts.id.renderButton(buttonContainer.value, {
    type: 'standard',
    theme: isDarkMode() ? 'filled_black' : 'outline',
    size: 'large',
    text: 'signin_with',
    shape: 'rectangular',
    logo_alignment: 'left',
    width: Math.min(400, Math.floor(buttonContainer.value.clientWidth)) || 320,
  })
}

onMounted(() => {
  if (!clientId) return

  darkMode.value = isDarkMode()
  themeObserver = new MutationObserver(() => {
    darkMode.value = isDarkMode()
    renderGoogleButton()
  })
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class'],
  })

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

onUnmounted(() => {
  themeObserver?.disconnect()
  themeObserver = null
})
</script>

<template>
  <div v-if="clientId" class="mb-3">
    <div class="social-auth-google" :class="{ 'social-auth-google--dark': darkMode }">
      <div ref="buttonContainer" class="social-auth-google__target"></div>
      <div class="social-auth-google__visual">
        <span class="social-auth-google__icon">
          <svg viewBox="0 0 18 18" aria-hidden="true" focusable="false">
            <path
              fill="#4285F4"
              d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z"
            />
            <path
              fill="#34A853"
              d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.33-1.58-5.04-3.7H.96v2.33A9 9 0 0 0 9 18z"
            />
            <path
              fill="#FBBC05"
              d="M3.96 10.72A5.41 5.41 0 0 1 3.68 9c0-.6.1-1.18.28-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.82.96 4.05l3-2.33z"
            />
            <path
              fill="#EA4335"
              d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.58C13.46.9 11.43 0 9 0A9 9 0 0 0 .96 4.95l3 2.33C4.67 5.16 6.66 3.58 9 3.58z"
            />
          </svg>
        </span>
        <span>{{ t('auth.signInWithGoogle') }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.social-auth-google {
  position: relative;
  height: 40px;
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
}

.social-auth-google__target {
  position: absolute;
  inset: 0;
  z-index: 2;
  opacity: 0.01;
}

.social-auth-google__visual {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  border: 1px solid #dadce0;
  border-radius: 4px;
  background: #ffffff;
  color: #3c4043;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1;
  box-shadow: var(--shadow-card);
  pointer-events: none;
  transition:
    background-color 160ms var(--ease-ios),
    border-color 160ms var(--ease-ios);
}

.social-auth-google__icon {
  display: inline-flex;
  width: 18px;
  height: 18px;
  align-items: center;
  justify-content: center;
  flex: 0 0 18px;
}

.social-auth-google__icon svg {
  display: block;
  width: 18px;
  height: 18px;
}

.social-auth-google:hover .social-auth-google__visual {
  background: #f8fafd;
}

.social-auth-google--dark .social-auth-google__visual {
  border-color: #3c4043;
  background: #202124;
  color: #ffffff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.28);
}

.social-auth-google--dark:hover .social-auth-google__visual {
  border-color: #4b5563;
  background: #2a2b2f;
}
</style>
