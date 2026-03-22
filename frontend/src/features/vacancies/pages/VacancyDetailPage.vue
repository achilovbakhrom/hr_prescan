<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyStatusBadge from '../components/VacancyStatusBadge.vue'
import VacancyOverview from '../components/VacancyOverview.vue'
import VacancyForm from '../components/VacancyForm.vue'
import ScreeningTab from '../components/ScreeningTab.vue'
import CandidatesTab from '../components/CandidatesTab.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import type { CreateVacancyRequest, VacancyStatus } from '../types/vacancy.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const vacancyStore = useVacancyStore()
const candidateStore = useCandidateStore()
const TAB_NAMES_BASE = ['overview', 'prescanning', 'candidates'] as const
const TAB_NAMES_WITH_INTERVIEW = ['overview', 'prescanning', 'interview', 'candidates'] as const
const tabNames = computed(() =>
  vacancy.value?.interviewEnabled ? TAB_NAMES_WITH_INTERVIEW : TAB_NAMES_BASE,
)
const candidatesTabIndex = computed(() => tabNames.value.length - 1)
const activeTab = computed({
  get: () => {
    const tab = route.query.tab as string
    const idx = (tabNames.value as readonly string[]).indexOf(tab)
    return idx >= 0 ? idx : 0
  },
  set: (val: number) => {
    router.replace({ query: { ...route.query, tab: tabNames.value[val] } })
  },
})
const vacancyId = computed(() => route.params.id as string)
const vacancy = computed(() => vacancyStore.currentVacancy)

const editFormData = computed(() => {
  if (!vacancy.value) return undefined
  const v = vacancy.value
  return {
    title: v.title,
    description: v.description,
    requirements: v.requirements,
    responsibilities: v.responsibilities,
    skills: v.skills,
    salaryMin: v.salaryMin,
    salaryMax: v.salaryMax,
    salaryCurrency: v.salaryCurrency,
    location: v.location,
    isRemote: v.isRemote,
    employmentType: v.employmentType,
    experienceLevel: v.experienceLevel,
    deadline: v.deadline,
    visibility: v.visibility,
    interviewEnabled: v.interviewEnabled,
    interviewMode: v.interviewMode,
    interviewDuration: v.interviewDuration,
    prescanningPrompt: v.prescanningPrompt,
    interviewPrompt: v.interviewPrompt,
    companyInfo: v.companyInfo,
    cvRequired: v.cvRequired,
  }
})

const prescanningQuestions = computed(() =>
  vacancy.value?.questions.filter((q) => q.step === 'prescanning') ?? [],
)
const interviewQuestions = computed(() =>
  vacancy.value?.questions.filter((q) => q.step === 'interview') ?? [],
)
const prescanningCriteria = computed(() =>
  vacancy.value?.criteria.filter((c) => c.step === 'prescanning') ?? [],
)
const interviewCriteria = computed(() =>
  vacancy.value?.criteria.filter((c) => c.step === 'interview') ?? [],
)

onMounted(() => {
  vacancyStore.fetchVacancyDetail(vacancyId.value)
})

const linkCopied = ref(false)

function copyShareLink(): void {
  if (!vacancy.value) return
  const url = `${window.location.origin}/jobs/share/${vacancy.value.shareToken}`
  navigator.clipboard.writeText(url).then(() => {
    linkCopied.value = true
    setTimeout(() => { linkCopied.value = false }, 2000)
  })
}

async function handleStatusChange(status: VacancyStatus): Promise<void> {
  await vacancyStore.changeStatus(vacancyId.value, status).catch(() => {})
}

async function handleUpdate(data: CreateVacancyRequest): Promise<void> {
  try {
    await vacancyStore.updateVacancy(vacancyId.value, data)
  } catch {
    /* store handles error */
  }
}
</script>

