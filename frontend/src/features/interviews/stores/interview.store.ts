import { ref } from 'vue'
import { defineStore } from 'pinia'
import { interviewService } from '../services/interview.service'
import type {
  Interview,
  InterviewDetail,
  ScheduleInterviewRequest,
} from '../types/interview.types'

export const useInterviewStore = defineStore('interview', () => {
  const interviews = ref<Interview[]>([])
  const currentInterview = ref<InterviewDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchInterviews(params?: {
    status?: string
  }): Promise<void> {
    loading.value = true
    error.value = null
    try {
      interviews.value = await interviewService.getInterviews(params)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function scheduleInterview(
    applicationId: string,
    data: ScheduleInterviewRequest,
  ): Promise<Interview> {
    loading.value = true
    error.value = null
    try {
      const interview = await interviewService.scheduleInterview(
        applicationId,
        data,
      )
      interviews.value.push(interview)
      return interview
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function fetchInterviewDetail(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentInterview.value = await interviewService.getInterviewDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function cancelInterview(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await interviewService.cancelInterview(id)
      if (currentInterview.value?.id === id) {
        currentInterview.value.status = updated.status
      }
      const index = interviews.value.findIndex((i) => i.id === id)
      if (index !== -1) {
        interviews.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function getObserverToken(id: string): Promise<string> {
    loading.value = true
    error.value = null
    try {
      const result = await interviewService.getObserverToken(id)
      return result.token
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function scheduleByCandidate(
    applicationId: string,
    data: ScheduleInterviewRequest,
  ): Promise<Interview> {
    loading.value = true
    error.value = null
    try {
      const interview = await interviewService.scheduleByCandidate(
        applicationId,
        data,
      )
      return interview
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function fetchCandidateInterview(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentInterview.value =
        await interviewService.getCandidateInterview(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  return {
    interviews,
    currentInterview,
    loading,
    error,
    fetchInterviews,
    scheduleInterview,
    fetchInterviewDetail,
    cancelInterview,
    getObserverToken,
    scheduleByCandidate,
    fetchCandidateInterview,
  }
})

function extractErrorMessage(err: unknown): string {
  if (
    typeof err === 'object' &&
    err !== null &&
    'response' in err &&
    typeof (err as Record<string, unknown>).response === 'object'
  ) {
    const response = (err as { response: { data?: { message?: string } } })
      .response
    if (response.data?.message) {
      return response.data.message
    }
  }
  if (err instanceof Error) {
    return err.message
  }
  return 'An unexpected error occurred'
}
