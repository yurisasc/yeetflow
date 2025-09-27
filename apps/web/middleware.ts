import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { securityConfig, generateCSPHeader } from './lib/security';

// Define auth routes that should redirect to home when authenticated
const authRoutes = ['/login', '/signup'];

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  const { pathname } = request.nextUrl;

  // Check if this is an auth route
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  // Get the access token from cookies
  const accessToken = request.cookies.get('access_token')?.value;

  // If accessing protected route without token, redirect to login
  if (!isAuthRoute && !accessToken) {
    const loginUrl = new URL('/login', request.url);
    // Preserve the original URL to redirect back after login
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If accessing auth route with token, redirect to flows (home)
  if (isAuthRoute && accessToken) {
    return NextResponse.redirect(new URL('/flows', request.url));
  }

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
