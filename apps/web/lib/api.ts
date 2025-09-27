import {
  createClient,
  refreshAccessTokenApiV1AuthRefreshPost,
} from '@yeetflow/api-client';
import { cookies } from 'next/headers';
import type { Token } from '@yeetflow/api-client';

// Server-side client creators with proper baseUrl configuration
const getBaseUrl = () =>
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

function isRefreshUrl(input: RequestInfo | URL): boolean {
  const url = typeof input === 'string' ? input : input.toString();
  return url.includes('/api/v1/auth/refresh');
}

export const createAPIClient = () => {
  const baseUrl = getBaseUrl();

  return createClient({
    baseUrl,
    fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
      const cookieStore = await cookies();
      const accessToken = cookieStore.get('access_token')?.value;

      const headers = new Headers(init?.headers || {});

      // Attach Authorization header if we have an access token and not bypassing
      if (
        accessToken &&
        !headers.has('Authorization') &&
        !isRefreshUrl(input)
      ) {
        headers.set('Authorization', `Bearer ${accessToken}`);
      }

      const reqInit: RequestInit = { ...init, headers };

      let response = await fetch(input, reqInit);

      // Only try refresh for 401 responses and avoid loops
      const alreadyRetried = headers.get('X-Retry-After-Refresh') === '1';
      if (response.status !== 401 || alreadyRetried || isRefreshUrl(input)) {
        return response;
      }

      const refreshToken = cookieStore.get('refresh_token')?.value;
      if (!refreshToken) return response;

      const bareClient = createClient({ baseUrl, fetch: globalThis.fetch });
      const refreshResult = await refreshAccessTokenApiV1AuthRefreshPost({
        client: bareClient,
        body: { refresh_token: refreshToken },
        throwOnError: true,
      });

      const token: Token = refreshResult.data!;

      const isProd = process.env.NODE_ENV === 'production';
      // Update cookies for the outgoing response
      cookieStore.set('access_token', token.access_token, {
        httpOnly: true,
        secure: isProd,
        sameSite: 'lax',
        path: '/',
        maxAge: token.expires_in,
      });
      if (token.refresh_token) {
        cookieStore.set('refresh_token', token.refresh_token, {
          httpOnly: true,
          secure: isProd,
          sameSite: 'lax',
          path: '/',
          maxAge: token.refresh_expires_in,
        });
      }

      // Retry original request once with the new access token
      const retryHeaders = new Headers(headers);
      retryHeaders.set('Authorization', `Bearer ${token.access_token}`);
      retryHeaders.set('X-Retry-After-Refresh', '1');

      response = await fetch(input, { ...reqInit, headers: retryHeaders });
      return response;
    },
  });
};

// Backwards compatible wrappers (deprecated)
export const createAuthenticatedClient = (_cookieHeader?: string) =>
  createAPIClient();

export const createUnauthenticatedClient = () => createAPIClient();
