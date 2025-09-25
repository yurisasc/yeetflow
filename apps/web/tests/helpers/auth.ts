import { expect, Page } from '@playwright/test';

const TOKEN_STORAGE_KEYS = {
  access: 'yeetflow_token',
  refresh: 'yeetflow_refresh_token',
};

export async function login(page: Page, email = 'admin@e2e.local', password = 'adminpass') {
  await page.goto('/login');
  await page.waitForLoadState('domcontentloaded');

  // Clear any existing tokens to avoid stale auth
  await page.evaluate(({ accessKey, refreshKey }) => {
    try {
      localStorage.removeItem(accessKey);
      localStorage.removeItem(refreshKey);
      sessionStorage.clear();
    } catch {
      // Ignore storage errors in browsers with restricted storage
    }
  }, { accessKey: TOKEN_STORAGE_KEYS.access, refreshKey: TOKEN_STORAGE_KEYS.refresh });

  // Request fresh tokens directly from the API
  const response = await page.request.post('/api/worker/api/v1/auth/login', {
    form: {
      grant_type: 'password',
      username: email,
      password,
    },
  });

  expect(response.ok()).toBeTruthy();
  const data = await response.json();

  if (!data?.access_token) {
    throw new Error('Login API did not return an access token');
  }

  // Store tokens within the browser context
  await page.evaluate(
    ({ tokens, accessKey, refreshKey }) => {
      try {
        localStorage.setItem(accessKey, tokens.access_token);
        if (tokens.refresh_token) {
          localStorage.setItem(refreshKey, tokens.refresh_token);
        }
      } catch (err) {
        console.error('Failed to persist auth tokens', err);
        throw err;
      }
    },
    {
      tokens: data,
      accessKey: TOKEN_STORAGE_KEYS.access,
      refreshKey: TOKEN_STORAGE_KEYS.refresh,
    },
  );

  // Navigate to flows and verify guard passed
  await page.goto('/flows');
  await page.waitForURL('/flows', { timeout: 10000 });
  await page.waitForSelector('[data-testid="flows-list"]', { timeout: 10000 });
}

export async function logout(page: Page) {
  // Click on user menu or logout button
  await page.click('[data-testid="user-menu"]');
  await page.click('[data-testid="logout-button"]');
  
  // Wait for navigation to login page
  await page.waitForURL('/login');
}
