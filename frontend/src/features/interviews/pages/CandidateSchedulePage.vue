<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview.store'
import ScheduleForm from '../components/ScheduleForm.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const applicationId = computed(() => route.params.applicationId as string)
const vacancyTitle = ref(
  (route.query.vacancy as string) || 'Interview',
)
const durationMinutes = ref(
  Number(route.query.duration) || 30,
)

async function handleSchedule(scheduledAt: string): Promise<void> {
  try {
    const interview = await interviewStore.scheduleByCandidate(
      applicationId.value,
      { scheduledAt },
    )
    router.push({
      name: ROUTE_NAMES.INTERVIEW_CONFIRMATION,
      params: { id: interview.id },
    })
  } catch {
    // error is set in store
  }
}
</script>

<template>
  <div class="mx-auto max-w-lg py-12">
    <div class="rounded-lg border border-gray-200 bg-white p-8">
      <h1 class="mb-6 text-2xl font-bold text-gray-900">
        Schedule Your Interview
      </h1>

      <p v-if="interviewStore.error" class="mb-4 text-sm text-red-600">
        {{ interviewStore.error }}
      </p>

      <ScheduleForm
        :loading="interviewStore.loading"
        :vacancy-title="vacancyTitle"
        :duration-minutes="durationMinutes"
        @submit="handleSchedule"
      />
    </div>
  </div>
</template>
