import { apiClient } from '@/shared/api/client'
import type {
  Company,
  CreateCompanyInput,
  UpdateCompanyInput,
  UserCompanyMembership,
} from '../types/company.types'

export const companyService = {
  async list(): Promise<UserCompanyMembership[]> {
    const response = await apiClient.get('/hr/companies/')
    return response.data
  },
  async create(data: CreateCompanyInput): Promise<Company> {
    const response = await apiClient.post('/hr/companies/', data)
    return response.data
  },
  async getDetail(id: string): Promise<Company> {
    const response = await apiClient.get(`/hr/companies/${id}/`)
    return response.data
  },
  async update(id: string, data: UpdateCompanyInput): Promise<Company> {
    const response = await apiClient.patch(`/hr/companies/${id}/`, data)
    return response.data
  },
  async uploadLogo(id: string, file: File): Promise<Company> {
    const form = new FormData()
    form.append('logo', file)
    const response = await apiClient.patch(`/hr/companies/${id}/`, form)
    return response.data
  },
  async softDelete(id: string): Promise<void> {
    await apiClient.delete(`/hr/companies/${id}/`)
  },
  async setDefault(id: string): Promise<{ company_id: string; is_default: boolean }> {
    const response = await apiClient.post(`/hr/companies/${id}/set-default/`)
    return response.data
  },
}
