import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test setup...');
  
  // Check if we're in mock mode
  if (process.env.E2E_MOCKS === 'true') {
    console.log('📡 E2E_MOCKS enabled - using mock data');
  } else {
    console.log('⚠️  E2E_MOCKS not enabled - tests may fail without real API');
  }

  // Verify the application is running
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    const baseURL = config.projects[0].use?.baseURL || 'http://localhost:3000';
    console.log(`🔍 Checking application at ${baseURL}...`);
    
    await page.goto(baseURL, { waitUntil: 'networkidle' });
    
    // Check if the app loaded successfully
    const title = await page.title();
    if (title.includes('Vantage AI') || title.includes('Vantage')) {
      console.log('✅ Application is running and accessible');
    } else {
      throw new Error(`Unexpected page title: ${title}`);
    }
    
  } catch (error) {
    console.error('❌ Failed to connect to application:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('✅ E2E test setup completed');
}

export default globalSetup;
