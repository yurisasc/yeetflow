// Export the generated API client
export * from "./generated";

import { createClientConfig } from "./config";
export { createClientConfig };

import { createClient } from "./generated/client";
export { createClient };

// Unauthenticated client for auth endpoints (login, signup, etc.)
export const unauthenticatedApiClient = createClient(createClientConfig({}));

// Server-side authenticated client helper
/**
 * Creates an authenticated API client for server-side use.
 * This function is framework-agnostic.
 * @param cookieHeader - The cookie string from the incoming request.
 */
export const getAuthenticatedApiClient = (cookieHeader: string | undefined) => {
  return createClient({
    ...createClientConfig({}),
    headers: {
      Cookie: cookieHeader || "",
    },
  });
};
