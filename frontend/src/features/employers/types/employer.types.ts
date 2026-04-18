export interface EmployerCompany {
  id: string
  name: string
  industry: string
  logo: string
  website: string
  description: string
  descriptionTranslations: Record<string, string>
  source: 'manual' | 'file' | 'website'
  createdAt: string
  updatedAt: string
}
