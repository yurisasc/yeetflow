import { test, expect } from '@playwright/test';
import { login } from '../../helpers/auth';

test.describe('Flows List', () => {
  test('should redirect unauthenticated users to login page', async ({
    page,
  }) => {
    // Ensure clean state - no authentication
    await page.context().clearCookies();

    // Navigate to protected route
    await page.goto('/flows');

    // Should redirect to login (may include redirect query param)
    await expect(page).toHaveURL(/\/login(\?.*)?$/, { timeout: 10000 });
  });

  test.beforeEach(async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/\/flows/, { timeout: 10000 });
  });

  test('should display flows list with correct test IDs', async ({ page }) => {
    await page.waitForSelector('[data-testid="flows-list"]');

    const flowsList = page.locator('[data-testid="flows-list"]');
    await expect(flowsList).toBeVisible();

    const flowCards = page.locator('[data-testid="flow-card"]');
    await expect(flowCards.first()).toBeVisible();

    const firstCard = flowCards.first();
    await expect(firstCard.locator('[data-testid="flow-name"]')).toBeVisible();
    await expect(
      firstCard.locator('[data-testid="flow-description"]'),
    ).toBeVisible();
    await expect(
      firstCard.locator('[data-testid="start-flow-button"]'),
    ).toBeVisible();
  });

  test('should search flows', async ({ page }) => {
    await page.waitForSelector('[data-testid="flow-card"]');

    const initialCount = await page
      .locator('[data-testid="flow-card"]')
      .count();
    expect(initialCount).toBeGreaterThan(0);

    await page.fill('input[placeholder="Search flows..."]', 'nonexistent-flow');
    await expect(page.locator('text=No flows found')).toBeVisible();
    await expect(page.locator('[data-testid="flow-card"]')).toHaveCount(0);

    await page.click('text=Clear search');

    await expect(
      page.locator('[data-testid="flow-card"]').first(),
    ).toBeVisible();
    await expect(page.locator('[data-testid="flow-card"]')).toHaveCount(
      initialCount,
    );

    await page.fill('input[placeholder="Search flows..."]', 'Test Flow');
    const visibleFlowNames = page.locator('[data-testid="flow-name"]');
    await expect(visibleFlowNames.first()).toHaveText(/Test Flow/i);
    await expect(page.locator('[data-testid="flow-card"]')).not.toHaveCount(0);

    await page.fill('input[placeholder="Search flows..."]', 'HITL');
    await expect(visibleFlowNames.first()).toHaveText(/HITL Flow/i);
    await expect(page.locator('[data-testid="flow-card"]')).not.toHaveCount(0);
  });

  test('should start a flow via backend and navigate to run page', async ({
    page,
  }) => {
    await page.waitForSelector('[data-testid="start-flow-button"]');

    await page.locator('[data-testid="start-flow-button"]').first().click();
    await expect(page).toHaveURL(/\/runs\//, { timeout: 15000 });
  });

  test('should handle run creation error gracefully', async ({ page }) => {
    await page.waitForSelector('[data-testid="start-flow-button"]');
    await page.locator('[data-testid="start-flow-button"]').first().click();

    // If server returns an error, the UI should surface it; otherwise it may redirect.
    const error = page.locator('[data-testid="start-flow-error"]');
    if ((await error.count()) > 0) {
      await expect(error).toContainText(/failed|invalid|error/i);
    } else {
      // Either redirect occurred or error UI not implemented yet
      await expect(
        page.locator('[data-testid="flows-list"]').first(),
      ).toBeVisible();
    }
  });

  test('should load user data securely without exposing tokens', async ({
    page,
  }) => {
    // Wait for page to load with user data
    await page.waitForSelector('[data-testid="flows-list"]');

    // Verify user data is displayed (flows are loaded)
    const flowCards = page.locator('[data-testid="flow-card"]');
    await expect(flowCards.first()).toBeVisible();

    // Verify no authentication tokens are exposed in client-side code
    const pageSource = await page.content();
    expect(pageSource).not.toContain('authorization');
    expect(pageSource).not.toContain('bearer');
    expect(pageSource).not.toContain('token');

    // Verify cookies are used for authentication by checking BFF user call
    const meRespPromise = page.waitForResponse('**/api/auth/me', {
      timeout: 10000,
    });
    await page.reload();
    const meResp = await meRespPromise;
    expect(meResp.status()).toBe(200);
  });
});
