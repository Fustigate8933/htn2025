<template>
  <LoadingScreen v-if="isLoading" />

  <div v-else class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-8">
      <WorkflowHeader />
      
      <ProgressIndicator 
        :steps="workflowSteps" 
        :current-step="currentStep" 
      />

      <div class="mb-8">
        <UploadStep
          v-if="currentStep === 0"
          v-model:upload-data="uploadData"
          :upload-status="uploadStatus"
          :can-proceed="canProceedToNextStep"
          :is-processing="isProcessing"
          @next="nextStep"
          @upload="handleFileUpload"
        />

        <GenerateStep
          v-if="currentStep === 1"
          v-model:generation-options="generationOptions"
          :generation-progress="generationProgress"
          :generation-results="generationResults"
          :is-generating="isGenerating"
          :overall-progress="overallProgress"
          :error="error"
          @previous="previousStep"
          @next="nextStep"
          @retry="generateContent"
        />

        <PreviewStep
          v-if="currentStep === 2"
          v-model:presentation-settings="presentationSettings"
          :is-presenting="isPresenting"
          :is-connecting-camera="isConnectingCamera"
          :has-camera-access="hasCameraAccess"
          @previous="previousStep"
          @start-presentation="startPresentation"
          @toggle-presentation="togglePresentation"
          @switch-to-human="switchToHuman"
          @switch-to-avatar="switchToAvatar"
          @connect-camera="connectCamera"
          @test-camera="testCamera"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LoadingScreen from '~/components/LoadingScreen.vue'
import WorkflowHeader from '~/components/WorkflowHeader.vue'
import ProgressIndicator from '~/components/ProgressIndicator.vue'
import UploadStep from '~/components/UploadStep.vue'
import GenerateStep from '~/components/GenerateStep.vue'
import PreviewStep from '~/components/PreviewStep.vue'

import { useWorkflow } from '~/composables/useWorkflow'

const {
  currentStep,
  isLoading,
  isProcessing,
  isGenerating,
  isPresenting,
  error,
  isConnectingCamera,
  hasCameraAccess,
  uploadData,
  uploadStatus,
  generationOptions,
  generationProgress,
  generationResults,
  presentationSettings,
  workflowSteps,
  
  canProceedToNextStep,
  overallProgress,
  
  handleFileUpload,
  nextStep,
  previousStep,
  generateContent,
  togglePresentation,
  switchToHuman,
  switchToAvatar,
  connectCamera,
  testCamera,
  startPresentation,
  restoreState
} = useWorkflow()

onMounted(() => {
  setTimeout(() => {
    isLoading.value = false
    
    const route = useRoute()
    const stepParam = route.query.step
    if (stepParam && typeof stepParam === 'string') {
      const stepNumber = parseInt(stepParam)
      if (stepNumber >= 0 && stepNumber <= 2) {
        restoreState(stepNumber)
      }
    }
  }, 1500)
})

watch(currentStep, (newStep) => {
  if (newStep === 1) {
    generateContent()
  }
})
</script>
