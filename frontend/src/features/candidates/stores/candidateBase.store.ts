import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { candidateService } from '../services/candidate.service'
import type {
  HRCandidateRecord,
  HRCandidateRecordDetail,
  HRCandidateRecordUpdate,
} from '../types/candidate.types'

export const useCandidateBaseStore = defineStore('candidateBase', () => {
  const candidates = ref<HRCandidateRecord[]>([])
  const currentCandidate = ref<HRCandidateRecordDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchCandidates(params?: { search?: string; ordering?: string }): Promise<void> {
    candidates.value = []
    loading.value = true
    error.value = null
    try {
      candidates.value = await candidateService.getCandidateBase(params)
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
      currentCandidate.value = await candidateService.getCandidateBaseDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function updateCandidate(id: string, data: HRCandidateRecordUpdate): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await candidateService.updateCandidateBase(id, data)
      currentCandidate.value = updated
      const index = candidates.value.findIndex((candidate) => candidate.id === id)
      if (index !== -1) candidates.value[index] = updated
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function deleteCandidate(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await candidateService.deleteCandidateBase(id)
      candidates.value = candidates.value.filter((candidate) => candidate.id !== id)
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
    loading,
    error,
    fetchCandidates,
    fetchCandidateDetail,
    updateCandidate,
    deleteCandidate,
  }
})
