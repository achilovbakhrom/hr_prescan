interface EvidenceSource {
  criteriaName: string
  aiNotes?: string
}

const STOP_WORDS = new Set([
  'about',
  'after',
  'also',
  'and',
  'are',
  'based',
  'but',
  'candidate',
  'from',
  'has',
  'have',
  'interview',
  'not',
  'score',
  'shows',
  'that',
  'the',
  'their',
  'this',
  'with',
])

function words(text: string): string[] {
  return text.match(/[\p{L}\p{N}]+/gu) || []
}

function uniqueUsefulWords(text: string, limit: number): string[] {
  const seen = new Set<string>()
  const result: string[] = []

  for (const word of words(text)) {
    const normalized = word.toLowerCase()
    if (normalized.length < 4 || STOP_WORDS.has(normalized) || seen.has(normalized)) continue
    seen.add(normalized)
    result.push(word)
    if (result.length >= limit) break
  }

  return result
}

export function buildEvidenceQuery(source: EvidenceSource): string {
  const criteriaTerms = uniqueUsefulWords(source.criteriaName, 3)
  const noteTerms = uniqueUsefulWords(source.aiNotes || '', 5)
  return [...criteriaTerms, ...noteTerms].slice(0, 6).join(' ')
}
