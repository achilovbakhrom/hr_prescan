<script setup lang="ts">
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Select from 'primevue/select'
import Message from 'primevue/message'
import Stepper from 'primevue/stepper'
import StepList from 'primevue/steplist'
import StepPanels from 'primevue/steppanels'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import CompanyInfoStep from '../components/CompanyInfoStep.vue'
import AdminAccountStep from '../components/AdminAccountStep.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CompanySize } from '../types/auth.types'

const authStore = useAuthStore()

const companyName = ref('')
const industry = ref('')
const size = ref<CompanySize | null>(null)
const country = ref('')
const adminFirstName = ref('')
const adminLastName = ref('')
const adminEmail = ref('')
const adminPassword = ref('')
const confirmPassword = ref('')
const errorMessage = ref<string | null>(null)
const registered = ref(false)
const activeStep = ref<string>('1')

const sizeOptions = [
  { label: '1-50 employees', value: 'small' as CompanySize },
  { label: '51-200 employees', value: 'medium' as CompanySize },
  { label: '201-1000 employees', value: 'large' as CompanySize },
  { label: '1000+ employees', value: 'enterprise' as CompanySize },
]

const companyStepSubmitted = ref(false)
const adminStepSubmitted = ref(false)

const companyErrors = ref({
  companyName: false,
  industry: false,
  size: false,
  country: false,
})

const adminErrors = ref({
  firstName: false,
  lastName: false,
  email: false,
  password: false,
  confirmPassword: false,
})

function validateCompanyStep(): boolean {
  companyStepSubmitted.value = true
  companyErrors.value.companyName = !companyName.value.trim()
  companyErrors.value.industry = !industry.value.trim()
  companyErrors.value.size = !size.value
  companyErrors.value.country = !country.value.trim()
  return !Object.values(companyErrors.value).some(Boolean)
}

function validateAdminStep(): boolean {
  adminStepSubmitted.value = true
  adminErrors.value.firstName = !adminFirstName.value.trim()
  adminErrors.value.lastName = !adminLastName.value.trim()
  adminErrors.value.email =
    !adminEmail.value || !adminEmail.value.includes('@')
  adminErrors.value.password =
    !adminPassword.value || adminPassword.value.length < 8
  adminErrors.value.confirmPassword =
    adminPassword.value !== confirmPassword.value
  return !Object.values(adminErrors.value).some(Boolean)
}

function goToAdminStep(): void {
  if (!validateCompanyStep()) return
  activeStep.value = '2'
}

async function handleSubmit(): Promise<void> {
  if (!validateAdminStep()) return
  errorMessage.value = null

  try {
    await authStore.registerCompany({
      companyName: companyName.value,
      industry: industry.value,
      size: size.value!,
      country: country.value,
      adminEmail: adminEmail.value,
      adminPassword: adminPassword.value,
      adminFirstName: adminFirstName.value,
      adminLastName: adminLastName.value,
    })
    registered.value = true
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error
        ? err.message
        : 'Registration failed. Please try again.'
  }
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-2xl rounded-lg bg-white p-8 shadow-md">
      <template v-if="registered">
        <div class="text-center">
          <h1 class="mb-4 text-2xl font-bold text-gray-900">
            Check Your Email
          </h1>
          <p class="mb-6 text-gray-600">
            We've sent a verification link to
            <strong>{{ adminEmail }}</strong
            >. Please check your inbox and click the link to activate your
            account.
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
          Register Your Company
        </h1>

        <Message v-if="errorMessage" severity="error" class="mb-4">
          {{ errorMessage }}
        </Message>

        <Stepper v-model:value="activeStep" linear>
          <StepList>
            <Step value="1">Company Info</Step>
            <Step value="2">Admin Account</Step>
          </StepList>
          <StepPanels>
            <StepPanel value="1">
              <CompanyInfoStep
                v-model:company-name="companyName"
                v-model:industry="industry"
                v-model:size="size"
                v-model:country="country"
                :submitted="companyStepSubmitted"
                :errors="companyErrors"
                :size-options="sizeOptions"
                @next="goToAdminStep"
              />
            </StepPanel>
            <StepPanel value="2">
              <AdminAccountStep
                v-model:first-name="adminFirstName"
                v-model:last-name="adminLastName"
                v-model:email="adminEmail"
                v-model:password="adminPassword"
                v-model:confirm-password="confirmPassword"
                :submitted="adminStepSubmitted"
                :errors="adminErrors"
                :loading="authStore.loading"
                @back="activeStep = '1'"
                @submit="handleSubmit"
              />
            </StepPanel>
          </StepPanels>
        </Stepper>

        <p class="mt-4 text-center text-sm text-gray-600">
          Already have an account?
          <RouterLink
            :to="{ name: ROUTE_NAMES.LOGIN }"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Login
          </RouterLink>
        </p>
      </template>
    </div>
  </div>
</template>
