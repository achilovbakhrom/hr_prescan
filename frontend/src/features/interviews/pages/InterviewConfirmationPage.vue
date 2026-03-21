<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import { useInterviewStore } from '../stores/interview.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

onMounted(() => interviewStore.fetchCandidateInterview(interviewId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleDownloadCalendar(): void {
  window.alert('Calendar invite download will be available in a future release.')
}

function handleGoToInterview(): void {
  router.push({
    name: ROUTE_NAMES.CANDIDATE_INTERVIEW,
    params: { id: interviewId.value },
  })
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

    <div
      v-else-if="interview"
      class="rounded-lg border border-green-200 bg-white p-8 text-center"
    >
      <i class="pi pi-check-circle mb-4 text-5xl text-green-500"></i>
      <h1 class="mb-2 text-2xl font-bold text-gray-900">
        Interview Scheduled!
      </h1>
      <p class="mb-6 text-gray-600">
        Your interview has been confirmed. Here are the details:
      </p>

      <div class="mb-6 rounded-lg bg-gray-50 p-4 text-left">
        <dl class="space-y-2 text-sm">
          <div class="flex justify-between">
            <dt class="text-gray-500">Date</dt>
            <dd class="font-medium">
              {{ formatDate(interview.createdAt) }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Time</dt>
            <dd class="font-medium">
              {{ formatTime(interview.createdAt) }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Duration</dt>
            <dd class="font-medium">
              {{ interview.durationMinutes }} minutes
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Position</dt>
            <dd class="font-medium">{{ interview.vacancyTitle }}</dd>
          </div>
        </dl>
      </div>

      <div class="flex flex-col gap-3">
        <Button
          label="Download Calendar Invite"
          icon="pi pi-download"
          severity="secondary"
          outlined
          @click="handleDownloadCalendar"
        />
        <Button
          label="Go to Interview Room"
          icon="pi pi-video"
          @click="handleGoToInterview"
        />
      </div>
    </div>
  </div>
</template>
