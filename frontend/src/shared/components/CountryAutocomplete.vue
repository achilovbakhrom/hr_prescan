<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AutoComplete from 'primevue/autocomplete'
import { fetchCountries, type Country } from '@/shared/services/country.service'
import { getTranslatedName, matchesTranslatedName } from '@/shared/composables/useTranslatedName'
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{
    modelValue: string
    invalid?: boolean
  }>(),
  {
    invalid: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const { t } = useI18n()

const countries = ref<Country[]>([])
const filteredCountries = ref<Country[]>([])
const selectedCountry = ref<Country | null>(null)

onMounted(async () => {
  countries.value = await fetchCountries()
  if (props.modelValue) {
    selectedCountry.value = countries.value.find((c) => c.code === props.modelValue) ?? null
  }
})

watch(
  () => props.modelValue,
  (code) => {
    if (!code) {
      selectedCountry.value = null
      return
    }
    const match = countries.value.find((c) => c.code === code)
    if (match && match.code !== selectedCountry.value?.code) {
      selectedCountry.value = match
    }
  },
)

function translatedLabel(item: Country): string {
  return getTranslatedName(item)
}

function search(event: { query: string }): void {
  filteredCountries.value = countries.value.filter((c) => matchesTranslatedName(c, event.query))
}

function onSelect(event: { value: Country }): void {
  selectedCountry.value = event.value
  emit('update:modelValue', event.value.code)
}

function onClear(): void {
  selectedCountry.value = null
  emit('update:modelValue', '')
}
</script>

<template>
  <AutoComplete
    :modelValue="selectedCountry"
    :suggestions="filteredCountries"
    :optionLabel="translatedLabel"
    :placeholder="t('auth.chooseRole.country')"
    :invalid="invalid"
    @complete="search"
    @item-select="onSelect"
    @clear="onClear"
    forceSelection
    dropdown
  />
</template>
