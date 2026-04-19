<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
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
}

async function handleCreate(): Promise<void> {
  if (!name.value || !country.value) return
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
    :style="{ width: '500px' }"
    :breakpoints="{ '640px': '95vw' }"
    @show="resetForm"
  >
    <div class="space-y-4">
      <div>
        <label class="mb-1 block text-sm font-medium"
          >{{ t('companies.name') }} <span class="text-red-500">*</span></label
        >
        <InputText v-model="name" class="w-full" :placeholder="t('companies.namePlaceholder')" />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium"
          >{{ t('companies.country') }} <span class="text-red-500">*</span></label
        >
        <InputText v-model="country" class="w-full" />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('companies.size') }}</label>
        <Select
          v-model="size"
          :options="sizeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('companies.industry') }}</label>
        <InputText v-model="customIndustry" class="w-full" />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('companies.website') }}</label>
        <InputText v-model="website" class="w-full" placeholder="https://..." />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('companies.description') }}</label>
        <Textarea v-model="description" class="w-full" rows="4" />
      </div>

      <p v-if="createError" class="text-sm text-red-500">{{ createError }}</p>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button :label="t('common.cancel')" severity="secondary" text @click="visible = false" />
        <Button
          :label="t('common.save')"
          icon="pi pi-check"
          :loading="creating"
          :disabled="!name || !country"
          @click="handleCreate"
        />
      </div>
    </template>
  </Dialog>
</template>
