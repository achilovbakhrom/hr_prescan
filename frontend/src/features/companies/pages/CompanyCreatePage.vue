<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
import CountryAutocomplete from '@/shared/components/CountryAutocomplete.vue'
import IndustryAutocomplete from '@/shared/components/IndustryAutocomplete.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import CompanyLogoPicker from '../components/CompanyLogoPicker.vue'
import { useCompanyStore } from '../stores/company.store'
import type { Company } from '../types/company.types'

const { t } = useI18n()
const router = useRouter()
const companyStore = useCompanyStore()

const name = ref('')
const industries = ref<string[]>([])
const country = ref('')
const website = ref('')
const description = ref('')
const size = ref<Company['size']>('small')
const saving = ref(false)
const submitted = ref(false)

const pendingLogo = ref<File | null>(null)
const pendingLogoUrl = ref<string | null>(null)
const logoError = ref<string | null>(null)

function onLogoPick(file: File): void {
  logoError.value = null
  if (pendingLogoUrl.value) URL.revokeObjectURL(pendingLogoUrl.value)
  pendingLogo.value = file
  pendingLogoUrl.value = URL.createObjectURL(file)
}

function onLogoReject(reason: string): void {
  logoError.value = reason
}

onBeforeUnmount(() => {
  if (pendingLogoUrl.value) URL.revokeObjectURL(pendingLogoUrl.value)
})

const previewName = computed(() => name.value || t('companies.namePlaceholder'))

const sizeOptions: { label: string; value: Company['size'] }[] = [
  { label: t('companies.sizeSmall'), value: 'small' },
  { label: t('companies.sizeMedium'), value: 'medium' },
  { label: t('companies.sizeLarge'), value: 'large' },
  { label: t('companies.sizeEnterprise'), value: 'enterprise' },
]

const errors = ref({ name: false, country: false, industries: false })

function validate(): boolean {
  errors.value.name = !name.value.trim()
  errors.value.country = !country.value.trim()
  errors.value.industries = industries.value.length === 0
  return !Object.values(errors.value).some(Boolean)
}

async function handleSave(): Promise<void> {
  submitted.value = true
  if (!validate()) return
  saving.value = true
  try {
    const company = await companyStore.createCompany({
      name: name.value,
      size: size.value,
      country: country.value,
      industries: industries.value,
      website: website.value || undefined,
      description: description.value || undefined,
    })
    if (pendingLogo.value) {
      try {
        await companyStore.uploadCompanyLogo(company.id, pendingLogo.value)
      } catch {
        // Company already created — don't block navigation on a logo failure.
        // Store surfaces the error; user can retry from the detail page.
      }
    }
    router.push({ name: ROUTE_NAMES.COMPANY_DETAIL, params: { id: company.id } })
  } catch {
    // store surfaces error
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-6">
    <button
      class="mb-4 flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 transition-colors hover:text-gray-900"
      @click="router.push({ name: ROUTE_NAMES.COMPANY_LIST })"
    >
      <i class="pi pi-arrow-left text-xs"></i>
      {{ t('common.back') }}
    </button>

    <h1 class="mb-6 text-2xl font-bold text-gray-900">{{ t('companies.create') }}</h1>

    <div class="mb-6 flex items-center gap-3">
      <CompanyLogoPicker
        :logo="pendingLogoUrl"
        :name="previewName"
        :uploading="false"
        @pick="onLogoPick"
        @reject="onLogoReject"
      />
      <div class="min-w-0">
        <p class="text-sm font-medium text-gray-900">{{ t('companies.logo') }}</p>
        <p class="text-xs text-gray-500">{{ t('companies.logoHint') }}</p>
      </div>
    </div>

    <p v-if="logoError" class="mb-3 text-sm text-red-600">{{ logoError }}</p>

    <div
      v-if="companyStore.error"
      class="mb-4 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 p-3 text-sm text-red-600"
    >
      {{ companyStore.error }}
    </div>

    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium">
        {{ t('companies.name') }} <span class="text-red-500">*</span>
      </label>
      <InputText
        v-model="name"
        class="w-full"
        :placeholder="t('companies.namePlaceholder')"
        :invalid="submitted && errors.name"
      />
    </div>

    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium">
        {{ t('companies.country') }} <span class="text-red-500">*</span>
      </label>
      <CountryAutocomplete v-model="country" :invalid="submitted && errors.country" />
    </div>

    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium">{{ t('companies.size') }}</label>
      <Select
        v-model="size"
        :options="sizeOptions"
        option-label="label"
        option-value="value"
        class="w-full"
      />
    </div>

    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium">
        {{ t('companies.industry') }} <span class="text-red-500">*</span>
      </label>
      <IndustryAutocomplete v-model="industries" :invalid="submitted && errors.industries" />
    </div>

    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium">{{ t('companies.website') }}</label>
      <InputText v-model="website" class="w-full" placeholder="https://..." />
    </div>

    <div class="mb-6">
      <label class="mb-1 block text-sm font-medium">{{ t('companies.description') }}</label>
      <Textarea v-model="description" class="w-full" rows="6" />
    </div>

    <div class="flex justify-end">
      <Button
        :label="t('common.save')"
        icon="pi pi-check"
        :loading="saving"
        @click="handleSave"
      />
    </div>
  </div>
</template>
