import { apiClient } from '@/shared/api/client'
import type { EmployerCompany } from '../types/employer.types'

export const employerService = {
  async list(): Promise<EmployerCompany[]> {
    const response = await apiClient.get('/hr/employers')
    return response.data
  },
  async create(data: Partial<EmployerCompany>): Promise<EmployerCompany> {
    const response = await apiClient.post('/hr/employers', data)
    return response.data
  },
  async getDetail(id: string): Promise<EmployerCompany> {
    const response = await apiClient.get(`/hr/employers/${id}`)
    return response.data
  },
  async update(id: string, data: Partial<EmployerCompany>): Promise<EmployerCompany> {
    const response = await apiClient.put(`/hr/employers/${id}`, data)
    return response.data
  },
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/hr/employers/${id}`)
  },
  async createFromFile(name: string, file: File): Promise<EmployerCompany> {
    const formData = new FormData()
    formData.append('name', name)
    formData.append('file', file)
    const response = await apiClient.post('/hr/employers/parse-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  async createFromUrl(name: string, url: string): Promise<EmployerCompany> {
    const response = await apiClient.post('/hr/employers/parse-url', { name, url })
    return response.data
  },
}
