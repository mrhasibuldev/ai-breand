'use client';

/**
 * Profile Edit Component
 *
 * Allows users to:
 * - Change their display name
 * - Upload/change profile photo
 * - Update email
 *
 * @component
 */

import { useState, useRef } from 'react';
import { X, Camera, Save } from 'lucide-react';
import { uploadAvatar } from '../../lib/avatar-service';
import { useAuth } from './AuthContext';

interface ProfileEditProps {
  /** Current profile data */
  initialName: string;
  initialEmail: string;
  initialPhotoUrl: string | null;
  /** Callback when profile is saved */
  onSave: (name: string, email: string, photoUrl: string | null) => void;
  /** Callback when dialog is closed */
  onClose: () => void;
}

export default function ProfileEdit({
  initialName,
  initialEmail,
  initialPhotoUrl,
  onSave,
  onClose,
}: ProfileEditProps) {
  const [name, setName] = useState(initialName);
  const [email, setEmail] = useState(initialEmail);
  const [photoUrl, setPhotoUrl] = useState<string | null>(initialPhotoUrl);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { user } = useAuth();

  /**
   * Handle file selection for profile photo
   */
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIsUploading(true);
      setUploadError('');

      try {
        if (!user) {
          throw new Error('User not authenticated');
        }

        // Upload to storage
        const { publicUrl } = await uploadAvatar(user.id, file);
        setPhotoUrl(publicUrl);
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('[ProfileEdit] Upload failed:', error);
        setUploadError(error instanceof Error ? error.message : 'Failed to upload image');
      } finally {
        setIsUploading(false);
      }
    }
  };

  /**
   * Trigger file input click
   */
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  /**
   * Remove profile photo
   */
  const handleRemovePhoto = () => {
    setPhotoUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * Handle save
   */
  const handleSave = () => {
    onSave(name, email, photoUrl);
    onClose();
  };

  return (
    <div className="profile-edit-overlay" onClick={onClose}>
      <div className="profile-edit-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="profile-edit-header">
          <h2>Edit Profile</h2>
          <button
            className="profile-edit-close"
            onClick={onClose}
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="profile-edit-content">
          {/* Profile Photo Section */}
          <div className="profile-photo-section">
            <div className="profile-photo-preview">
              {photoUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={photoUrl} alt="Profile" className="profile-photo-image" />
              ) : (
                <div className="profile-photo-placeholder">
                  {name.charAt(0).toUpperCase()}
                </div>
              )}
              <button
                className="profile-photo-upload"
                onClick={handleUploadClick}
                disabled={isUploading}
                aria-label="Change photo"
              >
                {isUploading ? (
                  <span className="uploading-text">Uploading...</span>
                ) : (
                  <Camera size={20} />
                )}
              </button>
            </div>
            {uploadError && (
              <div className="profile-upload-error">
                {uploadError}
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              aria-label="Upload photo"
            />
            {photoUrl && (
              <button
                className="profile-photo-remove"
                onClick={handleRemovePhoto}
                type="button"
              >
                Remove photo
              </button>
            )}
          </div>

          {/* Form Fields */}
          <div className="profile-edit-form">
            <label htmlFor="profile-name">
              Display Name
              <input
                id="profile-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                maxLength={50}
              />
            </label>

            <label htmlFor="profile-email">
              Email
              <input
                id="profile-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                disabled
                title="Email cannot be changed"
              />
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="profile-edit-footer">
          <button
            className="profile-edit-cancel"
            onClick={onClose}
            type="button"
          >
            Cancel
          </button>
          <button
            className="profile-edit-save"
            onClick={handleSave}
            disabled={!name.trim() || isUploading}
            type="button"
            style={{ opacity: (!name.trim() || isUploading) ? 0.5 : 1 }}
          >
            <Save size={16} />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
