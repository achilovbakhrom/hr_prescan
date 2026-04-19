import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { companyService } from '../services/company.service'
import type {
  Company,
  CreateCompanyInput,
  UpdateCompanyInput,
  UserCompanyMembership,
} from '../types/company.types'

export const useCompanyStore = defineStore('company', () => {
  const companies = ref<UserCompanyMembership[]>([])
  const currentCompany = ref<Company | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const defaultCompany = computed(() => companies.value.find((c) => c.isDefault) ?? null)
  const liveCount = computed(() => companies.value.filter((c) => !c.isDeleted).length)

  async function fetchCompanies(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      companies.value = await companyService.list()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchCompanyDetail(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentCompany.value = await companyService.getDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function createCompany(data: CreateCompanyInput): Promise<Company> {
    loading.value = true
    error.value = null
    try {
      const company = await companyService.create(data)
      // Re-fetch to pick up is_default + membership metadata applied by the backend.
      await fetchCompanies()
      return company
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function updateCompany(id: string, data: UpdateCompanyInput): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await companyService.update(id, data)
      if (currentCompany.value?.id === id) {
        currentCompany.value = updated
      }
      const index = companies.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        companies.value[index] = { ...companies.value[index], ...updated }
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function softDeleteCompany(id: string): Promise<void> {
    try {
      await companyService.softDelete(id)
      // Default may have transferred; refresh the list.
      await fetchCompanies()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function setDefaultCompany(id: string): Promise<void> {
    try {
      await companyService.setDefault(id)
      companies.value = companies.value.map((c) => ({ ...c, isDefault: c.id === id }))
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  return {
    companies,
    currentCompany,
    loading,
    error,
    defaultCompany,
    liveCount,
    fetchCompanies,
    fetchCompanyDetail,
    createCompany,
    updateCompany,
    softDeleteCompany,
    setDefaultCompany,
  }
})
