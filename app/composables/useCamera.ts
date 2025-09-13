import type { Ref } from 'vue'

export const useCamera = () => {
  // Global camera state
  const hasCameraAccess = ref(false)
  const isConnectingCamera = ref(false)
  const cameraStream = ref<MediaStream | null>(null)
  const cameraError = ref<string | null>(null)

  const connectCamera = async (): Promise<boolean> => {
    isConnectingCamera.value = true
    cameraError.value = null
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      })
      
      cameraStream.value = stream
      hasCameraAccess.value = true
      console.log('Camera connected successfully')
      return true
      
    } catch (error) {
      console.error('Camera access failed:', error)
      cameraError.value = 'Camera access denied or not available'
      hasCameraAccess.value = false
      return false
    } finally {
      isConnectingCamera.value = false
    }
  }

  const disconnectCamera = () => {
    if (cameraStream.value) {
      cameraStream.value.getTracks().forEach(track => track.stop())
      cameraStream.value = null
    }
    hasCameraAccess.value = false
    cameraError.value = null
  }

  const testCamera = async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      })
      
      console.log('Camera test successful:', stream)
      
      // Stop the test stream
      stream.getTracks().forEach(track => track.stop())
      
      return true
    } catch (error) {
      console.error('Camera test failed:', error)
      return false
    }
  }

  const getCameraStream = (): MediaStream | null => {
    return cameraStream.value
  }

  // Cleanup on app unmount
  if (process.client) {
    onBeforeUnmount(() => {
      disconnectCamera()
    })
  }

  return {
    // State
    hasCameraAccess: readonly(hasCameraAccess),
    isConnectingCamera: readonly(isConnectingCamera),
    cameraStream: readonly(cameraStream),
    cameraError: readonly(cameraError),
    
    // Methods
    connectCamera,
    disconnectCamera,
    testCamera,
    getCameraStream
  }
}
