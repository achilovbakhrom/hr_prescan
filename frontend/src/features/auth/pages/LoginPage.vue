<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import GoogleSignInButton from '../components/GoogleSignInButton.vue'
import TelegramSignInButton from '../components/TelegramSignInButton.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { GoogleAuthRole } from '../types/auth.types'
import {
  isGoogleNeedsCompanyResponse,
  isGoogleNeedsRoleResponse,
  isGoogleTokensResponse,
} from '../types/auth.types'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const errorMessage = ref<string | null>(null)
const submitted = ref(false)

const emailInvalid = ref(false)
const passwordInvalid = ref(false)

// Google sign-in — credential kept only in memory
const googleCredential = ref<string | null>(null)
const rolePickerVisible = ref(false)
const rolePickerLoading = ref(false)

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
  googleCredential.value = credential
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

async function handleRolePick(role: GoogleAuthRole): Promise<void> {
  if (!googleCredential.value) return
  rolePickerLoading.value = true
  errorMessage.value = null
  try {
    const response = await authStore.googleLogin(googleCredential.value, role)
    if (isGoogleTokensResponse(response)) {
      rolePickerVisible.value = false
      const redirect = router.currentRoute.value.query.redirect as string
      await router.push(redirect || { name: ROUTE_NAMES.DASHBOARD })
      return
    }
    if (isGoogleNeedsCompanyResponse(response)) {
      rolePickerVisible.value = false
      await router.push({ name: ROUTE_NAMES.COMPANY_REGISTER })
    }
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('auth.login.googleFailed')
  } finally {
    rolePickerLoading.value = false
  }
}

function handleGoogleError(msg: string): void {
  errorMessage.value = msg
}

async function handleTelegramSuccess(data: Parameters<typeof authStore.telegramLogin>[0]): Promise<void> {
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
    errorMessage.value =
      err instanceof Error ? err.message : 'Telegram sign-in failed.'
  }
}

function handleTelegramError(msg: string): void {
  errorMessage.value = msg
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
      <h1 class="mb-6 text-center text-2xl font-bold text-gray-900">
        {{ t('auth.login.title') }}
      </h1>

      <Message v-if="errorMessage" severity="error" class="mb-4">
        {{ errorMessage }}
      </Message>

      <GoogleSignInButton @success="handleGoogleSuccess" @error="handleGoogleError" />

      <RolePickerDialog
        v-model:visible="rolePickerVisible"
        :loading="rolePickerLoading"
        @pick="handleRolePick"
      />

      <TelegramSignInButton
        @success="handleTelegramSuccess"
        @error="handleTelegramError"
      />

      <div class="mb-4 flex items-center gap-3">
        <div class="h-px flex-1 bg-gray-200"></div>
        <span class="text-xs text-gray-400">{{ t('auth.login.orSignInWithEmail') }}</span>
        <div class="h-px flex-1 bg-gray-200"></div>
      </div>

      <form class="flex flex-col gap-4" @submit.prevent="handleLogin">
        <div class="flex flex-col gap-1">
          <label for="email" class="text-sm font-medium text-gray-700">
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
          <small v-if="submitted && emailInvalid" class="text-red-500">
            {{ t('auth.login.emailInvalid') }}
          </small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="password" class="text-sm font-medium text-gray-700">
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
          <small v-if="submitted && passwordInvalid" class="text-red-500">
            {{ t('auth.login.passwordRequired') }}
          </small>
        </div>

        <Button
          type="submit"
          :label="t('auth.login.submit')"
          :loading="authStore.loading"
          class="mt-2 w-full"
        />
      </form>

      <p class="mt-4 text-center text-sm text-gray-600">
        {{ t('auth.login.noAccount') }}
        <RouterLink
          :to="{ name: ROUTE_NAMES.REGISTER }"
          class="font-medium text-blue-600 hover:text-blue-500"
        >
          {{ t('auth.login.register') }}
        </RouterLink>
      </p>

    </div>
  </div>
</template>
