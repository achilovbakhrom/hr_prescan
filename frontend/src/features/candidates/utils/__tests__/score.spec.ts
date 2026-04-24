import { describe, expect, it } from 'vitest'
import { calculateOverallScore, normalizeScreeningScore } from '../score'

describe('candidate score helpers', () => {
  it('uses screening score for overall when CV score is also present', () => {
    expect(
      calculateOverallScore({
        cvMatchScore: 85,
        prescanningScore: 4,
        interviewScore: null,
      }),
    ).toBe(40)
  })

  it('falls back to CV score only before screening results exist', () => {
    expect(
      calculateOverallScore({
        cvMatchScore: 85,
        prescanningScore: null,
        interviewScore: null,
      }),
    ).toBe(85)
  })

  it('combines prescanning and interview scores without CV duplication', () => {
    expect(
      calculateOverallScore({
        cvMatchScore: 85,
        prescanningScore: 4,
        interviewScore: 8,
      }),
    ).toBe(65)
  })

  it('accepts screening scores already normalized to 100-point scale', () => {
    expect(normalizeScreeningScore(40)).toBe(40)
  })
})
