<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuthStore } from '../stores/auth.store'
import { apiClient } from '@/shared/api/client'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const token = ref((route.query.token as string) || '')
const firstName = ref('')
const lastName = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref<string | null>(null)
const submitted = ref(false)
const loading = ref(true)

// Invitation check state
const existingUser = ref(false)
const invitationEmail = ref('')
const companyName = ref('')
const invitationError = ref<string | null>(null)

const errors = ref({
  firstName: false,
  lastName: false,
  password: false,
  confirmPassword: false,
})

onMounted(async () => {
  if (!token.value) {
    loading.value = false
    return
  }
  try {
    const response = await apiClient.get('/auth/check-invitation', {
      params: { token: token.value },
    })
    existingUser.value = response.data.existingUser
    invitationEmail.value = response.data.email
    companyName.value = response.data.companyName

    // If user is already logged in with matching email, auto-accept
    if (authStore.isAuthenticated && authStore.user?.email === invitationEmail.value) {
      await handleAcceptAsLoggedIn()
      return
    }
  } catch (err: unknown) {
    const axErr = err as { response?: { data?: { detail?: string } } }
    invitationError.value = axErr.response?.data?.detail || 'Invalid invitation link.'
  } finally {
    loading.value = false
  }
})

function validate(): boolean {
  errors.value.firstName = !firstName.value.trim()
  errors.value.lastName = !lastName.value.trim()
  errors.value.password = !password.value || password.value.length < 8
  errors.value.confirmPassword = password.value !== confirmPassword.value
  return !Object.values(errors.value).some(Boolean)
}

async function handleSubmit(): Promise<void> {
  submitted.value = true
  errorMessage.value = null

  if (!validate()) return

  try {
    await authStore.acceptInvitation({
      token: token.value,
      password: password.value,
      firstName: firstName.value,
      lastName: lastName.value,
    })
    await router.push({
      name: ROUTE_NAMES.LOGIN,
      query: { message: 'invitation-accepted' },
    })
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error
        ? err.message
        : 'Failed to accept invitation. Please try again.'
  }
}

async function handleAcceptAsLoggedIn(): Promise<void> {
  try {
    await authStore.acceptCompanyInvitation(token.value)
    await authStore.fetchCompanies()
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error
        ? err.message
        : 'Failed to accept invitation.'
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
      <!-- Loading -->
      <div v-if="loading" class="py-8 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
      </div>

      <!-- Invalid link -->
      <template v-else-if="invitationError || !token">
        <h1 class="mb-4 text-center text-2xl font-bold text-gray-900">
          {{ t('auth.acceptInvitation.title') }}
        </h1>
        <Message severity="error">
          {{ invitationError || 'Invalid invitation link. Please check the link in your email.' }}
        </Message>
      </template>

      <!-- Existing user: prompt to login -->
      <template v-else-if="existingUser && !authStore.isAuthenticated">
        <div class="text-center">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
            <i class="pi pi-building text-2xl text-blue-600"></i>
          </div>
          <h1 class="mb-2 text-2xl font-bold text-gray-900">
            {{ t('auth.acceptInvitation.title') }}
          </h1>
          <p class="mb-6 text-sm text-gray-600">
            You've been invited to join <strong>{{ companyName }}</strong> as an HR team member.
            Please sign in to your existing account to accept.
          </p>

          <Message v-if="errorMessage" severity="error" class="mb-4">
            {{ errorMessage }}
          </Message>

          <Button
            :label="t('nav.signIn')"
            icon="pi pi-sign-in"
            class="w-full"
            @click="router.push({ name: ROUTE_NAMES.LOGIN, query: { redirect: route.fullPath } })"
          />

          <p class="mt-3 text-xs text-gray-500">
            Account: <strong>{{ invitationEmail }}</strong>
          </p>
        </div>
      </template>

      <!-- New user: registration form -->
      <template v-else-if="!existingUser">
        <h1 class="mb-2 text-center text-2xl font-bold text-gray-900">
          {{ t('auth.acceptInvitation.title') }}
        </h1>
        <p class="mb-6 text-center text-sm text-gray-600">
          Join <strong>{{ companyName }}</strong> as an HR team member.
        </p>

        <Message v-if="errorMessage" severity="error" class="mb-4">
          {{ errorMessage }}
        </Message>

        <form class="flex flex-col gap-4" @submit.prevent="handleSubmit">
          <div class="rounded-md bg-gray-50 px-3 py-2 text-sm text-gray-600">
            <i class="pi pi-envelope mr-1"></i> {{ invitationEmail }}
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-1">
              <label for="firstName" class="text-sm font-medium text-gray-700">
                {{ t('auth.acceptInvitation.firstName') }}
              </label>
              <InputText
                id="firstName"
                v-model="firstName"
                placeholder="First name"
                :invalid="submitted && errors.firstName"
                class="w-full"
              />
              <small v-if="submitted && errors.firstName" class="text-red-500">
                First name is required.
              </small>
            </div>
            <div class="flex flex-col gap-1">
              <label for="lastName" class="text-sm font-medium text-gray-700">
                {{ t('auth.acceptInvitation.lastName') }}
              </label>
              <InputText
                id="lastName"
                v-model="lastName"
                placeholder="Last name"
                :invalid="submitted && errors.lastName"
                class="w-full"
              />
              <small v-if="submitted && errors.lastName" class="text-red-500">
                Last name is required.
              </small>
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <label for="password" class="text-sm font-medium text-gray-700">
              {{ t('auth.acceptInvitation.password') }}
            </label>
            <Password
              v-model="password"
              input-id="password"
              placeholder="Minimum 8 characters"
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
              placeholder="Confirm your password"
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
            :label="t('auth.acceptInvitation.submit')"
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
      </template>
    </div>
  </div>
</template>
