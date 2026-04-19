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

// Unique gradient id so multiple logos on one page don't collide.
const gradId = `prismGrad-${useId()}`

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
        <linearGradient :id="gradId" x1="14" y1="50" x2="48" y2="14" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#3b5bff" />
          <stop offset="1" stop-color="#7c5cff" />
        </linearGradient>
      </defs>

      <!-- Prism pentagon -->
      <polygon
        class="app-logo__prism"
        points="10,16 32,10 50,16 50,48 32,54 10,48"
        :fill="`url(#${gradId})`"
        stroke-width="1"
        stroke-linejoin="round"
      />

      <!-- Incoming beam (exits left edge) -->
      <line
        class="app-logo__incoming"
        x1="-2"
        y1="32"
        x2="10"
        y2="32"
        stroke="var(--color-text-primary)"
        stroke-opacity="0.7"
        stroke-width="2"
        stroke-linecap="round"
      />

      <!-- Outgoing beams: --beam-final drives the hover-pulse end opacity. -->
      <line
        class="app-logo__beam app-logo__beam--top"
        x1="50"
        y1="22"
        x2="62"
        y2="16"
        stroke="var(--color-accent-celebrate)"
        stroke-width="2.5"
        stroke-linecap="round"
        opacity="1"
        style="--beam-final: 1"
      />
      <line
        class="app-logo__beam app-logo__beam--mid"
        x1="50"
        y1="32"
        x2="62"
        y2="32"
        stroke="var(--color-accent-ai)"
        stroke-width="2"
        stroke-linecap="round"
        opacity="0.7"
        style="--beam-final: 0.7"
      />
      <line
        class="app-logo__beam app-logo__beam--bot"
        x1="50"
        y1="42"
        x2="62"
        y2="48"
        stroke="var(--color-accent)"
        stroke-width="2"
        stroke-linecap="round"
        opacity="0.45"
        style="--beam-final: 0.45"
      />
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
.app-logo__prism {
  stroke: rgba(255, 255, 255, 0.25);
  transform-origin: 32px 32px;
  transform-box: fill-box;
}
/* Dark mode: brighter prism highlight + brighter incoming beam. */
:global(.dark) .app-logo__prism {
  stroke: rgba(255, 255, 255, 0.35);
}
:global(.dark) .app-logo__incoming {
  stroke: rgba(229, 231, 235, 0.8);
  stroke-opacity: 1;
}

/* prettier-ignore */
@media (prefers-reduced-motion: no-preference) {
  .app-logo__glyph { perspective: 400px; }
  .app-logo:hover .app-logo__prism { animation: app-logo-prism-rotate 2s ease-in-out infinite alternate; }
  .app-logo:hover .app-logo__beam { animation: app-logo-beam-pulse 600ms cubic-bezier(0.22, 1, 0.36, 1) both; }
  .app-logo:hover .app-logo__beam--mid { animation-delay: 80ms; }
  .app-logo:hover .app-logo__beam--bot { animation-delay: 160ms; }
  @keyframes app-logo-prism-rotate { from { transform: rotateY(0deg); } to { transform: rotateY(8deg); } }
  @keyframes app-logo-beam-pulse { from { opacity: 0; } to { opacity: var(--beam-final, 1); } }
}

/* prettier-ignore */
@media (prefers-reduced-motion: reduce) {
  .app-logo:hover .app-logo__beam--top { animation: app-logo-beam-flash 300ms ease-out both; }
  @keyframes app-logo-beam-flash { 0% { opacity: 0.4; } 50%, 100% { opacity: 1; } }
}
</style>
