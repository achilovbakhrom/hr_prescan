<script setup lang="ts">
defineProps<{
  item: {
    icon: string
    accent: string
    featured: boolean
    title: string
    description: string
    prompt: string
    tooltip: string
  }
  featuredLabel: string
}>()

defineEmits<{
  send: [prompt: string]
}>()
</script>

<template>
  <button
    type="button"
    class="ai-tool-card group relative flex min-h-[88px] w-full items-start gap-3 rounded-xl border bg-white p-3 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md dark:bg-slate-950"
    :class="[`ai-tool-card--${item.accent}`, item.featured ? 'ai-tool-card--featured' : '']"
    :title="item.tooltip"
    @click="$emit('send', item.prompt)"
  >
    <span class="ai-tool-icon flex h-10 w-10 shrink-0 items-center justify-center rounded-xl">
      <i :class="item.icon" class="text-sm"></i>
    </span>
    <span class="min-w-0">
      <span v-if="item.featured" class="ai-tool-badge">
        {{ featuredLabel }}
      </span>
      <span class="block text-sm font-semibold text-[color:var(--color-text-primary)]">
        {{ item.title }}
      </span>
      <span class="mt-0.5 block text-xs leading-5 text-[color:var(--color-text-secondary)]">
        {{ item.description }}
      </span>
    </span>
    <span class="ai-tool-tooltip">
      {{ item.tooltip }}
    </span>
  </button>
</template>

<style scoped>
.ai-tool-card {
  border-color: rgb(226 232 240);
}
.ai-tool-card--featured {
  border-width: 2px;
}
.ai-tool-badge {
  display: inline-flex;
  margin-bottom: 0.25rem;
  border-radius: 999px;
  padding: 0.125rem 0.375rem;
  font-size: 0.625rem;
  font-weight: 700;
  line-height: 1rem;
}
.ai-tool-tooltip {
  pointer-events: none;
  position: absolute;
  left: calc(100% + 0.75rem);
  top: 50%;
  z-index: 20;
  width: 16rem;
  transform: translateY(-50%);
  border-radius: 0.75rem;
  background: rgb(15 23 42);
  color: white;
  opacity: 0;
  padding: 0.625rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.25rem;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.2);
  transition: opacity 0.15s ease;
}
.ai-tool-card:hover .ai-tool-tooltip {
  opacity: 1;
}
.ai-tool-card--blue {
  border-color: rgb(191 219 254);
}
.ai-tool-card--blue .ai-tool-icon,
.ai-tool-card--blue .ai-tool-badge {
  background: rgb(219 234 254);
  color: rgb(29 78 216);
}
.ai-tool-card--emerald {
  border-color: rgb(167 243 208);
}
.ai-tool-card--emerald .ai-tool-icon,
.ai-tool-card--emerald .ai-tool-badge {
  background: rgb(209 250 229);
  color: rgb(4 120 87);
}
.ai-tool-card--amber {
  border-color: rgb(253 230 138);
}
.ai-tool-card--amber .ai-tool-icon,
.ai-tool-card--amber .ai-tool-badge {
  background: rgb(254 243 199);
  color: rgb(180 83 9);
}
.ai-tool-card--rose {
  border-color: rgb(254 205 211);
}
.ai-tool-card--rose .ai-tool-icon,
.ai-tool-card--rose .ai-tool-badge {
  background: rgb(255 228 230);
  color: rgb(190 18 60);
}
:global(.dark) .ai-tool-card {
  border-color: rgb(51 65 85);
}
</style>
