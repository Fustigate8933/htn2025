export default defineEventHandler(async (event) => {
  try {
    const backendUrl = "http://localhost:8000/health/"
    
    const response = await $fetch(backendUrl)
    
    return {
      success: true,
      backend: response,
      message: "Backend is running"
    }
  } catch (error) {
    console.error('Backend health check failed:', error)
    throw createError({
      statusCode: 503,
      statusMessage: "Backend server is not running or not accessible"
    })
  }
})
