<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import ConfirmDialog from 'primevue/confirmdialog'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyDetailHeader from '../components/VacancyDetailHeader.vue'
import VacancyOverview from '../components/VacancyOverview.vue'
import VacancyForm from '../components/VacancyForm.vue'
import ScreeningTab from '../components/ScreeningTab.vue'
import CandidatesTab from '../components/CandidatesTab.vue'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { batchTranslateItems } from '@/shared/api/translate'
import { getLocale } from '@/shared/i18n'
import type { CreateVacancyRequest, VacancyStatus } from '../types/vacancy.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const vacancyStore = useVacancyStore()
const candidateStore = useCandidateStore()

const TAB_NAMES_BASE = ['overview', 'prescanning', 'candidates'] as const
const TAB_NAMES_WITH_INTERVIEW = ['overview', 'prescanning', 'interview', 'candidates'] as const
const tabNames = computed(() => vacancy.value?.interviewEnabled ? TAB_NAMES_WITH_INTERVIEW : TAB_NAMES_BASE)
const candidatesTabIndex = computed(() => tabNames.value.length - 1)
const activeTab = computed({
  get: () => { const idx = (tabNames.value as readonly string[]).indexOf(route.query.tab as string); return idx >= 0 ? idx : 0 },
  set: (val: number) => { router.replace({ query: { ...route.query, tab: tabNames.value[val] } }) },
})
const vacancyId = computed(() => route.params.id as string)
const vacancy = computed(() => vacancyStore.currentVacancy)

const editFormData = computed(() => {
  if (!vacancy.value) return undefined
  const v = vacancy.value
  return {
    title: v.title, description: v.description, requirements: v.requirements, responsibilities: v.responsibilities,
    skills: v.skills, salaryMin: v.salaryMin, salaryMax: v.salaryMax, salaryCurrency: v.salaryCurrency,
    location: v.location, isRemote: v.isRemote, employmentType: v.employmentType, experienceLevel: v.experienceLevel,
    deadline: v.deadline, visibility: v.visibility, interviewEnabled: v.interviewEnabled, interviewMode: v.interviewMode,
    interviewDuration: v.interviewDuration, prescanningPrompt: v.prescanningPrompt, interviewPrompt: v.interviewPrompt,
    companyInfo: v.companyInfo, cvRequired: v.cvRequired,
  }
})

const prescanningQuestions = computed(() => vacancy.value?.questions.filter((q) => q.step === 'prescanning') ?? [])
const interviewQuestions = computed(() => vacancy.value?.questions.filter((q) => q.step === 'interview') ?? [])
const prescanningCriteria = computed(() => vacancy.value?.criteria.filter((c) => c.step === 'prescanning') ?? [])
const interviewCriteria = computed(() => vacancy.value?.criteria.filter((c) => c.step === 'interview') ?? [])

onMounted(() => { vacancyStore.fetchVacancyDetail(vacancyId.value) })

async function handleStatusChange(status: VacancyStatus): Promise<void> { await vacancyStore.changeStatus(vacancyId.value, status).catch(() => {}) }
async function handleUpdate(data: CreateVacancyRequest): Promise<void> { try { await vacancyStore.updateVacancy(vacancyId.value, data) } catch { /* store handles error */ } }

async function handleBatchTranslate(itemType: 'criteria' | 'questions', step: 'prescanning' | 'interview'): Promise<void> {
  try {
    const result = await batchTranslateItems({ vacancyId: vacancyId.value, itemType, step, targetLanguage: getLocale() })
    if (vacancy.value) {
      const itemList = itemType === 'criteria' ? vacancy.value.criteria : vacancy.value.questions
      for (const translated of result.items) { const item = itemList.find((i) => i.id === translated.id); if (item) item.translations = translated.translations }
    }
  } catch { /* silent */ }
}
</script>

