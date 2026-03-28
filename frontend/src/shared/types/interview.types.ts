export type IntegrityFlagType = 'face_not_visible' | 'multiple_faces' | 'gaze_deviation' | 'audio_anomaly' | 'cv_inconsistency'
export type IntegritySeverity = 'low' | 'medium' | 'high'

export interface InterviewScore {
  id: string
  criteriaId: string
  criteriaName: string
  score: number
  aiNotes: string
  aiNotesTranslations: Record<string, string>
}

export interface IntegrityFlag {
  id: string
  flagType: IntegrityFlagType
  severity: IntegritySeverity
  description: string
  timestampSeconds: number | null
}
