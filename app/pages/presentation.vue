<template>
  <div class="min-h-screen bg-black">
    <!-- Fullscreen Presentation Mode -->
    <div class="relative w-full h-screen">
      <!-- Main Presentation Area -->
      <div class="absolute inset-0 bg-gray-900">
        <!-- Slide Content -->
        <div class="w-full h-full flex items-center justify-center p-8">
          <div v-if="currentSlide" class="w-full h-full flex items-center justify-center">
            <!-- Display slide image if available -->
            <div v-if="currentSlide.image" class="w-full h-full flex items-center justify-center">
              <img 
                :src="currentSlide.image" 
                :alt="currentSlide.title"
                class="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
              />
            </div>
            <!-- Fallback to text if no image -->
            <div v-else class="text-center text-white max-w-4xl">
              <h1 class="text-4xl font-bold mb-6">{{ currentSlide.title }}</h1>
              <p class="text-xl text-gray-300 leading-relaxed">{{ currentSlide.content }}</p>
            </div>
          </div>
          <div v-else class="text-center text-white">
            <h1 class="text-6xl font-bold mb-4">Your Presentation</h1>
            <p class="text-2xl text-gray-300">Slide content will appear here</p>
          </div>
        </div>
        
        <!-- Avatar Video Overlay -->
        <div 
          v-if="currentMode === 'avatar'"
          :class="[
            'absolute transition-all duration-300 ease-in-out',
            getAvatarPosition()
          ]"
          :style="{ width: `${avatarSize}%`, height: `${avatarSize * 0.75}%` }"
        >
          <!-- Video Player -->
          <video 
            v-if="currentVideoUrl"
            ref="avatarVideo"
            :src="currentVideoUrl"
            class="w-full h-full object-cover rounded-lg shadow-2xl"
            :autoplay="isPlaying"
            :loop="false"
            :muted="false"
            @ended="onVideoEnd"
          />
          
          <!-- Video Not Available Placeholder -->
          <div 
            v-else
            class="w-full h-full bg-gray-800 rounded-lg shadow-2xl flex items-center justify-center border-2 border-dashed border-gray-600"
          >
            <div class="text-center text-white p-4">
              <UIcon name="line-md:loading-loop" class="size-8 mx-auto mb-2 text-blue-400 animate-spin" />
              <p class="text-sm text-gray-300">Avatar video</p>
              <p class="text-xs text-gray-400">generating in background...</p>
              <p class="text-xs text-gray-500 mt-1">This may take 2-5 minutes</p>
            </div>
          </div>
        </div>
        
        <!-- Human Camera Overlay -->
        <div 
          v-if="currentMode === 'human' && camera.hasCameraAccess"
          :class="[
            'absolute transition-all duration-300 ease-in-out',
            getAvatarPosition()
          ]"
          :style="{ width: `${avatarSize}%`, height: `${avatarSize * 0.75}%` }"
        >
          <video 
            ref="cameraVideo"
            class="w-full h-full object-cover rounded-lg shadow-2xl"
            :autoplay="true"
            :muted="true"
            :playsinline="true"
          />
        </div>
      </div>
      
      <!-- Question Recording Panel -->
      <div v-if="showRecordingPanel" class="absolute bottom-4 left-4 max-w-sm">
        <QuestionRecording 
					class="mb-[4rem]"
          :ppt-url="presentationData?.pptUrl || ''"
          @response-generated="onQuestionResponse"
        />
      </div>
      
      <!-- Control Panel (hidden by default, show on hover) -->
      <div 
        class="absolute top-4 right-4 opacity-0 hover:opacity-100 transition-opacity duration-300"
        @mouseenter="showControls = true"
        @mouseleave="showControls = false"
      >
        <div class="bg-black bg-opacity-75 rounded-lg p-4 backdrop-blur-sm">
          <div class="flex flex-col gap-3">
            <!-- Mode Toggle -->
            <div class="flex gap-2">
              <UButton 
                :variant="currentMode === 'human' ? 'solid' : 'outline'"
                size="sm"
                @click="switchToHuman"
                class="flex-1"
              >
                <UIcon name="ic:outline-person" class="mr-1" />
                Human
              </UButton>
              <UButton 
                :variant="currentMode === 'avatar' ? 'solid' : 'outline'"
                size="sm"
                @click="switchToAvatar"
                class="flex-1"
              >
                <UIcon name="ic:outline-face" class="mr-1" />
                Avatar
              </UButton>
            </div>
            
            <!-- Playback Controls -->
            <div class="flex gap-2">
              <UButton 
                size="sm"
                variant="outline"
                @click="togglePlayback"
              >
                <UIcon :name="isPlaying ? 'ic:outline-pause' : 'ic:outline-play-arrow'" />
              </UButton>
              <UButton 
                size="sm"
                variant="outline"
                @click="restartPresentation"
              >
                <UIcon name="ic:outline-replay" />
              </UButton>
            </div>
            
            <!-- Slide Navigation -->
            <div class="flex gap-2">
              <UButton 
                size="sm"
                variant="outline"
                @click="previousSlide"
                :disabled="currentSlideIndex === 0"
              >
                <UIcon name="ic:outline-arrow-back" />
              </UButton>
              <span class="text-white text-sm flex items-center px-2">
                {{ currentSlideIndex + 1 }} / {{ presentationData?.slides?.length || 0 }}
              </span>
              <UButton 
                size="sm"
                variant="outline"
                @click="nextSlide"
                :disabled="currentSlideIndex >= (presentationData?.slides?.length || 0) - 1"
              >
                <UIcon name="ic:outline-arrow-forward" />
              </UButton>
            </div>
            
            <!-- Settings -->
            <div class="space-y-2">
              <label class="block text-xs text-white">Avatar Size</label>
              <URange
                v-model="avatarSize"
                :min="20"
                :max="80"
                :step="5"
                class="w-full"
              />
            </div>
            
                            <!-- Camera Status -->
                <div v-if="camera.hasCameraAccess" class="space-y-2">
                  <label class="block text-xs text-white">Camera Status</label>
                  <div class="flex items-center gap-2">
                    <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span class="text-xs text-white">Camera Connected</span>
                  </div>
                </div>
          </div>
        </div>
      </div>
      
      <!-- Status Bar -->
      <div class="absolute bottom-4 left-4 right-4">
        <div class="bg-black bg-opacity-75 rounded-lg p-3 backdrop-blur-sm">
          <div class="flex items-center justify-between text-white text-sm">
            <div class="flex items-center gap-4">
              <span class="flex items-center gap-1">
                <div :class="[
                  'w-2 h-2 rounded-full',
                  currentMode === 'avatar' ? 'bg-green-500' : 'bg-blue-500'
                ]"></div>
                {{ currentMode === 'avatar' ? 'Avatar Mode' : 'Human Mode' }}
              </span>
              <span v-if="isPlaying" class="flex items-center gap-1">
                <UIcon name="ic:outline-play-arrow" class="text-green-500" />
                Playing
              </span>
              <span v-else class="flex items-center gap-1">
                <UIcon name="ic:outline-pause" class="text-yellow-500" />
                Paused
              </span>
              <span class="text-gray-400">
                Slide {{ currentSlideIndex + 1 }} of {{ presentationData?.slides?.length || 0 }}
              </span>
            </div>
            
                            <div class="flex items-center gap-4">
                  <span v-if="camera.hasCameraAccess" class="flex items-center gap-1 text-green-500">
                    <UIcon name="ic:outline-videocam" />
                    Camera Connected
                  </span>
                  <span class="text-gray-400">
                    Press R to toggle recording panel
                  </span>
                </div>
          </div>
        </div>
      </div>
      
      <!-- Loading Overlay -->
      <div 
        v-if="isLoading"
        class="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center"
      >
        <div class="text-center text-white">
          <UIcon name="line-md:loading-loop" class="size-12 animate-spin mx-auto mb-4" />
          <p>Loading presentation...</p>
        </div>
      </div>
      
      <!-- Error Overlay -->
      <div 
        v-if="error"
        class="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center"
      >
        <div class="text-center text-white max-w-md mx-auto p-6">
          <UIcon name="ic:outline-error" class="size-12 text-red-500 mx-auto mb-4" />
          <h3 class="text-xl font-bold mb-2">Presentation Error</h3>
          <p class="text-gray-300 mb-4">{{ error }}</p>
          <UButton @click="retryLoad">
            Retry
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCamera } from '~/composables/useCamera'
import QuestionRecording from '~/components/QuestionRecording.vue'

