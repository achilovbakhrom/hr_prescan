<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: 'sm' | 'md' | 'lg'
    /** When true (default), the logo is a link to `/`. Set false for decorative use. */
    linked?: boolean
    /** Override the destination route (defaults to `/`). */
    to?: string
    /** Which pieces to render. `full` = glyph + wordmark, `glyph` = mark only, `wordmark` = text only. */
    variant?: 'full' | 'glyph' | 'wordmark'
  }>(),
  {
    size: 'sm',
    linked: true,
    to: '/',
    variant: 'full',
  },
)

// Glyph sizes are tuned to read clearly in a 64-viewbox. Wordmark scales alongside.
const sizeMap = {
  sm: { svg: 28, wordmark: 'text-base' },
  md: { svg: 36, wordmark: 'text-lg' },
  lg: { svg: 48, wordmark: 'text-2xl' },
} as const

const dims = computed(() => sizeMap[props.size])

// Unique id so multiple logos on one page don't collide.
const gradId = `sparkGrad-${useId()}`

const showGlyph = computed(() => props.variant !== 'wordmark')
const showWordmark = computed(() => props.variant !== 'glyph')
</script>

<template>
  <component
    :is="linked ? 'RouterLink' : 'div'"
    :to="linked ? to : undefined"
    class="app-logo inline-flex items-center gap-2"
    aria-label="HR PreScan"
  >
    <svg
      v-if="showGlyph"
      class="app-logo__glyph"
      :width="dims.svg"
      :height="dims.svg"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <!-- Tile gradient: blue → indigo → violet, kept tighter than the reference -->
        <linearGradient :id="gradId" x1="8" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#4f8bff" />
          <stop offset="0.55" stop-color="#6d5cff" />
          <stop offset="1" stop-color="#a855f7" />
        </linearGradient>
      </defs>

      <!-- Flat rounded-square tile -->
      <rect x="4" y="4" width="56" height="56" rx="14" :fill="`url(#${gradId})`" />

      <!-- Scan-pulse glyph: a focal dot with three concentric arcs emanating
           outward — evokes sonar / signal / pre-screening scan. All line-drawn. -->
      <g
        fill="none"
        stroke="#ffffff"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <!-- Focal point -->
        <circle cx="20" cy="44" r="3.2" fill="#ffffff" stroke="none" />
        <!-- Innermost pulse -->
        <path class="app-logo__arc app-logo__arc--1" stroke-width="3.4"
          d="M20 34 A10 10 0 0 1 30 44" />
        <!-- Middle pulse -->
        <path class="app-logo__arc app-logo__arc--2" stroke-width="3.4"
          d="M20 26 A18 18 0 0 1 38 44" opacity="0.75" />
        <!-- Outer pulse -->
        <path class="app-logo__arc app-logo__arc--3" stroke-width="3.4"
          d="M20 18 A26 26 0 0 1 46 44" opacity="0.5" />
      </g>
    </svg>

    <span
      v-if="showWordmark"
      class="app-logo__wordmark font-semibold tracking-tight"
      :class="dims.wordmark"
    >
      HR PreScan
    </span>
  </component>
</template>

<style scoped>
.app-logo {
  color: var(--color-text-primary);
  text-decoration: none;
}
.app-logo__wordmark {
  color: var(--color-text-primary);
  line-height: 1;
}
/* prettier-ignore */
@media (prefers-reduced-motion: no-preference) {
  .app-logo__arc { transition: opacity 220ms ease-out, transform 420ms cubic-bezier(0.22, 1, 0.36, 1); transform-origin: 20px 44px; transform-box: view-box; }
  .app-logo:hover .app-logo__arc--1 { opacity: 1; }
  .app-logo:hover .app-logo__arc--2 { opacity: 1; transition-delay: 60ms; }
  .app-logo:hover .app-logo__arc--3 { opacity: 1; transition-delay: 120ms; }
}
</style>
