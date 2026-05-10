<script setup lang="ts">
defineProps<{
  level: number
  speaking: boolean
  muted?: boolean
  compact?: boolean
}>()

const bars = [0.18, 0.34, 0.5, 0.66, 0.82]
</script>

<template>
  <div
    class="voice-meter"
    :class="{
      'voice-meter--speaking': speaking,
      'voice-meter--muted': muted,
      'voice-meter--compact': compact,
    }"
    aria-hidden="true"
  >
    <span
      v-for="(threshold, index) in bars"
      :key="threshold"
      class="voice-meter__bar"
      :class="{ 'voice-meter__bar--active': !muted && level >= threshold }"
      :style="{ '--delay': `${index * 45}ms` }"
    ></span>
  </div>
</template>

<style scoped>
.voice-meter {
  display: flex;
  align-items: end;
  gap: 3px;
  height: 26px;
}

.voice-meter__bar {
  width: 4px;
  height: 34%;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.28);
  transition:
    height 120ms ease,
    background 120ms ease,
    opacity 120ms ease;
}

.voice-meter__bar:nth-child(2) {
  height: 48%;
}

.voice-meter__bar:nth-child(3) {
  height: 68%;
}

.voice-meter__bar:nth-child(4) {
  height: 52%;
}

.voice-meter__bar:nth-child(5) {
  height: 38%;
}

.voice-meter__bar--active {
  background: #39e58c;
  box-shadow: 0 0 10px rgba(57, 229, 140, 0.55);
}

.voice-meter--speaking .voice-meter__bar--active {
  animation: voice-meter-pulse 620ms ease-in-out infinite alternate;
  animation-delay: var(--delay);
}

.voice-meter--muted .voice-meter__bar {
  height: 26%;
  background: rgba(255, 255, 255, 0.18);
  box-shadow: none;
}

.voice-meter--compact {
  height: 18px;
}

.voice-meter--compact .voice-meter__bar {
  width: 3px;
}

@keyframes voice-meter-pulse {
  from {
    transform: scaleY(0.7);
  }
  to {
    transform: scaleY(1.18);
  }
}
</style>
