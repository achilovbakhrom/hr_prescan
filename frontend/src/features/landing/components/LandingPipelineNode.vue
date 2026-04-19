<script setup lang="ts">
/**
 * LandingPipelineNode — one step in the 3-step horizontal flow.
 * A big circular glass chip with icon + label + short description.
 *
 * The middle node (index === 1, the AI step) receives a subtle accent pulse
 * ring — this is the product's "hot spot", so it gets emphasis.
 */

const props = defineProps<{
  icon: string
  title: string
  description: string
  index: number
}>()

const isAccented = props.index === 1
</script>

<template>
  <div class="pipeline-node flex flex-col items-center text-center">
    <div
      class="bg-glass-2 border-glass shadow-glass pipeline-chip relative"
      :class="{ 'pipeline-chip--accent': isAccented }"
    >
      <i :class="icon" class="pipeline-chip-icon text-[color:var(--color-accent-ai)]"></i>
      <span class="pipeline-chip-step font-mono">{{ String(index + 1).padStart(2, '0') }}</span>
    </div>
    <h3 class="mt-6 text-lg font-semibold text-[color:var(--color-text-primary)] sm:text-xl">
      {{ title }}
    </h3>
    <p
      class="mt-2 max-w-[240px] text-sm leading-relaxed text-[color:var(--color-text-muted)] sm:text-base"
    >
      {{ description }}
    </p>
  </div>
</template>

<style scoped>
.pipeline-chip {
  width: 112px;
  height: 112px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    transform 320ms var(--ease-ios),
    box-shadow 320ms var(--ease-ios);
}
.pipeline-chip-icon {
  font-size: 2.25rem; /* 36px */
}
.pipeline-chip:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-glass-float);
}

/* Middle-node accent — subtle pulsing ring in AI violet. */
.pipeline-chip--accent {
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--color-accent-ai) 40%, transparent),
    0 0 40px color-mix(in srgb, var(--color-accent-ai) 25%, transparent),
    var(--shadow-glass-1);
  animation: pipeline-accent-pulse 2800ms ease-in-out infinite;
}
@keyframes pipeline-accent-pulse {
  0%,
  100% {
    box-shadow:
      0 0 0 1px color-mix(in srgb, var(--color-accent-ai) 40%, transparent),
      0 0 36px color-mix(in srgb, var(--color-accent-ai) 18%, transparent),
      var(--shadow-glass-1);
  }
  50% {
    box-shadow:
      0 0 0 2px color-mix(in srgb, var(--color-accent-ai) 55%, transparent),
      0 0 56px color-mix(in srgb, var(--color-accent-ai) 35%, transparent),
      var(--shadow-glass-1);
  }
}

.pipeline-chip-step {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  background: var(--color-accent-ai);
  color: var(--color-text-on-accent);
  padding: 4px 9px;
  border-radius: 9999px;
  box-shadow: var(--shadow-card);
}
@media (prefers-reduced-motion: reduce) {
  .pipeline-chip {
    transition: box-shadow 180ms linear;
  }
  .pipeline-chip:hover {
    transform: none;
  }
  .pipeline-chip--accent {
    animation: none;
  }
}
</style>
