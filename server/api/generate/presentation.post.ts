export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { ppt_blob, face_blob, voice_blob, style } = body

  if (!ppt_blob || !face_blob || !voice_blob) {
    throw createError({ 
      statusCode: 400, 
      statusMessage: "Missing required file blobs" 
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

