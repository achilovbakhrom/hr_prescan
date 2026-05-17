<script setup lang="ts">
import VoiceLevelMeter from './VoiceLevelMeter.vue'

withDefaults(
  defineProps<{
    name: string
    initials: string
    hasVideo: boolean
    isSpeaking: boolean
    audioLevel: number
    muted?: boolean
    compact?: boolean
    accent?: 'ai' | 'candidate'
  }>(),
  {
    muted: false,
    compact: false,
    accent: 'candidate',
  },
)

const videoEl = defineModel<HTMLVideoElement | null>('videoEl', { required: true })
</script>

<template>
  <section
    class="participant-tile"
    :class="{
      'participant-tile--compact': compact,
      'participant-tile--speaking': isSpeaking,
    }"
  >
    <video
      v-show="hasVideo"
      ref="videoEl"
      autoplay
      playsinline
      :muted="compact"
      class="h-full w-full object-cover"
    ></video>

    <div v-if="!hasVideo" class="participant-tile__empty">
      <div
        class="participant-tile__avatar"
        :class="
          accent === 'ai' ? 'participant-tile__avatar--ai' : 'participant-tile__avatar--candidate'
        "
      >
        <span class="participant-tile__avatar-ring"></span>
        {{ initials }}
      </div>
      <div v-if="!compact" class="mt-4 text-center">
        <p class="text-sm font-medium text-white/86">{{ name }}</p>
        <VoiceLevelMeter :level="audioLevel" :speaking="isSpeaking" :muted="muted" />
      </div>
    </div>

    <div class="participant-tile__label">
      <span class="truncate">{{ name }}</span>
      <VoiceLevelMeter :level="audioLevel" :speaking="isSpeaking" :muted="muted" compact />
      <span
        v-if="muted"
        aria-hidden="true"
        class="pi pi-microphone participant-tile__muted-icon"
      ></span>
    </div>
  </section>
</template>

<style>
@import './RoomParticipantTile.css';
</style>
