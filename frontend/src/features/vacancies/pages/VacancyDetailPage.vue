<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import ConfirmDialog from 'primevue/confirmdialog'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyDetailHeader from '../components/VacancyDetailHeader.vue'
import VacancyDetailLayout from '../components/VacancyDetailLayout.vue'
import VacancyDetailsForm from '../components/VacancyDetailsForm.vue'
import VacancyScreeningSection from '../components/VacancyScreeningSection.vue'
import VacancySettingsSection from '../components/VacancySettingsSection.vue'
import CandidatesTab from '../components/CandidatesTab.vue'
import { batchTranslateItems } from '@/shared/api/translate'
import { getLocale } from '@/shared/i18n'
import type { VacancyStatus } from '../types/vacancy.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()
const vacancyStore = useVacancyStore()

const vacancyId = computed(() => route.params.id as string)
const vacancy = computed(() => vacancyStore.currentVacancy)

const VALID_SECTIONS = ['details', 'prescanning', 'interview', 'candidates', 'settings'] as const
type SectionKey = (typeof VALID_SECTIONS)[number]

function defaultSection(): SectionKey {
  const v = vacancy.value
  if (!v) return 'details'
  if (v.status === 'draft') return 'prescanning'
  if ((v.candidatesTotal ?? 0) > 0) return 'candidates'
  return 'details'
}

const activeSection = computed<SectionKey>({
  get: () => {
    const q = route.query.section as string | undefined
    if (q && (VALID_SECTIONS as readonly string[]).includes(q)) return q as SectionKey
    return defaultSection()
  },
  set: (val) => {
    router.replace({ query: { ...route.query, section: val } })
  },
})

function navigateSection(key: string): void {
  if ((VALID_SECTIONS as readonly string[]).includes(key)) activeSection.value = key as SectionKey
}

const prescanningQuestions = computed(
  () => vacancy.value?.questions.filter((q) => q.step === 'prescanning') ?? [],
)
const interviewQuestions = computed(
  () => vacancy.value?.questions.filter((q) => q.step === 'interview') ?? [],
)
const prescanningCriteria = computed(
  () => vacancy.value?.criteria.filter((c) => c.step === 'prescanning') ?? [],
)
const interviewCriteria = computed(
  () => vacancy.value?.criteria.filter((c) => c.step === 'interview') ?? [],
)

const candidatesTotal = computed(() => vacancy.value?.candidatesTotal ?? 0)
const candidatesShortlisted = computed(() => vacancy.value?.candidatesShortlisted ?? 0)

onMounted(() => {
  vacancyStore.fetchVacancyDetail(vacancyId.value)
})

async function handleStatusChange(status: VacancyStatus): Promise<void> {
  try {
    await vacancyStore.changeStatus(vacancyId.value, status)
    const messageKey =
      status === 'published'
        ? 'vacancies.toast.published'
        : status === 'paused'
          ? 'vacancies.toast.paused'
          : status === 'archived'
            ? 'vacancies.toast.archived'
            : 'common.saved'
    toast.add({ severity: 'success', summary: t(messageKey), life: 2500 })
  } catch {
    toast.add({ severity: 'error', summary: vacancyStore.error || t('common.error'), life: 4500 })
  }
}

async function handleBatchTranslate(
  itemType: 'criteria' | 'questions',
  step: 'prescanning' | 'interview',
): Promise<void> {
  try {
    const result = await batchTranslateItems({
      vacancyId: vacancyId.value,
      itemType,
      step,
      targetLanguage: getLocale(),
    })
    if (vacancy.value) {
      const itemList = itemType === 'criteria' ? vacancy.value.criteria : vacancy.value.questions
      for (const translated of result.items) {
        const item = itemList.find((i) => i.id === translated.id)
        if (item) item.translations = translated.translations
      }
    }
  } catch {
    /* silent */
  }
}
</script>

<template>
  <div class="space-y-4 sm:space-y-5">
    <p
      v-if="vacancyStore.error && Object.keys(vacancyStore.fieldErrors).length === 0"
      class="text-sm text-red-600"
    >
      {{ vacancyStore.error }}
    </p>

    <div v-if="!vacancy && vacancyStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="vacancy">
      <!-- Persistent header (always visible regardless of section) -->
      <VacancyDetailHeader
        :title="vacancy.title"
        :status="vacancy.status"
        :share-token="vacancy.shareToken"
        :telegram-code="vacancy.telegramCode"
        :company-name="vacancy.companyName"
        :loading="vacancyStore.loading"
        @status-change="handleStatusChange"
      />

      <!-- Rail layout -->
      <VacancyDetailLayout
        :vacancy="vacancy"
        :active="activeSection"
        :candidates-total="candidatesTotal"
        :candidates-shortlisted="candidatesShortlisted"
        @navigate="navigateSection"
      >
        <div v-if="activeSection === 'details'" class="py-1">
          <VacancyDetailsForm :vacancy="vacancy" />
        </div>

        <div v-else-if="activeSection === 'prescanning'" class="py-1">
          <VacancyScreeningSection
            :vacancy="vacancy"
            step="prescanning"
            :questions="prescanningQuestions"
            :criteria="prescanningCriteria"
            :loading="vacancyStore.loading"
            @add-question="(d) => vacancyStore.addQuestion(vacancyId, d)"
            @update-question="(qId, d) => vacancyStore.updateQuestion(vacancyId, qId, d)"
            @delete-question="(qId) => vacancyStore.deleteQuestion(vacancyId, qId)"
            @generate-questions="() => vacancyStore.generateQuestions(vacancyId)"
            @add-criteria="(d) => vacancyStore.addCriteria(vacancyId, d)"
            @update-criteria="(cId, d) => vacancyStore.updateCriteria(vacancyId, cId, d)"
            @delete-criteria="(cId) => vacancyStore.deleteCriteria(vacancyId, cId)"
            @translate-questions="() => handleBatchTranslate('questions', 'prescanning')"
            @translate-criteria="() => handleBatchTranslate('criteria', 'prescanning')"
          />
        </div>

        <div v-else-if="activeSection === 'interview' && vacancy.interviewEnabled" class="py-1">
          <VacancyScreeningSection
            :vacancy="vacancy"
            step="interview"
            :questions="interviewQuestions"
            :criteria="interviewCriteria"
            :loading="vacancyStore.loading"
            @add-question="(d) => vacancyStore.addQuestion(vacancyId, d)"
            @update-question="(qId, d) => vacancyStore.updateQuestion(vacancyId, qId, d)"
            @delete-question="(qId) => vacancyStore.deleteQuestion(vacancyId, qId)"
            @generate-questions="() => vacancyStore.generateQuestions(vacancyId)"
            @add-criteria="(d) => vacancyStore.addCriteria(vacancyId, d)"
            @update-criteria="(cId, d) => vacancyStore.updateCriteria(vacancyId, cId, d)"
            @delete-criteria="(cId) => vacancyStore.deleteCriteria(vacancyId, cId)"
            @translate-questions="() => handleBatchTranslate('questions', 'interview')"
            @translate-criteria="() => handleBatchTranslate('criteria', 'interview')"
          />
        </div>

        <div v-else-if="activeSection === 'candidates'" class="py-1">
          <CandidatesTab :vacancy-id="vacancyId" :interview-enabled="vacancy.interviewEnabled" />
        </div>

        <div v-else-if="activeSection === 'settings'" class="py-1">
          <VacancySettingsSection :vacancy="vacancy" />
        </div>
      </VacancyDetailLayout>
    </template>

    <ConfirmDialog />
  </div>
</template>
