import { test, expect } from '@playwright/test';

test.describe.configure({ mode: 'serial' });

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

  test('second signup fails without admin token', async ({ page }) => {
    await page.fill('[data-testid="name-input"]', 'Second User');
    await page.fill('[data-testid="email-input"]', 'second@e2e.local');
    await page.fill('[data-testid="password-input"]', 'secondpass');
    await page.fill('[data-testid="confirm-password-input"]', 'secondpass');

    await page.evaluate(() => {
      const form = document.querySelector('[data-testid="signup-form"]');
      if (form) (form as HTMLFormElement).noValidate = true;
    });

    await page.click('[data-testid="signup-submit"]');

    const error = page.locator('[data-testid="signup-error"]');
    await expect(error).toBeVisible({ timeout: 10000 });
    await expect(error).toContainText(/Invalid or expired token/i);
  });

  test('has link to login page', async ({ page }) => {
    await page.click('text=Already have an account? Sign in');
    await page.waitForURL('/login');
  });
});
