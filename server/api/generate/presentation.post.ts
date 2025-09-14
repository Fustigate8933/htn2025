export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { ppt_blob, face_blob, voice_blob, voice_id, voice_choice, style } = body

  if (!ppt_blob || !face_blob) {
    throw createError({ 
      statusCode: 400, 
      statusMessage: "Missing required file blobs (PPT and Face)" 
    })
  }

  // Validate voice requirements based on choice
  if (voice_choice === 'upload' && !voice_blob) {
    throw createError({ 
      statusCode: 400, 
      statusMessage: "Voice blob is required when using upload option" 
    })
  }

  if (voice_choice === 'existing' && !voice_id) {
    throw createError({ 
      statusCode: 400, 
      statusMessage: "Voice ID is required when using existing voice option" 
    })
  }

  try {
    const backendUrl = "http://localhost:8000/generate/presentation"
    
    const response = await $fetch(backendUrl, {
      method: "POST",
      body: { 
        ppt_blob, 
        face_blob, 
        voice_blob, 
        voice_id,
        voice_choice,
        style: style || "professional" 
      }
    })

    return response
  } catch (error) {
    console.error('Presentation generation error:', error)
    throw createError({ 
      statusCode: 500, 
      statusMessage: "Failed to generate presentation" 
    })
  }
})

