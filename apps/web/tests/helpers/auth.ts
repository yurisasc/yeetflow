import { expect, Page } from '@playwright/test';

export async function login(
  page: Page,
  email = 'admin@e2e.local',
  password = 'adminpass',
) {
  // Perform login via the UI so cookies are set by the route handler
  await page.goto('/login');
  await page.waitForSelector('[data-testid="login-form"]');

  await page
    .locator('[data-testid="email-input"]')
    .waitFor({ state: 'visible' });
  await page
    .locator('[data-testid="password-input"]')
    .waitFor({ state: 'visible' });

  await page.fill('[data-testid="email-input"]', email);
  await page.fill('[data-testid="password-input"]', password);
  await page.click('[data-testid="login-submit"]');

  // Verify redirect and authenticated UI
  await expect(page).toHaveURL(/\/flows/, { timeout: 15000 });
  await expect(page.locator('[data-testid="flows-list"]')).toBeVisible();
}

export async function logout(page: Page) {
  // Call the BFF logout endpoint to clear HttpOnly cookies
  await page.evaluate(async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
  });

  // Navigate to login and verify
  await page.goto('/login');
  await expect(page).toHaveURL('/login');
}