// Types
interface Slide {
  id: number
  title: string
  content: string
  image?: string
  shapes?: any[]
}

interface PresentationData {
  slides: Slide[]
  videoUrls: string[]
  script: string
  pptUrl?: string
}

// Use shared camera state
const camera = useCamera()

// Reactive data
const currentMode = ref<'human' | 'avatar'>('avatar')
const isPlaying = ref(false)
const isLoading = ref(true)
const error = ref<string | null>(null)
const showControls = ref(false)
const showRecordingPanel = ref(true)

const avatarSize = ref(30)
const avatarPosition = ref('bottom-right')

const avatarVideo = ref<HTMLVideoElement | null>(null)
const cameraVideo = ref<HTMLVideoElement | null>(null)

const presentationData = ref<PresentationData | null>(null)
const currentSlideIndex = ref(0)
const currentVideoUrl = ref('')

// Computed
const currentSlide = computed(() => {
  if (!presentationData.value?.slides) return null
  return presentationData.value.slides[currentSlideIndex.value]
})

// Methods
const getAvatarPosition = () => {
  const positions = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'center': 'top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2'
  }
  return positions[avatarPosition.value as keyof typeof positions] || 'bottom-right'
}

const switchToHuman = async () => {
  currentMode.value = 'human'
  
  // Use shared camera state
  if (!camera.hasCameraAccess.value) {
    const success = await camera.connectCamera()
    if (!success) {
      error.value = 'Camera access is required for human mode'
      return
    }
  }
  
  // Set the camera stream to the video element
  await nextTick() // Ensure video element is mounted
  const stream = camera.getCameraStream()
  if (stream && cameraVideo.value) {
    cameraVideo.value.srcObject = stream
    console.log('Camera stream set to video element')
  } else {
    console.log('Camera stream or video element not available:', { stream: !!stream, video: !!cameraVideo.value })
  }
}

