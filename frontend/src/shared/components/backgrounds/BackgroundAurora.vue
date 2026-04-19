<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/shared/stores/theme.store'

/**
 * BackgroundAurora — default variant.
 * Three large blurred conic-gradient ribbons on coprime pan loops (45s/55s/65s).
 * Reduced-motion: single static dual-radial-gradient fallback.
 */

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.resolvedDark)
</script>

<template>
  <div
    aria-hidden="true"
    class="aurora-root pointer-events-none absolute inset-0 -z-10 overflow-hidden"
    :class="isDark ? 'aurora-dark' : 'aurora-light'"
  >
    <!-- Animated ribbons / orbs. Dark uses 6 orbs spread vertically through
         the full document so atmosphere reads during the whole scroll. -->
    <div class="aurora-ribbon aurora-ribbon--1" />
    <div class="aurora-ribbon aurora-ribbon--2" />
    <div class="aurora-ribbon aurora-ribbon--3" />
    <div class="aurora-ribbon aurora-ribbon--4 aurora-dark-only" />
    <div class="aurora-ribbon aurora-ribbon--5 aurora-dark-only" />
    <div class="aurora-ribbon aurora-ribbon--6 aurora-dark-only" />

    <!-- Static fallback used by @media (prefers-reduced-motion: reduce) -->
    <div class="aurora-fallback" />
  </div>
</template>

<style scoped>
.aurora-root {
  /* Isolate so blurred ribbons don't leak over app chrome. */
  isolation: isolate;
  /* Full scrollable document height — orbs spread through the page so
     atmosphere is visible throughout (also works under static fullPage
     screenshot where `position: fixed` only renders the initial viewport). */
  min-height: 100%;
}
/* Dark-mode-only orbs: hidden in light mode. */
.aurora-light .aurora-dark-only {
  display: none;
}

.aurora-ribbon {
  position: absolute;
  top: -25vh;
  left: -25vw;
  width: 150vw;
  height: 150vh;
  filter: blur(var(--blur-xl));
  will-change: transform, opacity;
  transform-origin: 50% 50%;
  mix-blend-mode: normal;
}

