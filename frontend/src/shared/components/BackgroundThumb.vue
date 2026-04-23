<script setup lang="ts">
/**
 * BackgroundThumb — miniature static render of one background variant.
 * Used inside FloatingBackgroundPicker's thumbnail tiles.
 *
 * Not a full re-render of the live background — a stylistic approximation
 * that reads well at 36×36. See spec §5.
 */
import type { BackgroundMode } from '@/shared/stores/theme.store'

interface Props {
  kind: Exclude<BackgroundMode, 'off'>
}

defineProps<Props>()
</script>

<template>
  <span class="bg-thumb" :data-kind="kind" aria-hidden="true" />
</template>

<style scoped>
.bg-thumb {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: inherit;
}

.bg-thumb[data-kind='mesh'] {
  background:
    radial-gradient(circle at 25% 30%, #7c5cff 0%, transparent 55%),
    radial-gradient(circle at 70% 40%, #2563eb 0%, transparent 50%),
    radial-gradient(circle at 50% 75%, #ff9b73 0%, transparent 55%);
  filter: blur(3px) saturate(1.3);
}

.bg-thumb[data-kind='constellation'] {
  background:
    radial-gradient(circle at 20% 25%, #7c5cff 0 1.5px, transparent 2px),
    radial-gradient(circle at 70% 20%, #7c5cff 0 1.5px, transparent 2px),
    radial-gradient(circle at 30% 70%, #7c5cff 0 1.5px, transparent 2px),
    radial-gradient(circle at 80% 75%, #7c5cff 0 1.5px, transparent 2px),
    radial-gradient(circle at 50% 50%, #7c5cff 0 1.5px, transparent 2px),
    linear-gradient(to right, transparent 45%, rgba(124, 92, 255, 0.25) 50%, transparent 55%),
    var(--color-surface-raised);
}

.bg-thumb[data-kind='vellum'] {
  background:
    radial-gradient(ellipse at 50% 40%, var(--color-surface-raised), transparent 70%),
    linear-gradient(135deg, var(--color-surface-base), var(--color-surface-sunken));
}

.bg-thumb[data-kind='aurora'] {
  background:
    radial-gradient(ellipse at 30% 20%, #60a5fa 0%, transparent 55%),
    radial-gradient(ellipse at 70% 35%, #c4b5fd 0%, transparent 55%),
    radial-gradient(ellipse at 50% 55%, #fdba74 0%, transparent 55%), var(--color-surface-raised);
  filter: blur(2px) saturate(1.3);
}

.bg-thumb[data-kind='waves'] {
  background:
    linear-gradient(180deg, transparent 50%, rgba(96, 165, 250, 0.35) 55%, transparent 60%),
    linear-gradient(180deg, transparent 65%, rgba(196, 181, 253, 0.35) 72%, transparent 78%),
    linear-gradient(180deg, transparent 80%, rgba(253, 186, 116, 0.35) 88%, transparent 94%),
    var(--color-surface-raised);
  filter: blur(1.5px);
}

.bg-thumb[data-kind='rays'] {
  background:
    conic-gradient(
      from 210deg at 25% 25%,
      transparent 0deg,
      rgba(96, 165, 250, 0.35) 25deg,
      transparent 55deg,
      rgba(196, 181, 253, 0.3) 95deg,
      transparent 135deg,
      rgba(253, 186, 116, 0.25) 180deg,
      transparent 220deg,
      transparent 360deg
    ),
    var(--color-surface-raised);
  filter: blur(2px);
}
</style>
