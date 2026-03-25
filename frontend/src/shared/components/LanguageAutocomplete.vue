<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AutoComplete from 'primevue/autocomplete'
import { fetchLanguages, type Language } from '@/shared/services/language.service'
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

const languages = ref<Language[]>([])
const filteredLanguages = ref<Language[]>([])
const selectedLanguage = ref<Language | null>(null)

onMounted(async () => {
  languages.value = await fetchLanguages()
  if (props.modelValue) {
    selectedLanguage.value =
      languages.value.find((l) => l.code === props.modelValue) ?? null
  }
})

watch(
  () => props.modelValue,
  (code) => {
    if (!code) {
      selectedLanguage.value = null
      return
    }
    const match = languages.value.find((l) => l.code === code)
    if (match && match.code !== selectedLanguage.value?.code) {
      selectedLanguage.value = match
    }
  },
)

function search(event: { query: string }): void {
  const query = event.query.toLowerCase()
  filteredLanguages.value = languages.value.filter((l) =>
    l.name.toLowerCase().includes(query),
  )
}

function onSelect(event: { value: Language }): void {
  selectedLanguage.value = event.value
  emit('update:modelValue', event.value.code)
}

function onClear(): void {
  selectedLanguage.value = null
  emit('update:modelValue', '')
}
</script>

<template>
  <AutoComplete
    :modelValue="selectedLanguage"
    :suggestions="filteredLanguages"
    optionLabel="name"
    :placeholder="t('common.language')"
    :invalid="invalid"
    @complete="search"
    @item-select="onSelect"
    @clear="onClear"
    forceSelection
    dropdown
  />
</template>
