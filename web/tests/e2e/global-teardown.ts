import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting E2E test teardown...');
  
  // Clean up any test data or resources if needed
  // For now, we're just logging completion
  
  console.log('✅ E2E test teardown completed');
}

export default globalTeardown;
