/**
 * Backend Authentication Service
 *
 * Handles authentication using the backend API
 * Uses HTTP-only cookies for session management
 */

const API_BASE = process.env.NEXT_PUBLIC_API_ORIGIN || 'http://localhost:4000';
const REQUEST_TIMEOUT = 15000; // 15 seconds

export interface User {
  id: string;
  email: string;
}

export interface AuthResponse {
  account_id: string;
  email: string;
  authenticated: boolean;
}

export interface SessionResponse {
  authenticated: boolean;
  account_id?: string;
  email?: string;
}

/**
 * Fetch with timeout
 */
async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = REQUEST_TIMEOUT): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    throw error;
  }
}

/**
 * Register a new user
 */
export async function signUp(email: string, password: string): Promise<AuthResponse> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Registration failed');
  }

  return response.json();
}

/**
 * Sign in a user
 */
export async function signIn(email: string, password: string): Promise<AuthResponse> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Login failed');
  }

  return response.json();
}

/**
 * Sign out the current user
 */
export async function signOut(): Promise<void> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Logout failed');
  }
}

/**
 * Get current session
 */
export async function getSession(): Promise<SessionResponse> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/auth/session`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    return { authenticated: false };
  }

  return response.json();
}

/**
 * Check if backend is configured
 */
export function isBackendConfigured(): boolean {
  return !!API_BASE;
}
