<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import { useInterviewStore } from '../stores/interview.store'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'

const route = useRoute()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const isCompleted = computed(() => interview.value?.status === 'completed')
const isScheduled = computed(() => interview.value?.status === 'scheduled')
const isInProgress = computed(() => interview.value?.status === 'in_progress')

onMounted(() => interviewStore.fetchCandidateInterview(interviewId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

function handleJoinInterview(): void {
  window.alert('LiveKit interview room will be available in Phase 7.')
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
        <h1 class="mb-2 text-2xl font-bold text-gray-900">Thank You!</h1>
        <p class="text-gray-600">
          Your interview has been completed. We will review your responses and
          get back to you soon.
        </p>
      </div>

      <!-- Pre-interview state -->
      <div
        v-else
        class="rounded-lg border border-gray-200 bg-white p-8"
      >
        <h1 class="mb-6 text-2xl font-bold text-gray-900">
          Your Interview
        </h1>

        <div class="space-y-4">
          <div class="rounded-lg bg-gray-50 p-4">
            <dl class="space-y-2 text-sm">
              <div class="flex justify-between">
                <dt class="text-gray-500">Position</dt>
                <dd class="font-medium">{{ interview.vacancyTitle }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Scheduled</dt>
                <dd class="font-medium">
                  {{ formatDate(interview.scheduledAt) }}
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Duration</dt>
                <dd class="font-medium">
                  {{ interview.durationMinutes }} minutes
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Status</dt>
                <dd>
                  <InterviewStatusBadge :status="interview.status" />
                </dd>
              </div>
            </dl>
          </div>

          <div class="rounded-lg border border-blue-100 bg-blue-50 p-4">
            <h3 class="mb-2 text-sm font-semibold text-blue-800">
              Instructions
            </h3>
            <ul class="list-inside list-disc space-y-1 text-sm text-blue-700">
              <li>Ensure you have a stable internet connection</li>
              <li>Use a well-lit, quiet room</li>
              <li>Allow camera and microphone access</li>
              <li>Keep your face visible throughout the interview</li>
            </ul>
          </div>

          <div class="rounded-lg border border-gray-200 p-4">
            <h3 class="mb-2 text-sm font-semibold text-gray-700">
              Camera & Microphone Test
            </h3>
            <p class="text-xs text-gray-500">
              Device testing will be available when LiveKit is integrated.
            </p>
          </div>

          <Button
            v-if="isScheduled || isInProgress"
            label="Join Interview"
            icon="pi pi-video"
            class="w-full"
            @click="handleJoinInterview"
          />
        </div>
      </div>
    </template>
  </div>
</template>
