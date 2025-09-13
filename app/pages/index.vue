<template>
	<div id="index-wrapper" class="flex flex-col items-center gap-10">
		<h1 class="font-bold text-4xl text-(--ui-primary)">
			Hack the stage
		</h1>

		<p class="text-lg max-w-3xl text-center">
			Transform your slide deck/powerpoint presentations with AI avatars. Upload your slides, face, and voice to create personalized presentation videos.
		</p>

		<div class="flex gap-10 w-full">
			<UCard variant="outline">
				<template #header>
					<div class="flex gap-4 items-center">
						<UIcon name="file-icons:microsoft-powerpoint" class="size-5 text-[var(--accent)]" />
						<h1 class="font-bold text-lg">Slide deck</h1>
					</div>
					<p>Your slide deck</p>
				</template>
				<div class="flex flex-col gap-2">
					<UFileUpload
						v-model="pptFile"
						class="w-62 h-90 hover:cursor-pointer"
						label="Drop your file here"
						description=".PPTX (Max 2MB)"
						:highlight="true"
					/>
				</div>
			</UCard>
			<UCard variant="outline">
				<template #header>
					<div class="flex gap-4 items-center">
						<UIcon name="iconoir:face-id" class="size-5 text-[var(--accent)]" />
						<h1 class="font-bold text-lg">Face image</h1>
					</div>
					<p>Clear photo of your face</p>
				</template>
				<div class="flex flex-col gap-2 w-full">
					<UFileUpload
						v-model="faceFile"
						class="w-62 h-90 hover:cursor-pointer"
						label="Drop your file here"
						description=".PNG, .JPG, .JPEG (Max 2MB)"
						:highlight="true"
					/>
				</div>
			</UCard>
			<UCard variant="outline">
				<template #header>
					<div class="flex gap-4 items-center">
						<UIcon name="ic:outline-record-voice-over" class="size-5 text-[var(--accent)]" />
						<h1 class="font-bold text-lg">Voice sample</h1>
					</div>
					<p>Audio file for your voice</p>
				</template>
				<div class="flex flex-col gap-2">
					<UFileUpload
						v-model="audioFile"
						class="w-62 h-90 hover:cursor-pointer"
						label="Drop your file here"
						description=".WAV (Max 2MB)"
						:highlight="true"
					/>
				</div>
			</UCard>
		</div>
	</div>
</template>

<script setup lang="ts">
const pptFile = ref(null)
const faceFile = ref(null)
const audioFile = ref(null)
</script>
