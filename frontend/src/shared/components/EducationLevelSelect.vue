<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Select from 'primevue/select'
import { fetchEducationLevels, type EducationLevel } from '@/shared/services/education-level.service'
import { useI18n } from 'vue-i18n'

withDefaults(
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

const educationLevels = ref<EducationLevel[]>([])

onMounted(async () => {
  educationLevels.value = await fetchEducationLevels()
})

function onChange(value: string): void {
  emit('update:modelValue', value)
}
</script>

<template>
  <Select
    :modelValue="modelValue"
    :options="educationLevels"
    optionLabel="name"
    optionValue="slug"
    :placeholder="t('common.educationLevel')"
    :invalid="invalid"
    @update:modelValue="onChange"
    class="w-full"
  />
</template>
