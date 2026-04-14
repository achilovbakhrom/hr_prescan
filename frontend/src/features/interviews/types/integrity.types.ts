/**
 * Types for anti-cheating integrity monitoring.
 *
 * These mirror the backend InterviewIntegrityFlag model.
 */

export type FlagType =
  | 'face_not_visible'
  | 'multiple_faces'
  | 'gaze_deviation'
  | 'audio_anomaly'
  | 'cv_inconsistency'

export type Severity = 'low' | 'medium' | 'high'

export interface IntegrityFlag {
  id: string
  flagType: FlagType
  severity: Severity
  description: string
  timestampSeconds: number | null
  createdAt?: string
}

export interface IntegrityFlagsResponse {
  interviewId: string
  flags: IntegrityFlag[]
  totalFlags: number
}

/**
 * Compute an overall integrity score (0–100) from a list of flags.
 *
 * Penalties per severity:
 *  - low:    5 points
 *  - medium: 15 points
 *  - high:   25 points
 */
export function computeIntegrityScore(flags: IntegrityFlag[]): number {
  const penalties: Record<Severity, number> = {
    low: 5,
    medium: 15,
    high: 25,
  }
  const totalPenalty = flags.reduce((acc, flag) => acc + (penalties[flag.severity] ?? 5), 0)
  return Math.max(0, 100 - totalPenalty)
}

/**
 * Human-readable label for each flag type.
 */
export const FLAG_TYPE_LABELS: Record<FlagType, string> = {
  face_not_visible: 'Face Not Visible',
  multiple_faces: 'Multiple Faces',
  gaze_deviation: 'Gaze Deviation',
  audio_anomaly: 'Audio Anomaly',
  cv_inconsistency: 'CV Inconsistency',
}

/**
 * Emoji icon for each flag type.
 */
export const FLAG_TYPE_ICONS: Record<FlagType, string> = {
  face_not_visible: '👤',
  multiple_faces: '👥',
  gaze_deviation: '👀',
  audio_anomaly: '🎙️',
  cv_inconsistency: '📄',
}
