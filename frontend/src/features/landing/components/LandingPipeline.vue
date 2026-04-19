<script setup lang="ts">
/**
 * LandingPipeline — animated 3-step horizontal flow: Apply → Prescreen → Interview.
 * Connector lines use a gradient in --color-accent-ai that draws on scroll-in
 * via CSS `stroke-dashoffset`. Mobile stacks vertically with short connectors.
 * Reduced-motion: lines fade in, no drawing animation.
 */
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import LandingPipelineNode from './LandingPipelineNode.vue'

const { t } = useI18n()

interface Step {
  icon: string
  title: string
  description: string
}

const steps = computed<Step[]>(() => [
  {
    icon: 'pi pi-send',
    title: t('landing.pipeline.step1'),
    description: t('landing.pipeline.step1Desc'),
  },
  {
    icon: 'pi pi-sparkles',
    title: t('landing.pipeline.step2'),
    description: t('landing.pipeline.step2Desc'),
  },
  {
    icon: 'pi pi-video',
    title: t('landing.pipeline.step3'),
    description: t('landing.pipeline.step3Desc'),
  },
])

// Draw the line on mount (with a small tick so the initial CSS state still
// renders and the transition plays). Default-true ensures the line is always
// visible under static/screenshot/reduced-motion paths.
const inView = ref(true)
onMounted(() => {
  inView.value = false
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      inView.value = true
    })
  })
})
</script>

<template>
  <section id="how-it-works" class="px-4 py-24 sm:px-6 md:py-32">
    <div class="mx-auto max-w-6xl">
      <div class="scroll-animate mb-16 text-center sm:mb-20">
        <h2
          class="mb-4 text-4xl font-semibold tracking-tight text-[color:var(--color-text-primary)] md:text-5xl"
        >
          {{ t('landing.howItWorks.title') }}
        </h2>
        <p
          class="mx-auto max-w-xl text-base leading-relaxed text-[color:var(--color-text-secondary)] md:text-lg"
        >
          {{ t('landing.pipeline.subtitle') }}
        </p>
      </div>

      <!-- Desktop: 3 nodes in a row, connector lines between.
           Connector sits at top = 56px (center of the 112px chip). -->
      <div class="hidden lg:block">
        <div class="relative flex items-start justify-between gap-8">
          <!-- Connector layer (absolute, behind nodes) -->
          <div
            class="pointer-events-none absolute inset-x-0 top-[54px] flex items-center px-[160px]"
          >
            <svg
              class="pipeline-svg w-full"
              :class="{ 'is-drawn': inView }"
              height="6"
              viewBox="0 0 1000 6"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <defs>
                <linearGradient id="pipelineGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0" stop-color="var(--color-accent-ai)" stop-opacity="0" />
                  <stop offset="0.08" stop-color="var(--color-accent-ai)" stop-opacity="0.95" />
                  <stop offset="0.92" stop-color="var(--color-accent-ai)" stop-opacity="0.95" />
                  <stop offset="1" stop-color="var(--color-accent-ai)" stop-opacity="0" />
                </linearGradient>
              </defs>
              <line
                x1="0"
                y1="3"
                x2="1000"
                y2="3"
                stroke="url(#pipelineGrad)"
                stroke-width="3"
                stroke-linecap="round"
                stroke-dasharray="1000"
                stroke-dashoffset="1000"
                class="pipeline-line"
              />
            </svg>
          </div>

          <div v-for="(step, i) in steps" :key="step.title" class="relative flex-1">
            <LandingPipelineNode
              :icon="step.icon"
              :title="step.title"
              :description="step.description"
              :index="i"
            />
          </div>
        </div>
      </div>

      <!-- Mobile: vertical stack with tall vertical connectors -->
      <div class="lg:hidden">
        <div class="flex flex-col items-center gap-8">
          <template v-for="(step, i) in steps" :key="step.title">
            <LandingPipelineNode
              :icon="step.icon"
              :title="step.title"
              :description="step.description"
              :index="i"
            />
            <div
              v-if="i < steps.length - 1"
              class="pipeline-v-connector"
              :class="{ 'is-drawn': inView }"
              aria-hidden="true"
            ></div>
          </template>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Line draws once when section enters viewport. Uses stroke-dashoffset so
   it truly feels drawn rather than simply fading. */
.pipeline-svg .pipeline-line {
  transition: stroke-dashoffset 1200ms var(--ease-ios);
}
.pipeline-svg.is-drawn .pipeline-line {
  stroke-dashoffset: 0;
}

/* Mobile vertical connector — tall enough to read as a real pipeline step,
   not a visual afterthought. Same draw-in feel via scaleY. */
.pipeline-v-connector {
  height: 80px;
  width: 3px;
  border-radius: 2px;
  background: linear-gradient(
    to bottom,
    transparent,
    var(--color-accent-ai) 18%,
    var(--color-accent-ai) 82%,
    transparent
  );
  opacity: 0.85;
  transform-origin: top center;
  transform: scaleY(0);
  transition: transform 720ms var(--ease-ios);
}
.pipeline-v-connector.is-drawn {
  transform: scaleY(1);
}

@media (prefers-reduced-motion: reduce) {
  .pipeline-svg .pipeline-line {
    transition: opacity 200ms linear;
    stroke-dashoffset: 0;
    opacity: 0;
  }
  .pipeline-svg.is-drawn .pipeline-line {
    opacity: 1;
  }
  .pipeline-v-connector {
    transform: none;
    transition: opacity 200ms linear;
    opacity: 0;
  }
  .pipeline-v-connector.is-drawn {
    opacity: 0.7;
  }
}
</style>
