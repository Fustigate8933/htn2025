<template>
  <div class="max-w-6xl mx-auto">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
        Step 3: Preview & Present
      </h2>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
          <UCard variant="outline" class="h-full">
            <template #header>
              <div class="flex gap-3 items-center">
                <UIcon name="ic:outline-present-to-all" class="size-6 text-purple-500" />
                <h3 class="font-bold text-lg">Presentation View</h3>
              </div>
            </template>
            
            <div class="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <div class="text-center">
                <UIcon name="ic:outline-play-circle" class="size-16 text-gray-400 mx-auto mb-4" />
                <p class="text-gray-600 dark:text-gray-400">
                  Avatar presentation will appear here
                </p>
              </div>
            </div>
            
            <div class="mt-4 flex gap-2 justify-center">
              <UButton variant="outline" @click="$emit('togglePresentation')">
                <UIcon name="ic:outline-play-arrow" class="mr-2" />
                {{ isPresenting ? 'Pause' : 'Play' }}
              </UButton>
              <UButton variant="outline" @click="$emit('switchToHuman')">
                <UIcon name="ic:outline-person" class="mr-2" />
                Switch to Human
              </UButton>
              <UButton variant="outline" @click="$emit('switchToAvatar')">
                <UIcon name="ic:outline-face" class="mr-2" />
                Switch to Avatar
              </UButton>
            </div>
          </UCard>
        </div>

        <div class="space-y-4">
          <UCard variant="outline">
            <template #header>
              <div class="flex gap-3 items-center">
                <UIcon name="ic:outline-control-camera" class="size-6 text-blue-500" />
                <h3 class="font-bold text-lg">Presentation Controls</h3>
              </div>
            </template>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium mb-2">Avatar Position</label>
                <USelect
                  v-model="presentationSettings.avatarPosition"
                  :options="avatarPositionOptions"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium mb-2">Avatar Size</label>
                <URange
                  v-model="presentationSettings.avatarSize"
                  :min="20"
                  :max="80"
                  :step="5"
                />
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Small</span>
                  <span>Large</span>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium mb-2">Auto-switch Timing</label>
                <UInput
                  v-model="presentationSettings.autoSwitchTime"
                  type="number"
                  min="0"
                  placeholder="Seconds (0 = manual)"
                />
              </div>
            </div>
          </UCard>

          <UCard variant="outline">
            <template #header>
              <div class="flex gap-3 items-center">
                <UIcon name="ic:outline-videocam" class="size-6 text-green-500" />
                <h3 class="font-bold text-lg">Camera Controls</h3>
              </div>
            </template>
            
            <div class="space-y-3">
              <UButton 
                block 
                variant="outline" 
                :loading="isConnectingCamera"
                @click="$emit('connectCamera')"
              >
                <UIcon name="ic:outline-videocam" class="mr-2" />
                {{ hasCameraAccess ? 'Camera Connected' : 'Connect Camera' }}
              </UButton>
              
              <div v-if="hasCameraAccess" class="space-y-2">
                <UButton 
                  block 
                  variant="outline" 
                  @click="$emit('switchToHuman')"
                >
                  <UIcon name="ic:outline-person" class="mr-2" />
                  Show Human Camera
                </UButton>
                
                <UButton 
                  block 
                  variant="outline" 
                  @click="$emit('switchToAvatar')"
                >
                  <UIcon name="ic:outline-face" class="mr-2" />
                  Show Avatar Video
                </UButton>
              </div>
              
              <div v-if="!hasCameraAccess" class="text-sm text-gray-500">
                <p>Connect your camera to switch between human and avatar views during presentation.</p>
                <UButton 
                  size="sm" 
                  variant="outline" 
                  @click="$emit('testCamera')"
                  class="mt-2"
                >
                  Test Camera
                </UButton>
              </div>
            </div>
          </UCard>
        </div>
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
          @click="$emit('startPresentation')"
        >
          Start Live Presentation
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface PresentationSettings {
  avatarPosition: string
  avatarSize: number
  autoSwitchTime: number
}

interface Props {
  presentationSettings: PresentationSettings
  isPresenting: boolean
  isConnectingCamera: boolean
  hasCameraAccess: boolean
}

interface Emits {
  (e: 'previous'): void
  (e: 'startPresentation'): void
  (e: 'togglePresentation'): void
  (e: 'switchToHuman'): void
  (e: 'switchToAvatar'): void
  (e: 'connectCamera'): void
  (e: 'testCamera'): void
  (e: 'update:presentationSettings', value: PresentationSettings): void
}

defineProps<Props>()
defineEmits<Emits>()

const avatarPositionOptions = [
  { label: 'Bottom Right', value: 'bottom-right' },
  { label: 'Bottom Left', value: 'bottom-left' },
  { label: 'Top Right', value: 'top-right' },
  { label: 'Top Left', value: 'top-left' },
  { label: 'Center', value: 'center' }
]
</script>
