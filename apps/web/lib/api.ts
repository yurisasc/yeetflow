import 'server-only';

import {
  createClient,
  refreshAccessTokenApiV1AuthRefreshPost,
} from '@yeetflow/api-client';
import { cookies } from 'next/headers';
import type { Token } from '@yeetflow/api-client';
import { SESSION_COOKIE_NAME, REFRESH_COOKIE_NAME } from '@/lib/constants';

// Server-side client creators with proper baseUrl configuration
const getBaseUrl = () =>
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

function isRefreshUrl(input: RequestInfo | URL): boolean {
  try {
    let urlStr: string;
    if (typeof input === 'string') urlStr = input;
    else if (input instanceof URL) urlStr = input.toString();
    else if (typeof Request !== 'undefined' && input instanceof Request)
      urlStr = input.url;
    else urlStr = String(input);
    return urlStr.includes('/api/v1/auth/refresh');
  } catch {
    return false;
  }
}

export const createAPIClient = () => {
  const baseUrl = getBaseUrl();

  return createClient({
    baseUrl,
    fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
      const cookieStore = await cookies();
      const accessToken = cookieStore.get(SESSION_COOKIE_NAME)?.value;

      // Start from Request's headers (if any), then overlay init.headers
      const headers = new Headers(
        input instanceof Request ? input.headers : undefined,
      );
      new Headers(init?.headers || {}).forEach((v, k) => headers.set(k, v));

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

      const refreshToken = cookieStore.get(REFRESH_COOKIE_NAME)?.value;
      if (!refreshToken) return response;

      try {
        const bareClient = createClient({ baseUrl, fetch: globalThis.fetch });
        const refreshResult = await refreshAccessTokenApiV1AuthRefreshPost({
          client: bareClient,
          body: { refresh_token: refreshToken },
          throwOnError: true,
        });

        const token: Token = refreshResult.data!;
        const isProd = process.env.NODE_ENV === 'production';

        // Best-effort cookie updates (may be disallowed in RSC render)
        try {
          cookieStore.set(SESSION_COOKIE_NAME, token.access_token, {
            httpOnly: true,
            secure: isProd,
            sameSite: 'lax',
            path: '/',
            maxAge: token.expires_in,
          });
          if (token.refresh_token) {
            cookieStore.set(REFRESH_COOKIE_NAME, token.refresh_token, {
              httpOnly: true,
              secure: isProd,
              sameSite: 'lax',
              path: '/',
              maxAge: token.refresh_expires_in,
            });
          }
        } catch {
          // ignore write errors in non-mutable contexts
        }

        // Retry original request once with the new access token
        const retryHeaders = new Headers(headers);
        retryHeaders.set('Authorization', `Bearer ${token.access_token}`);
        retryHeaders.set('X-Retry-After-Refresh', '1');

        response = await fetch(input, { ...reqInit, headers: retryHeaders });
        return response;
      } catch {
        // Refresh failed — return original 401
        return response;
      }
    },
  });
};

// Backwards compatible wrappers (deprecated)
export const createAuthenticatedClient = (_cookieHeader?: string) =>
  createAPIClient();

export const createUnauthenticatedClient = () => createAPIClient();
