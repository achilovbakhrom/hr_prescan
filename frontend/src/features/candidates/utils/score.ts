type ScoreValue = number | string | null | undefined

function toNumber(value: ScoreValue): number | null {
  if (value === null || value === undefined || value === '') return null
  const numberValue = Number(value)
  return Number.isFinite(numberValue) ? numberValue : null
}

export function normalizeScreeningScore(score: ScoreValue): number | null {
  const value = toNumber(score)
  if (value === null) return null
  return Math.round(value > 10 ? value : value * 10)
}

export function calculateOverallScore(scores: {
  cvMatchScore: ScoreValue
  prescanningScore: ScoreValue
  interviewScore: ScoreValue
}): number | null {
  const screeningScores = [
    { value: normalizeScreeningScore(scores.prescanningScore), weight: 30 },
    { value: normalizeScreeningScore(scores.interviewScore), weight: 50 },
  ].filter((item): item is { value: number; weight: number } => item.value !== null)

  if (!screeningScores.length) {
    const cvScore = toNumber(scores.cvMatchScore)
    return cvScore === null ? null : Math.round(cvScore)
  }

  const totalWeight = screeningScores.reduce((sum, item) => sum + item.weight, 0)
  const weightedTotal = screeningScores.reduce((sum, item) => sum + item.value * item.weight, 0)
  return Math.round(weightedTotal / totalWeight)
}
