<script setup lang="ts">
/**
 * PageShell — root page wrapper used by AppLayout / PublicLayout.
 * Stacks: AnimatedBackground (fixed, -z-10) → nav slot → main → footer slot
 *         → FloatingBackgroundPicker (fixed).
 *
 * Spec: docs/design/spec.md §5.
 *
 * Wiring this into the existing layouts happens in T10/T12 — this wave just
 * provides the primitive.
 */
import { computed } from 'vue'
import AnimatedBackground from './AnimatedBackground.vue'
import FloatingBackgroundPicker from './FloatingBackgroundPicker.vue'

type Variant = 'app' | 'public'

interface Props {
  variant?: Variant
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'app',
})

const mainClass = computed(() => {
  const base = ['relative', 'z-0', 'min-h-screen']
  if (props.variant === 'public') {
    base.push('mx-auto', 'w-full', 'max-w-6xl', 'px-4', 'sm:px-6', 'lg:px-8', 'py-6')
  } else {
    // App variant: wider gutter on mobile, comfortable desktop padding.
    base.push('px-4', 'sm:px-6', 'lg:px-8', 'py-4', 'sm:py-6')
  }
  return base
})
</script>

<template>
  <div class="relative">
    <!-- Background layer -->
    <AnimatedBackground />

    <!-- Navigation slot: consumers provide their own glass chrome. -->
    <header v-if="$slots.nav">
      <slot name="nav" />
    </header>

    <!-- Main content. Page-level fade transition is handled by the route-
         level `<RouterView v-slot>` in consumers; here we provide a stable
         entrance via `.animate-in` on the first child. Style below still
         exposes `.page-enter-*` classes for any parent-wrapped transition. -->
    <main :class="mainClass">
      <div class="animate-in">
        <slot />
      </div>
    </main>

    <!-- Footer slot (optional) -->
    <footer v-if="$slots.footer">
      <slot name="footer" />
    </footer>

    <!-- Floating controls: background + theme picker. Fixed-positioned, so
         DOM placement here has no visual impact. -->
    <FloatingBackgroundPicker />
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 240ms var(--ease-ios);
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .page-enter-active,
  .page-leave-active {
    transition: opacity 180ms linear;
  }
}
</style>