/* -------- Light-mode ribbon gradients -------- */
.aurora-light .aurora-ribbon--1 {
  background: conic-gradient(from 0deg at 50% 50%, #cfd9ff, #e4d4ff, #ffe0cf, #cfd9ff);
  opacity: 0.5;
  animation: aurora-pan-1 45s linear infinite;
}
.aurora-light .aurora-ribbon--2 {
  background: conic-gradient(from 90deg at 50% 50%, #d6ebff, transparent, #e9d5ff, #d6ebff);
  opacity: 0.5;
  animation: aurora-pan-2 55s linear infinite;
}
.aurora-light .aurora-ribbon--3 {
  background: conic-gradient(from 180deg at 50% 50%, #fff5e6, transparent, #dbeafe, #fff5e6);
  opacity: 0.5;
  animation: aurora-pan-3 65s linear infinite;
}

/* -------- Dark-mode: use three glowing radial orbs instead of conic ribbons --------
   Conic ribbons lose vibrancy under blur on a dark base — the gradient
   sweeps cancel out visually. Radial orbs at large scale + high opacity,
   positioned at different viewport corners, read as real glowing
   atmosphere. Each orb has a saturated center that fades to transparent,
   so they naturally layer without muddying. */
.aurora-dark .aurora-ribbon {
  /* Sizing: orbs extend well past viewport edges so they feel ambient
     rather than circular. Centered-off-screen by the pan keyframe. */
  width: 120vw;
  height: 120vh;
  filter: blur(var(--blur-xl));
  opacity: 1;
}
/* 6 orbs spread vertically through the document. Each orb is a large
   blurred radial gradient. Colors rotate violet → blue → fuchsia so the
   whole page reads as one cohesive atmosphere. */
.aurora-dark .aurora-ribbon--1 {
  /* Hero: deep violet glow, upper-left */
  background: radial-gradient(
    circle at 50% 50%,
    #a855f7 0%,
    #7c3aed 25%,
    rgba(124, 58, 237, 0.35) 50%,
    transparent 70%
  );
  top: -40vh;
  left: -30vw;
  animation: aurora-pan-1 45s ease-in-out infinite alternate;
}
.aurora-dark .aurora-ribbon--2 {
  /* Under-hero: cool blue, mid-right */
  background: radial-gradient(
    circle at 50% 50%,
    #3b82f6 0%,
    #1d4ed8 25%,
    rgba(29, 78, 216, 0.3) 50%,
    transparent 70%
  );
  top: 30vh;
  left: 35vw;
  animation: aurora-pan-2 55s ease-in-out infinite alternate;
}
.aurora-dark .aurora-ribbon--3 {
  /* Around stats: warm fuchsia accent, right edge */
  background: radial-gradient(
    circle at 50% 50%,
    #ec4899 0%,
    #be185d 25%,
    rgba(190, 24, 93, 0.25) 50%,
    transparent 70%
  );
  top: 60vh;
  left: 50vw;
  animation: aurora-pan-3 65s ease-in-out infinite alternate;
}
.aurora-dark .aurora-ribbon--4 {
  /* Features band: another violet, left side */
  background: radial-gradient(
    circle at 50% 50%,
    #8b5cf6 0%,
    #6d28d9 25%,
    rgba(109, 40, 217, 0.32) 50%,
    transparent 70%
  );
  top: 120vh;
  left: -20vw;
  animation: aurora-pan-1 58s ease-in-out infinite alternate;
}
.aurora-dark .aurora-ribbon--5 {
  /* Pipeline band: cyan/teal, right */
  background: radial-gradient(
    circle at 50% 50%,
    #22d3ee 0%,
    #0891b2 25%,
    rgba(8, 145, 178, 0.28) 50%,
    transparent 70%
  );
  top: 180vh;
  left: 40vw;
  animation: aurora-pan-2 72s ease-in-out infinite alternate;
}
.aurora-dark .aurora-ribbon--6 {
  /* CTA band: rose, center */
  background: radial-gradient(
    circle at 50% 50%,
    #f472b6 0%,
    #db2777 25%,
    rgba(219, 39, 119, 0.24) 50%,
    transparent 70%
  );
  top: 240vh;
  left: 10vw;
  animation: aurora-pan-3 80s ease-in-out infinite alternate;
}

/* Three coprime pans — translate + rotate around the viewport so loop boundary never aligns. */
@keyframes aurora-pan-1 {
  0% {
    transform: translate(-4%, -3%) rotate(0deg);
  }
  50% {
    transform: translate(4%, 3%) rotate(180deg);
  }
  100% {
    transform: translate(-4%, -3%) rotate(360deg);
  }
}
@keyframes aurora-pan-2 {
  0% {
    transform: translate(3%, -4%) rotate(0deg);
  }
  50% {
    transform: translate(-3%, 4%) rotate(-180deg);
  }
  100% {
    transform: translate(3%, -4%) rotate(-360deg);
  }
}
@keyframes aurora-pan-3 {
  0% {
    transform: translate(-3%, 4%) rotate(0deg);
  }
  50% {
    transform: translate(3%, -4%) rotate(180deg);
  }
  100% {
    transform: translate(-3%, 4%) rotate(360deg);
  }
}

/* Static fallback — hidden unless reduced motion is requested. */
.aurora-fallback {
  position: absolute;
  inset: 0;
  opacity: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse at 30% 20%, var(--color-accent-ai-soft), transparent 60%),
    radial-gradient(ellipse at 70% 80%, var(--color-accent-soft), transparent 60%);
}

@media (prefers-reduced-motion: reduce) {
  .aurora-ribbon {
    display: none;
  }
  .aurora-fallback {
    opacity: 1;
  }
}
</style>
