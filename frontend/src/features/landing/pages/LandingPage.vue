<script setup lang="ts">
import { useScrollAnimation } from '../composables/useScrollAnimation'
import LandingNav from '../components/LandingNav.vue'
import LandingHero from '../components/LandingHero.vue'
import LandingStats from '../components/LandingStats.vue'
import LandingFeatures from '../components/LandingFeatures.vue'
import LandingPipeline from '../components/LandingPipeline.vue'
import LandingJobs from '../components/LandingJobs.vue'
import LandingCta from '../components/LandingCta.vue'
import LandingFooter from '../components/LandingFooter.vue'

useScrollAnimation()
</script>

<template>
  <div class="relative min-h-screen">
    <LandingNav />
    <LandingHero />
    <LandingStats />
    <LandingFeatures />
    <LandingPipeline />
    <LandingJobs />
    <LandingCta />
    <LandingFooter />
  </div>
</template>

<style>
/* Scroll animation base */
.scroll-animate {
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity 0.6s ease,
    transform 0.6s ease;
}
.scroll-animate.animate-in {
  opacity: 1;
  transform: translateY(0);
}
.scroll-animate-delay-1 {
  transition-delay: 0.1s;
}
.scroll-animate-delay-2 {
  transition-delay: 0.2s;
}
.scroll-animate-delay-3 {
  transition-delay: 0.3s;
}
.scroll-animate-delay-4 {
  transition-delay: 0.4s;
}

/* Floating animation for hero background blobs */
@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(3deg);
  }
}
.animate-float {
  animation: float 6s ease-in-out infinite;
}
.animate-float-delayed {
  animation: float 8s ease-in-out 2s infinite;
}
</style>
