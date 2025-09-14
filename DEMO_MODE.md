# Demo Mode Configuration

This project includes a demo mode for showcasing the presentation generation workflow without requiring actual AI processing.

## Demo Mode Features

- **Fake Generation**: Simulates the generation process with a realistic progress bar
- **Predefined Content**: Uses 4 predefined slides with sample content
- **Predefined Videos**: Uses 4 demo videos (1.mp4, 2.mp4, 3.mp4, 4.mp4) from the public directory
- **Progress Simulation**: Runs for approximately 6 seconds with realistic progress steps

## How to Enable/Disable Demo Mode

In `app/composables/useWorkflow.ts`, change the `DEMO_MODE` constant:

```typescript
// Demo mode configuration - set to false for production
const DEMO_MODE = true  // Set to false for production mode
```

## Demo Content

### Slides
- Slide 1: Welcome message
- Slide 2: Fundamental concepts
- Slide 3: Practical applications
- Slide 4: Key takeaways and next steps

### Videos
The demo uses 4 predefined videos located in the `public/` directory:
- `/1.mp4` - Corresponds to Slide 1
- `/2.mp4` - Corresponds to Slide 2
- `/3.mp4` - Corresponds to Slide 3
- `/4.mp4` - Corresponds to Slide 4

## Progress Steps

The demo simulates the following progress steps over 6 seconds:
1. Processing slides (1 second)
2. Generating script (1.5 seconds)
3. Processing voice (2 seconds)
4. Creating avatar videos (1.5 seconds)

Total: 6 seconds

## Switching to Production Mode

To use the actual AI generation:
1. Set `DEMO_MODE = false` in `useWorkflow.ts`
2. Ensure the backend server is running
3. Make sure all required API keys are configured
4. Test with actual file uploads
