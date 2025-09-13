<template>
  <div class="max-w-4xl mx-auto">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
        Step 2: Generate Your Presentation
      </h2>
      
      <div class="space-y-6">
        <UCard variant="outline">
          <template #header>
            <div class="flex gap-3 items-center">
              <UIcon name="ic:outline-settings" class="size-6 text-blue-500" />
              <h3 class="font-bold text-lg">Generation Options</h3>
            </div>
          </template>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">Presentation Style</label>
              <USelect
                v-model="generationOptions.style"
                :options="styleOptions"
                placeholder="Select style"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">Language</label>
              <USelect
                v-model="generationOptions.language"
                :options="languageOptions"
                placeholder="Select language"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">Duration (minutes)</label>
              <UInput
                v-model="generationOptions.duration"
                type="number"
                min="1"
                max="30"
                placeholder="5-10 minutes recommended"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">Humor Level</label>
              <URange
                v-model="generationOptions.humorLevel"
                :min="1"
                :max="10"
                :step="1"
              />
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>Professional</span>
                <span>Entertaining</span>
              </div>
            </div>
          </div>
        </UCard>

        <UCard v-if="isGenerating" variant="outline">
          <template #header>
            <div class="flex gap-3 items-center">
              <UIcon name="line-md:loading-loop" class="size-6 text-blue-500 animate-spin" />
              <h3 class="font-bold text-lg">Generating Your Presentation</h3>
            </div>
          </template>
          
          <div class="">
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span>Processing slides...</span>
                <span v-if="generationProgress.slides" class="text-green-600">✓</span>
              </div>
              <div class="flex justify-between text-sm">
                <span>Generating script...</span>
                <span v-if="generationProgress.script" class="text-green-600">✓</span>
              </div>
              <div class="flex justify-between text-sm">
                <span>Creating voice clone...</span>
                <span v-if="generationProgress.voice" class="text-green-600">✓</span>
              </div>
              <div class="flex justify-between text-sm">
                <span>Generating avatar videos...</span>
                <span v-if="generationProgress.avatar" class="text-green-600">✓</span>
              </div>
            </div>
            
            <UProgress 
              :value="overallProgress" 
              :max="100"
              class="w-full"
            />
            <p class="text-sm text-gray-600 dark:text-gray-400">
              This may take 2-5 minutes depending on content length
            </p>
          </div>
        </UCard>

        <UCard v-if="error" variant="outline" class="border-red-200">
          <template #header>
            <div class="flex gap-3 items-center">
              <UIcon name="ic:outline-error" class="size-6 text-red-500" />
              <h3 class="font-bold text-lg text-red-600">Generation Failed</h3>
            </div>
          </template>
          
          <div class="">
            <p class="text-red-600">{{ error }}</p>
            <UButton @click="$emit('retry')" color="red" variant="outline">
              Try Again
            </UButton>
          </div>
        </UCard>

        <UCard v-if="generationResults" variant="outline">
          <template #header>
            <div class="flex gap-3 items-center">
              <UIcon name="line-md:check-circle" class="size-6 text-green-500" />
              <h3 class="font-bold text-lg">Generation Complete!</h3>
            </div>
          </template>
          
          <div class="">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h4 class="font-medium mb-2">Generated Script</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
                  {{ generationResults.script }}
                </p>
                <UButton size="sm" variant="outline" class="mt-2">
                  View Full Script
                </UButton>
              </div>
              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h4 class="font-medium mb-2">Avatar Videos</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ generationResults.slides.length }} slides generated
                </p>
                <UButton size="sm" variant="outline" class="mt-2">
                  Preview Videos
                </UButton>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <div class="mt-6 flex justify-between">
        <UButton 
          variant="outline" 
          @click="$emit('previous')"
        >
          Previous
        </UButton>
        <UButton 
          color="primary" 
          :disabled="!generationResults"
          @click="$emit('startPresentation')"
        >
          Start Presentation
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface GenerationOptions {
  style: string
  language: string
  duration: number
  humorLevel: number
}

interface GenerationProgress {
  slides: boolean
  script: boolean
  voice: boolean
  avatar: boolean
}

interface GenerationResults {
  script: string
  slides: any[]
  videoUrls: string[]
}

interface Props {
  generationOptions: GenerationOptions
  generationProgress: GenerationProgress
  generationResults: GenerationResults | null
  isGenerating: boolean
  overallProgress: number
  error: string | null
}

interface Emits {
  (e: 'previous'): void
  (e: 'next'): void
  (e: 'retry'): void
  (e: 'startPresentation'): void
  (e: 'update:generationOptions', value: GenerationOptions): void
}

defineProps<Props>()
defineEmits<Emits>()

const styleOptions = [
  { label: 'Professional', value: 'professional' },
  { label: 'Casual', value: 'casual' },
  { label: 'Humorous', value: 'humorous' },
  { label: 'Academic', value: 'academic' },
  { label: 'Sales', value: 'sales' }
]

const languageOptions = [
  { label: 'English (US)', value: 'en-US' },
  { label: 'English (UK)', value: 'en-GB' },
  { label: 'Spanish', value: 'es-ES' },
  { label: 'French', value: 'fr-FR' },
  { label: 'German', value: 'de-DE' },
  { label: 'Chinese (Simplified)', value: 'zh-CN' }
]
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
