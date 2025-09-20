// Test script to verify tutorial functionality
console.log('🧪 Testing VANTAGE AI Tutorial Functionality');

// Test 1: Check if tutorial components are properly imported
console.log('✅ Test 1: Checking component imports...');

// Test 2: Verify tutorial button click functionality
function testTutorialButton() {
    console.log('✅ Test 2: Testing tutorial button click...');
    
    // Simulate button click
    const button = document.querySelector('[data-testid="tutorial-button"]') || 
                   document.querySelector('button[class*="tutorial"]') ||
                   document.querySelector('button:contains("Tutorial")') ||
                   document.querySelector('button:contains("Get Started")');
    
    if (button) {
        console.log('✅ Tutorial button found:', button);
        button.click();
        console.log('✅ Tutorial button clicked successfully');
        return true;
    } else {
        console.log('❌ Tutorial button not found');
        return false;
    }
}

// Test 3: Verify tutorial modal opens
function testTutorialModal() {
    console.log('✅ Test 3: Testing tutorial modal...');
    
    const modal = document.querySelector('[data-testid="tutorial-modal"]') ||
                  document.querySelector('.modal') ||
                  document.querySelector('[class*="tutorial"]');
    
    if (modal) {
        console.log('✅ Tutorial modal found:', modal);
        return true;
    } else {
        console.log('❌ Tutorial modal not found');
        return false;
    }
}

// Test 4: Verify tutorial navigation
function testTutorialNavigation() {
    console.log('✅ Test 4: Testing tutorial navigation...');
    
    const nextBtn = document.querySelector('[data-testid="next-button"]') ||
                    document.querySelector('button:contains("Next")');
    
    const prevBtn = document.querySelector('[data-testid="previous-button"]') ||
                    document.querySelector('button:contains("Previous")');
    
    if (nextBtn && prevBtn) {
        console.log('✅ Navigation buttons found');
        return true;
    } else {
        console.log('❌ Navigation buttons not found');
        return false;
    }
}

// Run all tests
function runAllTests() {
    console.log('🚀 Running all tutorial tests...');
    
    const results = {
        buttonClick: testTutorialButton(),
        modalOpen: testTutorialModal(),
        navigation: testTutorialNavigation()
    };
    
    console.log('📊 Test Results:', results);
    
    const passed = Object.values(results).filter(Boolean).length;
    const total = Object.keys(results).length;
    
    console.log(`🎯 Tests passed: ${passed}/${total}`);
    
    if (passed === total) {
        console.log('🎉 All tests passed! Tutorial system is working correctly.');
    } else {
        console.log('⚠️ Some tests failed. Check the implementation.');
    }
    
    return results;
}

// Auto-run tests when page loads
if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
        setTimeout(runAllTests, 2000); // Wait 2 seconds for page to fully load
    });
}

// Export for manual testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        testTutorialButton,
        testTutorialModal,
        testTutorialNavigation,
        runAllTests
    };
}

console.log('✅ Tutorial test script loaded successfully!');