const switchToAvatar = async () => {
  currentMode.value = 'avatar'
  isPlaying.value = true
}

const togglePlayback = () => {
  isPlaying.value = !isPlaying.value
  
  if (avatarVideo.value) {
    if (isPlaying.value) {
      avatarVideo.value.play()
    } else {
      avatarVideo.value.pause()
    }
  }
}

const restartPresentation = () => {
  currentSlideIndex.value = 0
  isPlaying.value = true
  loadCurrentVideo()
  
  if (avatarVideo.value) {
    avatarVideo.value.currentTime = 0
    avatarVideo.value.play()
  }
}

const nextSlide = () => {
  if (currentSlideIndex.value < (presentationData.value?.slides.length || 0) - 1) {
    currentSlideIndex.value++
    loadCurrentVideo()
  }
}

const previousSlide = () => {
  if (currentSlideIndex.value > 0) {
    currentSlideIndex.value--
    loadCurrentVideo()
  }
}

const loadCurrentVideo = () => {
  if (presentationData.value?.videoUrls && presentationData.value.videoUrls[currentSlideIndex.value]) {
    const videoUrl = presentationData.value.videoUrls[currentSlideIndex.value]
    // Handle both placeholder URLs and actual video URLs
    if (videoUrl && videoUrl !== null && !videoUrl.startsWith('/api/generated/')) {
      // This is a real video URL from the batch generation (TopView URLs)
      currentVideoUrl.value = videoUrl
      console.log(`Loading video for slide ${currentSlideIndex.value + 1}: ${videoUrl}`)
    } else {
      // This is a placeholder URL or null, we'll show a message or handle it differently
      currentVideoUrl.value = ''
      console.log(`Video for slide ${currentSlideIndex.value + 1} is not yet available or still generating`)
    }
  } else {
    currentVideoUrl.value = ''
  }
}

const loadMockData = () => {
  // No mock data - show error instead
  error.value = 'No presentation data available. Please generate content first.'
  presentationData.value = null
}

