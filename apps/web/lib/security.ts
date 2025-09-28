const trustedSessionOrigins: string[] = [];

if (process.env.NEXT_PUBLIC_TRUSTED_SESSION_ORIGIN) {
  trustedSessionOrigins.push(process.env.NEXT_PUBLIC_TRUSTED_SESSION_ORIGIN);
}

export const securityConfig = {
  contentSecurityPolicy: {
    directives: {
      'default-src': ['self'],
      'script-src': ['self', 'unsafe-inline'],
      'style-src': ['self', 'unsafe-inline'], // Required for styled-components/Next.js
      'img-src': ['self', 'data:', 'https:'],
      'font-src': ['self', 'data:'],
      'connect-src': [
        'self',
        process.env.WORKER_BASE_URL || 'http://localhost:8000',
        ...trustedSessionOrigins,
        ...(process.env.NODE_ENV !== 'production' ? ['ws:', 'wss:'] : []),
      ],
      'frame-src': ['self', ...trustedSessionOrigins],
      'frame-ancestors': ['none'],
      'object-src': ['none'],
      'script-src-attr': ['none'], // Disallow inline event handlers
    },
  },

  // Security headers configuration
  headers: {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  },
};

/**
 * Generates CSP header string from directives
 */
export function generateCSPHeader(): string | undefined {
  // const directives = securityConfig.contentSecurityPolicy.directives;
  // return Object.entries(directives)
  //   .map(([directive, sources]) => `${directive} ${sources.join(' ')}`)
  //   .join('; ');
  // TODO: The CSP currently causes a lot of issues with the prod app, so it's disabled for now.
  //       Revisit this in the future.
  return undefined;
}

/**
 * Security utility functions for token handling
 */
export class SecurityUtils {
  /**
   * Sanitizes input to prevent XSS
   */
  static sanitizeInput(input: string): string {
    if (typeof input !== 'string') return '';
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  }

  /**
   * Validates token format (JWT)
   */
  static isValidJWT(token: string): boolean {
    if (!token || typeof token !== 'string') return false;

    const parts = token.split('.');
    if (parts.length !== 3) return false;

    try {
      // Validate each part is base64url encoded and ensure header/payload are JSON
      parts.forEach((part, index) => {
        const normalized = part.replace(/-/g, '+').replace(/_/g, '/');
        const paddingLength = (4 - (normalized.length % 4)) % 4;
        const padded = normalized + '='.repeat(paddingLength);

        let decoded: string;
        if (typeof atob === 'function') {
          decoded = atob(padded);
        } else if (typeof Buffer !== 'undefined') {
          decoded = Buffer.from(padded, 'base64').toString('utf-8');
        } else {
          throw new Error('No base64 decoder available');
        }

        if (index < 2) {
          JSON.parse(decoded);
        }
      });
      return true;
    } catch {
      return false;
    }
  }
}
