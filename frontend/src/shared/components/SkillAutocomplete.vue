<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AutoComplete from '@/shared/components/AppAutocomplete.vue'
import { fetchSkills, type Skill } from '@/shared/services/skill.service'
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

const skills = ref<Skill[]>([])
const filteredSkills = ref<Skill[]>([])
const selectedSkills = ref<Skill[]>([])

onMounted(async () => {
  skills.value = await fetchSkills()
  if (props.modelValue.length) {
    selectedSkills.value = skills.value.filter((s) => props.modelValue.includes(s.slug))
  }
})

watch(
  () => props.modelValue,
  (slugs) => {
    if (!slugs.length) {
      selectedSkills.value = []
      return
    }
    selectedSkills.value = skills.value.filter((s) => slugs.includes(s.slug))
  },
)

function search(event: { query: string }): void {
  const query = event.query.toLowerCase()
  filteredSkills.value = skills.value.filter(
    (s) =>
      s.name.toLowerCase().includes(query) &&
      !selectedSkills.value.some((sel) => sel.slug === s.slug),
  )
}

function onChange(value: Skill[]): void {
  selectedSkills.value = value
  emit(
    'update:modelValue',
    value.map((s) => s.slug),
  )
}
</script>

<template>
  <AutoComplete
    :modelValue="selectedSkills"
    :suggestions="filteredSkills"
    optionLabel="name"
    :placeholder="t('common.skills')"
    :invalid="invalid"
    multiple
    @complete="search"
    @update:modelValue="onChange"
    forceSelection
    dropdown
  />
</template>
