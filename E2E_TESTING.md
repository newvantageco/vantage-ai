# E2E Testing System

This document describes the comprehensive End-to-End (E2E) testing system implemented for the VANTAGE AI platform using Playwright.

## Overview

The E2E testing system provides:
- **Fast, deterministic tests** covering the complete user journey
- **Provider mocks** to avoid external API dependencies
- **Automated CI/CD integration** with GitHub Actions
- **Comprehensive test coverage** of critical user flows
- **Accessibility testing** for keyboard navigation and screen readers
- **Error handling validation** for robust user experience

## Test Structure

### Test Files
- `web/tests/e2e/smoke.spec.ts` - Main smoke tests covering the complete user journey
- `web/tests/e2e/fixtures/mocks.ts` - Mock data and API response fixtures
- `web/tests/e2e/global-setup.ts` - Global test setup and validation
- `web/tests/e2e/global-teardown.ts` - Global test cleanup

### Configuration
- `web/playwright.config.ts` - Playwright configuration with Chromium, tracing, and reporting
- `app/api/mocks.py` - API mock system for E2E testing
- `.github/workflows/e2e.yml` - CI/CD workflow for automated testing

## Test Coverage

### Complete User Journey
1. **OAuth Connection** - Connect Meta/LinkedIn accounts
2. **Brand Guide Creation** - Set up brand voice and audience
3. **Campaign Management** - Create and manage campaigns
4. **Content Planning** - Generate 14-day content plans
5. **Content Scheduling** - Schedule posts on calendar
6. **Scheduler Execution** - Process and post scheduled content
7. **Analytics & Insights** - View performance metrics
8. **Weekly Brief** - Generate and view weekly reports
9. **A/B Testing** - Create and manage content variants

### Accessibility Testing
- **Keyboard Navigation** - Tab through all interactive elements
- **Screen Reader Support** - Proper ARIA labels and landmarks
- **Focus Management** - Visible focus indicators
- **Semantic HTML** - Proper button and link semantics

### Error Handling
- **API Error States** - Graceful handling of failed requests
- **Loading States** - Proper loading indicators
- **Network Issues** - Offline and timeout scenarios

## Mock System

### Environment Gating
The mock system is controlled by the `E2E_MOCKS` environment variable:
```bash
E2E_MOCKS=true  # Enable mocks for testing
E2E_MOCKS=false # Use real APIs (not recommended for CI)
```

### Mocked Endpoints
- **OAuth Flows** - Meta and LinkedIn authentication
- **Publisher APIs** - Page management and posting
- **Insights APIs** - Performance metrics and analytics
- **Content Planning** - AI-generated content suggestions
- **Scheduling** - Post scheduling and execution
- **Reports** - Weekly briefs and analytics

### Mock Data
All mock data is defined in `web/tests/e2e/fixtures/mocks.ts` and includes:
- Realistic OAuth responses with access tokens
- Fake social media pages and posts
- Simulated engagement metrics
- Content plans with hashtags and scheduling
- Weekly briefs with recommendations

## Running Tests

### Local Development

#### Prerequisites
1. Start the API server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. Start the web server:
   ```bash
   cd web
   npm run dev
   ```

3. Install Playwright browsers:
   ```bash
   cd web
   npx playwright install --with-deps
   ```

#### Running Tests

**Basic test run (with mocks):**
```bash
./scripts/run-e2e.sh
```

**Run without mocks (requires real APIs):**
```bash
./scripts/run-e2e.sh --no-mocks
```

**Run in headed mode (see browser):**
```bash
./scripts/run-e2e.sh --headed
```

**Run in debug mode (step through tests):**
```bash
./scripts/run-e2e.sh --debug
```

**Run with UI mode (interactive):**
```bash
./scripts/run-e2e.sh --ui
```

#### Manual Test Commands

**Run all tests:**
```bash
cd web
npm run test:e2e
```

**Run specific test file:**
```bash
cd web
npx playwright test smoke.spec.ts
```

**Run tests in headed mode:**
```bash
cd web
npm run test:e2e:headed
```

**Run tests with UI:**
```bash
cd web
npm run test:e2e:ui
```

### CI/CD Integration

Tests run automatically on:
- **Pull Requests** - Full test suite on every PR
- **Main Branch** - Tests on every push to main
- **Manual Trigger** - Workflow dispatch for on-demand testing

#### CI Environment
- **Ubuntu Latest** - GitHub Actions runner
- **PostgreSQL 15** - Database service
- **Redis 7** - Cache service
- **Python 3.11** - API runtime
- **Node.js 18** - Web runtime

