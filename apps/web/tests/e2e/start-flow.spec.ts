import { test, expect } from '@playwright/test';

test.describe('YeetFlow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
  });

  test('user can select a flow and see embedded remote browser', async ({ page }) => {
    // Navigate to flows page
    await page.goto('/flows');

    // Wait for flows to load
    await page.waitForSelector('[data-testid="flows-list"]');

    // Select the first available flow
    const firstFlowButton = page.locator('[data-testid="start-flow-button"]').first();
    await expect(firstFlowButton).toBeVisible();

    // Click start flow
    await firstFlowButton.click();

    // Should navigate to run page
    await page.waitForURL(/\/runs\/.+/);

    // Wait for run page to load
    await page.waitForSelector('[data-testid="run-status"]');

    // Verify run status is displayed
    const statusElement = page.locator('[data-testid="run-status"]');
    await expect(statusElement).toBeVisible();

    // Wait for browser session to be embedded
    const sessionFrame = page.locator('[data-testid="session-iframe"]');
    await expect(sessionFrame).toBeVisible();

    // Verify iframe has src attribute
    await expect(sessionFrame).toHaveAttribute('src', /.+/);

    // Verify iframe src is a valid URL
    const iframeSrc = await sessionFrame.getAttribute('src');
    expect(iframeSrc).toMatch(/^https?:\/\//);
  });

  test('run page shows loading state initially', async ({ page }) => {
    // Navigate to a run page directly
    await page.goto('/runs/test-run-id');

    // Should show loading or initializing state
    const loadingElement = page.locator('[data-testid="loading-state"]').or(
      page.locator('text=/loading|initializing|starting/i')
    );
    await expect(loadingElement).toBeVisible();
  });

  test('flow selection displays available flows', async ({ page }) => {
    await page.goto('/flows');

    // Verify flows are displayed
    const flowsContainer = page.locator('[data-testid="flows-container"]');
    await expect(flowsContainer).toBeVisible();

    // Should have at least one flow
    const flowCards = page.locator('[data-testid="flow-card"]');
    await expect(flowCards.first()).toBeVisible();

    // Each flow should have a name and description
    const firstFlowName = flowCards.first().locator('[data-testid="flow-name"]');
    await expect(firstFlowName).toBeVisible();
    await expect(firstFlowName).not.toBeEmpty();

    const firstFlowDesc = flowCards.first().locator('[data-testid="flow-description"]');
    await expect(firstFlowDesc).toBeVisible();
  });

  test('run page updates status in real-time', async ({ page }) => {
    // Start a flow
    await page.goto('/flows');
    const startButton = page.locator('[data-testid="start-flow-button"]').first();
    await startButton.click();

    await page.waitForURL(/\/runs\/.+/);

    // Monitor status changes
    const statusElement = page.locator('[data-testid="run-status"]');

    // Initially should show running or pending
    await expect(statusElement).toHaveText(/running|pending|starting/i);

    // TODO: Test real-time status updates via Socket.IO
    // This would require setting up test WebSocket connections
  });

  test('embedded browser session is interactive', async ({ page }) => {
    // Start a flow
    await page.goto('/flows');
    const startButton = page.locator('[data-testid="start-flow-button"]').first();
    await startButton.click();

    await page.waitForURL(/\/runs\/.+/);

    // Wait for iframe to load
    const sessionFrame = page.locator('[data-testid="session-iframe"]');
    await expect(sessionFrame).toBeVisible();

    // Get the iframe content
    const frame = page.frameLocator('[data-testid="session-iframe"]');

    // Verify iframe content is loaded (basic check)
    // Note: Actual browser session content depends on Steel.dev setup
    const frameBody = frame.locator('body');
    await expect(frameBody).toBeVisible();
  });

  test('run page handles invalid run IDs', async ({ page }) => {
    // Navigate to invalid run ID
    await page.goto('/runs/invalid-run-id');

    // Should show error or not found message
    const errorElement = page.locator('[data-testid="error-message"]').or(
      page.locator('text=/not found|invalid|error/i')
    );
    await expect(errorElement).toBeVisible();
  });

  test('user can navigate back to flows from run page', async ({ page }) => {
    // Start a flow
    await page.goto('/flows');
    const startButton = page.locator('[data-testid="start-flow-button"]').first();
    await startButton.click();

    await page.waitForURL(/\/runs\/.+/);

    // Click back to flows button
    const backButton = page.locator('[data-testid="back-to-flows"]').or(
      page.locator('a[href="/flows"]')
    );
    await backButton.click();

    // Should navigate back to flows
    await page.waitForURL('/flows');
    await expect(page).toHaveURL('/flows');
  });
});
