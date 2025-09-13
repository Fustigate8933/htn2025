export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { ppt_blob, ppt_url } = body

  if (!ppt_blob) {
    throw createError({
      statusCode: 400,
      statusMessage: "PPT blob is required"
    })
  }

  try {
    const backendUrl = "http://localhost:8000/simple/process-ppt"

    const response = await $fetch(backendUrl, {
      method: "POST",
      body: { 
        ppt_blob,
        ppt_url 
      }
    })

    return response
  } catch (error) {
    console.error('Simple PPT processing error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: "Failed to process PPT file"
    })
  }
})
