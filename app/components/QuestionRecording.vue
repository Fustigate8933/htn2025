<template>
  <div class="question-recording">
    <!-- Recording Controls -->
    <div class="recording-controls">
      <div v-if="!recorder.hasPermission.value" class="permission-prompt">
        <UButton
          @click="requestPermission"
          :loading="isRequestingPermission"
          variant="outline"
          size="sm"
        >
          <UIcon name="ic:outline-mic" class="mr-2" />
          Enable Microphone
        </UButton>
      </div>
      
      <div v-else-if="!recorder.isRecording.value" class="start-recording">
        <UButton
          @click="startRecording"
          variant="solid"
          color="red"
          size="lg"
          class="record-button"
        >
          <UIcon name="ic:outline-mic" class="mr-2" />
          Record Question
        </UButton>
      </div>
      
      <div v-else class="stop-recording">
        <UButton
          @click="stopRecording"
          variant="solid"
          color="gray"
          size="lg"
          class="stop-button"
        >
          <UIcon name="ic:outline-stop" class="mr-2" />
          Stop Recording
        </UButton>
        
        <!-- Recording indicator -->
        <div class="recording-indicator">
          <div class="pulse-dot"></div>
          <span class="recording-text">Recording...</span>
        </div>
      </div>
    </div>
    
    <!-- Audio Playback (only show if processing failed) -->
    <div v-if="recorder.audioUrl.value && !recorder.isProcessing.value && !recorder.transcript.value" class="audio-playback">
      <div class="playback-controls">
        <audio
          :src="recorder.audioUrl.value"
          controls
          class="audio-player"
        />
        <UButton
          @click="clearRecording"
          variant="ghost"
          size="sm"
          color="gray"
        >
          <UIcon name="ic:outline-clear" />
        </UButton>
      </div>
    </div>
    
    <!-- Processing State -->
    <div v-if="recorder.isProcessing.value" class="processing-state">
      <UIcon name="line-md:loading-loop" class="animate-spin size-6 text-blue-500" />
      <span class="processing-text">Processing your question and generating response...</span>
    </div>
    
    <!-- Transcript Display -->
    <div v-if="recorder.transcript.value" class="transcript-display">
      <div class="transcript-header">
        <h4 class="transcript-title">Your Question:</h4>
        <UButton
          @click="clearRecording"
          variant="ghost"
          size="xs"
          color="gray"
        >
          <UIcon name="ic:outline-close" />
        </UButton>
      </div>
      <div class="transcript-content">
        <p class="transcript-text">{{ recorder.transcript.value }}</p>
      </div>
      
      <!-- Response Section -->
      <div v-if="recorder.response.value" class="response-section">
        <div class="response-header">
          <h4 class="response-title">Response:</h4>
        </div>
        <div class="response-content">
          <p class="response-text">{{ recorder.response.value }}</p>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="action-buttons">
        <UButton
          @click="speakResponse"
          :loading="isSpeaking"
          :disabled="!recorder.response.value"
          variant="outline"
        >
          <UIcon name="ic:outline-volume-up" class="mr-2" />
          Speak Response
        </UButton>
        <UButton
          @click="processRecording"
          :loading="recorder.isProcessing.value"
          variant="outline"
          size="sm"
        >
          <UIcon name="ic:outline-transcribe" class="mr-2" />
          Retry Processing
        </UButton>
        <UButton
          @click="clearRecording"
          variant="ghost"
          size="sm"
          color="gray"
        >
          <UIcon name="ic:outline-clear" />
        </UButton>
      </div>
    </div>
    
    <!-- Error Display -->
    <div v-if="recorder.error.value" class="error-display">
      <UAlert
        color="red"
        variant="soft"
        :title="recorder.error.value"
        :close-button="{ icon: 'ic:outline-close', color: 'red', variant: 'link', padded: false }"
        @close="clearError"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAudioRecording } from '~/composables/useAudioRecording'

// Props
interface Props {
  pptUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
  pptUrl: ''
})

// Emits
const emit = defineEmits<{
  responseGenerated: [question: string, response: string]
}>()

// Composables
const recorder = useAudioRecording(props.pptUrl)

// State
const isRequestingPermission = ref(false)
const isSpeaking = ref(false)

// Methods
const requestPermission = async () => {
  isRequestingPermission.value = true
  try {
    await recorder.requestMicrophonePermission()
  } finally {
    isRequestingPermission.value = false
  }
}

const startRecording = async () => {
  const success = await recorder.startRecording()
  if (success) {
    // Clear previous results
    recorder.clearRecording()
  }
}

const stopRecording = async () => {
  recorder.stopRecording()
  // Auto-process the recording after stopping
  await processRecording()
}

const processRecording = async () => {
  const result = await recorder.processAudio()
  if (result) {
    // Emit the event with both transcript and response
    emit('responseGenerated', result.transcript, result.response)
  }
}

const clearRecording = () => {
  recorder.clearRecording()
}

const clearError = () => {
  // Reset error state in the composable
  recorder.clearRecording()
}

const speakResponse = async () => {
  if (!recorder.response.value) return
  
  isSpeaking.value = true
  try {
    // Use the browser's speech synthesis API
    const utterance = new SpeechSynthesisUtterance(recorder.response.value)
    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.volume = 0.8
    
    utterance.onend = () => {
      isSpeaking.value = false
    }
    
    utterance.onerror = () => {
      isSpeaking.value = false
    }
    
    speechSynthesis.speak(utterance)
  } catch (error) {
    console.error('Failed to speak response:', error)
    isSpeaking.value = false
  }
}

// Auto-request permission on mount
onMounted(() => {
  if (!recorder.hasPermission.value) {
    requestPermission()
  }
})
</script>

<style scoped>
.question-recording {
  background: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(8px);
  color: white;
  max-width: 400px;
}

.recording-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
}

.permission-prompt {
  text-align: center;
}

.start-recording {
  text-align: center;
}

.stop-recording {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.record-button {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transform: scale(1);
  transition: transform 0.2s ease;
}

.record-button:hover {
  transform: scale(1.05);
}

.stop-button {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ef4444;
  font-weight: 500;
}

.pulse-dot {
  width: 12px;
  height: 12px;
  background-color: #ef4444;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.recording-text {
  font-size: 14px;
}

.audio-playback {
  padding: 16px;
  background: rgba(55, 65, 81, 0.5);
  border-radius: 8px;
  margin-bottom: 16px;
}

.playback-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.audio-player {
  flex: 1;
  height: 40px;
}

.processing-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  color: #3b82f6;
  margin-bottom: 16px;
}

.processing-text {
  margin-left: 8px;
}

.transcript-display {
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  color: #111827;
}

.transcript-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.transcript-title {
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.transcript-content {
  margin-bottom: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 4px;
  border-left: 4px solid #3b82f6;
}

.transcript-text {
  color: #374151;
  margin: 0;
}

.response-section {
  margin-top: 16px;
  padding: 12px;
  background: #f0fdf4;
  border-radius: 4px;
  border-left: 4px solid #22c55e;
}

.response-header {
  margin-bottom: 8px;
}

.response-title {
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.response-content {
  color: #374151;
}

.response-text {
  color: #374151;
  margin: 0;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  align-items: center;
}

.error-display {
  margin-top: 16px;
}

.mr-2 {
  margin-right: 8px;
}

.size-6 {
  width: 24px;
  height: 24px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.text-blue-500 {
  color: #3b82f6;
}
</style>
