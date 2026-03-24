<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Message from 'primevue/message'
import CountryAutocomplete from '@/shared/components/CountryAutocomplete.vue'
import IndustryAutocomplete from '@/shared/components/IndustryAutocomplete.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CompanySize } from '../types/auth.types'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

type Step = 'role' | 'company-form'

const step = ref<Step>('role')
const loading = ref(false)
const errorMessage = ref<string | null>(null)
const submitted = ref(false)

// Company form fields
const companyName = ref('')
const industries = ref<string[]>([])
const size = ref<CompanySize | null>(null)
const country = ref('')
const email = ref('')

interface SizeOption {
  label: string
  value: CompanySize
}

const sizeOptions: SizeOption[] = [
  { label: '1-50 employees', value: 'small' },
  { label: '51-200 employees', value: 'medium' },
  { label: '201-1000 employees', value: 'large' },
  { label: '1000+ employees', value: 'enterprise' },
]

const isTelegramUser = computed(() => {
  return authStore.user?.email?.endsWith('@telegram.local') ?? false
})

const errors = computed(() => ({
  companyName: !companyName.value.trim(),
  size: !size.value,
  country: !country.value.trim(),
  email: isTelegramUser.value && (!email.value.trim() || !email.value.includes('@')),
}))

async function handleCandidateClick(): Promise<void> {
  loading.value = true
  errorMessage.value = null
  try {
    await authStore.completeOnboarding()
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Something went wrong. Please try again.'
  } finally {
    loading.value = false
  }
}

function handleCompanyClick(): void {
  step.value = 'company-form'
}

function handleBack(): void {
  step.value = 'role'
  errorMessage.value = null
  submitted.value = false
}

async function handleCompanySubmit(): Promise<void> {
  submitted.value = true
  errorMessage.value = null

  if (Object.values(errors.value).some(Boolean)) return

  loading.value = true
  try {
    await authStore.completeCompanySetup({
      companyName: companyName.value,
      industries: industries.value,
      size: size.value!,
      country: country.value,
      ...(isTelegramUser.value ? { email: email.value } : {}),
    })
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Something went wrong. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-md sm:p-8">
      <!-- Role selection step -->
      <template v-if="step === 'role'">
        <h1 class="mb-8 text-center text-xl font-bold text-gray-900 sm:text-2xl">
          {{ t('auth.chooseRole.title') }}
        </h1>

        <Message v-if="errorMessage" severity="error" class="mb-4">
          {{ errorMessage }}
        </Message>

        <div class="flex flex-col gap-4">
          <button
            class="flex w-full cursor-pointer items-center gap-4 rounded-lg border-2 border-gray-200 p-4 text-left transition-colors hover:border-blue-500 hover:bg-blue-50 sm:p-6"
            :disabled="loading"
            @click="handleCandidateClick"
          >
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-green-100 sm:h-14 sm:w-14">
              <i class="pi pi-user text-xl text-green-600 sm:text-2xl" />
            </div>
            <div>
              <p class="text-base font-semibold text-gray-900 sm:text-lg">
                {{ t('auth.chooseRole.candidate') }}
              </p>
              <p class="mt-1 text-sm text-gray-500">
                {{ t('auth.chooseRole.candidateDescription') }}
              </p>
            </div>
          </button>

          <button
            class="flex w-full cursor-pointer items-center gap-4 rounded-lg border-2 border-gray-200 p-4 text-left transition-colors hover:border-blue-500 hover:bg-blue-50 sm:p-6"
            :disabled="loading"
            @click="handleCompanyClick"
          >
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-100 sm:h-14 sm:w-14">
              <i class="pi pi-building text-xl text-blue-600 sm:text-2xl" />
            </div>
            <div>
              <p class="text-base font-semibold text-gray-900 sm:text-lg">
                {{ t('auth.chooseRole.company') }}
              </p>
              <p class="mt-1 text-sm text-gray-500">
                {{ t('auth.chooseRole.companyDescription') }}
              </p>
            </div>
          </button>
        </div>
      </template>

      <!-- Company form step -->
      <template v-else>
        <h1 class="mb-6 text-center text-xl font-bold text-gray-900 sm:text-2xl">
          {{ t('auth.chooseRole.companyFormTitle') }}
        </h1>

        <Message v-if="errorMessage" severity="error" class="mb-4">
          {{ errorMessage }}
        </Message>

        <form class="flex flex-col gap-4" @submit.prevent="handleCompanySubmit">
          <div class="flex flex-col gap-1">
            <label for="companyName" class="text-sm font-medium text-gray-700">
              {{ t('auth.chooseRole.companyName') }}
            </label>
            <InputText
              id="companyName"
              v-model="companyName"
              :placeholder="t('auth.chooseRole.companyName')"
              :invalid="submitted && errors.companyName"
              class="w-full"
            />
            <small v-if="submitted && errors.companyName" class="text-red-500">
              {{ t('common.required_field') }}
            </small>
          </div>

          <div class="flex flex-col gap-1">
            <label for="industry" class="text-sm font-medium text-gray-700">
              {{ t('auth.chooseRole.industry') }}
            </label>
            <IndustryAutocomplete v-model="industries" />
          </div>

          <div class="flex flex-col gap-1">
            <label for="size" class="text-sm font-medium text-gray-700">
              {{ t('auth.chooseRole.size') }}
            </label>
            <Select
              id="size"
              v-model="size"
              :options="sizeOptions"
              option-label="label"
              option-value="value"
              :placeholder="t('auth.chooseRole.size')"
              :invalid="submitted && errors.size"
              class="w-full"
            />
            <small v-if="submitted && errors.size" class="text-red-500">
              {{ t('common.required_field') }}
            </small>
          </div>

          <div class="flex flex-col gap-1">
            <label for="country" class="text-sm font-medium text-gray-700">
              {{ t('auth.chooseRole.country') }}
            </label>
            <CountryAutocomplete
              v-model="country"
              :invalid="submitted && errors.country"
            />
            <small v-if="submitted && errors.country" class="text-red-500">
              {{ t('common.required_field') }}
            </small>
          </div>

          <div v-if="isTelegramUser" class="flex flex-col gap-1">
            <label for="email" class="text-sm font-medium text-gray-700">
              {{ t('auth.chooseRole.email') }}
            </label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              :placeholder="t('auth.chooseRole.email')"
              :invalid="submitted && errors.email"
              class="w-full"
            />
            <small class="text-gray-500">
              {{ t('auth.chooseRole.emailHint') }}
            </small>
            <small v-if="submitted && errors.email" class="text-red-500">
              {{ t('common.required_field') }}
            </small>
          </div>

          <div class="flex items-center justify-between gap-4 pt-2">
            <Button
              type="button"
              :label="t('auth.chooseRole.back')"
              severity="secondary"
              text
              icon="pi pi-arrow-left"
              @click="handleBack"
            />
            <Button
              type="submit"
              :label="t('auth.chooseRole.submit')"
              :loading="loading"
              icon="pi pi-check"
              icon-pos="right"
            />
          </div>
        </form>
      </template>
    </div>
  </div>
</template>
