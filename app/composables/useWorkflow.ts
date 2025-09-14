import type { Ref } from 'vue'
import { useCamera } from './useCamera'

export interface UploadData {
  pptFile: File | null
  faceFile: File | null
  voiceFile: File | null
}

export interface UploadStatus {
  ppt: 'idle' | 'uploading' | 'success' | 'error'
  face: 'idle' | 'uploading' | 'success' | 'error'
  voice: 'idle' | 'uploading' | 'success' | 'error'
}

export interface GenerationOptions {
  style: string
  language: string
  duration: number
  humorLevel: number
}

export interface GenerationProgress {
  slides: boolean
  script: boolean
  voice: boolean
  avatar: boolean
}

export interface GenerationResults {
  script: string
  slides: any[]
  videoUrls: string[]
  voiceId: string
  videoFileId: string
}

export interface PresentationSettings {
  avatarPosition: string
  avatarSize: number
  autoSwitchTime: number
}

export interface WorkflowStep {
  id: string
  title: string
}

export const useWorkflow = () => {
  // Use shared camera state
  const camera = useCamera()
  
  // State
  const currentStep = ref(0)
  const isLoading = ref(true)
  const isProcessing = ref(false)
  const isGenerating = ref(false)
  const isPresenting = ref(false)
  const error = ref<string | null>(null)

  const uploadData = ref<UploadData>({
    pptFile: null,
    faceFile: null,
    voiceFile: null
  })

  const uploadStatus = ref<UploadStatus>({
    ppt: 'idle',
    face: 'idle',
    voice: 'idle'
  })

  const voiceChoice = ref<'upload' | 'existing'>('upload')

  const uploadedFiles = ref({
    ppt: { blob: '', url: '' },
    face: { blob: '', url: '' },
    voice: { blob: '', url: '' }
  })

  const generationOptions = ref<GenerationOptions>({
    style: 'professional',
    language: 'en-US',
    duration: 5,
    humorLevel: 5
  })

  const generationProgress = ref<GenerationProgress>({
    slides: false,
    script: false,
    voice: false,
    avatar: false
  })

  const generationResults = ref<GenerationResults | null>(null)

  const presentationSettings = ref<PresentationSettings>({
    avatarPosition: 'bottom-right',
    avatarSize: 30,
    autoSwitchTime: 0
  })

  const workflowSteps: WorkflowStep[] = [
    { id: 'upload', title: 'Upload Materials' },
    { id: 'generate', title: 'Generate Content' }
  ]

  // Computed
  const canProceedToNextStep = computed(() => {
    if (currentStep.value === 0) {
      const pptValid = uploadStatus.value.ppt === 'success'
      const faceValid = uploadStatus.value.face === 'success'
      const voiceValid = voiceChoice.value === 'existing' || uploadStatus.value.voice === 'success'
      return pptValid && faceValid && voiceValid
    }
    return true
  })

  const overallProgress = computed(() => {
    const steps = Object.values(generationProgress.value)
    const completed = steps.filter(Boolean).length
    return (completed / steps.length) * 100
  })

  // Methods
  const handleFileUpload = async (type: keyof UploadStatus) => {
    const file = uploadData.value[`${type}File` as keyof UploadData] as File
    if (!file) return

    uploadStatus.value[type] = 'uploading'
    
    try {
      const form = new FormData()
      form.append('file', file)
      
      const response = await $fetch(`/api/upload/${type}`, {
        method: 'POST',
        body: form
      }) as { ok: boolean; blob: string; url: string }
      
      if (response.ok) {
        uploadStatus.value[type] = 'success'
        uploadedFiles.value[type] = {
          blob: response.blob,
          url: response.url
        }
      } else {
        uploadStatus.value[type] = 'error'
      }
    } catch (error) {
      console.error(`Upload error for ${type}:`, error)
      uploadStatus.value[type] = 'error'
    }
  }

  const nextStep = () => {
    if (currentStep.value < workflowSteps.length - 1) {
      currentStep.value++
    }
  }

  const previousStep = () => {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  const generateContent = async () => {
    isGenerating.value = true
    error.value = null
    
    try {
      console.log('Starting presentation generation with files:', {
        ppt: uploadedFiles.value.ppt.blob,
        face: uploadedFiles.value.face.blob,
        voice: uploadedFiles.value.voice.blob,
        style: generationOptions.value.style
      })
      
      // First, test if backend is running
      try {
        const healthCheck = await $fetch('/api/health')
        console.log('Backend health check:', healthCheck)
      } catch (healthError) {
        console.error('Backend not running or not accessible:', healthError)
        throw new Error('Backend server is not running. Please start the backend server first.')
      }
      
      // Use the full generation endpoint which now includes video generation
      console.log('Starting full presentation generation with video creation...')
      console.log('Files being sent:', {
        ppt_blob: uploadedFiles.value.ppt.blob,
        face_blob: uploadedFiles.value.face.blob,
        voice_blob: voiceChoice.value === 'upload' ? uploadedFiles.value.voice.blob : null,
        voice_id: voiceChoice.value === 'existing' ? '7649e9a20ba74165aa6b7873cd95e303' : null,
        voice_choice: voiceChoice.value,
        style: generationOptions.value.style
      })
      const response = await $fetch('/api/generate/presentation', {
        method: 'POST',
        body: {
          ppt_blob: uploadedFiles.value.ppt.blob,
          face_blob: uploadedFiles.value.face.blob,
          voice_blob: voiceChoice.value === 'upload' ? uploadedFiles.value.voice.blob : null,
          voice_id: voiceChoice.value === 'existing' ? '7649e9a20ba74165aa6b7873cd95e303' : null,
          voice_choice: voiceChoice.value,
          style: generationOptions.value.style
        }
      }) as { 
        success: boolean; 
        presentation: { 
          slides: any[]; 
          scripts: string[]; 
          video_urls: string[];
          voice_id: string;
          video_file_id: string;
        } 
      }
      
      console.log('Generation response:', response)
      
      if (response.success) {
        // Handle the response from the updated backend that now includes real video URLs
        const videoUrls = response.presentation.video_urls || []
        const scripts = response.presentation.scripts || []
        const voiceId = response.presentation.voice_id || 'demo_voice_fallback_123'
        const videoFileId = response.presentation.video_file_id || 'demo_video_fallback_456'
        
        generationResults.value = {
          script: scripts.join('\n\n'),
          slides: response.presentation.slides,
          videoUrls: videoUrls,
          voiceId: voiceId,
          videoFileId: videoFileId
        }
        
        // Mark all progress as complete
        generationProgress.value = {
          slides: true,
          script: true,
          voice: true,
          avatar: true
        }
        
        isGenerating.value = false
        console.log('Presentation generated successfully with videos:', {
          slides: response.presentation.slides.length,
          videos: videoUrls.length,
          scripts: scripts.length,
          voiceId: voiceId,
          videoFileId: videoFileId
        })
        console.log('Video URLs:', videoUrls)
        console.log('Voice ID:', voiceId)
        console.log('Video File ID:', videoFileId)
      } else {
        throw new Error('Generation failed')
      }
    } catch (err) {
      console.error('Generation error:', err)
      console.error('Full error details:', err)
      
      // Don't fall back to mock data - let the user know there's an issue
      isGenerating.value = false
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      error.value = `Failed to generate presentation: ${errorMessage}`
      
      // Show error in UI
      console.error('Presentation generation failed. Check backend logs and API connectivity.')
    }
  }

  const togglePresentation = () => {
    isPresenting.value = !isPresenting.value
  }

  const switchToHuman = () => {
    console.log('Switching to human view')
  }

  const switchToAvatar = () => {
    console.log('Switching to avatar view')
  }

  const connectCamera = async () => {
    return await camera.connectCamera()
  }

  const testCamera = async () => {
    return await camera.testCamera()
  }

  const startPresentation = () => {
    console.log('Starting live presentation')
    
    // Pass the generation results to the presentation page
    if (generationResults.value) {
      // Store the presentation data in sessionStorage for the presentation page to access
      const presentationData = {
        ...generationResults.value,
        pptUrl: uploadedFiles.value.ppt.url,
        videoBlob: uploadedFiles.value.face.blob,
        voiceId: generationResults.value.voiceId,
        videoFileId: generationResults.value.videoFileId
      }
      if (process.client) {
        sessionStorage.setItem('presentationData', JSON.stringify(presentationData))
      }
      console.log('Presentation data stored:', presentationData)
    }
    
    navigateTo('/presentation')
  }

  const restoreState = (stepNumber: number) => {
    currentStep.value = stepNumber
    
    if (stepNumber >= 1) {
      // Don't restore hardcoded data - let the user regenerate if needed
      console.log('Restoring to step', stepNumber, '- user should regenerate content')
    }
  }

  return {
    // State
    currentStep,
    isLoading,
    isProcessing,
    isGenerating,
    isPresenting,
    error,
    isConnectingCamera: camera.isConnectingCamera,
    hasCameraAccess: camera.hasCameraAccess,
    uploadData,
    uploadStatus,
    uploadedFiles,
    voiceChoice,
    generationOptions,
    generationProgress,
    generationResults,
    presentationSettings,
    workflowSteps,
    
    // Computed
    canProceedToNextStep,
    overallProgress,
    
    // Methods
    handleFileUpload,
    nextStep,
    previousStep,
    generateContent,
    togglePresentation,
    switchToHuman,
    switchToAvatar,
    connectCamera,
    testCamera,
    startPresentation,
    restoreState
  }
}
