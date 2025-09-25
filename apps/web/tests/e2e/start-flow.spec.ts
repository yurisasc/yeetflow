import { test, expect } from '@playwright/test';
import { login } from '../helpers/auth';

test.describe('Start Flow', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/flows');
  });

  test('should create run via backend POST and navigate to runs page', async ({ page }) => {
    // Wait for flows to load
    await page.waitForSelector('[data-testid="flow-card"]');
    
    // Get the first flow
    const firstFlowCard = page.locator('[data-testid="flow-card"]').first();
    const flowName = await firstFlowCard.locator('[data-testid="flow-name"]').textContent();
    
    // Intercept the POST request to create run
    const createRunRequest = page.waitForRequest('/api/worker/api/v1/runs');
    const createRunResponse = page.waitForResponse('/api/worker/api/v1/runs');
    
    // Click start flow
    await firstFlowCard.locator('[data-testid="start-flow-button"]').click();
    
    // Verify the POST request
    const request = await createRunRequest;
    expect(request.method()).toBe('POST');
    expect(request.headers()['content-type']).toContain('application/json');
    expect(request.headers()['authorization']).toBeTruthy();
    
    const requestBody = JSON.parse(request.postData() || '{}');
    expect(requestBody).toHaveProperty('flow_id');
    
    // Verify the response
    const response = await createRunResponse;
    expect(response.status()).toBe(201);
    
    const responseData = await response.json();
    expect(responseData).toHaveProperty('id');
    expect(responseData).toHaveProperty('session_url');
    expect(responseData.flow_id).toBe(requestBody.flow_id);
    
    // Verify navigation to runs page
    await expect(page).toHaveURL(new RegExp(`/runs/${responseData.id}$`));
    
    // Verify run status is shown
    await expect(page.locator('[data-testid="run-status"]')).toBeVisible();
    
    // Verify session iframe is present
    await expect(page.locator('[data-testid="session-iframe"]')).toBeVisible();
  });

  test('should handle flow creation error gracefully', async ({ page }) => {
    // Mock a 400 error for invalid flow_id
    await page.route('/api/worker/api/v1/runs', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid flow_id: flow does not exist' })
      });
    });
    
    // Try to start a flow
    await page.waitForSelector('[data-testid="start-flow-button"]');
    await page.locator('[data-testid="start-flow-button"]').first().click();
    
    // Should stay on flows page and show error (or handle gracefully)
    await expect(page).toHaveURL(/\/flows/);
  });
});
