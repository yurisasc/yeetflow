import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { securityConfig, generateCSPHeader } from './lib/security';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  
  // Add security headers
  Object.entries(securityConfig.headers).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
  
  // Add Content Security Policy
  response.headers.set('Content-Security-Policy', generateCSPHeader());
  
  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!api|_next/static|_next/image|favicon.ico|public).*)',
  ],
};
