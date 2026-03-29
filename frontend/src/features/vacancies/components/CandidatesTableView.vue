<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Menu from 'primevue/menu'
import ApplicationStatusBadge from '@/features/candidates/components/ApplicationStatusBadge.vue'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import {
  getTableOverallScore,
  getTableScoreClasses,
  getTableScoreBadge,
  buildRowMenuItems,
} from '../utils/scoreHelpers'

const selectedCandidates = defineModel<Application[]>('selectedCandidates', { required: true })

const props = defineProps<{
  interviewEnabled: boolean
  confirmRowStatus: (c: Application, toStatus: ApplicationStatus) => void
  searchQuery: string
}>()

const { t } = useI18n()
const router = useRouter()
const candidateStore = useCandidateStore()

function viewDetail(candidate: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: candidate.id } })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

const rowMenuRefs = ref<Record<string, InstanceType<typeof Menu> | null>>({})
function setRowMenuRef(id: string, el: unknown) { rowMenuRefs.value[id] = el as InstanceType<typeof Menu> | null }
function toggleRowMenu(event: Event, id: string) { rowMenuRefs.value[id]?.toggle(event) }
</script>

<template>
  <DataTable v-model:selection="selectedCandidates" :value="candidateStore.candidates" :loading="candidateStore.loading" row-hover data-key="id" scrollable class="text-sm">
    <Column selection-mode="multiple" header-style="width: 3rem" />

    <Column :header="t('candidates.title')" sortable sort-field="candidateName" style="min-width: 200px">
      <template #body="{ data }">
        <div class="flex cursor-pointer items-center gap-2.5" @click="viewDetail(data as Application)">
          <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-semibold text-blue-700">
            {{ (data as Application).candidateName.split(' ').map((n: string) => n[0]).slice(0, 2).join('').toUpperCase() }}
          </div>
          <div class="min-w-0">
            <p class="truncate font-medium text-gray-900">{{ (data as Application).candidateName }}</p>
            <p class="truncate text-xs text-gray-500">{{ (data as Application).candidateEmail }}</p>
          </div>
        </div>
      </template>
    </Column>

    <Column :header="t('common.status')" sortable sort-field="status" style="min-width: 120px">
      <template #body="{ data }"><ApplicationStatusBadge :status="(data as Application).status" /></template>
    </Column>

    <Column :header="t('candidates.overallScore')" sortable sort-field="matchScore" style="min-width: 80px">
      <template #body="{ data }">
        <span v-if="getTableOverallScore(data as Application) != null" class="inline-flex h-7 w-7 items-center justify-center rounded-full border-2 text-xs font-bold" :class="getTableScoreClasses(getTableOverallScore(data as Application)!)">
          {{ getTableOverallScore(data as Application) }}
        </span>
        <span v-else class="text-xs text-gray-400">---</span>
      </template>
    </Column>

    <Column header="CV" sortable sort-field="matchScore" style="min-width: 70px">
      <template #body="{ data }">
        <span v-if="(data as Application).matchScore !== null" class="rounded px-1.5 py-0.5 text-xs font-medium bg-blue-50 text-blue-700">{{ (data as Application).matchScore }}%</span>
        <span v-else class="text-xs text-gray-400">---</span>
      </template>
    </Column>

    <Column :header="t('candidates.prescanScore')" style="min-width: 80px">
      <template #body="{ data }">
        <span v-if="(data as Application).prescanningScore != null" class="rounded px-1.5 py-0.5 text-xs font-medium" :class="getTableScoreBadge((data as Application).prescanningScore!, 10)">{{ (data as Application).prescanningScore }}/10</span>
        <span v-else class="text-xs text-gray-400">---</span>
      </template>
    </Column>

    <Column v-if="interviewEnabled" :header="t('candidates.interviewScore')" style="min-width: 80px">
      <template #body="{ data }">
        <span v-if="(data as Application).interviewScore != null" class="rounded px-1.5 py-0.5 text-xs font-medium" :class="getTableScoreBadge((data as Application).interviewScore!, 10)">{{ (data as Application).interviewScore }}/10</span>
        <span v-else class="text-xs text-gray-400">---</span>
      </template>
    </Column>

    <Column :header="t('candidates.status.applied')" sortable sort-field="createdAt" style="min-width: 100px">
      <template #body="{ data }"><span class="text-xs text-gray-500">{{ formatDate((data as Application).createdAt) }}</span></template>
    </Column>

    <Column header="" style="width: 50px" :exportable="false">
      <template #body="{ data }">
        <button class="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600" @click.stop="toggleRowMenu($event, (data as Application).id)">
          <i class="pi pi-ellipsis-v text-sm"></i>
        </button>
        <Menu :ref="(el: unknown) => setRowMenuRef((data as Application).id, el)" :model="buildRowMenuItems(data as Application, interviewEnabled, viewDetail, confirmRowStatus)" :popup="true" />
      </template>
    </Column>

    <template #empty>
      <div class="py-8 text-center text-gray-500">
        <i class="pi pi-users mb-2 text-3xl"></i>
        <p v-if="searchQuery">{{ t('candidates.noMatchingCandidates', { query: searchQuery }) }}</p>
        <p v-else>{{ t('candidates.noCandidatesApplied') }}</p>
      </div>
    </template>
  </DataTable>
</template>
