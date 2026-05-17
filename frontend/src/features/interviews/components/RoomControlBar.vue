<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'

defineProps<{
  isMuted: boolean
  isCameraOff: boolean
}>()

const emit = defineEmits<{
  toggleMute: []
  toggleCamera: []
  leave: []
}>()

const { t } = useI18n()
</script>

<template>
  <GlassSurface
    level="float"
    class="room-controls pointer-events-auto flex items-center justify-center gap-2 !rounded-full p-2 shadow-glass-float"
  >
    <button
      class="room-controls__button"
      :class="{ 'room-controls__button--danger': isMuted }"
      :title="isMuted ? t('interviews.roomPage.unmute') : t('interviews.roomPage.mute')"
      @click="emit('toggleMute')"
    >
      <span
        aria-hidden="true"
        class="pi pi-microphone text-base"
        :class="{ 'room-controls__muted-icon': isMuted }"
      ></span>
    </button>

    <button
      class="room-controls__button"
      :class="{ 'room-controls__button--danger': isCameraOff }"
      :title="
        isCameraOff ? t('interviews.roomPage.turnOnCamera') : t('interviews.roomPage.turnOffCamera')
      "
      @click="emit('toggleCamera')"
    >
      <i :class="isCameraOff ? 'pi pi-video-slash' : 'pi pi-video'" class="text-base"></i>
    </button>

    <button
      class="room-controls__leave"
      :title="t('interviews.roomPage.leaveInterview')"
      @click="emit('leave')"
    >
      <i class="pi pi-phone text-base"></i>
      <span>{{ t('interviews.roomPage.leave') }}</span>
    </button>
  </GlassSurface>
</template>

<style scoped>
.room-controls__button,
.room-controls__leave {
  display: inline-flex;
  height: 44px;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 999px;
  color: var(--color-text-primary);
  transition:
    transform 120ms ease,
    filter 120ms ease,
    background 120ms ease;
}

.room-controls__button {
  width: 44px;
  background: var(--color-surface-raised);
}

.room-controls__button:hover,
.room-controls__leave:hover {
  filter: brightness(0.94);
  transform: translateY(-1px);
}

.room-controls__button--danger {
  background: var(--color-danger);
  color: white;
}

.room-controls__leave {
  gap: 8px;
  margin-left: 4px;
  background: var(--color-danger);
  padding: 0 18px;
  color: white;
  font-size: 14px;
  font-weight: 700;
}

.room-controls__leave .pi-phone {
  transform: rotate(135deg);
}

.room-controls__muted-icon {
  position: relative;
}

.room-controls__muted-icon::after {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 1.1em;
  height: 2px;
  border-radius: 999px;
  background: currentColor;
  content: '';
  transform: translate(-50%, -50%) rotate(-45deg);
}

@media (max-width: 480px) {
  .room-controls {
    width: calc(100vw - 24px);
  }

  .room-controls__button {
    flex: 0 0 44px;
  }

  .room-controls__leave {
    flex: 1;
  }
}
</style>
