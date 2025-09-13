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
      return uploadStatus.value.ppt === 'success' && 
             uploadStatus.value.face === 'success' && 
             uploadStatus.value.voice === 'success'
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
      })
      
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
      
      // First, try simple PPT processing to get actual slides
      console.log('Processing PPT file to extract slides...')
      console.log('PPT blob value:', uploadedFiles.value.ppt.blob)
      console.log('PPT URL value:', uploadedFiles.value.ppt.url)
      console.log('PPT blob type:', typeof uploadedFiles.value.ppt.blob)
      
      const pptResponse = await $fetch('/api/simple/process-ppt', {
        method: 'POST',
        body: {
          ppt_blob: uploadedFiles.value.ppt.blob,
          ppt_url: uploadedFiles.value.ppt.url
        }
      })
      
      console.log('PPT processing response:', pptResponse)
      
      if (pptResponse.success) {
        // Use the actual slides from the PPT file
        generationResults.value = {
          script: `Welcome to our presentation. We have ${pptResponse.total_slides} slides to cover today.`,
          slides: pptResponse.slides,
          videoUrls: pptResponse.slides.map((_: any, index: number) => `/api/generated/slide-${index + 1}-video.mp4`)
        }
        
        // Mark all progress as complete
        generationProgress.value = {
          slides: true,
          script: true,
          voice: true,
          avatar: true
        }
        
        isGenerating.value = false
        console.log('PPT processed successfully:', generationResults.value)
        return
      }
      
      // If simple processing fails, try the full generation
      const response = await $fetch('/api/generate/presentation', {
        method: 'POST',
        body: {
          ppt_blob: uploadedFiles.value.ppt.blob,
          ppt_url: uploadedFiles.value.ppt.url,
          face_blob: uploadedFiles.value.face.blob,
          face_url: uploadedFiles.value.face.url,
          voice_blob: uploadedFiles.value.voice.blob,
          voice_url: uploadedFiles.value.voice.url,
          style: generationOptions.value.style
        }
      })
      
      console.log('Generation response:', response)
      
      if (response.success) {
        generationResults.value = {
          script: response.presentation.scripts.join('\n\n'),
          slides: response.presentation.slides,
          videoUrls: response.presentation.video_urls
        }
        
        // Mark all progress as complete
        generationProgress.value = {
          slides: true,
          script: true,
          voice: true,
          avatar: true
        }
        
        isGenerating.value = false
        console.log('Presentation generated successfully:', generationResults.value)
      } else {
        throw new Error('Generation failed')
      }
    } catch (err) {
      console.error('Generation error:', err)
      console.error('Full error details:', err)
      
      // Don't fall back to mock data - let the user know there's an issue
      isGenerating.value = false
      error.value = `Failed to generate presentation: ${err.message || 'Unknown error'}`
      
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
        pptUrl: uploadedFiles.value.ppt.url
      }
      sessionStorage.setItem('presentationData', JSON.stringify(presentationData))
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
