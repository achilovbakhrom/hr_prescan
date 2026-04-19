<script setup lang="ts">
/**
 * GlassSurface — base translucent primitive.
 * Every glass-styled element in the app (cards, popovers, floating chrome,
 * etc.) should either compose this component or mirror its class contract.
 *
 * Spec: docs/design/spec.md §5.
 */
import { computed } from 'vue'

type Level = '1' | '2' | 'float'

interface Props {
  /** Translucency level. `float` is for dialogs/toasts/floating chrome. */
  level?: Level
  /** Rendered tag. Defaults to `div`. Use `'button'`, `'section'`, etc. */
  as?: string
  /** Adds hover-lift + cursor-pointer + focus-visible ring. */
  interactive?: boolean
  /** Drop the 1px glass border (for chips that sit inside other glass). */
  noBorder?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  level: '1',
  as: 'div',
  interactive: false,
  noBorder: false,
})

const surfaceClasses = computed(() => {
  const cls: string[] = ['rounded-md']

  // Level → bg + shadow
  if (props.level === 'float') {
    cls.push('bg-glass-float', 'shadow-glass-float')
  } else if (props.level === '2') {
    cls.push('bg-glass-2', 'shadow-glass')
  } else {
    cls.push('bg-glass-1', 'shadow-glass')
  }

  if (!props.noBorder) cls.push('border-glass')

  if (props.interactive) {
    cls.push(
      'cursor-pointer',
      'transition-transform',
      'duration-[240ms]',
      'ease-ios',
      'motion-safe:hover:-translate-y-px',
      'active:translate-y-0',
      'glass-surface-interactive',
    )
  }

  return cls
})
</script>

<template>
  <component :is="as" :class="surfaceClasses">
    <slot />
  </component>
</template>

<style scoped>
/* Focus-visible ring for interactive surfaces. We can't express
   `:focus-visible` via Tailwind utilities on an arbitrary `as` tag cleanly,
   so a scoped selector keeps the contract on this component. */
.glass-surface-interactive:focus-visible {
  outline: 2px solid var(--color-border-ring);
  outline-offset: 2px;
}
</style>
