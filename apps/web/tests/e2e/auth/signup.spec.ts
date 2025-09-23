import { test, expect } from '@playwright/test';

test.describe('Signup E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Ensure clean state
    await page.context().clearCookies();
    await page.goto('/signup');
    await page.evaluate(() => {
      try {
        localStorage.clear();
      } catch (e) {
        // Ignore localStorage errors in test environment
      }
    });
  });

  test('user can register and get redirected to flows', async ({ page }) => {
    // Fill signup form
    await page.fill('[data-testid="name-input"]', 'Test User');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'testpass123');
    await page.fill('[data-testid="confirm-password-input"]', 'testpass123');

    // Submit form
    await page.click('[data-testid="signup-submit"]');

    // Should redirect to flows after successful registration
    await page.waitForURL('/flows');
    await expect(page).toHaveURL('/flows');
  });

  test('shows error for mismatched passwords', async ({ page }) => {
    await page.fill('[data-testid="password-input"]', 'pass1');
    await page.fill('[data-testid="confirm-password-input"]', 'pass2');
    await page.click('[data-testid="signup-submit"]');

    const error = page.locator('[data-testid="signup-error"]');
    await expect(error).toBeVisible();
    await expect(error).toContainText(/passwords do not match/i);
  });

  test('shows error for existing email', async ({ page }) => {
    await page.fill('[data-testid="name-input"]', 'Demo User');
    await page.fill('[data-testid="email-input"]', 'demo@yeetflow.com');
    await page.fill('[data-testid="password-input"]', 'demo123');
    await page.fill('[data-testid="confirm-password-input"]', 'demo123');
    await page.click('[data-testid="signup-submit"]');

    const error = page.locator('[data-testid="signup-error"]');
    await expect(error).toBeVisible();
    await expect(error).toContainText(/already exists|registration failed/i);
  });

  test('has link to login page', async ({ page }) => {
    await page.click('text=Already have an account? Sign in');
    await page.waitForURL('/login');
  });
});
