<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import { useCandidateStore } from '../stores/candidate.store'
import CandidateOverview from '../components/CandidateOverview.vue'
import CvDataView from '../components/CvDataView.vue'
import MatchScoreView from '../components/MatchScoreView.vue'
import HRNotesPanel from '../components/HRNotesPanel.vue'
import type { ApplicationStatus } from '../types/candidate.types'

const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const candidateId = computed(() => route.params.id as string)
const candidate = computed(() => candidateStore.currentCandidate)

onMounted(() => candidateStore.fetchCandidateDetail(candidateId.value))

async function handleStatusChange(status: ApplicationStatus): Promise<void> {
  await candidateStore.updateStatus(candidateId.value, status).catch(() => {})
}

async function handleSaveNotes(note: string): Promise<void> {
  await candidateStore.addNote(candidateId.value, note).catch(() => {})
}

function handleDownloadCv(): void {
  if (candidate.value?.cvFile) {
    window.open(candidate.value.cvFile, '_blank')
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button
        class="text-gray-500 hover:text-gray-700"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">
        {{ candidate?.candidateName ?? 'Loading...' }}
      </h1>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <div v-if="!candidate && candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="candidate">
      <TabView>
        <TabPanel header="Overview">
          <div class="py-4">
            <CandidateOverview
              :candidate="candidate"
              :loading="candidateStore.loading"
              @status-change="handleStatusChange"
              @download-cv="handleDownloadCv"
            />
          </div>
        </TabPanel>
        <TabPanel header="CV Data">
          <div class="py-4">
            <CvDataView :data="candidate.cvParsedData" />
          </div>
        </TabPanel>
        <TabPanel header="Match Analysis">
          <div class="py-4">
            <MatchScoreView
              :overall-score="candidate.matchScore"
              :match-details="candidate.matchDetails"
            />
          </div>
        </TabPanel>
        <TabPanel header="Notes">
          <div class="py-4">
            <HRNotesPanel
              :notes="candidate.hrNotes"
              :loading="candidateStore.loading"
              @save="handleSaveNotes"
            />
          </div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>