<template>
  <div class="space-y-3 sm:space-y-4">
    <p v-if="vacancyStore.error && Object.keys(vacancyStore.fieldErrors).length === 0" class="text-sm text-red-600">{{ vacancyStore.error }}</p>

    <div v-if="!vacancy && vacancyStore.loading" class="py-12 text-center"><i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i></div>

    <template v-else-if="vacancy">
      <VacancyDetailHeader :title="vacancy.title" :status="vacancy.status" :share-token="vacancy.shareToken" :loading="vacancyStore.loading" @status-change="handleStatusChange" />

      <TabView v-model:activeIndex="activeTab" scrollable>
        <TabPanel value="0">
          <template #header><span class="text-xs sm:text-sm">{{ t('candidates.overview') }}</span></template>
          <div class="space-y-4 py-3 sm:py-4">
            <VacancyOverview :vacancy="vacancy" />
            <hr class="border-gray-200" />
            <VacancyForm :initial-data="editFormData" :loading="vacancyStore.loading" :field-errors="vacancyStore.fieldErrors" :error-message="vacancyStore.error" @save="handleUpdate" />
          </div>
        </TabPanel>

        <TabPanel value="1">
          <template #header><span class="text-xs sm:text-sm"><i class="pi pi-comments mr-1"></i>{{ t('vacancies.form.prescanning') }}</span></template>
          <ScreeningTab :vacancy-id="vacancyId" step="prescanning" :questions="prescanningQuestions" :criteria="prescanningCriteria" :loading="vacancyStore.loading"
            @add-question="(d) => vacancyStore.addQuestion(vacancyId, d)" @update-question="(qId, d) => vacancyStore.updateQuestion(vacancyId, qId, d)"
            @delete-question="(qId) => vacancyStore.deleteQuestion(vacancyId, qId)" @generate-questions="() => vacancyStore.generateQuestions(vacancyId)"
            @add-criteria="(d) => vacancyStore.addCriteria(vacancyId, d)" @update-criteria="(cId, d) => vacancyStore.updateCriteria(vacancyId, cId, d)"
            @delete-criteria="(cId) => vacancyStore.deleteCriteria(vacancyId, cId)" @translate-questions="() => handleBatchTranslate('questions', 'prescanning')" @translate-criteria="() => handleBatchTranslate('criteria', 'prescanning')" />
        </TabPanel>

        <TabPanel v-if="vacancy.interviewEnabled" value="2">
          <template #header><span class="text-xs sm:text-sm"><i class="pi pi-video mr-1"></i>{{ t('vacancies.form.interview') }}</span></template>
          <ScreeningTab :vacancy-id="vacancyId" step="interview" :questions="interviewQuestions" :criteria="interviewCriteria" :loading="vacancyStore.loading"
            @add-question="(d) => vacancyStore.addQuestion(vacancyId, d)" @update-question="(qId, d) => vacancyStore.updateQuestion(vacancyId, qId, d)"
            @delete-question="(qId) => vacancyStore.deleteQuestion(vacancyId, qId)" @generate-questions="() => vacancyStore.generateQuestions(vacancyId)"
            @add-criteria="(d) => vacancyStore.addCriteria(vacancyId, d)" @update-criteria="(cId, d) => vacancyStore.updateCriteria(vacancyId, cId, d)"
            @delete-criteria="(cId) => vacancyStore.deleteCriteria(vacancyId, cId)" @translate-questions="() => handleBatchTranslate('questions', 'interview')" @translate-criteria="() => handleBatchTranslate('criteria', 'interview')" />
        </TabPanel>

        <TabPanel :value="String(candidatesTabIndex)">
          <template #header>
            <span class="text-xs sm:text-sm">{{ t('candidates.title') }}</span>
            <span v-if="candidateStore.candidates.length" class="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-blue-500 px-1 text-[9px] font-bold text-white sm:h-5 sm:min-w-5 sm:px-1.5 sm:text-[10px]">{{ candidateStore.candidates.length }}</span>
          </template>
          <CandidatesTab :vacancy-id="vacancyId" :interview-enabled="vacancy?.interviewEnabled ?? false" />
        </TabPanel>
      </TabView>
    </template>

    <ConfirmDialog />
  </div>
</template>
