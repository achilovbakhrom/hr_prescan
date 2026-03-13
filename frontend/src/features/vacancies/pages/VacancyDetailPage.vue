<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyStatusBadge from '../components/VacancyStatusBadge.vue'
import VacancyShareLink from '../components/VacancyShareLink.vue'
import VacancyOverview from '../components/VacancyOverview.vue'
import VacancyForm from '../components/VacancyForm.vue'
import QuestionList from '../components/QuestionList.vue'
import CriteriaList from '../components/CriteriaList.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import ApplicationStatusBadge from '@/features/candidates/components/ApplicationStatusBadge.vue'
import type { Application } from '@/features/candidates/types/candidate.types'
import type { CreateVacancyRequest, VacancyStatus } from '../types/vacancy.types'

const route = useRoute()
const router = useRouter()
const vacancyStore = useVacancyStore()
const candidateStore = useCandidateStore()
const activeTab = ref(0)
const vacancyId = computed(() => route.params.id as string)
const vacancy = computed(() => vacancyStore.currentVacancy)

const editFormData = computed(() => {
  if (!vacancy.value) return undefined
  const v = vacancy.value
  return {
    title: v.title, description: v.description, requirements: v.requirements,
    responsibilities: v.responsibilities, skills: v.skills,
    salaryMin: v.salaryMin, salaryMax: v.salaryMax, salaryCurrency: v.salaryCurrency,
    location: v.location, isRemote: v.isRemote, employmentType: v.employmentType,
    experienceLevel: v.experienceLevel, deadline: v.deadline,
    visibility: v.visibility, interviewDuration: v.interviewDuration,
  }
})

onMounted(() => {
  vacancyStore.fetchVacancyDetail(vacancyId.value)
  candidateStore.fetchVacancyCandidates(vacancyId.value)
})

function viewCandidate(candidate: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: candidate.id } })
}

function viewAllCandidates(): void {
  router.push({ name: ROUTE_NAMES.VACANCY_CANDIDATES, params: { vacancyId: vacancyId.value } })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

async function handleStatusChange(status: VacancyStatus): Promise<void> {
  await vacancyStore.changeStatus(vacancyId.value, status).catch(() => {})
}

async function handleUpdate(data: CreateVacancyRequest, publish: boolean): Promise<void> {
  try {
    await vacancyStore.updateVacancy(vacancyId.value, data)
    if (publish && vacancy.value?.status === 'draft') {
      await vacancyStore.changeStatus(vacancyId.value, 'published')
    }
  } catch { /* store handles error */ }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button class="text-gray-500 hover:text-gray-700" @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })">
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">{{ vacancy?.title ?? 'Loading...' }}</h1>
      <VacancyStatusBadge v-if="vacancy" :status="vacancy.status" />
    </div>

    <p v-if="vacancyStore.error" class="text-sm text-red-600">{{ vacancyStore.error }}</p>

    <div v-if="!vacancy && vacancyStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="vacancy">
      <div class="flex items-center gap-2">
        <Button v-if="vacancy.status === 'draft'" label="Publish" icon="pi pi-send" size="small" @click="handleStatusChange('published')" />
        <Button v-if="vacancy.status === 'published'" label="Pause" icon="pi pi-pause" severity="warn" size="small" @click="handleStatusChange('paused')" />
        <Button v-if="vacancy.status === 'paused'" label="Resume" icon="pi pi-play" severity="success" size="small" @click="handleStatusChange('published')" />
        <Button v-if="vacancy.status !== 'closed'" label="Close" icon="pi pi-times" severity="danger" size="small" outlined @click="handleStatusChange('closed')" />
      </div>

      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <h3 class="mb-2 text-sm font-semibold text-gray-600">Share Link</h3>
        <VacancyShareLink :share-token="vacancy.shareToken" />
      </div>

      <TabView v-model:active-index="activeTab">
        <TabPanel header="Overview">
          <div class="space-y-4 py-4">
            <VacancyOverview :vacancy="vacancy" />
            <hr class="border-gray-200" />
            <VacancyForm :initial-data="editFormData" :loading="vacancyStore.loading" @save="handleUpdate" />
          </div>
        </TabPanel>
        <TabPanel header="Questions">
          <div class="py-4">
            <QuestionList
              :questions="vacancy.questions" :loading="vacancyStore.loading"
              @add="(d) => vacancyStore.addQuestion(vacancyId, d)"
              @update="(qId, d) => vacancyStore.updateQuestion(vacancyId, qId, d)"
              @delete="(qId) => vacancyStore.deleteQuestion(vacancyId, qId)"
              @generate="() => vacancyStore.generateQuestions(vacancyId)"
            />
          </div>
        </TabPanel>
        <TabPanel header="Criteria">
          <div class="py-4">
            <CriteriaList
              :criteria="vacancy.criteria" :loading="vacancyStore.loading"
              @add="(d) => vacancyStore.addCriteria(vacancyId, d)"
              @update="(cId, d) => vacancyStore.updateCriteria(vacancyId, cId, d)"
              @delete="(cId) => vacancyStore.deleteCriteria(vacancyId, cId)"
            />
          </div>
        </TabPanel>
        <TabPanel header="Candidates">
          <div class="py-4">
            <div v-if="candidateStore.loading && candidateStore.candidates.length === 0" class="py-8 text-center">
              <i class="pi pi-spinner pi-spin text-2xl text-gray-400"></i>
            </div>
            <div v-else-if="candidateStore.candidates.length === 0" class="py-8 text-center text-gray-500">
              <i class="pi pi-users mb-2 text-3xl"></i>
              <p>No candidates have applied yet</p>
            </div>
            <template v-else>
              <div class="mb-3 flex items-center justify-between">
                <p class="text-sm text-gray-500">{{ candidateStore.candidates.length }} candidate(s)</p>
                <button class="text-sm text-blue-600 hover:underline" @click="viewAllCandidates">View all</button>
              </div>
              <div class="space-y-2">
                <div
                  v-for="candidate in candidateStore.candidates.slice(0, 5)"
                  :key="candidate.id"
                  class="flex cursor-pointer items-center justify-between rounded-lg border border-gray-100 p-3 hover:bg-gray-50"
                  @click="viewCandidate(candidate)"
                >
                  <div>
                    <p class="font-medium">{{ candidate.candidateName }}</p>
                    <p class="text-sm text-gray-500">{{ candidate.candidateEmail }}</p>
                  </div>
                  <div class="flex items-center gap-3">
                    <span v-if="candidate.matchScore !== null" class="text-sm font-semibold">{{ candidate.matchScore }}%</span>
                    <ApplicationStatusBadge :status="candidate.status" />
                    <span class="text-xs text-gray-400">{{ formatDate(candidate.createdAt) }}</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>
