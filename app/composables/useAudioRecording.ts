import type { Ref } from 'vue'

export interface AudioRecordingState {
  isRecording: boolean
  isProcessing: boolean
  hasPermission: boolean
  error: string | null
  audioBlob: Blob | null
  audioUrl: string | null
  transcript: string | null
}

export const useAudioRecording = (pptUrl?: string) => {
  // State
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const hasPermission = ref(false)
  const error = ref<string | null>(null)
  const audioBlob = ref<Blob | null>(null)
  const audioUrl = ref<string | null>(null)
  const transcript = ref<string | null>(null)
  const response = ref<string | null>(null)
  
  // MediaRecorder instance
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioStream = ref<MediaStream | null>(null)
  const audioChunks = ref<Blob[]>([])

  const requestMicrophonePermission = async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      })
      
      audioStream.value = stream
      hasPermission.value = true
      error.value = null
      
      // Stop the stream immediately after getting permission
      stream.getTracks().forEach(track => track.stop())
      audioStream.value = null
      
      return true
    } catch (err) {
      console.error('Microphone permission denied:', err)
      error.value = 'Microphone access is required for recording'
      hasPermission.value = false
      return false
    }
  }

  const startRecording = async (): Promise<boolean> => {
    if (isRecording.value) return false
    
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      })
      
      audioStream.value = stream
      audioChunks.value = []
      
      // Create MediaRecorder
      mediaRecorder.value = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }
      
      mediaRecorder.value.onstop = () => {
        const blob = new Blob(audioChunks.value, { type: 'audio/webm' })
        audioBlob.value = blob
        audioUrl.value = URL.createObjectURL(blob)
        
        // Stop all tracks
        if (audioStream.value) {
          audioStream.value.getTracks().forEach(track => track.stop())
          audioStream.value = null
        }
      }
      
      mediaRecorder.value.start()
      isRecording.value = true
      error.value = null
      
      return true
    } catch (err) {
      console.error('Failed to start recording:', err)
      error.value = 'Failed to start recording'
      return false
    }
  }

  const stopRecording = () => {
    if (!isRecording.value || !mediaRecorder.value) return
    
    mediaRecorder.value.stop()
    isRecording.value = false
    mediaRecorder.value = null
  }

  const processAudio = async (): Promise<{transcript: string, response: string} | null> => {
    if (!audioBlob.value || isProcessing.value) return null
    
    isProcessing.value = true
    error.value = null
    
    try {
      // Convert audio to the format expected by the backend
      const formData = new FormData()
      formData.append('audio', audioBlob.value, 'question.webm')
      
      // Add PPT URL if available
      if (pptUrl) {
        formData.append('ppt_url', pptUrl)
      }
      
      // Call the backend API for complete processing (audio-to-text + response generation)
      const result = await $fetch('/api/question/process', {
        method: 'POST',
        body: formData
      })
      
      if (result.success && result.transcript && result.response) {
        transcript.value = result.transcript
        response.value = result.response
        return {
          transcript: result.transcript,
          response: result.response
        }
      } else {
        throw new Error('Failed to process audio')
      }
    } catch (err) {
      console.error('Audio processing failed:', err)
      error.value = 'Failed to process audio'
      return null
    } finally {
      isProcessing.value = false
    }
  }

  const clearRecording = () => {
    audioBlob.value = null
    audioUrl.value = null
    transcript.value = null
    response.value = null
    audioChunks.value = []
    
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
      audioUrl.value = null
    }
  }

  const getRecordingDuration = (): number => {
    // This is a simple approximation - in a real app you'd track actual duration
    return audioChunks.value.reduce((total, chunk) => total + chunk.size, 0) / 1000
  }

  // Cleanup on unmount
  onBeforeUnmount(() => {
    if (isRecording.value) {
      stopRecording()
    }
    
    if (audioStream.value) {
      audioStream.value.getTracks().forEach(track => track.stop())
    }
    
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
    }
  })

  return {
    // State
    isRecording: readonly(isRecording),
    isProcessing: readonly(isProcessing),
    hasPermission: readonly(hasPermission),
    error: readonly(error),
    audioBlob: readonly(audioBlob),
    audioUrl: readonly(audioUrl),
    transcript: readonly(transcript),
    response: readonly(response),
    
    // Methods
    requestMicrophonePermission,
    startRecording,
    stopRecording,
    processAudio,
    clearRecording,
    getRecordingDuration
  }
}
