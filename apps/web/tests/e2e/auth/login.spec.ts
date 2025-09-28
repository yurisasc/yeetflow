import { test, expect } from '@playwright/test';
import { login } from '../../helpers/auth';

test.describe('Authentication Login E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Ensure we're starting from a clean state
    await page.context().clearCookies();
    await page.goto('/login');
  });

  test('user can log in via email/password and access flows page', async ({
    page,
  }) => {
    await login(page);

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
    // a11y: ensure screen readers announce the error
    await expect(errorMessage).toHaveAttribute('role', /alert|status/);
    // BFF returns a generic message or forwards backend detail
    await expect(errorMessage).toContainText(
      /(Authentication failed|Invalid|Incorrect)/i,
    );

    // Verify no redirect to flows
    await expect(page).toHaveURL(/\/login(?:\?.*)?$/);
  });

  test('login redirects to protected page after success', async ({ page }) => {
    await login(page);

    await expect(page).toHaveURL('/flows');
  });
});
