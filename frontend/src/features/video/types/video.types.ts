export interface RoomConfig {
  url: string
  token: string
  roomName: string
}

export interface MediaDeviceInfo {
  deviceId: string
  label: string
  kind: 'audioinput' | 'audiooutput' | 'videoinput'
}

export type ConnectionState =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
