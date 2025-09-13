export default defineEventHandler(async (event) => {
  const formData = await readMultipartFormData(event)
  
  if (!formData) {
    throw createError({ 
      statusCode: 400, 
      statusMessage: "No form data provided" 
    })
  }

  // Extract form data
  let audioFile: any = null
  let videoFile: any = null
  let texts: string = ''
  let maxWorkers: string = '3'
  let noticeUrl: string | undefined = undefined

  for (const field of formData) {
    if (field.name === 'audio_file' && field.data) {
      audioFile = field
    } else if (field.name === 'video_file' && field.data) {
      videoFile = field
    } else if (field.name === 'texts' && field.data) {
      texts = field.data.toString()
    } else if (field.name === 'max_workers' && field.data) {
      maxWorkers = field.data.toString()
    } else if (field.name === 'notice_url' && field.data) {
      noticeUrl = field.data.toString()
    }
  }

  if (!audioFile || !videoFile || !texts) {
    throw createError({ 
      statusCode: 400, 
      statusMessage: "Missing required fields: audio_file, video_file, texts" 
    })
  }

  try {
    const backendUrl = "http://localhost:8000/batch/batch-videos"
    
    // Create form data for backend
    const backendFormData = new FormData()
    backendFormData.append('audio_file', new Blob([audioFile.data], { type: audioFile.type }), audioFile.filename)
    backendFormData.append('video_file', new Blob([videoFile.data], { type: videoFile.type }), videoFile.filename)
    backendFormData.append('texts', texts)
    backendFormData.append('max_workers', maxWorkers)
    if (noticeUrl) {
      backendFormData.append('notice_url', noticeUrl)
    }

    const response = await $fetch(backendUrl, {
      method: "POST",
      body: backendFormData
    })

    return response
  } catch (error) {
    console.error('Batch video generation error:', error)
    throw createError({ 
      statusCode: 500, 
      statusMessage: "Failed to generate batch videos" 
    })
  }
})

