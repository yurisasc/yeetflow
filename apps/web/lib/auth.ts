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

// Mock user data - in real app this would decode JWT
export function getCurrentUser(): User | null {
  const token = getToken();
  if (!token) return null;

  return {
    id: '1',
    email: 'demo@yeetflow.com',
    name: 'Demo User',
    role: 'admin', // Change to "user" to test non-admin experience
  };
}

export function logout(): void {
  removeToken();
  window.location.href = '/login';
}

export function isAdmin(): boolean {
  const user = getCurrentUser();
  return user?.role === 'admin';
}
