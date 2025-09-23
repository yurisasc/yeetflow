// JWT Authentication utilities for YeetFlow
// SECURITY WARNING: This module uses localStorage for token storage which is vulnerable to XSS attacks
// @deprecated - Use server-side session management with httpOnly Secure cookies instead
// TODO: Migrate to httpOnly Secure cookies and rotate existing tokens
// See: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html#token-storage-on-client-side
// Security documentation: ./security.ts

import { SecurityUtils } from './security';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  // SECURITY: Access token only through this centralized function
  // No logging or debugging should include the token value
  // WARNING: localStorage is accessible via XSS - migrate to httpOnly cookies
  return localStorage.getItem('yeetflow_token');
}

export function setToken(token: string): void {
  // SECURITY: Set token only through this centralized function
  // Validate token format before storage
  // WARNING: localStorage is accessible via XSS - migrate to httpOnly cookies
  if (!SecurityUtils.isValidJWT(token)) {
    console.error('Invalid JWT format rejected');
    return;
  }
  
  localStorage.setItem('yeetflow_token', token);
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  // SECURITY: Access refresh token only through this centralized function
  // WARNING: localStorage is accessible via XSS - migrate to httpOnly cookies
  return localStorage.getItem('yeetflow_refresh_token');
}

export function setRefreshToken(token: string): void {
  // SECURITY: Set refresh token only through this centralized function
  // WARNING: localStorage is accessible via XSS - migrate to httpOnly cookies
  if (!SecurityUtils.isValidJWT(token)) {
    console.error('Invalid refresh token JWT format rejected');
    return;
  }
  localStorage.setItem('yeetflow_refresh_token', token);
}

export function removeRefreshToken(): void {
  localStorage.removeItem('yeetflow_refresh_token');
}

export function removeTokens(): void {
  removeToken();
  removeRefreshToken();
}

export function removeToken(): void {
  localStorage.removeItem('yeetflow_token');
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export function getAuthHeader(): Record<string, string> {
  const token = getToken();
  // SECURITY: Never log or expose the token in error messages
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function decodeJWT(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => `%${('00' + c.charCodeAt(0).toString(16)).slice(-2)}`)
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export function getCurrentUser(): User | null {
  const token = getToken();
  if (!token) return null;

  const payload = decodeJWT(token);
  if (!payload) return null;

  return {
    id: payload.sub || '1',
    email: payload.email || 'demo@yeetflow.com',
    name: payload.name || 'Demo User',
    role: payload.role || 'user',
  };
}

export async function refreshToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch('/api/worker/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Only clear tokens on authentication failures (401/403)
      // Do not clear on server errors (500) or validation errors (422)
      if (response.status === 401 || response.status === 403) {
        removeTokens();
      }
      return null;
    }

    const data = await response.json();
    // SECURITY: Validate response structure before setting token
    if (!data.access_token || typeof data.access_token !== 'string') {
      console.error('Invalid token response from server');
      return null;
    }
    setToken(data.access_token);

    // Update refresh token if provided
    if (data.refresh_token) {
      setRefreshToken(data.refresh_token);
    }

    return data.access_token;
  } catch {
    // Don't clear tokens on network errors - they might be temporary
    return null;
  }
}

export function logout(): void {
  removeTokens();
  window.location.href = '/login';
}

export function isAdmin(): boolean {
  const user = getCurrentUser();
  return user?.role === 'admin';
}
