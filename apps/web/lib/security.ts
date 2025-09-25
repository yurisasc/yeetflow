// Security configuration for YeetFlow
// Implements Content Security Policy and other security headers

const scriptSrc: string[] = [
  "'self'",
  "'unsafe-eval'", // Required for Next.js development tooling
];

if (process.env.NODE_ENV !== 'production') {
  // Next.js dev server injects inline scripts for HMR and RSC refresh
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
      ],
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
    'X-XSS-Protection': '1; mode=block',
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
      // Validate each part is base64url encoded
      parts.forEach(part => {
        const base64 = part.replace(/-/g, '+').replace(/_/g, '/');
        atob(base64);
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
      return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }
    // Fallback for server-side rendering
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  }
}
