<script setup lang="ts">
/**
 * LandingHeroMockup — the tilted AI-chat product preview shown on desktop
 * beside the hero copy. Extracted from LandingHero so each file stays
 * under the 200-line limit.
 */
import { ref, onMounted, onUnmounted } from 'vue'
import GlassCard from '@/shared/components/GlassCard.vue'

interface DemoMessage {
  role: 'ai' | 'candidate'
  text: string
}

const visibleMessages = ref<DemoMessage[]>([])
const chatDemoComplete = ref(false)
let demoInterval: ReturnType<typeof setInterval> | null = null

const demoMessages: DemoMessage[] = [
  { role: 'ai', text: "Hi! I'm your AI interviewer. Ready to begin?" },
  { role: 'candidate', text: "Yes, let's go." },
  { role: 'ai', text: 'Tell me about a complex UI challenge you solved recently.' },
  { role: 'candidate', text: 'I built a real-time collaborative editor with CRDTs and Vue 3.' },
  { role: 'ai', text: 'Technical 9/10 · Communication 8/10. Advancing to interview stage.' },
]

onMounted(() => {
  let i = 0
  demoInterval = setInterval(() => {
    if (i < demoMessages.length) {
      visibleMessages.value.push(demoMessages[i])
      i++
    } else {
      chatDemoComplete.value = true
      if (demoInterval) clearInterval(demoInterval)
    }
  }, 1400)
})

onUnmounted(() => {
  if (demoInterval) clearInterval(demoInterval)
})
</script>

<template>
  <GlassCard class="hero-mockup-card">
    <div
      class="bg-glass-2 border-glass -mx-6 -mt-6 flex items-center gap-3 rounded-t-lg border-b px-5 py-3"
    >
      <div
        class="flex h-8 w-8 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)]"
      >
        <i class="pi pi-sparkles text-sm text-[color:var(--color-accent-ai)]"></i>
      </div>
      <div class="flex-1">
        <p class="text-sm font-semibold text-[color:var(--color-text-primary)]">AI Prescan</p>
        <div class="flex items-center gap-1.5">
          <span
            class="h-1.5 w-1.5 animate-pulse rounded-full bg-[color:var(--color-success)]"
          ></span>
          <span class="font-mono text-[11px] text-[color:var(--color-text-muted)]">
            live · 02:14
          </span>
        </div>
      </div>
    </div>

    <div class="h-[300px] space-y-3 overflow-hidden py-4">
      <TransitionGroup name="chat-msg" tag="div" class="space-y-3">
        <div
          v-for="(msg, idx) in visibleMessages"
          :key="idx"
          class="flex"
          :class="msg.role === 'candidate' ? 'justify-end' : 'justify-start'"
        >
          <div v-if="msg.role === 'ai'" class="flex max-w-[85%] gap-2">
            <div
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)]"
            >
              <i class="pi pi-sparkles text-[9px] text-[color:var(--color-accent-ai)]"></i>
            </div>
            <div
              class="rounded-2xl rounded-tl-sm bg-[color:var(--color-surface-raised)] px-3.5 py-2 text-sm text-[color:var(--color-text-primary)]"
            >
              {{ msg.text }}
            </div>
          </div>
          <div
            v-else
            class="max-w-[80%] rounded-2xl rounded-tr-sm bg-[color:var(--color-accent)] px-3.5 py-2 text-sm text-[color:var(--color-text-on-accent)]"
          >
            {{ msg.text }}
          </div>
        </div>
      </TransitionGroup>
      <div v-if="visibleMessages.length > 0 && !chatDemoComplete" class="flex items-center gap-2">
        <div
          class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)]"
        >
          <i class="pi pi-sparkles text-[9px] text-[color:var(--color-accent-ai)]"></i>
        </div>
        <div class="flex gap-1 rounded-2xl bg-[color:var(--color-surface-raised)] px-3.5 py-2.5">
          <span
            class="h-1.5 w-1.5 animate-bounce rounded-full bg-[color:var(--color-text-muted)]"
            style="animation-delay: 0ms"
          ></span>
          <span
            class="h-1.5 w-1.5 animate-bounce rounded-full bg-[color:var(--color-text-muted)]"
            style="animation-delay: 150ms"
          ></span>
          <span
            class="h-1.5 w-1.5 animate-bounce rounded-full bg-[color:var(--color-text-muted)]"
            style="animation-delay: 300ms"
          ></span>
        </div>
      </div>
    </div>
  </GlassCard>
</template>

<style scoped>
.hero-mockup-card {
  transform: rotate(1.5deg);
  transform-origin: center;
  transition: transform 420ms var(--ease-ios);
}
.hero-mockup-card:hover {
  transform: rotate(0deg) translateY(-2px);
}

.chat-msg-enter-active {
  transition: all 380ms var(--ease-ios);
}
.chat-msg-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

@media (prefers-reduced-motion: reduce) {
  .hero-mockup-card {
    transform: none;
    transition: none;
  }
}
</style>
