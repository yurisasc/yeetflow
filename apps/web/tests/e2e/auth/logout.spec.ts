import { test, expect } from '@playwright/test';
import { login, logout } from '../../helpers/auth';

test.describe('Authentication Logout E2E', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL('/flows');
  });

  test('user can log out and session is cleared', async ({ page }) => {
    // Verify user is logged in
    await expect(page.locator('[data-testid="flows-list"]')).toBeVisible();

    // Perform logout via BFF helper
    await logout(page);

    // Should redirect to login page (may include redirect param)
    await expect(page).toHaveURL(/\/login(\?.*)?$/);
  });

  test('logout clears session and prevents access to protected routes', async ({
    page,
  }) => {
    // Ensure user is logged in
    await expect(page.locator('[data-testid="flows-list"]')).toBeVisible();

    // Perform logout
    await logout(page);
    await expect(page).toHaveURL(/\/login(\?.*)?$/);

    // Try to access protected route directly
    await page.goto('/flows');

    // Should redirect back to login (may include redirect param)
    await expect(page).toHaveURL(/\/login(\?.*)?$/);
  });

  test('logout clears authentication cookies', async ({ page }) => {
    // Verify initial authenticated state
    await expect(page.locator('[data-testid="flows-list"]')).toBeVisible();

    // Perform logout via helper (BFF clears HttpOnly cookies)
    await logout(page);
    await expect(page).toHaveURL(/\/login(\?.*)?$/);

    // Check that auth cookies are cleared
    const finalCookies = await page.context().cookies();
    const authCookies = finalCookies.filter(
      (c) => c.name === 'access_token' || c.name === 'refresh_token',
    );
    expect(authCookies.length).toBe(0);
  });
});
