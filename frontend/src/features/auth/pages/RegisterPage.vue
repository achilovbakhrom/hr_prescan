<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Message from 'primevue/message'
import AuthShell from '../components/AuthShell.vue'
import AuthDivider from '../components/AuthDivider.vue'
import GoogleSignInButton from '../components/GoogleSignInButton.vue'
import TelegramSignInButton from '../components/TelegramSignInButton.vue'
import RegisterFormFields from '../components/RegisterFormFields.vue'
import RegisterSuccess from '../components/RegisterSuccess.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref<string | null>(null)
const submitted = ref(false)
const registered = ref(false)

const errors = ref({
  firstName: false,
  lastName: false,
  email: false,
  password: false,
  confirmPassword: false,
})

// Google sign-in — credential kept only in memory
const googleCredential = ref<string | null>(null)

function validate(): boolean {
  errors.value.firstName = !firstName.value.trim()
  errors.value.lastName = !lastName.value.trim()
  errors.value.email = !email.value || !email.value.includes('@')
  errors.value.password = !password.value || password.value.length < 8
  errors.value.confirmPassword = password.value !== confirmPassword.value
  return !Object.values(errors.value).some(Boolean)
}

async function handleRegister(): Promise<void> {
  submitted.value = true
  errorMessage.value = null
  if (!validate()) return
  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      firstName: firstName.value,
      lastName: lastName.value,
    })
    registered.value = true
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Registration failed. Please try again.'
  }
}

async function handleGoogleSuccess(credential: string): Promise<void> {
  errorMessage.value = null
  googleCredential.value = credential
  try {
    await authStore.googleLogin(credential)
    await router.push(
      authStore.user?.onboardingCompleted === false
        ? { name: ROUTE_NAMES.CHOOSE_ROLE }
        : { name: ROUTE_NAMES.DASHBOARD },
    )
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Google sign-in failed.'
  }
}

async function handleTelegramSuccess(
  data: Parameters<typeof authStore.telegramLogin>[0],
): Promise<void> {
  errorMessage.value = null
  try {
    await authStore.telegramLogin(data)
    await router.push(
      authStore.user?.onboardingCompleted === false
        ? { name: ROUTE_NAMES.CHOOSE_ROLE }
        : { name: ROUTE_NAMES.DASHBOARD },
    )
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Telegram sign-in failed.'
  }
}
</script>

<template>
  <AuthShell :title="registered ? '' : t('auth.register.title')">
    <RegisterSuccess v-if="registered" :email="email" />

    <template v-else>
      <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

      <GoogleSignInButton
        @success="handleGoogleSuccess"
        @error="(msg: string) => (errorMessage = msg)"
      />
      <TelegramSignInButton
        @success="handleTelegramSuccess"
        @error="(msg: string) => (errorMessage = msg)"
      />

      <AuthDivider :label="t('auth.register.orRegisterWithEmail')" />

      <RegisterFormFields
        v-model:first-name="firstName"
        v-model:last-name="lastName"
        v-model:email="email"
        v-model:password="password"
        v-model:confirm-password="confirmPassword"
        :submitted="submitted"
        :errors="errors"
        :loading="authStore.loading"
        @submit="handleRegister"
      />
    </template>

    <template v-if="!registered" #footer>
      {{ t('auth.register.hasAccount') }}
      <RouterLink
        :to="{ name: ROUTE_NAMES.LOGIN }"
        class="font-medium text-[color:var(--color-accent)] hover:underline"
      >
        {{ t('auth.register.signIn') }}
      </RouterLink>
    </template>
  </AuthShell>
</template>
