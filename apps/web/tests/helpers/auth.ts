import { Page } from '@playwright/test';

export async function login(page: Page, email = 'admin@e2e.local', password = 'adminpass') {
  // Navigate to login page
  await page.goto('/login');
  
  // Wait for login form to be ready
  await page.waitForSelector('[data-testid="login-form"]');
  
  // Fill in the form using test IDs
  await page.fill('[data-testid="email-input"]', email);
  await page.fill('[data-testid="password-input"]', password);
  
  // Submit the form using test ID
  await page.click('[data-testid="login-submit"]');
  
  // Wait for navigation to flows page or error message
  try {
    // First wait for token to be set
    await page.waitForFunction(() => {
      try {
        return !!localStorage.getItem('yeetflow_token');
      } catch {
        return false;
      }
    }, { timeout: 10000 });
    // Then wait for URL change
    await page.waitForURL('/flows', { timeout: 10000 });
  } catch (error) {
    // Check if we're still on login page with error
    const errorElement = page.locator('[data-testid="login-error"]');
    if (await errorElement.isVisible()) {
      const errorText = await errorElement.textContent();
      throw new Error(`Login failed: ${errorText}`);
    }
    throw error;
  }
}

export async function logout(page: Page) {
  // Click on user menu or logout button
  await page.click('[data-testid="user-menu"]');
  await page.click('[data-testid="logout-button"]');
  
  // Wait for navigation to login page
  await page.waitForURL('/login');
}
