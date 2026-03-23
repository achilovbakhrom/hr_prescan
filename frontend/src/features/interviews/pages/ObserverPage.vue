<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useInterviewStore } from '../stores/interview.store'
import ConnectionStatus from '@/features/video/components/ConnectionStatus.vue'
import { useLiveKit } from '@/features/video/composables/useLiveKit'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const livekitUrl = computed(() => {
  return import.meta.env.VITE_LIVEKIT_URL || 'wss://localhost:7880'
})

const {
  connectionState,
  error: livekitError,
  connectAsObserver,
  disconnect,
} = useLiveKit()

const isJoined = ref(false)

onMounted(async () => {
  await interviewStore.fetchInterviewDetail(interviewId.value)

  if (interview.value && interview.value.status === 'in_progress') {
    try {
      const token = await interviewStore.getObserverToken(interviewId.value)
      await connectAsObserver({
        url: livekitUrl.value,
        token,
        roomName: interview.value.livekitRoomName,
      })
      isJoined.value = true
    } catch {
      // error set in store or livekit composable
    }
  }
})

async function handleLeave(): Promise<void> {
  await disconnect()
  router.back()
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button class="text-gray-500 hover:text-gray-700" @click="router.back()">
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">{{ t('interviews.observerPage.title') }}</h1>
    </div>

    <p v-if="interviewStore.error" class="text-sm text-red-600">
      {{ interviewStore.error }}
    </p>
    <p v-if="livekitError" class="text-sm text-red-600">
      {{ livekitError }}
    </p>

    <div
      v-if="interviewStore.loading && !interview"
      class="py-12 text-center"
    >
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-if="interview">
      <!-- Interview not in progress -->
      <div
        v-if="interview.status !== 'in_progress' && !isJoined"
        class="rounded-lg border border-yellow-200 bg-yellow-50 p-6 text-center"
      >
        <i class="pi pi-info-circle mb-3 text-3xl text-yellow-500"></i>
        <p class="text-gray-700">
          {{ t('interviews.observerPage.notInProgress') }}
        </p>
        <p class="mt-2 text-sm text-gray-500">
          {{ t('common.status') }}: {{ interview.status }}
        </p>
      </div>

      <!-- Observer View -->
      <template v-if="isJoined">
        <div
          class="flex items-center justify-between rounded-lg bg-white p-4 shadow-sm"
        >
          <div class="flex items-center gap-4">
            <ConnectionStatus :state="connectionState" />
            <span class="rounded bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
              {{ t('interviews.observerPage.observerMode') }}
            </span>
          </div>
          <div class="text-sm text-gray-600">
            <span class="font-medium">{{ interview.candidateName }}</span>
            <span class="mx-2 text-gray-400">|</span>
            <span>{{ interview.vacancyTitle }}</span>
          </div>
        </div>

        <!-- Audio-only observer area -->
        <div
          class="flex min-h-[300px] items-center justify-center rounded-lg bg-gray-900 p-8"
        >
          <div class="text-center">
            <div
              class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gray-700"
            >
              <i class="pi pi-headphones text-3xl text-gray-400"></i>
            </div>
            <p class="text-sm text-gray-400">
              {{ t('interviews.observerPage.listeningAudio') }}
            </p>
            <p class="mt-1 text-xs text-gray-500">
              {{ t('interviews.observerPage.audioOnlyNote') }}
            </p>
          </div>
        </div>

        <div class="flex justify-center">
          <Button
            :label="t('interviews.observerPage.leaveObservation')"
            icon="pi pi-sign-out"
            severity="secondary"
            @click="handleLeave"
          />
        </div>
      </template>
    </template>
  </div>
</template>
