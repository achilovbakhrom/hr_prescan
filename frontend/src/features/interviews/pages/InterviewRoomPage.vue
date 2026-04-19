<script setup lang="ts">
/**
 * InterviewRoomPage — candidate video interview (LiveKit).
 *
 * T13 redesign: cinematic dark base with a subtle ambient glow behind
 * glass chrome (top strip, control pill, side cards). Video tiles stay
 * pitch black for contrast. Standalone route — no PublicLayout. We
 * mount AnimatedBackground at very low opacity so the ambient mood is
 * there without fighting the video. FloatingBackgroundPicker is
 * suppressed to avoid distracting the candidate mid-interview.
 */
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import AnimatedBackground from '@/shared/components/AnimatedBackground.vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import { useThemeStore } from '@/shared/stores/theme.store'
import { useInterviewRoom } from '../composables/useInterviewRoom'
import RoomIdleView from '../components/RoomIdleView.vue'
import RoomPreviewView from '../components/RoomPreviewView.vue'
import RoomConnectedView from '../components/RoomConnectedView.vue'

const { t } = useI18n()
const route = useRoute()
const themeStore = useThemeStore()
const token = computed(() => route.params.token as string)

const room = useInterviewRoom(() => token.value)

onMounted(() => {
  // Use Vellum as a calm backdrop behind the cinematic layer.
  if (themeStore.backgroundMode === 'off') {
    themeStore.setBackgroundMode('vellum')
  }
})
</script>

<template>
  <div class="relative flex h-screen flex-col bg-[#0a0d14]">
    <!-- Ambient, dimmed so the cinematic layer dominates -->
    <div class="pointer-events-none absolute inset-0 opacity-30">
      <AnimatedBackground />
    </div>

    <!-- Loading -->
    <div v-if="room.loading.value" class="relative z-0 flex flex-1 items-center justify-center">
      <i class="pi pi-spinner pi-spin text-4xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <!-- Fetch error -->
    <div
      v-else-if="room.fetchError.value"
      class="relative z-0 flex flex-1 items-center justify-center p-8"
    >
      <GlassCard class="max-w-md text-center">
        <i class="pi pi-exclamation-triangle mb-4 text-5xl text-[color:var(--color-danger)]"></i>
        <p class="mb-4 text-[color:var(--color-text-primary)]">{{ room.fetchError.value }}</p>
        <Button :label="t('errors.goBack')" severity="secondary" @click="room.router.back()" />
      </GlassCard>
    </div>

    <template v-else-if="room.interview.value">
      <!-- IDLE -->
      <RoomIdleView
        v-if="room.connectionState.value === 'idle'"
        class="relative z-0"
        :interview="room.interview.value"
        :can-join="room.canJoin.value"
        @start-preview="room.startPreview"
      />

      <!-- PREVIEW -->
      <RoomPreviewView
        v-else-if="room.connectionState.value === 'preview'"
        class="relative z-0"
        v-model:preview-video-el="room.previewVideoEl.value"
        :interview="room.interview.value"
        :is-muted="room.isMuted.value"
        :is-camera-off="room.isCameraOff.value"
        :get-initials="room.getInitials"
        @toggle-mic="room.togglePreviewMic"
        @toggle-camera="room.togglePreviewCamera"
        @join-room="room.joinRoom"
        @cancel="room.cancelPreview"
      />

      <!-- CONNECTING -->
      <div
        v-else-if="room.connectionState.value === 'connecting'"
        class="relative z-0 flex flex-1 items-center justify-center"
      >
        <div class="text-center">
          <i class="pi pi-spinner pi-spin mb-4 text-5xl text-[color:var(--color-accent)]"></i>
          <p class="text-lg text-[color:var(--color-text-primary)]">
            {{ t('interviews.roomPage.joiningInterview') }}
          </p>
        </div>
      </div>

      <!-- ERROR -->
      <div
        v-else-if="room.connectionState.value === 'error'"
        class="relative z-0 flex flex-1 items-center justify-center p-8"
      >
        <GlassCard class="w-full max-w-md text-center">
          <div
            class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-danger)]/20"
          >
            <i class="pi pi-exclamation-triangle text-2xl text-[color:var(--color-danger)]"></i>
          </div>
          <h2 class="mb-2 text-lg font-semibold text-[color:var(--color-text-primary)]">
            {{ t('interviews.roomPage.somethingWentWrong') }}
          </h2>
          <p class="mb-6 text-sm text-[color:var(--color-text-secondary)]">
            {{ room.errorMessage.value }}
          </p>
          <div class="flex justify-center gap-3">
            <Button
              :label="t('errors.goBack')"
              severity="secondary"
              outlined
              @click="room.connectionState.value = 'idle'"
            />
            <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" @click="room.startPreview" />
          </div>
        </GlassCard>
      </div>

      <!-- CONNECTED -->
      <RoomConnectedView
        v-else-if="room.connectionState.value === 'connected'"
        class="relative z-0"
        v-model:local-video-el="room.localVideoEl.value"
        v-model:remote-video-el="room.remoteVideoEl.value"
        v-model:remote-audio-el="room.remoteAudioEl.value"
        :interview="room.interview.value"
        :is-muted="room.isMuted.value"
        :is-camera-off="room.isCameraOff.value"
        :has-remote-video="room.hasRemoteVideo.value"
        :remote-participant-name="room.remoteParticipantName.value"
        :formatted-time="room.formattedTime.value"
        :get-initials="room.getInitials"
        @toggle-mute="room.toggleMute"
        @toggle-camera="room.toggleCamera"
        @leave="room.leaveInterview"
      />

      <!-- ENDED -->
      <div
        v-else-if="room.connectionState.value === 'ended'"
        class="relative z-0 flex flex-1 items-center justify-center p-8"
      >
        <GlassCard accent="celebrate" class="w-full max-w-md text-center">
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)]"
          >
            <i class="pi pi-check text-3xl text-[color:var(--color-accent-celebrate)]"></i>
          </div>
          <h2 class="mb-2 text-xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('interviews.status.completed') }}
          </h2>
          <p class="mb-1 text-[color:var(--color-text-secondary)]">
            {{ t('interviews.roomPage.duration') }}
            <span class="font-mono">{{ room.formattedTime.value }}</span>
          </p>
          <p class="mb-6 text-sm text-[color:var(--color-text-muted)]">
            {{ t('interviews.roomPage.thankYou') }}
          </p>
          <Button
            :label="t('errors.goHome')"
            icon="pi pi-home"
            class="w-full"
            @click="room.router.push('/')"
          />
        </GlassCard>
      </div>
    </template>
  </div>
</template>
