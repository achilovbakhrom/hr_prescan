/**
 * Deterministic node layout + nearest-neighbor linking for BackgroundConstellation.
 * Pure + computed once at module load; kept out of the .vue file so the component
 * stays under the 200-line limit.
 */

export interface ConstellationNode {
  x: number
  y: number
}

export interface ConstellationLine {
  x1: number
  y1: number
  x2: number
  y2: number
}

/** Tiny deterministic PRNG (mulberry32) so layout is stable across reloads. */
function mulberry32(seed: number): () => number {
  let a = seed
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function buildNodes(): ConstellationNode[] {
  const rand = mulberry32(0xc0ffee)
  const nodes: ConstellationNode[] = []
  const step = 1000 / 7 // 6x6 grid inside viewBox 0..1000
  for (let row = 0; row < 6; row++) {
    for (let col = 0; col < 6; col++) {
      // Skip 4 corners so we end up with 32 nodes (≤40 cap).
      const isCorner =
        (row === 0 && col === 0) ||
        (row === 0 && col === 5) ||
        (row === 5 && col === 0) ||
        (row === 5 && col === 5)
      if (isCorner) continue
      const cx = (col + 1) * step
      const cy = (row + 1) * step
      const jitterX = (rand() - 0.5) * step * 0.6
      const jitterY = (rand() - 0.5) * step * 0.6
      nodes.push({ x: cx + jitterX, y: cy + jitterY })
    }
  }
  return nodes
}

function buildLines(nodes: ConstellationNode[]): ConstellationLine[] {
  const out: ConstellationLine[] = []
  const seen = new Set<string>()
  for (let i = 0; i < nodes.length; i++) {
    const dists = nodes
      .map((n, j) => ({ j, d: (n.x - nodes[i].x) ** 2 + (n.y - nodes[i].y) ** 2 }))
      .filter((e) => e.j !== i)
      .sort((a, b) => a.d - b.d)
      .slice(0, 2)
    for (const { j } of dists) {
      const key = i < j ? `${i}-${j}` : `${j}-${i}`
      if (seen.has(key)) continue
      seen.add(key)
      out.push({ x1: nodes[i].x, y1: nodes[i].y, x2: nodes[j].x, y2: nodes[j].y })
    }
  }
  return out
}

// Computed once at module load — identical on every mount, zero flicker.
export const CONSTELLATION_NODES: readonly ConstellationNode[] = buildNodes()
export const CONSTELLATION_LINES: readonly ConstellationLine[] = buildLines(
  CONSTELLATION_NODES.slice(),
)
