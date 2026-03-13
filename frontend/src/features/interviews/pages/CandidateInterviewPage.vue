<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import { useInterviewStore } from '../stores/interview.store'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import PreInterviewCheck from '../components/PreInterviewCheck.vue'
import InInterviewView from '../components/InInterviewView.vue'
import PostInterviewView from '../components/PostInterviewView.vue'

type InterviewPhase = 'loading' | 'pre' | 'in' | 'post'

const route = useRoute()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const phase = ref<InterviewPhase>('loading')

const livekitUrl = computed(() => {
  return import.meta.env.VITE_LIVEKIT_URL || 'wss://localhost:7880'
})

onMounted(async () => {
  await interviewStore.fetchCandidateInterview(interviewId.value)
  if (interview.value) {
    if (
      interview.value.status === 'completed' ||
      interview.value.status === 'cancelled'
    ) {
      phase.value = 'post'
    } else {
      phase.value = 'pre'
    }
  }
})

function handleJoinInterview(): void {
  phase.value = 'in'
}

function handleInterviewEnd(): void {
  phase.value = 'post'
}
</script>

<template>
  <div class="mx-auto max-w-3xl py-8">
    <!-- Loading -->
    <div
      v-if="phase === 'loading' && interviewStore.loading"
      class="py-12 text-center"
    >
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <p v-if="interviewStore.error" class="mb-4 text-sm text-red-600">
      {{ interviewStore.error }}
    </p>

    <template v-if="interview">
      <!-- Pre-Interview Check -->
      <PreInterviewCheck
        v-if="phase === 'pre'"
        :interview="interview"
        @join="handleJoinInterview"
      />

      <!-- In-Interview -->
      <InInterviewView
        v-if="phase === 'in'"
        :interview="interview"
        :livekit-url="livekitUrl"
        @end="handleInterviewEnd"
      />

      <!-- Post-Interview -->
      <PostInterviewView v-if="phase === 'post'" />
    </template>
  </div>
</template>
