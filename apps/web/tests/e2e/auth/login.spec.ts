import { test, expect } from '@playwright/test';

test.describe('Authentication Login E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Ensure we're starting from a clean state
    await page.context().clearCookies();
    await page.goto('/login');
    // Handle localStorage access gracefully
    await page.evaluate(() => {
      try {
        localStorage.clear();
      } catch (e) {
        // Ignore localStorage errors in test environment
      }
    });
  });

  test('user can log in via email/password and access flows page', async ({
    page,
  }) => {
    // Wait for login form to load
    await page.waitForSelector('[data-testid="login-form"]');

    // Fill in credentials
    await page.fill('[data-testid="email-input"]', 'demo@yeetflow.com');
    await page.fill('[data-testid="password-input"]', 'demo123');

    // Submit the login form
    await page.click('[data-testid="login-submit"]');

    // Wait for login to complete and redirect to flows
    await page.waitForURL('/flows');

    // Verify we're on flows page and authenticated UI loads
    await expect(page).toHaveURL('/flows');
    await expect(page.locator('[data-testid="flows-list"]')).toBeVisible();
  });

  test('login fails with invalid credentials', async ({ page }) => {
    // Wait for login form
    await page.waitForSelector('[data-testid="login-form"]');

    // Fill invalid credentials
    await page.fill('[data-testid="email-input"]', 'invalid@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');

    // Submit
    await page.click('[data-testid="login-submit"]');

    // Verify error message appears
    const errorMessage = page.locator('[data-testid="login-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/Incorrect email or password/i);

    // Verify no redirect to flows
    await expect(page).not.toHaveURL('/flows');
  });

  test('login redirects to protected page after success', async ({ page }) => {
    // Wait for login form to load
    await page.waitForSelector('[data-testid="login-form"]');

    // Login should redirect to flows
    await page.fill('[data-testid="email-input"]', 'demo@yeetflow.com');
    await page.fill('[data-testid="password-input"]', 'demo123');
    await page.click('[data-testid="login-submit"]');

    // Should redirect to flows
    await page.waitForURL('/flows');
  });
});
