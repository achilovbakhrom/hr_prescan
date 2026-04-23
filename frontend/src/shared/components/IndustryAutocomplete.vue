<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import AutoComplete from '@/shared/components/AppAutocomplete.vue'
import { fetchIndustries, type Industry } from '@/shared/services/industry.service'
import { getTranslatedName, matchesTranslatedName } from '@/shared/composables/useTranslatedName'
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{
    modelValue: string[]
    invalid?: boolean
    size?: 'small' | 'large'
  }>(),
  {
    invalid: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  hasOther: [value: boolean]
}>()

const { t } = useI18n()

const industries = ref<Industry[]>([])
const filteredIndustries = ref<Industry[]>([])
const selectedIndustries = ref<Industry[]>([])

const hasOtherSelected = computed(() => selectedIndustries.value.some((i) => i.slug === 'other'))

onMounted(async () => {
  industries.value = await fetchIndustries()
  if (props.modelValue.length) {
    selectedIndustries.value = industries.value.filter((i) => props.modelValue.includes(i.slug))
  }
  emit('hasOther', hasOtherSelected.value)
})

watch(
  () => props.modelValue,
  (slugs) => {
    if (!slugs.length) {
      selectedIndustries.value = []
      return
    }
    selectedIndustries.value = industries.value.filter((i) => slugs.includes(i.slug))
  },
)

function translatedLabel(item: Industry): string {
  return getTranslatedName(item)
}

function search(event: { query: string }): void {
  filteredIndustries.value = industries.value.filter(
    (i) =>
      matchesTranslatedName(i, event.query) &&
      !selectedIndustries.value.some((s) => s.slug === i.slug),
  )
}

function onChange(value: Industry[]): void {
  selectedIndustries.value = value
  emit(
    'update:modelValue',
    value.map((i) => i.slug),
  )
  emit(
    'hasOther',
    value.some((i) => i.slug === 'other'),
  )
}
</script>

<template>
  <AutoComplete
    :modelValue="selectedIndustries"
    :suggestions="filteredIndustries"
    :optionLabel="translatedLabel"
    :placeholder="t('auth.chooseRole.industry')"
    :invalid="invalid"
    :size="size"
    class="w-full"
    input-class="w-full"
    multiple
    @complete="search"
    @update:modelValue="onChange"
    forceSelection
    dropdown
  />
</template>
