import { test, expect } from '@playwright/test';

// This setup test runs once before all browser projects (see playwright.config.ts)
// It bootstraps the first admin user via the UI to cover the full flow once.

test.describe('E2E setup', () => {
  test('bootstrap first admin user via UI', async ({ page }) => {
    const email = 'admin@e2e.local';
    const password = 'adminpass';
    const name = 'E2E Admin';

    await page.context().clearCookies();
    await page.goto('/signup');
    await page.fill('[data-testid="name-input"]', name);
    await page.fill('[data-testid="email-input"]', email);
    await page.fill('[data-testid="password-input"]', password);
    await page.fill('[data-testid="confirm-password-input"]', password);
    await page.waitForSelector('[data-testid="signup-submit"]:not([disabled])');
    await page.click('[data-testid="signup-submit"]');

    await page.waitForURL('/flows', { timeout: 15000 });
    await expect(page).toHaveURL('/flows');
  });
});
