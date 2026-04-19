<script setup lang="ts">
/**
 * ErrorShell — shared chrome for 403 / 404 / 500 error pages.
 *
 * Error routes live OUTSIDE PublicLayout/AppLayout in the router
 * (catch-all must be last), so this shell provides its own PageShell
 * to render AnimatedBackground + FloatingBackgroundPicker.
 *
 * Each error page forces its own background variant on mount
 * (spec §9): 404 → Vellum, 403 → Vellum, 500 → Mesh.
 *
 * Layout: full-bleed background + centered GlassCard with big Prism
 * glyph, display-scale error number, one-line message + single CTA.
 */
import { onMounted } from 'vue'
import PageShell from '@/shared/components/PageShell.vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import { useThemeStore, type BackgroundMode } from '@/shared/stores/theme.store'

const props = defineProps<{
  /** Which background to force on mount. */
  background: Extract<BackgroundMode, 'mesh' | 'vellum'>
  /** Big number (e.g. "404"). */
  code: string
}>()

const themeStore = useThemeStore()

onMounted(() => {
  if (themeStore.backgroundMode !== props.background) {
    themeStore.setBackgroundMode(props.background)
  }
})
</script>

<template>
  <PageShell variant="public">
    <div class="flex min-h-[80vh] items-center justify-center px-4 py-16">
      <!-- error-wrap owns the ambient glow, outside GlassCard's overflow-hidden. -->
      <div class="error-wrap relative w-full max-w-md">
        <GlassCard class="relative z-10">
          <div class="flex flex-col items-center text-center">
            <AppLogo variant="glyph" size="lg" :linked="false" class="mb-4" />

            <p class="text-display font-mono tracking-tight text-[color:var(--color-text-primary)]">
              {{ code }}
            </p>

            <slot name="title" />
            <slot name="description" />

            <div class="mt-8 flex w-full flex-col gap-3 sm:flex-row sm:justify-center">
              <slot name="actions" />
            </div>

            <div v-if="$slots.footer" class="mt-10 text-xs text-[color:var(--color-text-muted)]">
              <slot name="footer" />
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  </PageShell>
</template>

<style scoped>
/* Ambient glow BEHIND the card so the card pops against the animated
   background. Positioned on the outer wrapper — NOT inside GlassCard —
   because GlassCard uses `overflow-hidden` which would clip the glow. */
.error-wrap::before {
  content: '';
  position: absolute;
  inset: -20px -30px;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse at 30% 0%, var(--color-accent-ai-soft), transparent 60%),
    radial-gradient(ellipse at 70% 100%, var(--color-accent-celebrate-soft), transparent 60%);
  opacity: 0.55;
  filter: blur(32px);
}

:global(.dark .error-wrap::before) {
  opacity: 0.8;
}

@media (prefers-reduced-motion: reduce) {
  .error-wrap::before {
    opacity: 0.35;
    filter: none;
  }
}
</style>
