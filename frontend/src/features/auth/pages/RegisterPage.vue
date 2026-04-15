<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import GoogleSignInButton from '../components/GoogleSignInButton.vue'
import RolePickerDialog from '../components/RolePickerDialog.vue'
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
const rolePickerVisible = ref(false)
const rolePickerLoading = ref(false)

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
    errorMessage.value = err instanceof Error ? err.message : t('auth.register.registrationFailed')
  }
}

async function handleGoogleSuccess(credential: string): Promise<void> {
  errorMessage.value = null
  googleCredential.value = credential
  try {
    const response = await authStore.googleLogin(credential)
    if (isGoogleTokensResponse(response)) {
      await router.push({ name: ROUTE_NAMES.DASHBOARD })
      return
    }
    if (isGoogleNeedsRoleResponse(response)) {
      rolePickerVisible.value = true
      return
    }
    if (isGoogleNeedsCompanyResponse(response)) {
      await router.push({ name: ROUTE_NAMES.COMPANY_REGISTER })
    }
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('auth.register.googleFailed')
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
      await router.push({ name: ROUTE_NAMES.DASHBOARD })
      return
    }
    if (isGoogleNeedsCompanyResponse(response)) {
      rolePickerVisible.value = false
      await router.push({ name: ROUTE_NAMES.COMPANY_REGISTER })
    }
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('auth.register.googleFailed')
  } finally {
    rolePickerLoading.value = false
  }
}

function handleGoogleError(msg: string): void {
  errorMessage.value = msg
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
      <template v-if="registered">
        <div class="text-center">
          <h1 class="mb-4 text-2xl font-bold text-gray-900">
            {{ t('auth.register.checkEmail') }}
          </h1>
          <p class="mb-6 text-gray-600">
            {{ t('auth.register.verificationSent') }}
            <strong>{{ email }}</strong
            >{{ t('auth.register.verificationSentSuffix') }}
          </p>
          <RouterLink
            :to="{ name: ROUTE_NAMES.LOGIN }"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            {{ t('auth.register.backToLogin') }}
          </RouterLink>
        </div>
      </template>

      <template v-else>
        <h1 class="mb-6 text-center text-2xl font-bold text-gray-900">
          {{ t('auth.register.title') }}
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

        <div class="mb-4 flex items-center gap-3">
          <div class="h-px flex-1 bg-gray-200"></div>
          <span class="text-xs text-gray-400">{{ t('auth.register.orRegisterWithEmail') }}</span>
          <div class="h-px flex-1 bg-gray-200"></div>
        </div>

        <form class="flex flex-col gap-4" @submit.prevent="handleRegister">
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-1">
              <label for="firstName" class="text-sm font-medium text-gray-700">
                {{ t('auth.register.firstName') }}
              </label>
              <InputText
                id="firstName"
                v-model="firstName"
                :placeholder="t('auth.register.firstNamePlaceholder')"
                :invalid="submitted && errors.firstName"
                class="w-full"
              />
              <small v-if="submitted && errors.firstName" class="text-red-500">
                {{ t('auth.register.firstNameRequired') }}
              </small>
            </div>

            <div class="flex flex-col gap-1">
              <label for="lastName" class="text-sm font-medium text-gray-700">
                {{ t('auth.register.lastName') }}
              </label>
              <InputText
                id="lastName"
                v-model="lastName"
                :placeholder="t('auth.register.lastNamePlaceholder')"
                :invalid="submitted && errors.lastName"
                class="w-full"
              />
              <small v-if="submitted && errors.lastName" class="text-red-500">
                {{ t('auth.register.lastNameRequired') }}
              </small>
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <label for="email" class="text-sm font-medium text-gray-700">
              {{ t('auth.register.email') }}
            </label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              :placeholder="t('auth.register.emailPlaceholder')"
              :invalid="submitted && errors.email"
              class="w-full"
            />
            <small v-if="submitted && errors.email" class="text-red-500">
              {{ t('auth.register.invalidEmail') }}
            </small>
          </div>

          <div class="flex flex-col gap-1">
            <label for="password" class="text-sm font-medium text-gray-700">
              {{ t('auth.register.password') }}
            </label>
            <Password
              v-model="password"
              input-id="password"
              :placeholder="t('auth.register.passwordPlaceholder')"
              toggle-mask
              :invalid="submitted && errors.password"
              class="w-full"
              input-class="w-full"
            />
            <small v-if="submitted && errors.password" class="text-red-500">
              {{ t('auth.register.passwordTooShort') }}
            </small>
          </div>

          <div class="flex flex-col gap-1">
            <label for="confirmPassword" class="text-sm font-medium text-gray-700">
              {{ t('auth.register.confirmPassword') }}
            </label>
            <Password
              v-model="confirmPassword"
              input-id="confirmPassword"
              :placeholder="t('auth.register.confirmPasswordPlaceholder')"
              :feedback="false"
              toggle-mask
              :invalid="submitted && errors.confirmPassword"
              class="w-full"
              input-class="w-full"
            />
            <small v-if="submitted && errors.confirmPassword" class="text-red-500">
              {{ t('auth.register.passwordMismatch') }}
            </small>
          </div>

          <Button
            type="submit"
            :label="t('auth.register.submit')"
            :loading="authStore.loading"
            class="mt-2 w-full"
          />
        </form>

        <p class="mt-4 text-center text-sm text-gray-600">
          {{ t('auth.register.hasAccount') }}
          <RouterLink
            :to="{ name: ROUTE_NAMES.LOGIN }"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            {{ t('auth.register.signIn') }}
          </RouterLink>
        </p>

        <p class="mt-2 text-center text-sm text-gray-600">
          {{ t('auth.register.wantToHire') }}
          <RouterLink
            :to="{ name: ROUTE_NAMES.COMPANY_REGISTER }"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            {{ t('auth.register.registerCompany') }}
          </RouterLink>
        </p>
      </template>
    </div>
  </div>
</template>
