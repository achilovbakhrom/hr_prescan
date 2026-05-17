export type IntegrityFlagType =
  | 'face_not_visible'
  | 'multiple_faces'
  | 'gaze_deviation'
  | 'audio_anomaly'
  | 'cv_inconsistency'
export type IntegritySeverity = 'low' | 'medium' | 'high'

export interface InterviewScore {
  id: string
  criteriaId: string
  criteria?: string
  criteriaName: string
  criteriaTranslations?: Record<string, string>
  score: number
  aiNotes: string
  aiNotesTranslations: Record<string, string>
  evidence?: InterviewEvidence[]
}

export interface InterviewEvidence {
  line?: number | null
  speaker?: string
  timestamp?: number | null
  quote: string
}

export interface DecisionSupport {
  recommendation?: string
  strengths?: string[]
  risks?: string[]
  positiveMoments?: string[]
  positive_moments?: string[]
  negativeMoments?: string[]
  negative_moments?: string[]
  conclusion?: string
  nextStep?: string
  next_step?: string
}

export interface IntegrityFlag {
  id: string
  flagType: IntegrityFlagType
  severity: IntegritySeverity
  description: string
  timestampSeconds: number | null
}
