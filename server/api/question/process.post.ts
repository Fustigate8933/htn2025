export default defineEventHandler(async (event) => {
  try {
    // Parse the multipart form data
    const formData = await readMultipartFormData(event)
    
    if (!formData || formData.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No audio file provided'
      })
    }
    
    // Find the audio file in the form data
    const audioFile = formData.find(field => field.name === 'audio')
    
    if (!audioFile || !audioFile.data) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Audio file not found in request'
      })
    }
    
    // Validate audio file size
    if (audioFile.data.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Audio file is empty'
      })
    }
    
    console.log(`Audio file received: ${audioFile.data.length} bytes, type: ${audioFile.type}`)
    
    // Find the PPT URL in the form data
    const pptUrlField = formData.find(field => field.name === 'ppt_url')
    const pptUrl = pptUrlField ? pptUrlField.data.toString() : null
    
    // Find the voice ID in the form data
    const voiceIdField = formData.find(field => field.name === 'voice_id')
    const voiceId = voiceIdField ? voiceIdField.data.toString() : null
    
    // Find the video file ID in the form data
    const videoFileIdField = formData.find(field => field.name === 'video_file_id')
    const videoFileId = videoFileIdField ? videoFileIdField.data.toString() : null
    
    // Find the slide number in the form data
    const slideNumberField = formData.find(field => field.name === 'slide_number')
    const slideNumber = slideNumberField ? parseInt(slideNumberField.data.toString()) : 0
    
    // Create FormData to forward to backend
    const backendFormData = new FormData()
    const audioBlob = new Blob([audioFile.data], { type: audioFile.type || 'audio/webm' })
    backendFormData.append('audio', audioBlob, 'question.webm')
    
    // Add PPT URL if available
    if (pptUrl) {
      backendFormData.append('ppt_url', pptUrl)
    }
    
    // Add voice ID if available
    if (voiceId) {
      backendFormData.append('voice_id', voiceId)
    }
    
    // Add video file ID if available
    if (videoFileId) {
      backendFormData.append('video_file_id', videoFileId)
    }
    
    // Add slide number
    backendFormData.append('slide_number', slideNumber.toString())
    
    // Forward to backend for processing
    const backendUrl = 'http://localhost:8000/questions/audio-to-text'
    
    // Log the FormData contents for debugging
    console.log('FormData contents:')
    for (const [key, value] of backendFormData.entries()) {
      if (value instanceof File || value instanceof Blob) {
        console.log(`${key}: [File/Blob] ${value.size} bytes, type: ${value.type}`)
      } else {
        console.log(`${key}: ${value}`)
      }
    }
    
    const response = await $fetch(backendUrl, {
      method: 'POST',
      body: backendFormData
      // Don't set Content-Type header - let the browser set it automatically for FormData
    })
    
    if (response.success && response.transcript && response.response) {
      return {
        success: true,
        transcript: response.transcript,
        response: response.response,
        audio_url: response.url
      }
    } else {
      throw createError({
        statusCode: 500,
        statusMessage: 'Failed to process audio'
      })
    }
    
  } catch (error) {
    console.error('Question processing error:', error)
    
    // Log more details about the error
    if (error.data) {
      console.error('Backend error response:', error.data)
    }
    if (error.statusCode) {
      console.error('Backend status code:', error.statusCode)
    }
    if (error.statusMessage) {
      console.error('Backend status message:', error.statusMessage)
    }
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to process question audio'
    })
  }
})
