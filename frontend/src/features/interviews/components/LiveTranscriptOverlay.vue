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
  bottom: 96px;
  z-index: 15;
  display: flex;
  width: min(680px, calc(100vw - 32px));
  max-height: 168px;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
  pointer-events: none;
  transform: translateX(-50%);
}

.live-transcript__line {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  background: rgba(5, 8, 14, 0.7);
  color: white;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(14px);
  animation: transcript-in 180ms ease-out;
}

.live-transcript__line--draft {
  opacity: 0.72;
}

.live-transcript__speaker {
  color: rgba(255, 255, 255, 0.64);
  font-size: 11px;
  font-weight: 600;
}

.live-transcript__text {
  font-size: 12px;
  line-height: 1.45;
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
    bottom: 92px;
    left: 50%;
    width: calc(100vw - 24px);
    max-height: 126px;
  }
}
</style>
