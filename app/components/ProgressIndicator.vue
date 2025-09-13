<template>
  <div class="mb-8">
    <div class="flex items-center justify-center space-x-4">
      <div 
        v-for="(step, index) in steps" 
        :key="step.id"
        class="flex items-center"
      >
        <div 
          :class="[
            'w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium',
            currentStep >= index ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'
          ]"
        >
          {{ index + 1 }}
        </div>
        <span 
          :class="[
            'ml-2 text-sm font-medium',
            currentStep >= index ? 'text-blue-600' : 'text-gray-500'
          ]"
        >
          {{ step.title }}
        </span>
        <div 
          v-if="index < steps.length - 1"
          :class="[
            'w-16 h-0.5 ml-4',
            currentStep > index ? 'bg-blue-600' : 'bg-gray-200'
          ]"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface WorkflowStep {
  id: string
  title: string
}

interface Props {
  steps: WorkflowStep[]
  currentStep: number
}

defineProps<Props>()
</script>
