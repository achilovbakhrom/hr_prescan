<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import AuthShell from '../components/AuthShell.vue'
import AuthDivider from '../components/AuthDivider.vue'
import GoogleSignInButton from '../components/GoogleSignInButton.vue'
import TelegramSignInButton from '../components/TelegramSignInButton.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const errorMessage = ref<string | null>(null)
const submitted = ref(false)

const emailInvalid = ref(false)
const passwordInvalid = ref(false)

function validate(): boolean {
  emailInvalid.value = !email.value || !email.value.includes('@')
  passwordInvalid.value = !password.value
  return !emailInvalid.value && !passwordInvalid.value
}

async function handleLogin(): Promise<void> {
  submitted.value = true
  errorMessage.value = null

  if (!validate()) return

  try {
    await authStore.login({
      email: email.value,
      password: password.value,
    })
    const redirect = router.currentRoute.value.query.redirect as string
    await router.push(redirect || { name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('auth.login.loginFailed')
  }
}

async function handleGoogleSuccess(credential: string): Promise<void> {
  errorMessage.value = null
  try {
    await authStore.googleLogin(credential)
    if (authStore.user?.onboardingCompleted === false) {
      await router.push({ name: ROUTE_NAMES.CHOOSE_ROLE })
    } else {
      const redirect = router.currentRoute.value.query.redirect as string
      await router.push(redirect || { name: ROUTE_NAMES.DASHBOARD })
    }
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('auth.login.googleFailed')
  }
}

function handleGoogleError(msg: string): void {
  errorMessage.value = msg
}

async function handleTelegramSuccess(
  data: Parameters<typeof authStore.telegramLogin>[0],
): Promise<void> {
  errorMessage.value = null
  try {
    await authStore.telegramLogin(data)
    if (authStore.user?.onboardingCompleted === false) {
      await router.push({ name: ROUTE_NAMES.CHOOSE_ROLE })
    } else {
      const redirect = router.currentRoute.value.query.redirect as string
      await router.push(redirect || { name: ROUTE_NAMES.DASHBOARD })
    }
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Telegram sign-in failed.'
  }
}

function handleTelegramError(msg: string): void {
  errorMessage.value = msg
}
</script>

<template>
  <AuthShell :title="t('auth.login.title')">
    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <GoogleSignInButton @success="handleGoogleSuccess" @error="handleGoogleError" />
    <TelegramSignInButton @success="handleTelegramSuccess" @error="handleTelegramError" />

    <AuthDivider :label="t('auth.login.orSignInWithEmail')" />

    <form class="flex flex-col gap-4" @submit.prevent="handleLogin">
      <div class="flex flex-col gap-1.5">
        <label
          for="email"
          class="text-xs font-medium uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('auth.login.email') }}
        </label>
        <InputText
          id="email"
          v-model="email"
          type="email"
          :placeholder="t('auth.login.emailPlaceholder')"
          :invalid="submitted && emailInvalid"
          class="w-full"
        />
        <small v-if="submitted && emailInvalid" class="text-[color:var(--color-danger)]">
          {{ t('auth.login.emailInvalid') }}
        </small>
      </div>

      <div class="flex flex-col gap-1.5">
        <label
          for="password"
          class="text-xs font-medium uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('auth.login.password') }}
        </label>
        <Password
          v-model="password"
          input-id="password"
          :placeholder="t('auth.login.passwordPlaceholder')"
          :feedback="false"
          toggle-mask
          :invalid="submitted && passwordInvalid"
          class="w-full"
          input-class="w-full"
        />
        <small v-if="submitted && passwordInvalid" class="text-[color:var(--color-danger)]">
          {{ t('auth.login.passwordRequired') }}
        </small>
      </div>

      <Button
        type="submit"
        :label="t('auth.login.submit')"
        :loading="authStore.loading"
        class="auth-primary-button mt-2 w-full"
      />
    </form>

    <template #footer>
      {{ t('auth.login.noAccount') }}
      <RouterLink
        :to="{ name: ROUTE_NAMES.REGISTER }"
        class="font-medium text-[color:var(--color-accent)] hover:underline"
      >
        {{ t('auth.login.register') }}
      </RouterLink>
    </template>
  </AuthShell>
</template>

<style scoped>
:global(html.dark) .auth-primary-button {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28) !important;
}

:global(html.dark) .auth-primary-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
  border-color: #60a5fa !important;
}
</style>
