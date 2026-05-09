<script setup lang="ts">
/**
 * LandingCatMascot — small decorative cat marker for the hero.
 */
import CuteCatFace from '@/shared/components/CuteCatFace.vue'
</script>

<template>
  <div class="landing-cat-mascot" aria-hidden="true">
    <CuteCatFace class="landing-cat-mascot__svg" />
    <span class="landing-cat-mascot__leaf" />
  </div>
</template>

<style scoped>
.landing-cat-mascot {
  position: absolute;
  top: clamp(5rem, 9vw, 8rem);
  right: clamp(1rem, 5vw, 5rem);
  width: clamp(92px, 9vw, 132px);
  aspect-ratio: 1;
  opacity: 0.96;
  filter: drop-shadow(0 18px 28px rgba(180, 83, 9, 0.14));
  animation: mascot-peek 5.8s ease-in-out infinite;
}

.landing-cat-mascot__svg {
  width: 100%;
  height: 100%;
}

.landing-cat-mascot__leaf {
  position: absolute;
  right: -2%;
  bottom: 16%;
  width: 20%;
  height: 13%;
  border-radius: 100% 0 100% 0;
  background: rgba(74, 222, 128, 0.58);
  transform: rotate(-12deg);
}

@keyframes mascot-peek {
  0%,
  100% {
    transform: translateY(4px) rotate(-1deg);
  }
  50% {
    transform: translateY(-5px) rotate(1deg);
  }
}

@media (max-width: 1023px) {
  .landing-cat-mascot {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .landing-cat-mascot {
    animation: none;
  }
}
</style>
