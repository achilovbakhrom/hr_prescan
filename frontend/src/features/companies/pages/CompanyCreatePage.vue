<script setup lang="ts">
/**
 * CompanyCreatePage — centered GlassCard form.
 * Spec: docs/design/spec.md §9 Companies block.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from '@/shared/components/AppSelect.vue'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import CountryAutocomplete from '@/shared/components/CountryAutocomplete.vue'
import IndustryAutocomplete from '@/shared/components/IndustryAutocomplete.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
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
    router.push({ name: ROUTE_NAMES.COMPANY_DETAIL, params: { id: company.id } })
  } catch {
    /* store surfaces error */
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-4">
    <button
      class="flex items-center gap-1.5 text-sm text-[color:var(--color-text-muted)] transition-colors hover:text-[color:var(--color-text-primary)]"
      @click="router.push({ name: ROUTE_NAMES.COMPANY_LIST })"
    >
      <i class="pi pi-arrow-left text-xs"></i>
      {{ t('common.back') }}
    </button>

    <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
      {{ t('companies.create') }}
    </h1>

    <p
      v-if="companyStore.error"
      class="rounded-lg border border-[color:var(--color-danger)] bg-[color:var(--color-danger)]/10 p-3 text-sm text-[color:var(--color-danger)]"
    >
      {{ companyStore.error }}
    </p>

    <GlassCard>
      <form class="space-y-5" @submit.prevent="handleSave">
        <div class="rounded-xl bg-[color:var(--color-accent-soft)]/70 px-4 py-3">
          <p class="text-sm font-medium text-[color:var(--color-text-primary)]">
            {{ t('companies.createHint') }}
          </p>
        </div>

        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div class="sm:col-span-2">
            <label
              class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]"
            >
              {{ t('companies.name') }} <span class="text-[color:var(--color-danger)]">*</span>
            </label>
            <InputText
              v-model="name"
              class="w-full"
              :placeholder="t('companies.namePlaceholder')"
              :invalid="submitted && errors.name"
            />
            <small v-if="submitted && errors.name" class="text-[color:var(--color-danger)]">
              {{ t('companies.nameRequired') }}
            </small>
          </div>

          <div>
            <label
              class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]"
            >
              {{ t('companies.country') }} <span class="text-[color:var(--color-danger)]">*</span>
            </label>
            <CountryAutocomplete v-model="country" :invalid="submitted && errors.country" />
            <small v-if="submitted && errors.country" class="text-[color:var(--color-danger)]">
              {{ t('companies.countryRequired') }}
            </small>
          </div>

          <div>
            <label
              class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]"
            >
              {{ t('companies.size') }}
            </label>
            <Select
              v-model="size"
              :options="sizeOptions"
              option-label="label"
              option-value="value"
              :placeholder="t('companies.sizePlaceholder')"
              class="w-full"
            />
          </div>

          <div class="sm:col-span-2">
            <label
              class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]"
            >
              {{ t('companies.industry') }} <span class="text-[color:var(--color-danger)]">*</span>
            </label>
            <IndustryAutocomplete v-model="industries" :invalid="submitted && errors.industries" />
            <small v-if="submitted && errors.industries" class="text-[color:var(--color-danger)]">
              {{ t('companies.industryRequired') }}
            </small>
          </div>

          <div class="sm:col-span-2">
            <label
              class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]"
            >
              {{ t('companies.website') }}
            </label>
            <InputText
              v-model="website"
              class="w-full"
              :placeholder="t('companies.websitePlaceholder')"
            />
          </div>

          <div class="sm:col-span-2">
            <label
              class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]"
            >
              {{ t('companies.description') }}
            </label>
            <Textarea
              v-model="description"
              class="w-full"
              rows="6"
              :placeholder="t('companies.descriptionPlaceholder')"
            />
          </div>
        </div>

        <div class="flex justify-end pt-2">
          <Button :label="t('common.save')" icon="pi pi-check" :loading="saving" type="submit" />
        </div>
      </form>
    </GlassCard>
  </div>
</template>
