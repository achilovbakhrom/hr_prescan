// Line-art SVG path data for AnimatedBackground animals.
// Each animal is drawn inside a 100x100 viewBox using `currentColor` stroke so
// it can be tinted via Tailwind text utilities. Paths are intentionally sparse
// (minimal line-art) and meant to feel like sketched illustrations.

export interface AnimalArt {
  id: string
  viewBox: string
  paths: string[]
}

export const FOX: AnimalArt = {
  id: 'fox',
  viewBox: '0 0 100 100',
  paths: [
    'M20 40 L50 20 L80 40 L70 60 L50 68 L30 60 Z',
    'M20 40 L18 22 L34 30',
    'M80 40 L82 22 L66 30',
    'M44 52 L50 60 L56 52',
    'M38 44 L42 44',
    'M58 44 L62 44',
    'M48 56 L52 56',
    'M72 60 Q92 58 88 38',
  ],
}

export const OWL: AnimalArt = {
  id: 'owl',
  viewBox: '0 0 100 100',
  paths: [
    'M30 30 Q30 14 50 14 Q70 14 70 30 L72 70 Q50 88 28 70 Z',
    'M36 36 A7 7 0 1 0 50 36 A7 7 0 1 0 36 36',
    'M50 36 A7 7 0 1 0 64 36 A7 7 0 1 0 50 36',
    'M43 36 L43.5 36',
    'M57 36 L57.5 36',
    'M47 44 L50 52 L53 44 Z',
    'M36 54 Q42 68 36 78',
    'M64 54 Q58 68 64 78',
    'M44 84 L44 90',
    'M56 84 L56 90',
    'M32 20 L28 10',
    'M68 20 L72 10',
  ],
}

export const DEER: AnimalArt = {
  id: 'deer',
  viewBox: '0 0 100 100',
  paths: [
    'M28 58 Q28 46 44 46 L66 46 Q78 46 78 58 L78 72 L70 72 L70 62 L40 62 L40 72 L32 72 Z',
    'M66 46 L72 30 Q80 22 82 16',
    'M82 16 L88 24 L80 28',
    'M80 16 L84 6',
    'M80 16 L74 8',
    'M84 6 L90 4',
    'M74 8 L70 2',
    'M80 22 L81 22',
    'M34 72 L34 82',
    'M44 72 L44 82',
    'M64 72 L64 82',
    'M74 72 L74 82',
    'M28 52 L22 50',
  ],
}

export const JELLYFISH: AnimalArt = {
  id: 'jellyfish',
  viewBox: '0 0 100 100',
  paths: [
    'M20 42 Q20 18 50 18 Q80 18 80 42 L78 48 Q50 44 22 48 Z',
    'M32 36 Q50 28 68 36',
    'M28 48 Q26 60 30 72 Q28 82 32 92',
    'M40 50 Q38 64 42 76 Q40 86 44 94',
    'M52 50 Q50 64 54 76 Q52 86 56 94',
    'M64 50 Q62 62 66 74 Q64 84 68 92',
    'M74 48 Q72 58 76 70',
  ],
}

export const WHALE: AnimalArt = {
  id: 'whale',
  viewBox: '0 0 100 100',
  paths: [
    'M12 58 Q20 38 50 40 Q80 42 86 54 L94 48 L90 62 L94 72 L84 66 Q70 78 48 76 Q20 76 12 58 Z',
    'M18 60 Q36 66 58 62',
    'M32 54 L33 54',
    'M52 66 Q58 74 66 72',
    'M40 40 Q38 30 42 22',
    'M40 40 Q44 32 48 28',
  ],
}

export const TURTLE: AnimalArt = {
  id: 'turtle',
  viewBox: '0 0 100 100',
  paths: [
    'M22 56 Q22 34 50 34 Q78 34 78 56 Q78 66 50 66 Q22 66 22 56 Z',
    'M36 44 L44 50 L40 60',
    'M50 40 L50 60',
    'M64 44 L56 50 L60 60',
    'M78 54 Q88 54 88 48 Q88 42 80 42',
    'M84 48 L85 48',
    'M30 62 Q24 72 34 74',
    'M68 64 Q74 72 66 76',
    'M22 54 L14 54',
  ],
}

export const BUBBLE: AnimalArt = {
  id: 'bubble',
  viewBox: '0 0 100 100',
  paths: [
    'M50 50 A38 38 0 1 0 50 49.99',
    'M34 34 Q42 28 50 32',
  ],
}

export const LEAF: AnimalArt = {
  id: 'leaf',
  viewBox: '0 0 100 100',
  paths: [
    'M18 78 Q30 30 82 22 Q74 70 22 82 Z',
    'M26 74 Q50 50 76 28',
    'M36 66 L48 58',
    'M46 62 L56 54',
    'M56 58 L64 48',
  ],
}

export const ANIMAL_MAP: Record<string, AnimalArt> = {
  fox: FOX,
  owl: OWL,
  deer: DEER,
  jellyfish: JELLYFISH,
  whale: WHALE,
  turtle: TURTLE,
  bubble: BUBBLE,
  leaf: LEAF,
}
