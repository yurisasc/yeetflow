import { test, expect } from '@playwright/test';
import { login } from '../../helpers/auth';

test.describe('Flows List', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/\/flows/);
  });

  test('should display flows list with correct test IDs', async ({ page }) => {
    await page.waitForSelector('[data-testid="flows-list"]');

    const flowsList = page.locator('[data-testid="flows-list"]');
    await expect(flowsList).toBeVisible();

    const flowCards = page.locator('[data-testid="flow-card"]');
    await expect(flowCards.first()).toBeVisible();

    const firstCard = flowCards.first();
    await expect(firstCard.locator('[data-testid="flow-name"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="flow-description"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="start-flow-button"]')).toBeVisible();
  });

  test('should search flows', async ({ page }) => {
    await page.waitForSelector('[data-testid="flow-card"]');

    const initialCount = await page.locator('[data-testid="flow-card"]').count();
    expect(initialCount).toBeGreaterThan(0);

    await page.fill('input[placeholder="Search flows..."]', 'nonexistent-flow');
    await expect(page.locator('text=No flows found')).toBeVisible();
    await expect(page.locator('[data-testid="flow-card"]')).toHaveCount(0);

    await page.click('text=Clear search');

    await expect(page.locator('[data-testid="flow-card"]').first()).toBeVisible();
    await expect(page.locator('[data-testid="flow-card"]')).toHaveCount(initialCount);

    await page.fill('input[placeholder="Search flows..."]', 'Test Flow');
    const visibleFlowNames = page.locator('[data-testid="flow-name"]');
    await expect(visibleFlowNames.first()).toHaveText(/Test Flow/i);
    await expect(page.locator('[data-testid="flow-card"]')).not.toHaveCount(0);

    await page.fill('input[placeholder="Search flows..."]', 'HITL');
    await expect(visibleFlowNames.first()).toHaveText(/HITL Flow/i);
    await expect(page.locator('[data-testid="flow-card"]')).not.toHaveCount(0);
  });

  test('should load flows from backend', async ({ page }) => {
    const flowsRequest = page.waitForRequest('/api/worker/api/v1/flows');

    await page.reload();
    await flowsRequest;

    const request = await flowsRequest;
    expect(request.method()).toBe('GET');
    expect(request.headers()['authorization']).toBeTruthy();
  });

  test('should start a flow via backend and navigate to run page', async ({ page }) => {
    await page.waitForSelector('[data-testid="start-flow-button"]');

    const mockRunId = 'mock-run-id';
    let capturedFlowId: string | undefined;
    let capturedAuth: string | undefined;

    await page.route('**/api/worker/api/v1/runs', async (route) => {
      const request = route.request();
      const body = request.postDataJSON();
      capturedFlowId = body?.flow_id;
      const headers = request.headers();
      capturedAuth = headers['authorization'];

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: mockRunId }),
      });
    });

    try {
      await page.locator('[data-testid="start-flow-button"]').first().click();

      await expect(page).toHaveURL(new RegExp(`/runs/${mockRunId}$`));
      await page.waitForSelector('[data-testid="run-status"]');

      expect(capturedFlowId).toBeTruthy();
      expect(capturedAuth).toBeTruthy();
    } finally {
      await page.unroute('**/api/worker/api/v1/runs');
    }
  });

  test('should handle run creation error gracefully', async ({ page }) => {
    await page.waitForSelector('[data-testid="start-flow-button"]');

    await page.route('/api/worker/api/v1/runs', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid flow_id: flow does not exist' }),
      });
    });

    await page.locator('[data-testid="start-flow-button"]').first().click();

    await expect(page).toHaveURL(/\/flows/);
    await expect(page.locator('[data-testid="start-flow-error"]')).toHaveText(
      /invalid flow_id/i,
    );
  });
});
