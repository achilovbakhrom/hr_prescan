<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import QuestionList from './QuestionList.vue'
import CriteriaList from './CriteriaList.vue'
import { useVacancyStore } from '../stores/vacancy.store'
import type {
  InterviewMode,
  InterviewQuestion,
  VacancyCriteria,
  VacancyDetail,
} from '../types/vacancy.types'

const props = defineProps<{
  vacancy: VacancyDetail
  step: 'prescanning' | 'interview'
  questions: InterviewQuestion[]
  criteria: VacancyCriteria[]
  loading: boolean
}>()

const emit = defineEmits<{
  addQuestion: [data: { text: string; category?: string; step?: string }]
  updateQuestion: [questionId: string, data: Partial<InterviewQuestion>]
  deleteQuestion: [questionId: string]
  generateQuestions: []
  addCriteria: [data: { name: string; description?: string; weight?: number; step?: string }]
  updateCriteria: [criteriaId: string, data: Partial<VacancyCriteria>]
  deleteCriteria: [criteriaId: string]
  translateQuestions: []
  translateCriteria: []
}>()

const { t } = useI18n()
const toast = useToast()
const vacancyStore = useVacancyStore()

const languageOptions = [
  { label: 'English', value: 'en' },
  { label: 'Русский', value: 'ru' },
  { label: `O'zbekcha`, value: 'uz' },
]

const interviewModeOptions = computed(() => [
  { label: t('vacancies.interviewMode.chat'), value: 'chat' as InterviewMode },
  { label: t('vacancies.interviewMode.meet'), value: 'meet' as InterviewMode },
])

// Local form state mirroring vacancy fields for this step
const language = ref(props.vacancy.prescanningLanguage || 'en')
const prompt = ref(
  props.step === 'prescanning'
    ? props.vacancy.prescanningPrompt || ''
    : props.vacancy.interviewPrompt || '',
)
const interviewMode = ref<InterviewMode>(props.vacancy.interviewMode || 'chat')
const interviewDuration = ref<number>(props.vacancy.interviewDuration || 30)
const saving = ref(false)

watch(
  () => props.vacancy,
  (v) => {
    language.value = v.prescanningLanguage || 'en'
    prompt.value =
      props.step === 'prescanning' ? v.prescanningPrompt || '' : v.interviewPrompt || ''
    interviewMode.value = v.interviewMode || 'chat'
    interviewDuration.value = v.interviewDuration || 30
  },
  { deep: true },
)

const dirty = computed(() => {
  if (props.step === 'prescanning') {
    return (
      language.value !== (props.vacancy.prescanningLanguage || 'en') ||
      prompt.value !== (props.vacancy.prescanningPrompt || '')
    )
  }
  return (
    prompt.value !== (props.vacancy.interviewPrompt || '') ||
    interviewMode.value !== (props.vacancy.interviewMode || 'chat') ||
    interviewDuration.value !== (props.vacancy.interviewDuration || 30)
  )
})

async function save(): Promise<void> {
  saving.value = true
  try {
    const payload: Record<string, unknown> =
      props.step === 'prescanning'
        ? { prescanningLanguage: language.value, prescanningPrompt: prompt.value }
        : {
            interviewPrompt: prompt.value,
            interviewMode: interviewMode.value,
            interviewDuration: interviewDuration.value,
          }
    await vacancyStore.updateVacancy(props.vacancy.id, payload)
    toast.add({ severity: 'success', summary: t('common.saved'), life: 2500 })
  } catch {
    toast.add({ severity: 'error', summary: t('common.error'), life: 4000 })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Block 1: Language & Instructions -->
    <section class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5">
      <h3 class="mb-1 text-sm font-semibold text-gray-900">
        {{ t('vacancies.screening.languageAndInstructions') }}
      </h3>
      <p class="mb-4 text-xs text-gray-500">{{ t('vacancies.screening.languageHint') }}</p>

      <div v-if="step === 'prescanning'" class="mb-4">
        <label class="mb-1 block text-xs font-medium text-gray-600">{{
          t('vacancies.form.prescanningLanguage')
        }}</label>
        <Dropdown
          v-model="language"
          :options="languageOptions"
          option-label="label"
          option-value="value"
          class="w-full sm:w-60"
        />
      </div>

      <div v-if="step === 'interview'" class="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-600">{{
            t('vacancies.form.interviewMode')
          }}</label>
          <Dropdown
            v-model="interviewMode"
            :options="interviewModeOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </div>
        <div v-if="interviewMode === 'meet'">
          <label class="mb-1 block text-xs font-medium text-gray-600">{{
            t('vacancies.form.interviewDuration')
          }}</label>
          <InputNumber v-model="interviewDuration" class="w-full" :min="10" :max="120" :step="5" />
        </div>
      </div>

      <div>
        <label class="mb-1 block text-xs font-medium text-gray-600"
          >{{
            step === 'prescanning'
              ? t('vacancies.form.prescanningPrompt')
              : t('vacancies.form.interviewPrompt')
          }}
          ({{ t('common.optional') }})</label
        >
        <p class="mb-2 text-xs text-gray-400">
          {{
            step === 'prescanning'
              ? t('vacancies.form.prescanningPromptHint')
              : t('vacancies.form.interviewPromptHint')
          }}
        </p>
        <Textarea
          v-model="prompt"
          class="w-full"
          rows="4"
          :placeholder="
            step === 'prescanning'
              ? t('vacancies.form.prescanningPromptPlaceholder')
              : t('vacancies.form.interviewPromptPlaceholder')
          "
        />
      </div>

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

    <!-- Block 2: Questions -->
    <section class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5">
      <QuestionList
        :questions="questions"
        :loading="loading"
        @add="(d) => emit('addQuestion', { ...d, step })"
        @update="(qId, d) => emit('updateQuestion', qId, d)"
        @delete="(qId) => emit('deleteQuestion', qId)"
        @generate="() => emit('generateQuestions')"
        @translate-all="() => emit('translateQuestions')"
      />
    </section>

    <!-- Block 3: Criteria -->
    <section class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5">
      <CriteriaList
        :criteria="criteria"
        :loading="loading"
        @add="(d) => emit('addCriteria', { ...d, step })"
        @update="(cId, d) => emit('updateCriteria', cId, d)"
        @delete="(cId) => emit('deleteCriteria', cId)"
        @translate-all="() => emit('translateCriteria')"
      />
    </section>
  </div>
</template>
