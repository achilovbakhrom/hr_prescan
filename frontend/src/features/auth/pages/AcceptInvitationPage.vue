<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuthStore } from '../stores/auth.store'
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

const errors = ref({
  firstName: false,
  lastName: false,
  password: false,
  confirmPassword: false,
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

  if (!token.value) {
    errorMessage.value = 'Invalid invitation link. No token provided.'
    return
  }

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
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
      <h1 class="mb-6 text-center text-2xl font-bold text-gray-900">
        {{ t('auth.acceptInvitation.title') }}
      </h1>

      <Message v-if="!token" severity="error" class="mb-4">
        Invalid invitation link. Please check the link in your email.
      </Message>

      <Message v-if="errorMessage" severity="error" class="mb-4">
        {{ errorMessage }}
      </Message>

      <form
        v-if="token"
        class="flex flex-col gap-4"
        @submit.prevent="handleSubmit"
      >
        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <label
              for="firstName"
              class="text-sm font-medium text-gray-700"
            >
              {{ t('auth.acceptInvitation.firstName') }}
            </label>
            <InputText
              id="firstName"
              v-model="firstName"
              placeholder="First name"
              :invalid="submitted && errors.firstName"
              class="w-full"
            />
            <small
              v-if="submitted && errors.firstName"
              class="text-red-500"
            >
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
          <label
            for="confirmPassword"
            class="text-sm font-medium text-gray-700"
          >
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
          <small
            v-if="submitted && errors.confirmPassword"
            class="text-red-500"
          >
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
    </div>
  </div>
</template>
