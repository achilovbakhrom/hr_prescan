<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import AutoComplete, {
  type AutoCompleteCompleteEvent,
  type AutoCompleteOptionSelectEvent,
} from 'primevue/autocomplete'
import Button from 'primevue/button'
import type { CompanySize } from '../types/auth.types'
import { COUNTRIES, countryDisplayName, type Country } from '@/shared/constants/countries'

interface SizeOption {
  label: string
  value: CompanySize
}

const props = defineProps<{
  companyName: string
  industry: string
  size: CompanySize | null
  country: string
  submitted: boolean
  errors: {
    companyName: boolean
    industry: boolean
    size: boolean
    country: boolean
  }
  sizeOptions: SizeOption[]
}>()

const emit = defineEmits<{
  'update:companyName': [value: string]
  'update:industry': [value: string]
  'update:size': [value: CompanySize | null]
  'update:country': [value: string]
  next: []
}>()

const { t, locale } = useI18n()

// Localized country labels for the autocomplete list.
const countryLabels = computed(() =>
  COUNTRIES.map((c) => ({ country: c, label: countryDisplayName(c, locale.value) })),
)

// The AutoComplete's internal value — can be a raw string (free typing)
// or a label object (after selection). We keep the parent `country` prop
// as the plain display name string via `update:country`.
const countryInput = ref<string | { country: Country; label: string }>(props.country)
const countrySuggestions = ref<{ country: Country; label: string }[]>([])

// Sync external prop changes into the local input (e.g. parent resets).
watch(
  () => props.country,
  (newValue) => {
    const current =
      typeof countryInput.value === 'string' ? countryInput.value : countryInput.value.label
    if (current !== newValue) {
      countryInput.value = newValue
    }
  },
)

function searchCountries(event: AutoCompleteCompleteEvent): void {
  const query = event.query.trim().toLowerCase()
  if (!query) {
    countrySuggestions.value = countryLabels.value.slice()
    return
  }
  countrySuggestions.value = countryLabels.value.filter(
    (item) =>
      item.label.toLowerCase().includes(query) ||
      item.country.name.toLowerCase().includes(query) ||
      item.country.code.toLowerCase() === query,
  )
}

function onCountrySelect(event: AutoCompleteOptionSelectEvent): void {
  const selected = event.value as { country: Country; label: string }
  emit('update:country', selected.label)
}

function onCountryInput(value: unknown): void {
  // User typed freely — accept raw string and bubble up.
  if (typeof value === 'string') {
    emit('update:country', value)
  } else if (value && typeof value === 'object' && 'label' in value) {
    emit('update:country', (value as { label: string }).label)
  }
}
</script>

<template>
  <form class="flex flex-col gap-4 pt-4" @submit.prevent="emit('next')">
    <div class="flex flex-col gap-1">
      <label for="companyName" class="text-sm font-medium text-gray-700">
        {{ t('auth.companyRegister.companyName') }}
      </label>
      <InputText
        id="companyName"
        :model-value="companyName"
        :placeholder="t('auth.companyRegister.companyNamePlaceholder')"
        :invalid="submitted && errors.companyName"
        class="w-full"
        @update:model-value="emit('update:companyName', $event as string)"
      />
      <small v-if="submitted && errors.companyName" class="text-red-500">
        {{ t('auth.companyRegister.companyNameRequired') }}
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="industry" class="text-sm font-medium text-gray-700">
        {{ t('auth.companyRegister.industry') }}
      </label>
      <InputText
        id="industry"
        :model-value="industry"
        :placeholder="t('auth.companyRegister.industryPlaceholder')"
        :invalid="submitted && errors.industry"
        class="w-full"
        @update:model-value="emit('update:industry', $event as string)"
      />
      <small v-if="submitted && errors.industry" class="text-red-500">
        {{ t('auth.companyRegister.industryRequired') }}
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="size" class="text-sm font-medium text-gray-700">
        {{ t('auth.companyRegister.size') }}
      </label>
      <Select
        id="size"
        :model-value="size"
        :options="sizeOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('auth.companyRegister.sizePlaceholder')"
        :invalid="submitted && errors.size"
        class="w-full"
        @update:model-value="emit('update:size', $event as CompanySize)"
      />
      <small v-if="submitted && errors.size" class="text-red-500">
        {{ t('auth.companyRegister.sizeRequired') }}
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="country" class="text-sm font-medium text-gray-700">
        {{ t('auth.companyRegister.country') }}
      </label>
      <AutoComplete
        id="country"
        v-model="countryInput"
        :suggestions="countrySuggestions"
        option-label="label"
        :placeholder="t('auth.companyRegister.countryPlaceholder')"
        :invalid="submitted && errors.country"
        complete-on-focus
        class="w-full"
        input-class="w-full"
        @complete="searchCountries"
        @option-select="onCountrySelect"
        @update:model-value="onCountryInput"
      />
      <small v-if="submitted && errors.country" class="text-red-500">
        {{ t('auth.companyRegister.countryRequired') }}
      </small>
    </div>

    <div class="flex justify-end pt-2">
      <Button
        type="submit"
        :label="t('auth.companyRegister.next')"
        icon="pi pi-arrow-right"
        icon-pos="right"
      />
    </div>
  </form>
</template>
