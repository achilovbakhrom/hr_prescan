import { computed } from 'vue'
import type { Ref } from 'vue'
import type { IntegrityFlag, Severity } from '../types/integrity.types'

export function useIntegrityScore(flags: Ref<IntegrityFlag[]>) {
  const integrityScore = computed<number>(() => {
    if (flags.value.length === 0) return 100
    const penalties: Record<Severity, number> = { low: 5, medium: 15, high: 25 }
    const totalPenalty = flags.value.reduce((acc, flag) => acc + (penalties[flag.severity] ?? 5), 0)
    return Math.max(0, 100 - totalPenalty)
  })

  const scoreColor = computed<string>(() => {
    if (integrityScore.value >= 80) return 'text-green-600'
    if (integrityScore.value >= 60) return 'text-yellow-600'
    if (integrityScore.value >= 40) return 'text-orange-600'
    return 'text-red-600'
  })

  const scoreLabel = computed<string>(() => {
    if (integrityScore.value >= 80) return 'good'
    if (integrityScore.value >= 60) return 'fair'
    if (integrityScore.value >= 40) return 'poor'
    return 'critical'
  })

  return { integrityScore, scoreColor, scoreLabel }
}