<template>
  <div class="space-y-3 sm:space-y-4">
    <!-- Header -->
    <div class="flex items-center gap-2 sm:gap-3">
      <button
        class="shrink-0 rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
        @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
      >
        <i class="pi pi-arrow-left"></i>
      </button>
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <h1 class="truncate text-base font-bold sm:text-lg md:text-2xl">
            {{ vacancy?.title ?? t('common.loading') }}
          </h1>
          <VacancyStatusBadge v-if="vacancy" :status="vacancy.status" />
        </div>
      </div>
    </div>

    <p v-if="vacancyStore.error" class="text-sm text-red-600">
      {{ vacancyStore.error }}
    </p>

    <div v-if="!vacancy && vacancyStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="vacancy">
      <!-- Action buttons: draft -> published <-> paused -> archived -->
      <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
        <Button
          v-if="vacancy.status === 'draft'"
          :label="t('vacancies.actions.publish')"
          icon="pi pi-send"
          size="small"
          @click="handleStatusChange('published')"
        />
        <Button
          v-if="vacancy.status === 'published'"
          :label="t('vacancies.actions.pause')"
          icon="pi pi-pause"
          severity="warn"
          size="small"
          @click="handleStatusChange('paused')"
        />
        <Button
          v-if="vacancy.status === 'paused'"
          :label="t('vacancies.actions.resume')"
          icon="pi pi-play"
          severity="success"
          size="small"
          @click="handleStatusChange('published')"
        />
        <Button
          v-if="vacancy.status === 'published' || vacancy.status === 'paused'"
          :label="t('vacancies.actions.archive')"
          icon="pi pi-inbox"
          severity="secondary"
          size="small"
          outlined
          @click="handleStatusChange('archived')"
        />
        <Button
          :label="linkCopied ? t('common.copied') : t('common.copyLink')"
          :icon="linkCopied ? 'pi pi-check' : 'pi pi-link'"
          :severity="linkCopied ? 'success' : 'secondary'"
          size="small"
          outlined
          @click="copyShareLink"
        />
      </div>

      <!-- Tabs -->
      <TabView v-model:activeIndex="activeTab" scrollable>
        <TabPanel value="0">
          <template #header>
            <span class="text-xs sm:text-sm">{{ t('candidates.overview') }}</span>
          </template>
          <div class="space-y-4 py-3 sm:py-4">
            <VacancyOverview :vacancy="vacancy" />
            <hr class="border-gray-200" />
            <VacancyForm
              :initial-data="editFormData"
              :loading="vacancyStore.loading"
              @save="handleUpdate"
            />
          </div>
        </TabPanel>

        <!-- Prescanning tab -->
        <TabPanel value="1">
          <template #header>
            <span class="text-xs sm:text-sm"><i class="pi pi-comments mr-1"></i>{{ t('vacancies.form.prescanning') }}</span>
          </template>
          <ScreeningTab
            :vacancy-id="vacancyId"
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
          />
        </TabPanel>

        <!-- Interview tab (only when enabled) -->
        <TabPanel v-if="vacancy.interviewEnabled" value="2">
          <template #header>
            <span class="text-xs sm:text-sm"><i class="pi pi-video mr-1"></i>{{ t('vacancies.form.interview') }}</span>
          </template>
          <ScreeningTab
            :vacancy-id="vacancyId"
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
          />
        </TabPanel>

        <!-- Candidates tab (always last) -->
        <TabPanel :value="String(candidatesTabIndex)">
          <template #header>
            <span class="text-xs sm:text-sm">{{ t('candidates.title') }}</span>
            <span
              v-if="candidateStore.candidates.length"
              class="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-blue-500 px-1 text-[9px] font-bold text-white sm:h-5 sm:min-w-5 sm:px-1.5 sm:text-[10px]"
            >
              {{ candidateStore.candidates.length }}
            </span>
          </template>
          <CandidatesTab
            :vacancy-id="vacancyId"
            :interview-enabled="vacancy?.interviewEnabled ?? false"
          />
        </TabPanel>
      </TabView>
    </template>

    <ConfirmDialog />
  </div>
</template>

<style scoped>
:deep(.p-tabview-panels) {
  border-top: none !important;
  background: white !important;
  border-radius: 0 0 0.5rem 0.5rem !important;
}

:deep(.p-tabview-tablist) {
  border-width: 0 0 1px 0 !important;
  border-color: #e5e7eb !important;
}

:deep(.p-tabview-tab-header) {
  border: none !important;
  padding: 0.5rem 0.75rem !important;
}

@media (min-width: 640px) {
  :deep(.p-tabview-tab-header) {
    padding: 0.75rem 1rem !important;
  }
}
</style>
