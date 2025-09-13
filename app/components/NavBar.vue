<template>
	<div class="flex justify-between py-3 w-full h-full">
		<NuxtLink to="/">
			<h1 class="font-bold text-2xl">
				HTN
			</h1>
		</NuxtLink>
		<UButton class="hover:cursor-pointer text-center flex justify-center items-center" :icon="colorMode.value === 'dark' ? 'line-md:sunny-outline-loop' : 'line-md:moon-alt-loop'" size="md" @click="toggleTheme" />
	</div>
</template>

<script setup lang="ts">
const colorMode = useColorMode()

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<style scoped>

</style>