const onVideoEnd = () => {
  // Auto-advance to next slide when video ends
  if (currentSlideIndex.value < (presentationData.value?.slides.length || 0) - 1) {
    nextSlide()
  } else {
    // End of presentation
    isPlaying.value = false
  }
}


const loadPresentation = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    // Load presentation data from sessionStorage (passed from workflow)
    const storedData = sessionStorage.getItem('presentationData')
    
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData)
        presentationData.value = {
          slides: parsedData.slides || [],
          videoUrls: parsedData.videoUrls || [],
          script: parsedData.script || ''
        }
        console.log('Loaded presentation data from workflow:', presentationData.value)
      } catch (parseError) {
        console.error('Failed to parse presentation data:', parseError)
        // Fall back to mock data
        loadMockData()
      }
    } else {
      console.log('No presentation data found, using mock data')
      // Fall back to mock data if no data is available
      loadMockData()
    }
    
    // Load first video
    loadCurrentVideo()
    
    // Check if camera is already connected from workflow
    if (camera.hasCameraAccess.value) {
      console.log('Camera already connected from workflow')
      const stream = camera.getCameraStream()
      if (stream && cameraVideo.value) {
        cameraVideo.value.srcObject = stream
      }
    } else {
      console.log('Camera not connected, will connect when needed')
    }
    
    isLoading.value = false
  } catch (err) {
    console.error('Failed to load presentation:', err)
    error.value = 'Failed to load presentation data'
    isLoading.value = false
  }
}

const retryLoad = () => {
  error.value = null
  loadPresentation()
}

const onQuestionResponse = (question: string, response: string) => {
  console.log('Question received:', question)
  console.log('Response generated:', response)
  
  // You could add logic here to:
  // - Display the response on screen
  // - Save the Q&A to a log
  // - Trigger additional presentation actions
  // - Send the response to the avatar for speaking
  
  // For now, just log it
  console.log('Q&A session:', { question, response })
}

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case ' ':
      event.preventDefault()
      togglePlayback()
      break
    case 'ArrowRight':
      event.preventDefault()
      nextSlide()
      break
    case 'ArrowLeft':
      event.preventDefault()
      previousSlide()
      break
    case '1':
      event.preventDefault()
      switchToHuman()
      break
    case '2':
      event.preventDefault()
      switchToAvatar()
      break
    case 'r':
    case 'R':
      event.preventDefault()
      showRecordingPanel.value = !showRecordingPanel.value
      break
  }
}

// Lifecycle
onMounted(async () => {
  await loadPresentation()
  
  // Add keyboard event listener
  document.addEventListener('keydown', handleKeydown)
  
  // Auto-start avatar mode
  setTimeout(() => {
    switchToAvatar()
  }, 1000)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  
  // Note: We don't disconnect the camera here because it's shared
  // The camera will be cleaned up when the app unmounts
})

// Watch for slide changes
watch(currentSlideIndex, (newIndex) => {
  console.log(`Switched to slide ${newIndex + 1}`)
  loadCurrentVideo()
})

// Watch for mode changes
watch(currentMode, (newMode) => {
  console.log(`Switched to ${newMode} mode`)
  if (newMode === 'human' && camera.hasCameraAccess.value) {
    // Ensure camera stream is set when switching to human mode
    const stream = camera.getCameraStream()
    if (stream && cameraVideo.value) {
      cameraVideo.value.srcObject = stream
      console.log('Camera stream set on mode switch')
    }
  }
})

// Watch for camera access changes
watch(() => camera.hasCameraAccess.value, (hasAccess) => {
  console.log('Camera access changed:', hasAccess)
  if (hasAccess && currentMode.value === 'human') {
    const stream = camera.getCameraStream()
    if (stream && cameraVideo.value) {
      cameraVideo.value.srcObject = stream
      console.log('Camera stream set on access change')
    }
  }
})
</script>

<style scoped>
/* Fullscreen styles */
:deep(body) {
  overflow: hidden;
}

/* Custom video controls */
video::-webkit-media-controls {
  display: none;
}

video::-webkit-media-controls-panel {
  display: none;
}

video::-webkit-media-controls-play-button {
  display: none;
}

video::-webkit-media-controls-start-playback-button {
  display: none;
}
</style>
