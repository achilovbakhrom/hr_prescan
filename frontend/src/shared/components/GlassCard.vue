<script setup lang="ts">
/**
 * GlassCard — padded glass container with optional title/subtitle/header/footer.
 * Composes `GlassSurface level="1"`.
 *
 * Spec: docs/design/spec.md §5. AI-origin cards (assistant prompts, prescan
 * suggestions) use `accent="ai"`. Celebrate cards (offers, pass confirmations)
 * use `accent="celebrate"`.
 */
import { computed, useSlots } from 'vue'
import GlassSurface from './GlassSurface.vue'

type Accent = 'default' | 'ai' | 'celebrate'

interface Props {
  title?: string
  subtitle?: string
  accent?: Accent
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  accent: 'default',
})

const slots = useSlots()

const hasHeader = computed(() => Boolean(props.title || slots.header))

const cardClass = computed(() => {
  const cls: string[] = ['glass-card', 'relative', 'p-5', 'md:p-6', 'rounded-lg', 'overflow-hidden']
  if (props.accent === 'ai') cls.push('glass-card--ai')
  if (props.accent === 'celebrate') cls.push('glass-card--celebrate')
  return cls
})
</script>

<template>
  <GlassSurface :class="cardClass" level="1">
    <header
      v-if="hasHeader"
      class="relative z-10 pb-3 mb-4 border-b border-[color:var(--color-border-soft)]"
    >
      <slot name="header">
        <h3 v-if="title" class="text-lg font-semibold text-[color:var(--color-text-primary)]">
          {{ title }}
        </h3>
        <p v-if="subtitle" class="mt-1 text-sm text-[color:var(--color-text-secondary)]">
          {{ subtitle }}
        </p>
      </slot>
    </header>

    <div class="relative z-10">
      <slot />
    </div>

    <footer
      v-if="$slots.footer"
      class="relative z-10 pt-3 mt-4 border-t border-[color:var(--color-border-soft)]"
    >
      <slot name="footer" />
    </footer>
  </GlassSurface>
</template>

<style scoped>
/* Accent tint: 1px top border + faint radial glow behind content.
   Glow sits under content via negative z-index and `overflow-hidden` clipping. */
.glass-card--ai {
  border-top: 1px solid var(--color-accent-ai);
}
.glass-card--ai::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background: radial-gradient(ellipse at 20% 0%, var(--color-accent-ai-soft), transparent 55%);
  opacity: 0.7;
}

.glass-card--celebrate {
  border-top: 1px solid var(--color-accent-celebrate);
}
.glass-card--celebrate::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background: radial-gradient(
    ellipse at 80% 0%,
    var(--color-accent-celebrate-soft),
    transparent 55%
  );
  opacity: 0.7;
}
</style>
