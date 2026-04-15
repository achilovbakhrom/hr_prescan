<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Message from 'primevue/message'
import CountryAutocomplete from '@/shared/components/CountryAutocomplete.vue'
import IndustryAutocomplete from '@/shared/components/IndustryAutocomplete.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CompanySize } from '@/shared/types/auth.types'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const companyName = ref('')
const industries = ref<string[]>([])
const size = ref<CompanySize | null>(null)
const country = ref('')
const email = ref('')

const loading = ref(false)
const submitted = ref(false)
const errorMessage = ref<string | null>(null)

const requiresEmail = computed(() => {
  const userEmail = authStore.user?.email ?? ''
  return userEmail.endsWith('@telegram.local')
})

const errors = ref({
  companyName: false,
  industries: false,
  size: false,
  country: false,
  email: false,
})

const sizeOptions = computed(() => [
  { label: t('auth.companySetup.sizeSmall'), value: 'small' as CompanySize },
  { label: t('auth.companySetup.sizeMedium'), value: 'medium' as CompanySize },
  { label: t('auth.companySetup.sizeLarge'), value: 'large' as CompanySize },
  { label: t('auth.companySetup.sizeEnterprise'), value: 'enterprise' as CompanySize },
])

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(): boolean {
  errors.value.companyName = !companyName.value.trim()
  errors.value.industries = industries.value.length === 0
  errors.value.size = !size.value
  errors.value.country = !country.value.trim()
  errors.value.email = requiresEmail.value && !emailRegex.test(email.value.trim())
  return !Object.values(errors.value).some(Boolean)
}

async function handleSubmit(): Promise<void> {
  submitted.value = true
  errorMessage.value = null
  if (!validate()) return

  loading.value = true
  try {
    const payload: {
      company_name: string
      industries: string[]
      size: string
      country: string
      email?: string
    } = {
      company_name: companyName.value.trim(),
      industries: industries.value,
      size: size.value as string,
      country: country.value,
    }
    if (requiresEmail.value) {
      payload.email = email.value.trim()
    }
    await authStore.completeCompanySetup(payload)
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('auth.companySetup.submitError')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-md sm:p-8">
      <h1 class="mb-2 text-center text-xl font-bold text-gray-900 sm:text-2xl">
        {{ t('auth.companySetup.title') }}
      </h1>
      <p class="mb-6 text-center text-sm text-gray-500">
        {{ t('auth.companySetup.subtitle') }}
      </p>

      <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

      <form class="flex flex-col gap-5" @submit.prevent="handleSubmit">
        <div class="flex flex-col gap-1">
          <label for="company-name" class="text-sm font-medium text-gray-700">
            {{ t('auth.companySetup.companyName') }}
          </label>
          <InputText
            id="company-name"
            v-model="companyName"
            :placeholder="t('auth.companySetup.companyNamePlaceholder')"
            :invalid="submitted && errors.companyName"
            class="w-full"
          />
          <small v-if="submitted && errors.companyName" class="text-red-500">
            {{ t('auth.companySetup.companyNameRequired') }}
          </small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="industries" class="text-sm font-medium text-gray-700">
            {{ t('auth.companySetup.industries') }}
          </label>
          <IndustryAutocomplete v-model="industries" :invalid="submitted && errors.industries" />
          <small v-if="submitted && errors.industries" class="text-red-500">
            {{ t('auth.companySetup.industriesRequired') }}
          </small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="size" class="text-sm font-medium text-gray-700">
            {{ t('auth.companySetup.size') }}
          </label>
          <Select
            id="size"
            v-model="size"
            :options="sizeOptions"
            option-label="label"
            option-value="value"
            :placeholder="t('auth.companySetup.sizePlaceholder')"
            :invalid="submitted && errors.size"
            class="w-full"
          />
          <small v-if="submitted && errors.size" class="text-red-500">
            {{ t('auth.companySetup.sizeRequired') }}
          </small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="country" class="text-sm font-medium text-gray-700">
            {{ t('auth.companySetup.country') }}
          </label>
          <CountryAutocomplete v-model="country" :invalid="submitted && errors.country" />
          <small v-if="submitted && errors.country" class="text-red-500">
            {{ t('auth.companySetup.countryRequired') }}
          </small>
        </div>

        <div v-if="requiresEmail" class="flex flex-col gap-1">
          <label for="email" class="text-sm font-medium text-gray-700">
            {{ t('auth.companySetup.email') }}
          </label>
          <InputText
            id="email"
            v-model="email"
            type="email"
            :placeholder="t('auth.companySetup.emailPlaceholder')"
            :invalid="submitted && errors.email"
            class="w-full"
          />
          <small v-if="submitted && errors.email" class="text-red-500">
            {{ t('auth.companySetup.emailRequired') }}
          </small>
        </div>

        <div class="pt-2">
          <Button
            type="submit"
            :label="t('auth.companySetup.submit')"
            :loading="loading"
            class="w-full"
          />
        </div>
      </form>
    </div>
  </div>
</template>
