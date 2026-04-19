export interface Company {
  id: string
  name: string
  industries: string[]
  customIndustry: string
  size: 'small' | 'medium' | 'large' | 'enterprise'
  country: string
  logo: string | null
  website: string | null
  description: string | null
  isDeleted: boolean
  createdAt: string
  updatedAt: string
}

export interface UserCompanyMembership extends Company {
  isDefault: boolean
  role: 'admin' | 'hr' | 'candidate'
}

export interface CreateCompanyInput {
  name: string
  size: Company['size']
  country: string
  industries?: string[]
  customIndustry?: string
  website?: string
  description?: string
}

export type UpdateCompanyInput = Partial<CreateCompanyInput> & { logo?: string }
