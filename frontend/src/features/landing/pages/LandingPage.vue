<script setup lang="ts">
/**
 * LandingPage — composes the 8 redesigned marketing sections.
 *
 * The landing route is registered outside of PublicLayout (see
 * `frontend/src/app/router.ts`), so this page provides its own PageShell
 * wrapper to get AnimatedBackground + FloatingBackgroundPicker. It also
 * pins the background to Vellum (the signature mood for marketing) unless
 * the user has explicitly picked a different variant via the picker.
 */
import AnimatedBackground from '@/shared/components/AnimatedBackground.vue'
import FloatingBackgroundPicker from '@/shared/components/FloatingBackgroundPicker.vue'
import { useScrollAnimation } from '../composables/useScrollAnimation'
import LandingNav from '../components/LandingNav.vue'
import LandingHero from '../components/LandingHero.vue'
import LandingStats from '../components/LandingStats.vue'
import LandingFeatures from '../components/LandingFeatures.vue'
import LandingPipeline from '../components/LandingPipeline.vue'
import LandingCta from '../components/LandingCta.vue'
import LandingFooter from '../components/LandingFooter.vue'
// LandingJobs is temporarily unmounted — see docs/design/spec.md §9. Restore
// once a public /api/public/vacancies endpoint is wired up with real data.

useScrollAnimation()

// The user's background choice from the FloatingBackgroundPicker is honored —
// we no longer force the landing page to a specific variant on mount. The
// global default lives in `theme.store.readBackground()` for first-time
// visitors.
</script>

<template>
  <!-- Page root is transparent so the Vellum (fixed, behind `main`) bleeds
       through every scroll section. Each section is also bg-transparent and
       stacks its content inside GlassCard / GlassSurface — the "floating
       islands on atmosphere" pattern from spec §9. -->
  <div class="landing-page relative min-h-screen bg-transparent">
    <!-- Background layer (fixed, full-bleed) -->
    <AnimatedBackground />

    <!-- Sticky translucent header -->
    <LandingNav />

    <!-- Main scroll column -->
    <main class="relative z-0 bg-transparent pb-24 md:pb-12">
      <LandingHero />
      <LandingStats />
      <LandingFeatures />
      <LandingPipeline />
      <LandingCta />
      <LandingFooter />
    </main>

    <!-- Floating chrome — background + theme picker -->
    <FloatingBackgroundPicker />
  </div>
</template>

<style>
/* Entrance + scroll reveal shared classes. Kept global so child sections can
   reference them without <style scoped> barriers. */
/* Default = fully visible. The first-mount opacity/translate was invisible
   under static screenshot/slow-load paths when IntersectionObserver hadn't
   fired yet. Entrance animation now only plays if we explicitly start it
   from a below-fold mount. */
.scroll-animate {
  opacity: 1;
  transform: none;
  transition:
    opacity 520ms var(--ease-ios),
    transform 520ms var(--ease-ios);
}
.scroll-animate.animate-in {
  opacity: 1;
  transform: translateY(0);
}
.scroll-animate-delay-1 {
  transition-delay: 80ms;
}
.scroll-animate-delay-2 {
  transition-delay: 160ms;
}
.scroll-animate-delay-3 {
  transition-delay: 240ms;
}
.scroll-animate-delay-4 {
  transition-delay: 320ms;
}

@media (prefers-reduced-motion: reduce) {
  .scroll-animate {
    transform: none;
    transition: opacity 180ms linear;
  }
}
</style>
