<script setup lang="ts">
/**
 * LandingPage — marketing page composed to match the Figma redesign:
 * Nav → Hero → Logos → How it works → Features → CTA(+Telegram) → Footer.
 *
 * Flat surface with soft radial glows (the Figma ellipses), not the animated
 * mesh — consistent with the flattened app theme.
 */
import { useScrollAnimation } from '../composables/useScrollAnimation'
import LandingNav from '../components/LandingNav.vue'
import LandingHero from '../components/LandingHero.vue'
import LandingLogos from '../components/LandingLogos.vue'
import LandingHowItWorks from '../components/LandingHowItWorks.vue'
import LandingFeatures from '../components/LandingFeatures.vue'
import LandingCta from '../components/LandingCta.vue'
import LandingFooter from '../components/LandingFooter.vue'

useScrollAnimation()
</script>

<template>
  <div class="landing-page relative isolate min-h-screen w-full overflow-x-clip">
    <!-- Background: smooth light lavender wash (Figma), concentrated softly
         in the hero area and fading to near-white below. -->
    <div
      class="pointer-events-none fixed inset-0 -z-10"
      style="
        background:
          radial-gradient(ellipse 70% 50% at 78% 8%, rgba(236, 72, 153, 0.08), transparent 60%),
          radial-gradient(ellipse 90% 60% at 20% -5%, rgba(124, 58, 237, 0.1), transparent 60%),
          linear-gradient(180deg, #f6f4ff 0%, #fbfaff 38%, #ffffff 100%);
      "
    ></div>
    <div
      class="pointer-events-none fixed inset-0 -z-10 hidden dark:block"
      style="
        background:
          radial-gradient(ellipse 80% 50% at 78% 6%, rgba(236, 72, 153, 0.12), transparent 60%),
          radial-gradient(ellipse 90% 60% at 18% -5%, rgba(124, 58, 237, 0.16), transparent 60%),
          linear-gradient(180deg, #0c0a16 0%, #08070f 45%, #07060d 100%);
      "
    ></div>

    <LandingNav />

    <main class="relative z-0 pb-16">
      <LandingHero />
      <LandingLogos />
      <LandingHowItWorks />
      <LandingFeatures />
      <LandingCta />
      <LandingFooter />
    </main>
  </div>
</template>

<style>
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

@media (prefers-reduced-motion: reduce) {
  .scroll-animate {
    transform: none;
    transition: opacity 180ms linear;
  }
}
</style>
