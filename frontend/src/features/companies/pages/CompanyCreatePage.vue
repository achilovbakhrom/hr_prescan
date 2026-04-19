<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useCompanyStore } from '../stores/company.store'
import type { Company } from '../types/company.types'

const { t } = useI18n()
const router = useRouter()
const companyStore = useCompanyStore()

const name = ref('')
const customIndustry = ref('')
const country = ref('')
const website = ref('')
const description = ref('')
const size = ref<Company['size']>('small')
const saving = ref(false)

const sizeOptions: { label: string; value: Company['size'] }[] = [
  { label: t('companies.sizeSmall'), value: 'small' },
  { label: t('companies.sizeMedium'), value: 'medium' },
  { label: t('companies.sizeLarge'), value: 'large' },
  { label: t('companies.sizeEnterprise'), value: 'enterprise' },
]

async function handleSave(): Promise<void> {
  if (!name.value || !country.value) return
  saving.value = true
  try {
    const company = await companyStore.createCompany({
      name: name.value,
      size: size.value,
      country: country.value,
      customIndustry: customIndustry.value || undefined,
      website: website.value || undefined,
      description: description.value || undefined,
    })
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
      class="mb-4 flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-900"
      @click="router.push({ name: ROUTE_NAMES.COMPANY_LIST })"
    >
      <i class="pi pi-arrow-left text-xs"></i>
      {{ t('common.back') }}
    </button>

    <h1 class="mb-6 text-2xl font-bold text-gray-900">{{ t('companies.create') }}</h1>

    <div
      v-if="companyStore.error"
      class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600"
    >
      {{ companyStore.error }}
    </div>

    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium"
        >{{ t('companies.name') }} <span class="text-red-500">*</span></label
      >
      <InputText v-model="name" class="w-full" :placeholder="t('companies.namePlaceholder')" />
    </div>

    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium"
        >{{ t('companies.country') }} <span class="text-red-500">*</span></label
      >
      <InputText v-model="country" class="w-full" />
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
      <label class="mb-1 block text-sm font-medium">{{ t('companies.industry') }}</label>
      <InputText v-model="customIndustry" class="w-full" />
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
        :disabled="!name || !country"
        @click="handleSave"
      />
    </div>
  </div>
</template>
