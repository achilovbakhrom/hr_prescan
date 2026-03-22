import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { employerService } from '../services/employer.service'
import type { EmployerCompany } from '../types/employer.types'

export const useEmployerStore = defineStore('employer', () => {
  const employers = ref<EmployerCompany[]>([])
  const currentEmployer = ref<EmployerCompany | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchEmployers(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      employers.value = await employerService.list()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchEmployerDetail(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentEmployer.value = await employerService.getDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function createEmployer(data: Partial<EmployerCompany>): Promise<EmployerCompany> {
    loading.value = true
    error.value = null
    try {
      const employer = await employerService.create(data)
      employers.value.unshift(employer)
      return employer
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function createEmployerFromFile(name: string, file: File): Promise<EmployerCompany> {
    loading.value = true
    error.value = null
    try {
      const employer = await employerService.createFromFile(name, file)
      employers.value.unshift(employer)
      return employer
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function createEmployerFromUrl(name: string, url: string): Promise<EmployerCompany> {
    loading.value = true
    error.value = null
    try {
      const employer = await employerService.createFromUrl(name, url)
      employers.value.unshift(employer)
      return employer
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function updateEmployer(id: string, data: Partial<EmployerCompany>): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await employerService.update(id, data)
      if (currentEmployer.value?.id === id) {
        currentEmployer.value = updated
      }
      const index = employers.value.findIndex((e) => e.id === id)
      if (index !== -1) {
        employers.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function deleteEmployer(id: string): Promise<void> {
    try {
      await employerService.delete(id)
      employers.value = employers.value.filter((e) => e.id !== id)
      if (currentEmployer.value?.id === id) {
        currentEmployer.value = null
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  return {
    employers,
    currentEmployer,
    loading,
    error,
    fetchEmployers,
    fetchEmployerDetail,
    createEmployer,
    createEmployerFromFile,
    createEmployerFromUrl,
    updateEmployer,
    deleteEmployer,
  }
})
