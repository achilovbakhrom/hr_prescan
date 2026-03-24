<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AutoComplete from 'primevue/autocomplete'
import { fetchIndustries, type Industry } from '@/shared/services/industry.service'
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{
    modelValue: string[]
    invalid?: boolean
  }>(),
  {
    invalid: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const { t } = useI18n()

const industries = ref<Industry[]>([])
const filteredIndustries = ref<Industry[]>([])
const selectedIndustries = ref<Industry[]>([])

onMounted(async () => {
  industries.value = await fetchIndustries()
  if (props.modelValue.length) {
    selectedIndustries.value = industries.value.filter((i) =>
      props.modelValue.includes(i.slug),
    )
  }
})

watch(
  () => props.modelValue,
  (slugs) => {
    if (!slugs.length) {
      selectedIndustries.value = []
      return
    }
    selectedIndustries.value = industries.value.filter((i) =>
      slugs.includes(i.slug),
    )
  },
)

function search(event: { query: string }): void {
  const query = event.query.toLowerCase()
  filteredIndustries.value = industries.value.filter(
    (i) =>
      i.name.toLowerCase().includes(query) &&
      !selectedIndustries.value.some((s) => s.slug === i.slug),
  )
}

function onChange(value: Industry[]): void {
  selectedIndustries.value = value
  emit(
    'update:modelValue',
    value.map((i) => i.slug),
  )
}
</script>

<template>
  <AutoComplete
    :modelValue="selectedIndustries"
    :suggestions="filteredIndustries"
    optionLabel="name"
    :placeholder="t('auth.chooseRole.industry')"
    :invalid="invalid"
    multiple
    @complete="search"
    @update:modelValue="onChange"
    forceSelection
    dropdown
  />
</template>
