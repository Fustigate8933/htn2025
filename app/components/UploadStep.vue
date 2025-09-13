<template>
  <div class="max-w-4xl mx-auto">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
        Step 1: Upload Your Materials
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UCard variant="outline" class="h-full">
          <template #header>
            <div class="flex gap-3 items-center">
              <UIcon name="file-icons:microsoft-powerpoint" class="size-6 text-red-500" />
              <h3 class="font-bold text-lg">Slide Deck</h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Your presentation slides</p>
          </template>
          <div class="flex flex-col gap-3">
            <UFileUpload
              v-model="uploadData.pptFile"
              class="w-full h-50 hover:cursor-pointer"
              label="Drop your PPTX file here"
              description=".PPTX (Max 10MB)"
              :highlight="true"
              color="secondary"
              accept=".pptx,.ppt"
              @change="handleFileUpload('ppt')"
            />
            <div v-if="uploadStatus.ppt" class="text-sm">
              <span v-if="uploadStatus.ppt === 'uploading'" class="text-blue-600">
                <UIcon name="line-md:loading-loop" class="inline mr-1" />
                Uploading...
              </span>
              <span v-else-if="uploadStatus.ppt === 'success'" class="text-green-600">
                <UIcon name="line-md:check-circle" class="inline mr-1" />
                Uploaded successfully
              </span>
              <span v-else-if="uploadStatus.ppt === 'error'" class="text-red-600">
                <UIcon name="line-md:close-circle" class="inline mr-1" />
                Upload failed
              </span>
            </div>
          </div>
        </UCard>

        <UCard variant="outline" class="h-full">
          <template #header>
            <div class="flex gap-3 items-center">
              <UIcon name="ic:outline-videocam" class="size-6 text-blue-500" />
              <h3 class="font-bold text-lg">Face Video</h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Short video of your face</p>
          </template>
          <div class="flex flex-col gap-3">
            <UFileUpload
              v-model="uploadData.faceFile"
              class="w-full h-50 hover:cursor-pointer"
              label="Drop your video here"
              description=".MP4, .MOV, .AVI (Max 50MB)"
              :highlight="true"
              color="secondary"
              accept=".mp4,.mov,.avi"
              @change="handleFileUpload('face')"
            />
            <div v-if="uploadStatus.face" class="text-sm">
              <span v-if="uploadStatus.face === 'uploading'" class="text-blue-600">
                <UIcon name="line-md:loading-loop" class="inline mr-1" />
                Uploading...
              </span>
              <span v-else-if="uploadStatus.face === 'success'" class="text-green-600">
                <UIcon name="line-md:check-circle" class="inline mr-1" />
                Uploaded successfully
              </span>
              <span v-else-if="uploadStatus.face === 'error'" class="text-red-600">
                <UIcon name="line-md:close-circle" class="inline mr-1" />
                Upload failed
              </span>
            </div>
          </div>
        </UCard>

        <UCard variant="outline" class="h-full">
          <template #header>
            <div class="flex gap-3 items-center">
              <UIcon name="ic:outline-record-voice-over" class="size-6 text-green-500" />
              <h3 class="font-bold text-lg">Voice Sample</h3>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Audio file for voice cloning</p>
          </template>
          <div class="flex flex-col gap-3">
            <UFileUpload
              v-model="uploadData.voiceFile"
              class="w-full h-50 hover:cursor-pointer"
              label="Drop your audio here"
              description=".WAV, .MP3 (Max 10MB)"
              :highlight="true"
              color="secondary"
              accept=".wav,.mp3"
              @change="handleFileUpload('voice')"
            />
            <div v-if="uploadStatus.voice" class="text-sm">
              <span v-if="uploadStatus.voice === 'uploading'" class="text-blue-600">
                <UIcon name="line-md:loading-loop" class="inline mr-1" />
                Uploading...
              </span>
              <span v-else-if="uploadStatus.voice === 'success'" class="text-green-600">
                <UIcon name="line-md:check-circle" class="inline mr-1" />
                Uploaded successfully
              </span>
              <span v-else-if="uploadStatus.voice === 'error'" class="text-red-600">
                <UIcon name="line-md:close-circle" class="inline mr-1" />
                Upload failed
              </span>
            </div>
          </div>
        </UCard>
      </div>

      <div class="mt-6 flex justify-end">
        <UButton 
          color="primary" 
          :disabled="!canProceed"
          :loading="isProcessing"
          @click="$emit('next')"
        >
          Next: Generate Content
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface UploadData {
  pptFile: File | null
  faceFile: File | null
  voiceFile: File | null
}

interface UploadStatus {
  ppt: 'idle' | 'uploading' | 'success' | 'error'
  face: 'idle' | 'uploading' | 'success' | 'error'
  voice: 'idle' | 'uploading' | 'success' | 'error'
}

interface Props {
  uploadData: UploadData
  uploadStatus: UploadStatus
  canProceed: boolean
  isProcessing: boolean
}

interface Emits {
  (e: 'next'): void
  (e: 'upload', type: keyof UploadStatus): void
  (e: 'update:uploadData', value: UploadData): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleFileUpload = (type: keyof UploadStatus) => {
  emit('upload', type)
}
</script>
