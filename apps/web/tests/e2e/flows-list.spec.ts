import { test, expect } from '@playwright/test';
import { login } from '../helpers/auth';

test.describe('Flows List', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/flows');
  });

  test('should display flows list with correct test IDs', async ({ page }) => {
    // Wait for flows to load
    await page.waitForSelector('[data-testid="flows-list"]');
    
    // Check that flows list container is visible
    const flowsList = page.locator('[data-testid="flows-list"]');
    await expect(flowsList).toBeVisible();

    // Check that we have flow cards
    const flowCards = page.locator('[data-testid="flow-card"]');
    await expect(flowCards.first()).toBeVisible();

    // Check that each flow card has the required elements
    const firstCard = flowCards.first();
    await expect(firstCard.locator('[data-testid="flow-name"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="flow-description"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="start-flow-button"]')).toBeVisible();
  });

  test('should search flows', async ({ page }) => {
    // Wait for initial load
    await page.waitForSelector('[data-testid="flow-card"]');
    
    const initialCount = await page.locator('[data-testid="flow-card"]').count();
    expect(initialCount).toBeGreaterThan(0);

    // Search for a non-existent flow
    await page.fill('input[placeholder="Search flows..."]', 'nonexistent-flow');
    
    // Should show no results
    await expect(page.locator('text=No flows found')).toBeVisible();
    
    // Clear search
    await page.click('text=Clear search');
    
    // Should show flows again
    const finalCount = await page.locator('[data-testid="flow-card"]').count();
    expect(finalCount).toBeGreaterThan(0);
  });

  test('should load flows from backend', async ({ page }) => {
    // Intercept the API call to verify it's using the backend
    const flowsRequest = page.waitForRequest('/api/worker/api/v1/flows');
    
    await page.reload();
    await flowsRequest;
    
    // Verify the request includes auth header
    const request = await flowsRequest;
    expect(request.headers()['authorization']).toBeTruthy();
  });
});
