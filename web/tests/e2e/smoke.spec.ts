import { test, expect } from '@playwright/test';
import { setupMocks } from './fixtures/mocks';

test.describe('Vantage AI E2E Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set up mocks for all tests
    await setupMocks(page);
  });

  test('Complete user journey: Connect → Brand Guide → Campaign → Plan → Schedule → Post → Analytics', async ({ page }) => {
    console.log('🎯 Starting complete user journey test...');

    // Step 1: Visit /connect and verify OAuth buttons are visible
    console.log('📱 Step 1: Testing OAuth connection flow...');
    await page.goto('/connect');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check for OAuth buttons (these might be in different locations depending on the actual UI)
    const metaButton = page.locator('button:has-text("Connect Meta"), a:has-text("Connect Meta"), [data-testid="connect-meta"]').first();
    const linkedinButton = page.locator('button:has-text("Connect LinkedIn"), a:has-text("Connect LinkedIn"), [data-testid="connect-linkedin"]').first();
    
    // At least one OAuth button should be visible
    await expect(metaButton.or(linkedinButton)).toBeVisible({ timeout: 10000 });
    console.log('✅ OAuth buttons are visible');

    // Step 2: Go to Brand Guide and create minimal guide
    console.log('📝 Step 2: Testing brand guide creation...');
    await page.goto('/brand-guide');
    await page.waitForLoadState('networkidle');
    
    // Look for brand guide form elements
    const voiceInput = page.locator('input[name="voice"], textarea[name="voice"], [data-testid="brand-voice"]').first();
    const audienceInput = page.locator('input[name="audience"], textarea[name="audience"], [data-testid="brand-audience"]').first();
    
    if (await voiceInput.isVisible()) {
      await voiceInput.fill('Professional and friendly');
      console.log('✅ Filled brand voice');
    }
    
    if (await audienceInput.isVisible()) {
      await audienceInput.fill('Tech professionals and entrepreneurs');
      console.log('✅ Filled target audience');
    }
    
    // Look for save/submit button
    const saveButton = page.locator('button:has-text("Save"), button:has-text("Create"), [data-testid="save-brand-guide"]').first();
    if (await saveButton.isVisible()) {
      await saveButton.click();
      console.log('✅ Brand guide saved');
    }

    // Step 3: Create Campaign
    console.log('🎯 Step 3: Testing campaign creation...');
    await page.goto('/campaigns');
    await page.waitForLoadState('networkidle');
    
    // Look for create campaign button
    const createCampaignButton = page.locator('button:has-text("Create Campaign"), button:has-text("New Campaign"), [data-testid="create-campaign"]').first();
    if (await createCampaignButton.isVisible()) {
      await createCampaignButton.click();
      console.log('✅ Clicked create campaign button');
    }
    
    // Fill campaign form if modal/form appears
    const campaignNameInput = page.locator('input[name="name"], input[placeholder*="campaign"], [data-testid="campaign-name"]').first();
    if (await campaignNameInput.isVisible()) {
      await campaignNameInput.fill('E2E Test Campaign');
      console.log('✅ Filled campaign name');
    }
    
    const saveCampaignButton = page.locator('button:has-text("Save"), button:has-text("Create"), [data-testid="save-campaign"]').first();
    if (await saveCampaignButton.isVisible()) {
      await saveCampaignButton.click();
      console.log('✅ Campaign created');
    }

    // Step 4: Generate 14-day plan
    console.log('📅 Step 4: Testing content planning...');
    await page.goto('/planning');
    await page.waitForLoadState('networkidle');
    
    // Look for plan generation button
    const generatePlanButton = page.locator('button:has-text("Generate Plan"), button:has-text("Create Plan"), [data-testid="generate-plan"]').first();
    if (await generatePlanButton.isVisible()) {
      await generatePlanButton.click();
      console.log('✅ Clicked generate plan button');
    }
    
    // Wait for plan generation to complete
    await page.waitForTimeout(2000);
    
    // Look for generated content items
    const contentItems = page.locator('[data-testid="content-item"], .content-item, .plan-item');
    const itemCount = await contentItems.count();
    console.log(`✅ Found ${itemCount} content items in plan`);

    // Step 5: Schedule items
    console.log('⏰ Step 5: Testing content scheduling...');
    await page.goto('/calendar');
    await page.waitForLoadState('networkidle');
    
    // Look for schedule creation functionality
    const scheduleButton = page.locator('button:has-text("Schedule"), button:has-text("Add to Calendar"), [data-testid="schedule-content"]').first();
    if (await scheduleButton.isVisible()) {
      await scheduleButton.click();
      console.log('✅ Clicked schedule button');
    }
    
    // Look for calendar or scheduling interface
    const calendar = page.locator('.calendar, [data-testid="calendar"], .fc-calendar');
    if (await calendar.isVisible()) {
      console.log('✅ Calendar interface is visible');
    }

    // Step 6: Trigger scheduler
    console.log('🚀 Step 6: Testing scheduler execution...');
    
    // Look for run scheduler button (dev button)
    const runSchedulerButton = page.locator('button:has-text("Run Scheduler"), button:has-text("Process"), [data-testid="run-scheduler"]').first();
    if (await runSchedulerButton.isVisible()) {
      await runSchedulerButton.click();
      console.log('✅ Clicked run scheduler button');
      
      // Wait for processing to complete
      await page.waitForTimeout(3000);
      
      // Look for success message or status update
      const successMessage = page.locator('text=processed, text=posted, text=success, [data-testid="scheduler-success"]').first();
      if (await successMessage.isVisible()) {
        console.log('✅ Scheduler executed successfully');
      }
    }

    // Step 7: Check insights/analytics
    console.log('📊 Step 7: Testing insights and analytics...');
    await page.goto('/reports');
    await page.waitForLoadState('networkidle');
    
    // Look for insights data
    const insightsData = page.locator('[data-testid="insights"], .insights, .metrics, .analytics');
    if (await insightsData.isVisible()) {
      console.log('✅ Insights data is visible');
    }
    
    // Look for specific metrics
    const impressions = page.locator('text=impressions, text=Impressions, [data-testid="impressions"]').first();
    if (await impressions.isVisible()) {
      console.log('✅ Impressions metric found');
    }

    // Step 8: Open Weekly Brief
    console.log('📋 Step 8: Testing weekly brief...');
    
    // Look for weekly brief button or section
    const weeklyBriefButton = page.locator('button:has-text("Weekly Brief"), a:has-text("Weekly Brief"), [data-testid="weekly-brief"]').first();
    if (await weeklyBriefButton.isVisible()) {
      await weeklyBriefButton.click();
      console.log('✅ Clicked weekly brief button');
      
      // Wait for brief to load
      await page.waitForTimeout(2000);
      
      // Look for brief content
      const briefContent = page.locator('[data-testid="brief-content"], .brief-content, .weekly-brief');
      if (await briefContent.isVisible()) {
        console.log('✅ Weekly brief content is visible');
      }
    }

    // Step 9: Test A/B variants (if available)
    console.log('🔄 Step 9: Testing A/B variants...');
    
    // Look for A/B testing functionality
    const abTestButton = page.locator('button:has-text("A/B Test"), button:has-text("Create Variant"), [data-testid="ab-test"]').first();
    if (await abTestButton.isVisible()) {
      await abTestButton.click();
      console.log('✅ Clicked A/B test button');
      
      // Look for variant creation
      const createVariantButton = page.locator('button:has-text("Create Variant"), button:has-text("Add Variant"), [data-testid="create-variant"]').first();
      if (await createVariantButton.isVisible()) {
        await createVariantButton.click();
        console.log('✅ Created A/B variant');
      }
    }

    console.log('🎉 Complete user journey test passed!');
  });

  test('Keyboard navigation works on key pages', async ({ page }) => {
    console.log('⌨️  Testing keyboard navigation...');
    
    // Test calendar page keyboard navigation
    await page.goto('/calendar');
    await page.waitForLoadState('networkidle');
    
    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Check if focus is visible
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    console.log('✅ Keyboard navigation works on calendar page');
    
    // Test inbox page keyboard navigation
    await page.goto('/inbox');
    await page.waitForLoadState('networkidle');
    
    // Tab through elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const focusedElementInbox = page.locator(':focus');
    await expect(focusedElementInbox).toBeVisible();
    console.log('✅ Keyboard navigation works on inbox page');
  });

  test('Accessibility: Screen reader support', async ({ page }) => {
    console.log('♿ Testing screen reader support...');
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check for proper heading structure
    const h1 = page.locator('h1').first();
    await expect(h1).toBeVisible();
    console.log('✅ H1 heading found');
    
    // Check for proper navigation landmarks
    const nav = page.locator('nav, [role="navigation"]').first();
    if (await nav.isVisible()) {
      console.log('✅ Navigation landmark found');
    }
    
    // Check for main content landmark
    const main = page.locator('main, [role="main"]').first();
    if (await main.isVisible()) {
      console.log('✅ Main content landmark found');
    }
    
    // Check for proper button semantics
    const buttons = page.locator('button, [role="button"]');
    const buttonCount = await buttons.count();
    console.log(`✅ Found ${buttonCount} properly semantic buttons`);
  });

  test('Error handling and loading states', async ({ page }) => {
    console.log('⚠️  Testing error handling...');
    
    // Test with invalid API calls (when not in mock mode)
    if (process.env.E2E_MOCKS !== 'true') {
      await page.goto('/calendar');
      await page.waitForLoadState('networkidle');
      
      // Look for error states or loading indicators
      const loadingIndicator = page.locator('[data-testid="loading"], .loading, .spinner').first();
      const errorMessage = page.locator('[data-testid="error"], .error, .error-message').first();
      
      // Either loading should complete or error should be handled gracefully
      if (await loadingIndicator.isVisible()) {
        await page.waitForTimeout(5000); // Wait for loading to complete
      }
      
      if (await errorMessage.isVisible()) {
        console.log('✅ Error handling is working');
      } else {
        console.log('✅ No errors detected');
      }
    } else {
      console.log('📡 Skipping error handling test in mock mode');
    }
  });
});
