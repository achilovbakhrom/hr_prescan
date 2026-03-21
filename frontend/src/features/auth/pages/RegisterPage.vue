<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import GoogleSignInButton from '../components/GoogleSignInButton.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const authStore = useAuthStore()

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
      err instanceof Error
        ? err.message
        : 'Registration failed. Please try again.'
  }
}

async function handleGoogleSuccess(credential: string): Promise<void> {
  errorMessage.value = null
  try {
    await authStore.googleLogin(credential)
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Google sign-in failed.'
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
            Check Your Email
          </h1>
          <p class="mb-6 text-gray-600">
            We've sent a verification link to
            <strong>{{ email }}</strong>. Please check your inbox and click the
            link to activate your account.
          </p>
          <RouterLink
            :to="{ name: ROUTE_NAMES.LOGIN }"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Back to Login
          </RouterLink>
        </div>
      </template>

      <template v-else>
        <h1 class="mb-6 text-center text-2xl font-bold text-gray-900">
          Create Account
        </h1>

        <Message v-if="errorMessage" severity="error" class="mb-4">
          {{ errorMessage }}
        </Message>

        <GoogleSignInButton
          @success="handleGoogleSuccess"
          @error="handleGoogleError"
        />

        <div class="mb-4 flex items-center gap-3">
          <div class="h-px flex-1 bg-gray-200"></div>
          <span class="text-xs text-gray-400">or register with email</span>
          <div class="h-px flex-1 bg-gray-200"></div>
        </div>

        <form class="flex flex-col gap-4" @submit.prevent="handleRegister">
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-1">
              <label
                for="firstName"
                class="text-sm font-medium text-gray-700"
              >
                First Name
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
                Last Name
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
            <label for="email" class="text-sm font-medium text-gray-700">
              Email
            </label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              placeholder="Enter your email"
              :invalid="submitted && errors.email"
              class="w-full"
            />
            <small v-if="submitted && errors.email" class="text-red-500">
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
              placeholder="Minimum 8 characters"
              toggle-mask
              :invalid="submitted && errors.password"
              class="w-full"
              input-class="w-full"
            />
            <small v-if="submitted && errors.password" class="text-red-500">
              Password must be at least 8 characters.
            </small>
          </div>

          <div class="flex flex-col gap-1">
            <label
              for="confirmPassword"
              class="text-sm font-medium text-gray-700"
            >
              Confirm Password
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
              Passwords do not match.
            </small>
          </div>

          <Button
            type="submit"
            label="Create Account"
            :loading="authStore.loading"
            class="mt-2 w-full"
          />
        </form>

        <p class="mt-4 text-center text-sm text-gray-600">
          Already have an account?
          <RouterLink
            :to="{ name: ROUTE_NAMES.LOGIN }"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Login
          </RouterLink>
        </p>

        <p class="mt-2 text-center text-sm text-gray-600">
          Want to hire?
          <RouterLink
            :to="{ name: ROUTE_NAMES.COMPANY_REGISTER }"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Register your company
          </RouterLink>
        </p>
      </template>
    </div>
  </div>
</template>
