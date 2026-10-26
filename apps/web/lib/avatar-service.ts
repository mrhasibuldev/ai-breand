/**
 * Avatar Service
 *
 * Handles avatar upload with localStorage fallback for development
 * Supabase Storage dependency removed
 */

export interface UploadResult {
  publicUrl: string;
  storagePath: string;
}

const LOCAL_STORAGE_KEY = 'nexusai_avatar';

/**
 * Save avatar to localStorage
 */
function saveAvatarToLocalStorage(userId: string, file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const dataUrl = reader.result as string;
        localStorage.setItem(`${LOCAL_STORAGE_KEY}_${userId}`, dataUrl);
        console.log('[Avatar] Saved to localStorage');
        resolve(dataUrl);
      } catch (e) {
        reject(e);
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Load avatar from localStorage
 */
export function loadAvatarFromLocalStorage(userId: string): string | null {
  try {
    const dataUrl = localStorage.getItem(`${LOCAL_STORAGE_KEY}_${userId}`);
    if (dataUrl) {
      console.log('[Avatar] Loaded from localStorage');
      return dataUrl;
    }
    return null;
  } catch (e) {
    console.warn('[Avatar] Failed to load from localStorage:', e);
    return null;
  }
}

/**
 * Upload avatar to localStorage (development storage)
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

  // Save to localStorage
  const dataUrl = await saveAvatarToLocalStorage(userId, file);

  return {
    publicUrl: dataUrl,
    storagePath: 'local',
  };
}

/**
 * Delete avatar from localStorage
 */
export async function deleteAvatar(storagePath: string, userId?: string): Promise<void> {
  if (storagePath === 'local' && userId) {
    try {
      localStorage.removeItem(`${LOCAL_STORAGE_KEY}_${userId}`);
      console.log('[Avatar] Deleted from localStorage');
    } catch (e) {
      console.warn('[Avatar] Failed to delete from localStorage:', e);
    }
    return;
  }

  console.warn('[Avatar] Cannot delete from non-local storage path:', storagePath);
}