#### CI Steps
1. **Setup** - Install dependencies and browsers
2. **Database** - Run migrations and seed test data
3. **Services** - Start API and web servers
4. **Testing** - Run E2E test suite
5. **Artifacts** - Upload reports, traces, and screenshots

## Test Results

### Reports
- **HTML Report** - Interactive test results in `web/playwright-report/`
- **JSON Report** - Machine-readable results in `web/test-results/results.json`
- **GitHub Integration** - Test results in PR comments

### Artifacts (on failure)
- **Test Traces** - Step-by-step execution traces
- **Screenshots** - Visual evidence of failures
- **Videos** - Video recordings of test execution

### Debugging
1. **Check traces** - Open `web/test-results/` in Playwright trace viewer
2. **View screenshots** - Check `web/test-results/` for failure screenshots
3. **Read logs** - Check CI logs for detailed error messages
4. **Reproduce locally** - Run the same test locally with `--debug`

## Configuration

### Environment Variables

**Required for testing:**
```bash
E2E_MOCKS=true                    # Enable mock mode
BASE_URL=http://localhost:3000    # Web app URL
API_BASE=http://localhost:8000/api/v1  # API base URL
```

**Database configuration:**
```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/vantage_ai
REDIS_URL=redis://localhost:6379
```

**Authentication (for non-mock mode):**
```bash
CLERK_JWKS_URL=https://your-clerk-domain.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://your-clerk-domain.clerk.accounts.dev
```

### Playwright Configuration

Key settings in `web/playwright.config.ts`:
- **Browser**: Chromium only (for speed and consistency)
- **Parallelization**: Full parallel execution
- **Retries**: 2 retries on CI, 0 locally
- **Timeouts**: 30s default, 120s for web server startup
- **Tracing**: On first retry for debugging
- **Screenshots**: Only on failure
- **Videos**: Retained on failure

## Best Practices

### Writing Tests
1. **Use data-testid attributes** - More reliable than text-based selectors
2. **Wait for network idle** - Ensure pages are fully loaded
3. **Test user workflows** - Focus on actual user actions
4. **Handle async operations** - Use proper waits and timeouts
5. **Clean up state** - Reset between tests when needed

### Maintaining Mocks
1. **Keep mocks realistic** - Use real-world data structures
2. **Update mocks with API changes** - Sync with actual API responses
3. **Test mock mode locally** - Verify mocks work before CI
4. **Document mock data** - Explain what each mock represents

### Debugging Failures
1. **Check browser console** - Look for JavaScript errors
2. **Verify network requests** - Ensure APIs are responding
3. **Test locally first** - Reproduce issues locally before CI
4. **Use debug mode** - Step through tests with `--debug`
5. **Check traces** - Use Playwright trace viewer for detailed analysis

## Troubleshooting

### Common Issues

**Tests fail with "Page not found":**
- Ensure web server is running on port 3000
- Check BASE_URL environment variable

**Tests fail with "API not responding":**
- Ensure API server is running on port 8000
- Check API_BASE environment variable
- Verify E2E_MOCKS is set correctly

**Tests fail with "Element not found":**
- Check if UI has changed (selectors may be outdated)
- Use data-testid attributes for more reliable selectors
- Wait for elements to be visible before interacting

**Tests are flaky:**
- Add proper waits for async operations
- Use networkidle wait strategy
- Increase timeouts for slow operations

### Getting Help

1. **Check CI logs** - Look for error messages in GitHub Actions
2. **Run locally** - Reproduce issues in your development environment
3. **Use debug mode** - Step through tests to identify the exact failure point
4. **Check traces** - Use Playwright trace viewer for detailed analysis
5. **Review test code** - Ensure tests are written correctly

## Future Enhancements

### Planned Improvements
1. **Visual Regression Testing** - Screenshot comparison for UI changes
2. **Performance Testing** - Measure page load times and Core Web Vitals
3. **Mobile Testing** - Add mobile device testing
4. **Cross-browser Testing** - Add Firefox and Safari support
5. **API Testing** - Direct API endpoint testing
6. **Load Testing** - Stress testing with multiple users

### Monitoring
1. **Test Metrics** - Track test execution times and success rates
2. **Flaky Test Detection** - Identify and fix unreliable tests
3. **Coverage Reporting** - Measure test coverage across user flows
4. **Alerting** - Notify team of test failures and regressions
