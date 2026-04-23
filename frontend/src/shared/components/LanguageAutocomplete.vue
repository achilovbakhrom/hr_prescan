<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import AutoComplete from '@/shared/components/AppAutocomplete.vue'
import { fetchLanguages, type Language } from '@/shared/services/language.service'
import { useI18n } from 'vue-i18n'

interface DisplayLanguage extends Language {
  displayName: string
}

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

const { t, locale } = useI18n()

const languages = ref<Language[]>([])
const filteredLanguages = ref<DisplayLanguage[]>([])
const selectedLanguage = ref<DisplayLanguage | null>(null)

function getLocalizedName(lang: Language): string {
  if (locale.value === 'ru' && lang.nameRu) return lang.nameRu
  if (locale.value === 'uz' && lang.nameUz) return lang.nameUz
  return lang.name
}

const displayLanguages = computed(() => {
  const isNonEn = locale.value !== 'en'
  return languages.value
    .map((l) => ({ ...l, displayName: getLocalizedName(l) }))
    .sort((a, b) => {
      if (isNonEn) {
        const aTranslated = a.displayName !== a.name
        const bTranslated = b.displayName !== b.name
        if (aTranslated !== bTranslated) return aTranslated ? -1 : 1
      }
      return a.displayName.localeCompare(b.displayName)
    })
})

function findDisplay(code: string): DisplayLanguage | null {
  return displayLanguages.value.find((l) => l.code === code) ?? null
}

onMounted(async () => {
  languages.value = await fetchLanguages()
  if (props.modelValue) {
    selectedLanguage.value = findDisplay(props.modelValue)
  }
})

watch(
  () => props.modelValue,
  (code) => {
    if (!code) {
      selectedLanguage.value = null
      return
    }
    if (code !== selectedLanguage.value?.code) {
      selectedLanguage.value = findDisplay(code)
    }
  },
)

function search(event: { query: string }): void {
  const query = event.query.toLowerCase()
  filteredLanguages.value = displayLanguages.value.filter(
    (l) => l.displayName.toLowerCase().includes(query) || l.name.toLowerCase().includes(query),
  )
}

function onSelect(event: { value: DisplayLanguage }): void {
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
    optionLabel="displayName"
    :placeholder="t('common.language')"
    :invalid="invalid"
    @complete="search"
    @item-select="onSelect"
    @clear="onClear"
    forceSelection
    dropdown
  />
</template>
