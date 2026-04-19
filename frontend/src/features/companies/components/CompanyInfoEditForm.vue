<script setup lang="ts">
/**
 * CompanyInfoEditForm — inline edit form for a single company.
 * Extracted from CompanyDetailPage for size discipline.
 */
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import type { Company } from '../types/company.types'

const props = defineProps<{
  company: Company
  saving: boolean
}>()

const emit = defineEmits<{
  save: [
    payload: {
      name: string
      customIndustry: string
      website: string
      description: string
    },
  ]
  cancel: []
}>()

const { t } = useI18n()

const name = ref(props.company.name)
const customIndustry = ref(props.company.customIndustry)
const website = ref(props.company.website ?? '')
const description = ref(props.company.description ?? '')

watch(
  () => props.company,
  (c) => {
    name.value = c.name
    customIndustry.value = c.customIndustry
    website.value = c.website ?? ''
    description.value = c.description ?? ''
  },
)

function handleSubmit(): void {
  if (!name.value) return
  emit('save', {
    name: name.value,
    customIndustry: customIndustry.value,
    website: website.value,
    description: description.value,
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <div>
      <label class="mb-1 block text-sm font-medium text-[color:var(--color-text-secondary)]">
        {{ t('companies.name') }} <span class="text-[color:var(--color-danger)]">*</span>
      </label>
      <InputText v-model="name" class="w-full" />
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium text-[color:var(--color-text-secondary)]">
        {{ t('companies.industry') }}
      </label>
      <InputText v-model="customIndustry" class="w-full" />
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium text-[color:var(--color-text-secondary)]">
        {{ t('companies.website') }}
      </label>
      <InputText v-model="website" class="w-full" placeholder="https://..." />
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium text-[color:var(--color-text-secondary)]">
        {{ t('companies.description') }}
      </label>
      <Textarea v-model="description" class="w-full" rows="6" />
    </div>
    <div class="flex justify-end gap-2">
      <Button
        :label="t('common.cancel')"
        severity="secondary"
        type="button"
        @click="$emit('cancel')"
      />
      <Button
        :label="t('common.save')"
        icon="pi pi-check"
        type="submit"
        :loading="saving"
        :disabled="!name"
      />
    </div>
  </form>
</template>
