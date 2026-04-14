import { ref, onUnmounted } from 'vue'
import {
  Room,
  RoomEvent,
  Track,
  type RemoteTrack,
  type RemoteTrackPublication,
  type RemoteParticipant,
} from 'livekit-client'
import type { RoomConfig, ConnectionState } from '../types/video.types'

export function useLiveKit() {
  const room = ref<Room | null>(null)
  const connectionState = ref<ConnectionState>('disconnected')
  const isMicEnabled = ref(true)
  const isCameraEnabled = ref(true)
  const remoteAudioTrack = ref<RemoteTrack | null>(null)
  const error = ref<string | null>(null)

  async function connect(config: RoomConfig): Promise<void> {
    try {
      connectionState.value = 'connecting'
      error.value = null
      const newRoom = new Room()

      newRoom.on(RoomEvent.Connected, () => {
        connectionState.value = 'connected'
      })

      newRoom.on(RoomEvent.Disconnected, () => {
        connectionState.value = 'disconnected'
      })

      newRoom.on(RoomEvent.Reconnecting, () => {
        connectionState.value = 'reconnecting'
      })

      newRoom.on(
        RoomEvent.TrackSubscribed,
        (
          track: RemoteTrack,
          _publication: RemoteTrackPublication,
          _participant: RemoteParticipant,
        ) => {
          if (track.kind === Track.Kind.Audio) {
            remoteAudioTrack.value = track
            const audioElement = track.attach()
            document.body.appendChild(audioElement)
          }
        },
      )

      await newRoom.connect(config.url, config.token)
      await newRoom.localParticipant.setMicrophoneEnabled(true)
      await newRoom.localParticipant.setCameraEnabled(true)

      room.value = newRoom
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to connect'
      connectionState.value = 'disconnected'
    }
  }

  async function connectAsObserver(config: RoomConfig): Promise<void> {
    try {
      connectionState.value = 'connecting'
      error.value = null
      const newRoom = new Room()

      newRoom.on(RoomEvent.Connected, () => {
        connectionState.value = 'connected'
      })

      newRoom.on(RoomEvent.Disconnected, () => {
        connectionState.value = 'disconnected'
      })

      newRoom.on(RoomEvent.Reconnecting, () => {
        connectionState.value = 'reconnecting'
      })

      newRoom.on(
        RoomEvent.TrackSubscribed,
        (
          track: RemoteTrack,
          _publication: RemoteTrackPublication,
          _participant: RemoteParticipant,
        ) => {
          if (track.kind === Track.Kind.Audio) {
            remoteAudioTrack.value = track
            const audioElement = track.attach()
            document.body.appendChild(audioElement)
          }
        },
      )

      await newRoom.connect(config.url, config.token)

      room.value = newRoom
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to connect'
      connectionState.value = 'disconnected'
    }
  }

  async function disconnect(): Promise<void> {
    if (room.value) {
      await room.value.disconnect()
      room.value = null
    }
  }

  async function toggleMic(): Promise<void> {
    if (room.value) {
      isMicEnabled.value = !isMicEnabled.value
      await room.value.localParticipant.setMicrophoneEnabled(isMicEnabled.value)
    }
  }

  async function toggleCamera(): Promise<void> {
    if (room.value) {
      isCameraEnabled.value = !isCameraEnabled.value
      await room.value.localParticipant.setCameraEnabled(isCameraEnabled.value)
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    room,
    connectionState,
    isMicEnabled,
    isCameraEnabled,
    remoteAudioTrack,
    error,
    connect,
    connectAsObserver,
    disconnect,
    toggleMic,
    toggleCamera,
  }
}
