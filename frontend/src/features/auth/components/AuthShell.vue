<script setup lang="ts">
/**
 * AuthShell — shared chrome for every auth page.
 *
 * Forces the background to Vellum on mount (calm, focused vibe per spec §9),
 * renders the Prism glyph, optional title + subtitle, and a centered
 * GlassCard that holds the form. Width is configurable:
 *   - 'md'  (max-w-md) for login / register / verify / accept-invitation
 *   - 'lg'  (max-w-lg) for choose-role
 *   - '2xl' (max-w-2xl) for company-setup wizard
 *
 * Spec: docs/design/spec.md §9 ("Auth" row).
 */
import { onMounted } from 'vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import { useThemeStore } from '@/shared/stores/theme.store'

type Width = 'md' | 'lg' | '2xl'

withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
    width?: Width
  }>(),
  {
    title: '',
    subtitle: '',
    width: 'md',
  },
)

const themeStore = useThemeStore()

// Auth is short-lived; force Vellum on mount (spec §9).
onMounted(() => {
  if (themeStore.backgroundMode !== 'vellum') {
    themeStore.setBackgroundMode('vellum')
  }
})

const widthClass: Record<Width, string> = {
  md: 'max-w-md',
  lg: 'max-w-lg',
  '2xl': 'max-w-2xl',
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center px-4 py-10 sm:py-12">
    <!-- auth-wrap owns the ambient glow. It sits OUTSIDE GlassCard
         because GlassCard has `overflow-hidden` which clips any ::after. -->
    <div class="auth-wrap relative w-full" :class="widthClass[width]">
      <!-- Prism glyph atop the card for brand presence -->
      <div class="relative z-10 mb-6 flex justify-center">
        <AppLogo variant="glyph" size="lg" :linked="false" />
      </div>

      <GlassCard class="relative z-10">
        <div v-if="title || subtitle || $slots.header" class="mb-6 text-center">
          <slot name="header">
            <h1
              v-if="title"
              class="text-xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-2xl"
            >
              {{ title }}
            </h1>
            <p v-if="subtitle" class="mt-2 text-sm text-[color:var(--color-text-secondary)]">
              {{ subtitle }}
            </p>
          </slot>
        </div>

        <slot />

        <footer
          v-if="$slots.footer"
          class="mt-6 text-center text-sm text-[color:var(--color-text-secondary)]"
        >
          <slot name="footer" />
        </footer>
      </GlassCard>
    </div>
  </div>
</template>

<style scoped>
/* Ambient glow BEHIND the card so the card pops against Vellum.
   Positioned on the outer wrapper — NOT inside GlassCard — because
   GlassCard uses `overflow-hidden` which would clip the glow. */
.auth-wrap::before {
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

/* Dark mode: stronger glow so the card reads against near-black Vellum. */
:global(.dark .auth-wrap::before) {
  opacity: 0.8;
}

@media (prefers-reduced-motion: reduce) {
  .auth-wrap::before {
    opacity: 0.35;
    filter: none;
  }
}
</style>
