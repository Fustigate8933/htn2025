export default defineEventHandler(async (event) => {
  const body = await readMultipartFormData(event)

  if (!body || !body.length) {
    throw createError({ statusCode: 400, statusMessage: "No file uploaded" })
  }

  const file = body[0]
  const backendUrl = "http://localhost:8000/upload/voice"

  const form = new FormData()
  form.append("file", new Blob([file.data], { type: file.type }), file.filename)

  const res = await $fetch(backendUrl, {
    method: "POST",
    body: form as any
  })

  return res
})

