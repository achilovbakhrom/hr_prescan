<script setup lang="ts">
import type { LiveTranscriptLine } from '../composables/useInterviewRoom'

defineProps<{
  lines: LiveTranscriptLine[]
}>()
</script>

<template>
  <div v-if="lines.length" class="live-transcript">
    <div
      v-for="line in lines"
      :key="line.id"
      class="live-transcript__line"
      :class="{ 'live-transcript__line--draft': !line.final }"
    >
      <span class="live-transcript__speaker">{{ line.speaker }}</span>
      <span class="live-transcript__text">{{ line.text }}</span>
    </div>
  </div>
</template>

<style scoped>
.live-transcript {
  position: absolute;
  left: 50%;
  bottom: 140px;
  z-index: 15;
  display: flex;
  width: min(860px, calc(100vw - 40px));
  max-height: 240px;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
  pointer-events: none;
  transform: translateX(-50%);
}

.live-transcript__line {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  background: rgba(5, 8, 14, 0.78);
  color: white;
  box-shadow: 0 16px 42px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(18px);
  animation: transcript-in 180ms ease-out;
}

.live-transcript__line--draft {
  opacity: 0.72;
}

.live-transcript__speaker {
  color: rgba(255, 255, 255, 0.64);
  font-size: 12px;
  font-weight: 600;
}

.live-transcript__text {
  font-size: 15px;
  line-height: 1.5;
}

@keyframes transcript-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .live-transcript {
    right: auto;
    bottom: 132px;
    left: 50%;
    width: calc(100vw - 28px);
    max-height: 184px;
  }

  .live-transcript__line {
    padding: 10px 12px;
  }

  .live-transcript__text {
    font-size: 14px;
  }
}
</style>
