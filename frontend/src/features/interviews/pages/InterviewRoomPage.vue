<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useInterviewRoom } from '../composables/useInterviewRoom'
import RoomIdleView from '../components/RoomIdleView.vue'
import RoomPreviewView from '../components/RoomPreviewView.vue'
import RoomConnectedView from '../components/RoomConnectedView.vue'

const { t } = useI18n()
const route = useRoute()
const token = computed(() => route.params.token as string)

const room = useInterviewRoom(() => token.value)
</script>

<template>
  <div class="flex h-screen flex-col bg-[#202124]">
    <!-- Loading -->
    <div v-if="room.loading.value" class="flex flex-1 items-center justify-center">
      <i class="pi pi-spinner pi-spin text-4xl text-gray-400"></i>
    </div>

    <!-- Fetch error -->
    <div v-else-if="room.fetchError.value" class="flex flex-1 items-center justify-center p-8">
      <div class="max-w-md text-center">
        <i class="pi pi-exclamation-triangle mb-4 text-5xl text-red-400"></i>
        <p class="mb-4 text-white">{{ room.fetchError.value }}</p>
        <Button :label="t('errors.goBack')" severity="secondary" @click="room.router.back()" />
      </div>
    </div>

    <!-- Main states -->
    <template v-else-if="room.interview.value">
      <!-- IDLE -->
      <RoomIdleView
        v-if="room.connectionState.value === 'idle'"
        :interview="room.interview.value"
        :can-join="room.canJoin.value"
        @start-preview="room.startPreview"
      />

      <!-- PREVIEW -->
      <RoomPreviewView
        v-else-if="room.connectionState.value === 'preview'"
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
      <div v-else-if="room.connectionState.value === 'connecting'" class="flex flex-1 items-center justify-center">
        <div class="text-center">
          <i class="pi pi-spinner pi-spin mb-4 text-5xl text-blue-400"></i>
          <p class="text-lg text-white">{{ t('interviews.roomPage.joiningInterview') }}</p>
        </div>
      </div>

      <!-- ERROR -->
      <div v-else-if="room.connectionState.value === 'error'" class="flex flex-1 items-center justify-center p-8">
        <div class="w-full max-w-md rounded-2xl bg-[#303134] p-8 text-center shadow-2xl">
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-500/20">
            <i class="pi pi-exclamation-triangle text-2xl text-red-400"></i>
          </div>
          <h2 class="mb-2 text-lg font-medium text-white">{{ t('interviews.roomPage.somethingWentWrong') }}</h2>
          <p class="mb-6 text-sm text-gray-400">{{ room.errorMessage.value }}</p>
          <div class="flex justify-center gap-3">
            <Button :label="t('errors.goBack')" severity="secondary" outlined @click="room.connectionState.value = 'idle'" />
            <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" @click="room.startPreview" />
          </div>
        </div>
      </div>

      <!-- CONNECTED -->
      <RoomConnectedView
        v-else-if="room.connectionState.value === 'connected'"
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
      <div v-else-if="room.connectionState.value === 'ended'" class="flex flex-1 items-center justify-center p-8">
        <div class="w-full max-w-md rounded-2xl bg-[#303134] p-8 text-center shadow-2xl">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20">
            <i class="pi pi-check text-3xl text-green-400"></i>
          </div>
          <h2 class="mb-2 text-xl font-medium text-white">{{ t('interviews.status.completed') }}</h2>
          <p class="mb-1 text-gray-400">{{ t('interviews.roomPage.duration') }} {{ room.formattedTime.value }}</p>
          <p class="mb-6 text-sm text-gray-500">{{ t('interviews.roomPage.thankYou') }}</p>
          <Button :label="t('errors.goHome')" icon="pi pi-home" class="w-full" @click="room.router.push('/')" />
        </div>
      </div>
    </template>
  </div>
</template>
