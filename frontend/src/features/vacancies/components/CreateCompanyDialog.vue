<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from '@/shared/components/AppSelect.vue'
import Button from 'primevue/button'
import CountryAutocomplete from '@/shared/components/CountryAutocomplete.vue'
import { extractErrorMessage } from '@/shared/api/errors'
import { companyService } from '@/features/companies/services/company.service'
import type { Company } from '@/features/companies/types/company.types'

const emit = defineEmits<{
  created: [company: Company]
}>()

const visible = defineModel<boolean>('visible', { required: true })

const { t } = useI18n()

const name = ref('')
const customIndustry = ref('')
const country = ref('')
const website = ref('')
const description = ref('')
const size = ref<Company['size']>('small')
const creating = ref(false)
const createError = ref('')
const submitted = ref(false)

const sizeOptions = [
  { label: t('companies.sizeSmall'), value: 'small' },
  { label: t('companies.sizeMedium'), value: 'medium' },
  { label: t('companies.sizeLarge'), value: 'large' },
  { label: t('companies.sizeEnterprise'), value: 'enterprise' },
]

function resetForm(): void {
  name.value = ''
  customIndustry.value = ''
  country.value = ''
  website.value = ''
  description.value = ''
  size.value = 'small'
  createError.value = ''
  submitted.value = false
}

function validate(): boolean {
  return Boolean(name.value.trim() && country.value.trim())
}

async function handleCreate(): Promise<void> {
  submitted.value = true
  if (!validate()) return
  creating.value = true
  createError.value = ''
  try {
    const company = await companyService.create({
      name: name.value,
      size: size.value,
      country: country.value,
      customIndustry: customIndustry.value || undefined,
      website: website.value || undefined,
      description: description.value || undefined,
    })
    emit('created', company)
    visible.value = false
  } catch (err: unknown) {
    createError.value = extractErrorMessage(err)
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    :header="t('companies.create')"
    modal
    :style="{ width: '560px' }"
    :breakpoints="{ '640px': '95vw' }"
    @show="resetForm"
  >
    <div class="space-y-5">
      <div class="rounded-xl bg-[color:var(--color-accent-soft)]/70 px-4 py-3">
        <p class="text-sm font-medium text-[color:var(--color-text-primary)]">
          {{ t('companies.createHint') }}
        </p>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="sm:col-span-2">
          <label class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]">
            {{ t('companies.name') }} <span class="text-[color:var(--color-danger)]">*</span>
          </label>
          <InputText
            v-model="name"
            class="w-full"
            :placeholder="t('companies.namePlaceholder')"
            :invalid="submitted && !name.trim()"
          />
          <small v-if="submitted && !name.trim()" class="text-[color:var(--color-danger)]">
            {{ t('companies.nameRequired') }}
          </small>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]">
            {{ t('companies.country') }} <span class="text-[color:var(--color-danger)]">*</span>
          </label>
          <CountryAutocomplete v-model="country" :invalid="submitted && !country.trim()" />
          <small v-if="submitted && !country.trim()" class="text-[color:var(--color-danger)]">
            {{ t('companies.countryRequired') }}
          </small>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]">
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
          <label class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]">
            {{ t('companies.industry') }}
          </label>
          <InputText
            v-model="customIndustry"
            class="w-full"
            :placeholder="t('companies.industryPlaceholder')"
          />
        </div>

        <div class="sm:col-span-2">
          <label class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]">
            {{ t('companies.website') }}
          </label>
          <InputText
            v-model="website"
            class="w-full"
            :placeholder="t('companies.websitePlaceholder')"
          />
        </div>

        <div class="sm:col-span-2">
          <label class="mb-1.5 block text-sm font-medium text-[color:var(--color-text-secondary)]">
            {{ t('companies.description') }}
          </label>
          <Textarea
            v-model="description"
            class="w-full"
            rows="4"
            :placeholder="t('companies.descriptionPlaceholder')"
          />
        </div>
      </div>
      <p
        v-if="createError"
        class="rounded-lg border border-[color:var(--color-danger)] bg-[color:var(--color-danger)]/10 px-3 py-2 text-sm text-[color:var(--color-danger)]"
      >
        {{ createError }}
      </p>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button :label="t('common.cancel')" severity="secondary" text @click="visible = false" />
        <Button
          :label="t('common.save')"
          icon="pi pi-check"
          :loading="creating"
          :disabled="!name.trim() || !country.trim()"
          @click="handleCreate"
        />
      </div>
    </template>
  </Dialog>
</template>
