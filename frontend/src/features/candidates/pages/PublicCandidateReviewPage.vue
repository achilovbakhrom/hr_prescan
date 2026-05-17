<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import GlassCard from '@/shared/components/GlassCard.vue'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import PublicReviewFeedbackForm from '../components/PublicReviewFeedbackForm.vue'
import PublicReviewSessionCard from '../components/PublicReviewSessionCard.vue'
import { candidateService, type PublicCandidateReview } from '../services/candidate.service'

const route = useRoute()
const review = ref<PublicCandidateReview | null>(null)
const loading = ref(false)
const error = ref('')
const token = computed(() => route.params.token as string)

onMounted(async () => {
  loading.value = true
  try {
    review.value = await candidateService.getPublicCandidateReview(token.value)
  } catch {
    error.value = 'Candidate review is unavailable.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-5 px-4 py-6">
    <div v-if="loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>
    <p v-else-if="error" class="py-12 text-center text-sm text-red-600">{{ error }}</p>

    <template v-else-if="review">
      <GlassCard>
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Hiring manager review
            </p>
            <h1 class="mt-1 text-2xl font-bold text-gray-900">
              {{ review.candidate.candidateName }}
            </h1>
            <p class="mt-1 text-sm text-gray-600">
              {{ review.candidate.vacancyTitle }} · {{ review.candidate.companyName }}
            </p>
            <p class="mt-1 text-sm text-gray-500">{{ review.candidate.candidateEmail }}</p>
          </div>
          <ApplicationStatusBadge :status="review.candidate.status" />
        </div>
      </GlassCard>

      <GlassCard>
        <PublicReviewFeedbackForm :token="token" />
      </GlassCard>

      <GlassCard v-for="session in review.sessions" :key="session.id">
        <PublicReviewSessionCard :session="session" />
      </GlassCard>
    </template>
  </div>
</template>
