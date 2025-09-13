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
    
    // Create FormData to forward to backend
    const backendFormData = new FormData()
    const audioBlob = new Blob([audioFile.data], { type: audioFile.type || 'audio/webm' })
    backendFormData.append('audio', audioBlob, 'question.webm')
    
    // Forward to backend for processing
    const backendUrl = 'http://localhost:8000/questions/audio-to-text'
    
    const response = await $fetch(backendUrl, {
      method: 'POST',
      body: backendFormData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
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
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to process question audio'
    })
  }
})
