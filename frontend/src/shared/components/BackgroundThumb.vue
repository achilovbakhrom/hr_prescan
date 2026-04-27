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
    radial-gradient(ellipse at 18% 22%, rgba(37, 99, 235, 0.7), transparent 58%),
    radial-gradient(ellipse at 82% 30%, rgba(20, 184, 166, 0.58), transparent 58%),
    radial-gradient(ellipse at 52% 86%, rgba(244, 114, 182, 0.5), transparent 62%),
    linear-gradient(135deg, rgba(124, 92, 255, 0.28), rgba(253, 186, 116, 0.22));
  filter: blur(2px) saturate(1.25);
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
    linear-gradient(112deg, transparent 0 28%, rgba(255, 255, 255, 0.72) 29% 33%, transparent 34%),
    linear-gradient(112deg, transparent 0 64%, rgba(15, 23, 42, 0.12) 65% 66%, transparent 67%),
    radial-gradient(ellipse at 18% 12%, rgba(59, 130, 246, 0.35), transparent 58%),
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
    linear-gradient(155deg, transparent 30%, rgba(37, 99, 235, 0.42) 31% 34%, transparent 35%),
    linear-gradient(155deg, transparent 50%, rgba(20, 184, 166, 0.36) 51% 54%, transparent 55%),
    linear-gradient(155deg, transparent 68%, rgba(124, 92, 255, 0.32) 69% 72%, transparent 73%),
    var(--color-surface-raised);
  filter: blur(0.6px);
}

.bg-thumb[data-kind='ocean'] {
  background:
    linear-gradient(175deg, rgba(248, 250, 252, 0.58) 0 24%, transparent 25%),
    linear-gradient(160deg, transparent 34%, rgba(20, 184, 166, 0.38) 35% 38%, transparent 39%),
    linear-gradient(160deg, transparent 56%, rgba(14, 165, 233, 0.34) 57% 60%, transparent 61%),
    radial-gradient(ellipse at 34% 62%, rgba(37, 99, 235, 0.48), transparent 52%),
    linear-gradient(180deg, rgba(219, 234, 254, 0.84), rgba(125, 211, 252, 0.42));
  filter: saturate(1.16);
}

.bg-thumb[data-kind='rays'] {
  background:
    repeating-linear-gradient(
      118deg,
      transparent 0 9px,
      rgba(15, 23, 42, 0.12) 10px 11px,
      transparent 12px 21px
    ),
    linear-gradient(118deg, transparent 12%, rgba(37, 99, 235, 0.34) 25%, transparent 38%),
    linear-gradient(118deg, transparent 46%, rgba(20, 184, 166, 0.28) 58%, transparent 72%),
    var(--color-surface-raised);
  filter: blur(0.8px);
}
</style>
