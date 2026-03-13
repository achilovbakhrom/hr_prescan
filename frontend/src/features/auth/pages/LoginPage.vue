<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const authStore = useAuthStore()

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
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Login failed. Please try again.'
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
      <h1 class="mb-6 text-center text-2xl font-bold text-gray-900">
        Sign In
      </h1>

      <Message v-if="errorMessage" severity="error" class="mb-4">
        {{ errorMessage }}
      </Message>

      <form class="flex flex-col gap-4" @submit.prevent="handleLogin">
        <div class="flex flex-col gap-1">
          <label for="email" class="text-sm font-medium text-gray-700">
            Email
          </label>
          <InputText
            id="email"
            v-model="email"
            type="email"
            placeholder="Enter your email"
            :invalid="submitted && emailInvalid"
            class="w-full"
          />
          <small v-if="submitted && emailInvalid" class="text-red-500">
            Please enter a valid email address.
          </small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="password" class="text-sm font-medium text-gray-700">
            Password
          </label>
          <Password
            v-model="password"
            input-id="password"
            placeholder="Enter your password"
            :feedback="false"
            toggle-mask
            :invalid="submitted && passwordInvalid"
            class="w-full"
            input-class="w-full"
          />
          <small v-if="submitted && passwordInvalid" class="text-red-500">
            Password is required.
          </small>
        </div>

        <Button
          type="submit"
          label="Sign In"
          :loading="authStore.loading"
          class="mt-2 w-full"
        />
      </form>

      <p class="mt-4 text-center text-sm text-gray-600">
        Don't have an account?
        <RouterLink
          :to="{ name: ROUTE_NAMES.REGISTER }"
          class="font-medium text-blue-600 hover:text-blue-500"
        >
          Register
        </RouterLink>
      </p>
    </div>
  </div>
</template>
