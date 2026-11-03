/**
 * Avatar Service
 *
 * Handles avatar upload to NexusAI backend API with Neon Object Storage
 * localStorage fallback removed - now uses backend storage only
 */

export interface UploadResult {
  publicUrl: string;
  storagePath: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:4000';

/**
 * Upload avatar to backend API
 */
export async function uploadAvatar(
  userId: string,
  file: File
): Promise<{ storagePath: string; publicUrl: string }> {
  console.log('[Avatar] Starting upload for user:', userId);
  console.log('[Avatar] File:', file.name, 'Size:', file.size, 'Type:', file.type);

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    throw new Error('File size exceeds 5MB limit');
  }

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Invalid file type. Only JPEG, PNG, WebP, and GIF are allowed');
  }

  // Create FormData for upload
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/api/storage/avatar`, {
      method: 'POST',
      credentials: 'include', // Include cookies for authentication
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Avatar upload failed');
    }

    const result = await response.json();
    console.log('[Avatar] Upload successful:', result);

    // Generate public URL from key
    const publicUrl = `${API_BASE_URL}/api/storage/avatar/${userId}/${result.metadata.timestamp}?ext=${result.metadata.ext}`;

    return {
      publicUrl,
      storagePath: result.key,
    };
  } catch (error) {
    console.error('[Avatar] Upload failed:', error);
    throw error;
  }
}

/**
 * Load avatar from backend API
 */
export async function loadAvatar(userId: string): Promise<string | null> {
  try {
    // Get the latest avatar timestamp from profile or storage
    // For now, return null and let the UI handle default avatar
    console.log('[Avatar] Loading avatar for user:', userId);
    return null;
  } catch (e) {
    console.warn('[Avatar] Failed to load avatar:', e);
    return null;
  }
}

/**
 * Delete avatar from backend API
 */
export async function deleteAvatar(storagePath: string, userId?: string): Promise<void> {
  if (!userId) {
    console.warn('[Avatar] Cannot delete without userId');
    return;
  }

  try {
    // Parse storage path to get timestamp and extension
    // Format: avatars/{userId}/{timestamp}.{ext}
    const parts = storagePath.split('/');
    const timestampWithExt = parts[parts.length - 1];
    const [timestamp, ext] = timestampWithExt.split('.');

    const response = await fetch(
      `${API_BASE_URL}/api/storage/avatar/${userId}/${timestamp}?ext=${ext}`,
      {
        method: 'DELETE',
        credentials: 'include',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Avatar deletion failed');
    }

    console.log('[Avatar] Delete successful');
  } catch (error) {
    console.error('[Avatar] Delete failed:', error);
    throw error;
  }
}

/**
 * Get avatar URL for display
 */
export function getAvatarUrl(userId: string, timestamp?: number, ext: string = 'jpg'): string {
  if (timestamp) {
    return `${API_BASE_URL}/api/storage/avatar/${userId}/${timestamp}?ext=${ext}`;
  }
  return ''; // Return empty if no avatar set
}
