<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { interviewService } from '../services/interview.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { InterviewDetail } from '../types/interview.types'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()

const token = route.params.token as string
const loading = ref(true)
const errorState = ref<'expired' | 'closed' | 'completed' | 'error' | null>(null)
const errorMessage = ref('')
const interview = ref<InterviewDetail | null>(null)

onMounted(async () => {
  try {
    const data = await interviewService.getInterviewByToken(token)
    interview.value = data

    if (data.status === 'completed') {
      errorState.value = 'completed'
      loading.value = false
      return
    }

    if (data.status === 'expired') {
      errorState.value = 'expired'
      loading.value = false
      return
    }

    if (data.status === 'cancelled') {
      errorState.value = 'closed'
      loading.value = false
      return
    }

    // Redirect based on screening mode
    if (data.screeningMode === 'chat') {
      router.replace({ name: ROUTE_NAMES.CHAT_INTERVIEW, params: { token } })
    } else {
      router.replace({ name: ROUTE_NAMES.INTERVIEW_ROOM, params: { token } })
    }
  } catch (err: unknown) {
    const axiosErr = err as { response?: { status?: number; data?: { detail?: string; message?: string } } }
    const status = axiosErr.response?.status
    const detail = axiosErr.response?.data?.detail ?? axiosErr.response?.data?.message ?? ''

    if (status === 404) {
      errorState.value = 'error'
      errorMessage.value = 'Interview not found. The link may be invalid.'
    } else if (status === 410 || detail.toLowerCase().includes('expired')) {
      errorState.value = 'expired'
      errorMessage.value = detail || 'This interview link has expired.'
    } else if (detail.toLowerCase().includes('closed')) {
      errorState.value = 'closed'
      errorMessage.value = detail || 'This vacancy has been closed.'
    } else {
      errorState.value = 'error'
      errorMessage.value = detail || 'Something went wrong. Please try again later.'
    }
    loading.value = false
  }
})
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center px-4 py-12">
    <!-- Loading spinner -->
    <div v-if="loading" class="text-center">
      <i class="pi pi-spinner pi-spin mb-4 text-4xl text-blue-500"></i>
      <p class="text-gray-600">{{ t('interviews.gatewayPage.loading') }}</p>
    </div>

    <!-- Error states -->
    <div v-else class="w-full max-w-md text-center">
      <!-- Completed -->
      <template v-if="errorState === 'completed'">
        <div class="rounded-lg border border-green-200 bg-green-50 p-8">
          <i class="pi pi-check-circle mb-4 text-5xl text-green-500"></i>
          <h1 class="mb-2 text-2xl font-bold text-gray-900">{{ t('interviews.gatewayPage.interviewCompleted') }}</h1>
          <p class="mb-4 text-gray-600">
            {{ t('interviews.gatewayPage.completedMessage') }}
          </p>
          <RouterLink to="/jobs" class="text-blue-600 hover:underline">
            {{ t('interviews.gatewayPage.browseMoreJobs') }}
          </RouterLink>
        </div>
      </template>

      <!-- Expired -->
      <template v-else-if="errorState === 'expired'">
        <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-8">
          <i class="pi pi-clock mb-4 text-5xl text-yellow-500"></i>
          <h1 class="mb-2 text-2xl font-bold text-gray-900">{{ t('interviews.gatewayPage.linkExpired') }}</h1>
          <p class="mb-4 text-gray-600">
            {{ errorMessage || t('interviews.states.expired') }}
          </p>
          <RouterLink to="/jobs" class="text-blue-600 hover:underline">
            {{ t('interviews.gatewayPage.browseMoreJobs') }}
          </RouterLink>
        </div>
      </template>

      <!-- Vacancy closed -->
      <template v-else-if="errorState === 'closed'">
        <div class="rounded-lg border border-gray-200 bg-gray-50 p-8">
          <i class="pi pi-ban mb-4 text-5xl text-gray-400"></i>
          <h1 class="mb-2 text-2xl font-bold text-gray-900">{{ t('interviews.gatewayPage.vacancyClosed') }}</h1>
          <p class="mb-4 text-gray-600">
            {{ errorMessage || t('interviews.states.closed') }}
          </p>
          <RouterLink to="/jobs" class="text-blue-600 hover:underline">
            {{ t('interviews.gatewayPage.browseMoreJobs') }}
          </RouterLink>
        </div>
      </template>

      <!-- Generic error -->
      <template v-else>
        <div class="rounded-lg border border-red-200 bg-red-50 p-8">
          <i class="pi pi-exclamation-triangle mb-4 text-5xl text-red-400"></i>
          <h1 class="mb-2 text-2xl font-bold text-gray-900">{{ t('interviews.gatewayPage.somethingWentWrong') }}</h1>
          <p class="mb-4 text-gray-600">{{ errorMessage }}</p>
          <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" @click="$router.go(0)" />
        </div>
      </template>
    </div>
  </div>
</template>
