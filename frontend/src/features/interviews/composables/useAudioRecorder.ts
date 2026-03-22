import { ref, onUnmounted } from 'vue'

export function useAudioRecorder(maxDuration = 120) {
  const isRecording = ref(false)
  const duration = ref(0)
  const audioBlob = ref<Blob | null>(null)
  const error = ref('')

  let mediaRecorder: MediaRecorder | null = null
  let stream: MediaStream | null = null
  let timer: ReturnType<typeof setInterval> | null = null
  let chunks: Blob[] = []

  function cleanup(): void {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      stream = null
    }
    mediaRecorder = null
    chunks = []
  }

  async function startRecording(): Promise<void> {
    error.value = ''
    audioBlob.value = null
    duration.value = 0

    if (typeof MediaRecorder === 'undefined') {
      error.value = 'Audio recording is not supported in this browser.'
      return
    }

    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch (err: unknown) {
      const domErr = err as DOMException
      if (domErr.name === 'NotAllowedError' || domErr.name === 'PermissionDeniedError') {
        error.value = 'Microphone access was denied. Please allow microphone permissions.'
      } else if (domErr.name === 'NotFoundError' || domErr.name === 'DevicesNotFoundError') {
        error.value = 'No microphone found. Please connect a microphone and try again.'
      } else {
        error.value = 'Could not access the microphone. Please check your device settings.'
      }
      return
    }

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : ''

    try {
      mediaRecorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream)
    } catch {
      error.value = 'Failed to initialize audio recorder.'
      cleanup()
      return
    }

    chunks = []

    mediaRecorder.addEventListener('dataavailable', (event: BlobEvent) => {
      if (event.data.size > 0) {
        chunks.push(event.data)
      }
    })

    mediaRecorder.addEventListener('stop', () => {
      const recordedMime = mediaRecorder?.mimeType || 'audio/webm'
      audioBlob.value = new Blob(chunks, { type: recordedMime })
    })

    mediaRecorder.start(250)
    isRecording.value = true

    timer = setInterval(() => {
      duration.value += 1
      if (duration.value >= maxDuration) {
        stopRecording()
      }
    }, 1000)
  }

  function stopRecording(): Promise<Blob> {
    return new Promise<Blob>((resolve, reject) => {
      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        isRecording.value = false
        reject(new Error('No active recording'))
        return
      }

      mediaRecorder.addEventListener(
        'stop',
        () => {
          const recordedMime = mediaRecorder?.mimeType || 'audio/webm'
          const blob = new Blob(chunks, { type: recordedMime })
          audioBlob.value = blob
          isRecording.value = false
          cleanup()
          resolve(blob)
        },
        { once: true },
      )

      mediaRecorder.stop()
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      if (stream) {
        stream.getTracks().forEach((track) => track.stop())
        stream = null
      }
    })
  }

  function cancelRecording(): void {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
    }
    isRecording.value = false
    duration.value = 0
    audioBlob.value = null
    error.value = ''
    cleanup()
  }

  onUnmounted(() => {
    cancelRecording()
  })

  return {
    isRecording,
    duration,
    audioBlob,
    error,
    startRecording,
    stopRecording,
    cancelRecording,
  }
}
