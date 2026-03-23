<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useInterviewStore } from '../stores/interview.store'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const isCompleted = computed(() => interview.value?.status === 'completed')
const isScheduled = computed(() => interview.value?.status === 'pending')
const isInProgress = computed(() => interview.value?.status === 'in_progress')

onMounted(() => interviewStore.fetchCandidateInterview(interviewId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

function handleJoinInterview(): void {
  router.push({ name: ROUTE_NAMES.INTERVIEW_ROOM, params: { id: interviewId.value } })
}
</script>

<template>
  <div class="mx-auto max-w-lg py-12">
    <div
      v-if="!interview && interviewStore.loading"
      class="py-12 text-center"
    >
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <p v-if="interviewStore.error" class="mb-4 text-sm text-red-600">
      {{ interviewStore.error }}
    </p>

    <template v-if="interview">
      <!-- Completed state -->
      <div
        v-if="isCompleted"
        class="rounded-lg border border-green-200 bg-green-50 p-8 text-center"
      >
        <i class="pi pi-check-circle mb-4 text-5xl text-green-500"></i>
        <h1 class="mb-2 text-2xl font-bold text-gray-900">{{ t('interviews.candidatePage.thankYou') }}</h1>
        <p class="text-gray-600">
          {{ t('interviews.candidatePage.completedMessage') }}
        </p>
      </div>

      <!-- Pre-interview state -->
      <div
        v-else
        class="rounded-lg border border-gray-200 bg-white p-8"
      >
        <h1 class="mb-6 text-2xl font-bold text-gray-900">
          {{ t('interviews.candidatePage.yourInterview') }}
        </h1>

        <div class="space-y-4">
          <div class="rounded-lg bg-gray-50 p-4">
            <dl class="space-y-2 text-sm">
              <div class="flex justify-between">
                <dt class="text-gray-500">{{ t('interviews.preCheck.position') }}</dt>
                <dd class="font-medium">{{ interview.vacancyTitle }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">{{ t('interviews.preCheck.scheduled') }}</dt>
                <dd class="font-medium">
                  {{ formatDate(interview.createdAt) }}
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">{{ t('interviews.preCheck.duration') }}</dt>
                <dd class="font-medium">
                  {{ t('interviews.preCheck.durationMinutes', { minutes: interview.durationMinutes }) }}
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">{{ t('common.status') }}</dt>
                <dd>
                  <InterviewStatusBadge :status="interview.status" />
                </dd>
              </div>
            </dl>
          </div>

          <div class="rounded-lg border border-blue-100 bg-blue-50 p-4">
            <h3 class="mb-2 text-sm font-semibold text-blue-800">
              {{ t('interviews.candidatePage.instructions') }}
            </h3>
            <ul class="list-inside list-disc space-y-1 text-sm text-blue-700">
              <li>{{ t('interviews.preCheck.stableConnection') }}</li>
              <li>{{ t('interviews.preCheck.quietRoom') }}</li>
              <li>{{ t('interviews.preCheck.allowCameraMicAccess') }}</li>
              <li>{{ t('interviews.preCheck.faceVisible') }}</li>
            </ul>
          </div>

          <div class="rounded-lg border border-gray-200 p-4">
            <h3 class="mb-2 text-sm font-semibold text-gray-700">
              {{ t('interviews.candidatePage.cameraMicTest') }}
            </h3>
            <p class="text-xs text-gray-500">
              {{ t('interviews.candidatePage.deviceTestNote') }}
            </p>
          </div>

          <Button
            v-if="isScheduled || isInProgress"
            :label="t('interviews.candidatePage.joinInterview')"
            icon="pi pi-video"
            class="w-full"
            @click="handleJoinInterview"
          />
        </div>
      </div>
    </template>
  </div>
</template>
