<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Select from '@/shared/components/AppSelect.vue'
import { PRESCANNING_LANGUAGE_OPTIONS } from '@/shared/i18n/supportedLocales'
import { useVacancyStore } from '../stores/vacancy.store'
import type { InstructionStyle, StepType, VacancyDetail } from '../types/vacancy.types'

const props = defineProps<{
  vacancy: VacancyDetail
  step: StepType
}>()

const { t } = useI18n()
const toast = useToast()
const vacancyStore = useVacancyStore()

const language = ref(props.vacancy.prescanningLanguage || 'en')
const instruction = ref(currentInstruction(props.vacancy))
const interviewDuration = ref<number>(props.vacancy.interviewDuration || 30)
const style = ref<InstructionStyle>('balanced')
const saving = ref(false)
const generating = ref(false)

const interviewLocked = computed(
  () =>
    props.vacancy.canChangeInterviewMode === false ||
    (props.vacancy.canChangeInterviewMode == null && (props.vacancy.candidatesTotal ?? 0) > 0),
)

const styleOptions = computed(() => [
  { label: t('vacancies.instructions.styleBalanced'), value: 'balanced' },
  { label: t('vacancies.instructions.styleLight'), value: 'light' },
  { label: t('vacancies.instructions.styleStrict'), value: 'strict' },
])

const dirty = computed(() => {
  if (props.step === 'prescanning') {
    return (
      language.value !== (props.vacancy.prescanningLanguage || 'en') ||
      instruction.value !== (props.vacancy.prescanningPrompt || '')
    )
  }
  return (
    instruction.value !== (props.vacancy.interviewPrompt || '') ||
    interviewDuration.value !== (props.vacancy.interviewDuration || 30)
  )
})

watch(
  () => props.vacancy,
  (vacancy) => {
    language.value = vacancy.prescanningLanguage || 'en'
    instruction.value = currentInstruction(vacancy)
    interviewDuration.value = vacancy.interviewDuration || 30
  },
  { deep: true },
)

function currentInstruction(vacancy: VacancyDetail): string {
  return props.step === 'prescanning'
    ? vacancy.prescanningPrompt || ''
    : vacancy.interviewPrompt || ''
}

async function generate(): Promise<void> {
  generating.value = true
  try {
    instruction.value = await vacancyStore.generateInstructions(
      props.vacancy.id,
      props.step,
      style.value,
    )
    toast.add({ severity: 'success', summary: t('vacancies.instructions.generated'), life: 2500 })
  } catch {
    toast.add({ severity: 'error', summary: vacancyStore.error || t('common.error'), life: 4000 })
  } finally {
    generating.value = false
  }
}

async function save(): Promise<void> {
  saving.value = true
  try {
    const payload: Record<string, unknown> =
      props.step === 'prescanning'
        ? { prescanningLanguage: language.value, prescanningPrompt: instruction.value }
        : { interviewPrompt: instruction.value, interviewDuration: interviewDuration.value ?? 30 }
    if (props.step === 'interview' && !interviewLocked.value) payload.interviewMode = 'meet'
    await vacancyStore.updateVacancy(props.vacancy.id, payload)
    toast.add({ severity: 'success', summary: t('common.saved'), life: 2500 })
  } catch {
    toast.add({ severity: 'error', summary: vacancyStore.error || t('common.error'), life: 4000 })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section
    class="rounded-xl border border-gray-100 bg-white p-5 dark:border-gray-800 dark:bg-gray-800"
  >
    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-50">
          {{ t('vacancies.instructions.title') }}
        </h3>
        <p class="mt-1 text-xs text-gray-500">{{ t('vacancies.instructions.hint') }}</p>
      </div>
      <div class="flex flex-col gap-2 sm:flex-row">
        <Select
          v-model="style"
          :options="styleOptions"
          option-label="label"
          option-value="value"
          class="w-full sm:w-36"
        />
        <Button
          :label="t('vacancies.instructions.generate')"
          icon="pi pi-sparkles"
          size="small"
          :loading="generating"
          :disabled="vacancyStore.loading"
          @click="generate"
        />
      </div>
    </div>

    <div v-if="step === 'prescanning'" class="mb-4">
      <label class="mb-1 block text-xs font-medium text-gray-600">
        {{ t('vacancies.form.prescanningLanguage') }}
      </label>
      <Select
        v-model="language"
        :options="PRESCANNING_LANGUAGE_OPTIONS"
        option-label="label"
        option-value="value"
        class="w-full sm:w-60"
      />
    </div>

    <div v-if="step === 'interview'" class="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <label class="mb-1 block text-xs font-medium text-gray-600">
          {{ t('vacancies.form.interviewMode') }}
        </label>
        <div class="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm">
          {{ t('vacancies.interviewMode.meet') }}
        </div>
      </div>
      <div>
        <label class="mb-1 block text-xs font-medium text-gray-600">
          {{ t('vacancies.form.interviewDuration') }}
        </label>
        <InputNumber v-model="interviewDuration" class="w-full" :min="10" :max="120" :step="5" />
      </div>
    </div>

    <Textarea
      v-model="instruction"
      class="w-full"
      rows="7"
      :placeholder="t('vacancies.instructions.placeholder')"
    />
    <p class="mt-2 whitespace-pre-line text-xs text-gray-500">
      {{ t('vacancies.instructions.example') }}
    </p>

    <div v-if="dirty" class="mt-4 flex justify-end">
      <Button
        :label="t('common.save')"
        icon="pi pi-check"
        size="small"
        :loading="saving"
        @click="save"
      />
    </div>
  </section>
</template>
