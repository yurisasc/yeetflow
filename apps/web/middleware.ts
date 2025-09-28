import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { securityConfig, generateCSPHeader } from './lib/security';
import { SESSION_COOKIE_NAME } from '@/lib/constants';

// Define auth routes that should redirect to home when authenticated
const authRoutes = ['/login', '/signup'];

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  const { pathname } = request.nextUrl;

  // Check if this is an auth route
  const isAuthRoute = authRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  // Get the access token from cookies
  const accessToken = request.cookies.get(SESSION_COOKIE_NAME)?.value;

  // If accessing protected route without token, redirect to login
  if (!isAuthRoute && !accessToken) {
    const loginUrl = new URL('/login', request.url);
    // Preserve the original URL to redirect back after login
    loginUrl.searchParams.set('redirect', pathname);
    const res = NextResponse.redirect(loginUrl);
    Object.entries(securityConfig.headers).forEach(([key, value]) => {
      res.headers.set(key, value);
    });
    res.headers.set('Content-Security-Policy', generateCSPHeader());
    return res;
  }

  // If accessing auth route with token, redirect to flows (home)
  if (isAuthRoute && accessToken) {
    const res = NextResponse.redirect(new URL('/flows', request.url));
    Object.entries(securityConfig.headers).forEach(([key, value]) => {
      res.headers.set(key, value);
    });
    res.headers.set('Content-Security-Policy', generateCSPHeader());
    return res;
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
     * - _next/data (data fetching)
     * - favicon.ico (favicon file)
     * - robots.txt (robots.txt file)
     * - sitemap.xml (sitemap.xml file)
     * - manifest.json (manifest.json file)
     * - site.webmanifest (site.webmanifest file)
     * - manifest.webmanifest (manifest.webmanifest file)
     */
    '/((?!api|_next/static|_next/image|_next/data|favicon.ico|robots.txt|sitemap.xml|manifest.json|site.webmanifest|manifest.webmanifest).*)',
  ],
};
