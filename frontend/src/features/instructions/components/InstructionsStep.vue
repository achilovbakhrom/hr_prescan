<script setup lang="ts">
/**
 * A single numbered step: index badge, title + description, and a real
 * screenshot. The screenshot opens full-size in a new tab on click.
 */
import type { GuideStep } from '../data/guide.types'

const props = defineProps<{
  step: GuideStep
  index: number
}>()

/** Fall back to the English screenshot if the localized one is missing. */
function onImageError(e: Event): void {
  const img = e.target as HTMLImageElement
  if (
    img.src !== location.origin + props.step.imageFallback &&
    !img.src.endsWith(props.step.imageFallback)
  ) {
    img.src = props.step.imageFallback
  }
}
</script>

<template>
  <li class="flex flex-col gap-4 sm:flex-row sm:gap-5">
    <!-- Step number + connector -->
    <div class="flex shrink-0 flex-row items-center gap-3 sm:flex-col sm:items-center">
      <span
        class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white"
        aria-hidden="true"
      >
        {{ index }}
      </span>
      <span class="hidden w-px flex-1 bg-[color:var(--color-border-soft)] sm:block"></span>
    </div>

    <div class="min-w-0 flex-1 pb-8">
      <h3 class="text-base font-semibold text-[color:var(--color-text-primary)]">
        {{ step.title }}
      </h3>
      <p class="mt-1 text-sm leading-relaxed text-[color:var(--color-text-secondary)]">
        {{ step.description }}
      </p>

      <a
        :href="step.image"
        target="_blank"
        rel="noopener"
        class="group mt-4 block overflow-hidden rounded-xl border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-base)] shadow-sm transition-shadow hover:shadow-md"
      >
        <img
          :src="step.image"
          :alt="step.imageAlt"
          loading="lazy"
          class="w-full object-cover transition-transform duration-200 group-hover:scale-[1.01]"
          @error="onImageError"
        />
      </a>
    </div>
  </li>
</template>
