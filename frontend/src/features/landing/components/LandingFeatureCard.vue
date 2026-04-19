<script setup lang="ts">
/**
 * LandingFeatureCard — a single feature tile used by LandingFeatures.
 * Composes GlassCard. Exposed as a sub-component to keep the parent small
 * and to make the hoverLift / accent styling easy to isolate.
 */
import GlassCard from '@/shared/components/GlassCard.vue'

defineProps<{
  icon: string
  title: string
  description: string
  accent?: 'ai' | 'celebrate' | 'accent'
}>()
</script>

<template>
  <GlassCard class="feature-card h-full">
    <div
      class="feature-icon mb-6 flex h-14 w-14 items-center justify-center rounded-full"
      :class="{
        'bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]':
          accent === 'ai',
        'bg-[color:var(--color-accent-celebrate-soft)] text-[color:var(--color-accent-celebrate)]':
          accent === 'celebrate',
        'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]':
          accent === 'accent' || !accent,
      }"
    >
      <i :class="icon" class="text-2xl"></i>
    </div>
    <h3 class="mb-2 text-lg font-semibold text-[color:var(--color-text-primary)]">
      {{ title }}
    </h3>
    <p class="text-sm leading-relaxed text-[color:var(--color-text-secondary)]">
      {{ description }}
    </p>
  </GlassCard>
</template>

<style scoped>
.feature-card {
  transition:
    transform 240ms var(--ease-ios),
    box-shadow 240ms var(--ease-ios);
}
.feature-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-glass-float);
}
@media (prefers-reduced-motion: reduce) {
  .feature-card {
    transition: box-shadow 180ms linear;
  }
  .feature-card:hover {
    transform: none;
  }
}
</style>
