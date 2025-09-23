// JWT Authentication utilities for YeetFlow

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('yeetflow_token');
}

export function setToken(token: string): void {
  localStorage.setItem('yeetflow_token', token);
}

export function removeToken(): void {
  localStorage.removeItem('yeetflow_token');
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export function getAuthHeader(): Record<string, string> {
  const token = getToken();
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
  const token = getToken();
  if (!token) return null;

  try {
    const response = await fetch('/api/worker/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ refresh_token: token }),
    });

    if (!response.ok) {
      removeToken();
      return null;
    }

    const data = await response.json();
    setToken(data.access_token);
    return data.access_token;
  } catch {
    removeToken();
    return null;
  }
}

export function logout(): void {
  removeToken();
  window.location.href = '/login';
}

export function isAdmin(): boolean {
  const user = getCurrentUser();
  return user?.role === 'admin';
}
