<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import { useCandidateBaseStore } from '../stores/candidateBase.store'
import type { Application } from '../types/candidate.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateBaseStore()
const candidateId = computed(() => route.params.id as string)
const record = computed(() => candidateStore.currentCandidate)
const candidateName = ref('')
const candidatePhone = ref('')
const notes = ref('')

function hydrateForm(): void {
  candidateName.value = record.value?.candidateName ?? ''
  candidatePhone.value = record.value?.candidatePhone ?? ''
  notes.value = record.value?.notes ?? ''
}

async function fetchRecord(): Promise<void> {
  await candidateStore.fetchCandidateDetail(candidateId.value)
  hydrateForm()
}

async function saveRecord(): Promise<void> {
  await candidateStore.updateCandidate(candidateId.value, {
    candidateName: candidateName.value,
    candidatePhone: candidatePhone.value,
    notes: notes.value,
  })
  hydrateForm()
}

async function deleteRecord(): Promise<void> {
  await candidateStore.deleteCandidate(candidateId.value)
  router.push({ name: ROUTE_NAMES.CANDIDATE_LIST, query: { tab: 'base' } })
}

function openApplication(application: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: application.id } })
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(value))
}

function scoreLabel(value: number | string | null): string {
  if (value === null || value === undefined || value === '') return '-'
  const numberValue = typeof value === 'string' ? Number(value) : value
  return Number.isNaN(numberValue) ? String(value) : numberValue.toFixed(1)
}

onMounted(fetchRecord)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-2 sm:gap-3">
      <button
        class="shrink-0 rounded-lg p-1.5 text-[color:var(--color-text-muted)] transition-colors hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left"></i>
      </button>
      <div class="min-w-0 flex-1">
        <h1
          class="truncate text-lg font-bold text-[color:var(--color-text-primary)] sm:text-xl md:text-2xl"
        >
          {{ record?.candidateName ?? t('common.loading') }}
        </h1>
        <p v-if="record" class="truncate text-xs text-[color:var(--color-text-muted)] sm:text-sm">
          {{ record.candidateEmail }}
        </p>
      </div>
      <Button
        icon="pi pi-trash"
        severity="danger"
        text
        :aria-label="t('common.delete')"
        @click="deleteRecord"
      />
    </div>

    <p v-if="candidateStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ candidateStore.error }}
    </p>
    <div v-if="!record && candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else-if="record">
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <GlassCard class="space-y-3">
          <div>
            <label class="mb-1 block text-xs font-medium text-[color:var(--color-text-muted)]">
              {{ t('common.name') }}
            </label>
            <InputText v-model="candidateName" class="w-full" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-[color:var(--color-text-muted)]">
              {{ t('candidates.application.email') }}
            </label>
            <InputText :model-value="record.candidateEmail" class="w-full" disabled />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-[color:var(--color-text-muted)]">
              {{ t('candidates.application.phone') }}
            </label>
            <InputText v-model="candidatePhone" class="w-full" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-[color:var(--color-text-muted)]">
              {{ t('candidates.notes') }}
            </label>
            <Textarea v-model="notes" class="w-full" rows="5" auto-resize />
          </div>
          <Button
            :label="t('common.save')"
            icon="pi pi-save"
            class="w-full"
            :loading="candidateStore.loading"
            @click="saveRecord"
          />
        </GlassCard>

        <GlassCard class="!p-0 overflow-hidden">
          <DataTable
            :value="record.applications"
            data-key="id"
            responsive-layout="scroll"
            striped-rows
            @row-click="openApplication($event.data)"
          >
            <Column field="vacancyTitle" :header="t('nav.vacancies')" style="min-width: 220px" />
            <Column :header="t('common.status')" style="width: 130px">
              <template #body="{ data }">
                <ApplicationStatusBadge :status="data.status" />
              </template>
            </Column>
            <Column :header="t('candidates.overallScore')" style="width: 120px">
              <template #body="{ data }">{{ scoreLabel(data.matchScore) }}</template>
            </Column>
            <Column :header="t('candidates.prescanScore')" style="width: 120px">
              <template #body="{ data }">{{ scoreLabel(data.prescanningScore) }}</template>
            </Column>
            <Column :header="t('candidates.interviewScore')" style="width: 120px">
              <template #body="{ data }">{{ scoreLabel(data.interviewScore) }}</template>
            </Column>
            <Column :header="t('common.createdAt')" style="width: 150px">
              <template #body="{ data }">{{ formatDate(data.createdAt) }}</template>
            </Column>
          </DataTable>
        </GlassCard>
      </div>
    </template>
  </div>
</template>
