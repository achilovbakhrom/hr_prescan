import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { candidateService } from '../services/candidate.service'
import type {
  Application,
  ApplicationDetail,
  ApplicationStatus,
  SubmitApplicationRequest,
} from '../types/candidate.types'

export const useCandidateStore = defineStore('candidate', () => {
  const candidates = ref<Application[]>([])
  const currentCandidate = ref<ApplicationDetail | null>(null)
  const myApplications = ref<Application[]>([])
  const currentApplication = ref<ApplicationDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // HR actions
  async function fetchVacancyCandidates(
    vacancyId: string,
    params?: { status?: string; ordering?: string; search?: string },
  ): Promise<void> {
    candidates.value = []
    loading.value = true
    error.value = null
    try {
      candidates.value = await candidateService.getVacancyCandidates(vacancyId, params)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchAllCandidates(
    params?: { status?: string; ordering?: string; search?: string; vacancyId?: string },
  ): Promise<void> {
    candidates.value = []
    loading.value = true
    error.value = null
    try {
      candidates.value = await candidateService.getAllCandidates(params)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchCandidateDetail(id: string): Promise<void> {
    currentCandidate.value = null
    loading.value = true
    error.value = null
    try {
      currentCandidate.value = await candidateService.getCandidateDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(id: string, status: ApplicationStatus): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await candidateService.updateCandidateStatus(id, status)
      if (currentCandidate.value?.id === id) {
        currentCandidate.value.status = updated.status
      }
      const index = candidates.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        candidates.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function addNote(id: string, note: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await candidateService.addCandidateNote(id, note)
      if (currentCandidate.value?.id === id) {
        currentCandidate.value.hrNotes = updated.hrNotes
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  // Public / candidate actions
  async function submitApplication(
    vacancyId: string,
    data: SubmitApplicationRequest,
  ): Promise<Application> {
    loading.value = true
    error.value = null
    try {
      const application = await candidateService.submitApplication(vacancyId, data)
      return application
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function fetchMyApplications(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      myApplications.value = await candidateService.getMyApplications()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchMyApplicationDetail(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentApplication.value = await candidateService.getMyApplicationDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function bulkUpdateStatus(
    applicationIds: string[],
    status: ApplicationStatus,
  ): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await candidateService.bulkUpdateStatus(applicationIds, status)
      candidates.value = candidates.value.map((c: Application) =>
        applicationIds.includes(c.id) ? { ...c, status } : c,
      )
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  return {
    candidates,
    currentCandidate,
    myApplications,
    currentApplication,
    loading,
    error,
    fetchVacancyCandidates,
    fetchAllCandidates,
    fetchCandidateDetail,
    updateStatus,
    addNote,
    submitApplication,
    fetchMyApplications,
    fetchMyApplicationDetail,
    bulkUpdateStatus,
  }
})
