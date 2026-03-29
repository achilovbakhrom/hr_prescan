<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Message from 'primevue/message'
import CountryAutocomplete from '@/shared/components/CountryAutocomplete.vue'
import IndustryAutocomplete from '@/shared/components/IndustryAutocomplete.vue'
import type { CompanySize } from '../types/auth.types'

const { t } = useI18n()

defineProps<{
  errorMessage: string | null
  loading: boolean
  showEmailField: boolean
}>()

const emit = defineEmits<{
  submit: [data: { companyName: string; industries: string[]; size: CompanySize; country: string; email?: string }]
  back: []
}>()

const companyName = ref('')
const industries = ref<string[]>([])
const size = ref<CompanySize | null>(null)
const country = ref('')
const email = ref('')
const submitted = ref(false)

const sizeOptions = [
  { label: '1-50 employees', value: 'small' as CompanySize },
  { label: '51-200 employees', value: 'medium' as CompanySize },
  { label: '201-1000 employees', value: 'large' as CompanySize },
  { label: '1000+ employees', value: 'enterprise' as CompanySize },
]

const errors = computed(() => ({
  companyName: !companyName.value.trim(),
  size: !size.value,
  country: !country.value.trim(),
  email: false,
}))

function handleSubmit(): void {
  submitted.value = true
  if (Object.values(errors.value).some(Boolean)) return
  emit('submit', {
    companyName: companyName.value, industries: industries.value,
    size: size.value!, country: country.value,
    ...(email.value.trim() ? { email: email.value } : {}),
  })
}
</script>

<template>
  <div>
    <h1 class="mb-6 text-center text-xl font-bold text-gray-900 sm:text-2xl">{{ t('auth.chooseRole.companyFormTitle') }}</h1>
    <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

    <form class="flex flex-col gap-4" @submit.prevent="handleSubmit">
      <div class="flex flex-col gap-1">
        <label for="companyName" class="text-sm font-medium text-gray-700">{{ t('auth.chooseRole.companyName') }}</label>
        <InputText id="companyName" v-model="companyName" :placeholder="t('auth.chooseRole.companyName')" :invalid="submitted && errors.companyName" class="w-full" />
        <small v-if="submitted && errors.companyName" class="text-red-500">{{ t('common.required_field') }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="industry" class="text-sm font-medium text-gray-700">{{ t('auth.chooseRole.industry') }}</label>
        <IndustryAutocomplete v-model="industries" />
      </div>
      <div class="flex flex-col gap-1">
        <label for="size" class="text-sm font-medium text-gray-700">{{ t('auth.chooseRole.size') }}</label>
        <Select id="size" v-model="size" :options="sizeOptions" option-label="label" option-value="value" :placeholder="t('auth.chooseRole.size')" :invalid="submitted && errors.size" class="w-full" />
        <small v-if="submitted && errors.size" class="text-red-500">{{ t('common.required_field') }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="country" class="text-sm font-medium text-gray-700">{{ t('auth.chooseRole.country') }}</label>
        <CountryAutocomplete v-model="country" :invalid="submitted && errors.country" />
        <small v-if="submitted && errors.country" class="text-red-500">{{ t('common.required_field') }}</small>
      </div>
      <div v-if="showEmailField" class="flex flex-col gap-1">
        <label for="email" class="text-sm font-medium text-gray-700">{{ t('auth.chooseRole.email') }}</label>
        <InputText id="email" v-model="email" type="email" :placeholder="t('auth.chooseRole.email')" class="w-full" />
        <small class="text-gray-500">{{ t('auth.chooseRole.emailHint') }}</small>
      </div>
      <div class="flex items-center justify-between gap-4 pt-2">
        <Button type="button" :label="t('auth.chooseRole.back')" severity="secondary" text icon="pi pi-arrow-left" @click="emit('back')" />
        <Button type="submit" :label="t('auth.chooseRole.submit')" :loading="loading" icon="pi pi-check" icon-pos="right" />
      </div>
    </form>
  </div>
</template>
