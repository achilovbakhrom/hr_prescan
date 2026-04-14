export type ApplicationStatus =
  | 'applied'
  | 'prescanned'
  | 'interviewed'
  | 'shortlisted'
  | 'hired'
  | 'rejected'
  | 'expired'
  | 'archived'

export interface Application {
  id: string
  vacancyId: string
  vacancyTitle: string
  candidateName: string
  candidateEmail: string
  candidatePhone: string
  cvFile: string
  cvOriginalFilename: string
  matchScore: number | null
  prescanningScore: number | null
  interviewScore: number | null
  status: ApplicationStatus
  createdAt: string
  updatedAt: string
}
