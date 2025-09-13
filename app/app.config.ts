export default defineAppConfig({
	ui: {
		button: {
			slots: {
				base: [
					'rounded-md font-medium inline-flex items-center cursor-pointer disabled:cursor-not-allowed aria-disabled:cursor-not-allowed disabled:opacity-75 aria-disabled:opacity-75',
					'transition-colors'
				]
			}
		},
	}
})
