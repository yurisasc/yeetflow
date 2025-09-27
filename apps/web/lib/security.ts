const scriptSrc: string[] = ["'self'"];

const trustedSessionOrigins: string[] = [];

if (process.env.NEXT_PUBLIC_TRUSTED_SESSION_ORIGIN) {
  trustedSessionOrigins.push(process.env.NEXT_PUBLIC_TRUSTED_SESSION_ORIGIN);
}

if (process.env.NODE_ENV !== 'production') {
  // Next.js dev server injects inline scripts for HMR and RSC refresh
  scriptSrc.push("'unsafe-eval'");
  scriptSrc.push("'unsafe-inline'");
}

export const securityConfig = {
  contentSecurityPolicy: {
    directives: {
      'default-src': ["'self'"],
      'script-src': scriptSrc,
      'style-src': [
        "'self'",
        "'unsafe-inline'", // Required for styled-components/Next.js
        // TODO: Remove 'unsafe-inline' in production
      ],
      'img-src': ["'self'", 'data:', 'https:'],
      'font-src': ["'self'", 'data:'],
      'connect-src': [
        "'self'",
        process.env.WORKER_BASE_URL || 'http://localhost:8000',
        ...trustedSessionOrigins,
        ...(process.env.NODE_ENV !== 'production' ? ['ws:', 'wss:'] : []),
      ],
      'frame-src': ["'self'", ...trustedSessionOrigins],
      'frame-ancestors': ["'none'"],
      'form-action': ["'self'"],
      'base-uri': ["'self'"],
      'object-src': ["'none'"],
      'script-src-attr': ["'none'"], // Disallow inline event handlers
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
export function generateCSPHeader(): string {
  const directives = securityConfig.contentSecurityPolicy.directives;
  return Object.entries(directives)
    .map(([directive, sources]) => `${directive} ${sources.join(' ')}`)
    .join('; ');
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

  /**
   * Creates a secure random string for CSRF tokens
   */
  static generateCSRFToken(): string {
    if (typeof window !== 'undefined' && window.crypto) {
      const array = new Uint8Array(32);
      window.crypto.getRandomValues(array);
      return Array.from(array, (byte) =>
        byte.toString(16).padStart(2, '0'),
      ).join('');
    }
    // Fallback for server-side rendering
    return (
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }
}
