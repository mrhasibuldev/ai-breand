/**
 * Backend Profile Service
 *
 * Handles profile operations using the backend API
 */

const API_BASE = process.env.NEXT_PUBLIC_API_ORIGIN || 'http://localhost:4000';
const REQUEST_TIMEOUT = 10000; // 10 seconds

export interface UserProfile {
  id: string;
  account_id: string;
  display_name?: string;
  age_band?: string;
  locale?: string;
  timezone?: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface CreateProfileInput {
  displayName?: string;
  ageBand?: string;
  locale?: string;
  timezone?: string;
}

export interface UpdateProfileInput {
  displayName?: string;
  ageBand?: string;
  locale?: string;
  timezone?: string;
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
 * Get current user's profile
 */
export async function getProfile(): Promise<UserProfile | null> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/profile`, {
    method: 'GET',
    credentials: 'include',
  });

  if (response.status === 404) {
    return null; // Profile not found
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get profile');
  }

  return response.json();
}

/**
 * Create a new profile
 */
export async function createProfile(input: CreateProfileInput): Promise<UserProfile> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/profile`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create profile');
  }

  return response.json();
}

/**
 * Update profile
 */
export async function updateProfile(input: UpdateProfileInput): Promise<UserProfile | null> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(input),
  });

  if (response.status === 404) {
    return null; // Profile not found
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to update profile');
  }

  return response.json();
}
