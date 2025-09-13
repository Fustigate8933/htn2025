export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const taskId = query.taskId as string
  
  if (!taskId) {
    throw createError({ 
      statusCode: 400, 
      statusMessage: "Missing taskId parameter" 
    })
  }

  try {
    const backendUrl = `http://localhost:8000/batch/status/${taskId}`
    
    const response = await $fetch(backendUrl, {
      method: "GET"
    })

    return response
  } catch (error) {
    console.error('Batch status check error:', error)
    throw createError({ 
      statusCode: 500, 
      statusMessage: "Failed to check batch status" 
    })
  }
})

