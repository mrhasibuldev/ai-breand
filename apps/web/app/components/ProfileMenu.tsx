'use client';

/**
 * Profile Menu Component
 *
 * Dropdown menu for authenticated users with:
 * - User profile information
 * - Settings (main entry point for profile editing and account management)
 * - Logout
 */

import { Settings, LogOut } from 'lucide-react';

interface ProfileMenuProps {
  /** Profile name */
  profileName: string;
  /** Profile email */
  profileEmail: string;
  /** Profile photo URL */
  profilePhoto: string | null;
  /** Whether menu is open */
  isOpen: boolean;
  /** Callback when menu closes */
  onClose: () => void;
  /** Callback when Settings is clicked */
  onSettings: () => void;
  /** Callback when Logout is clicked */
  onLogout: () => void;
  /** Menu position coordinates */
  position?: { top: number; left: number };
}

export default function ProfileMenu({
  profileName,
  profileEmail,
  profilePhoto,
  isOpen,
  onClose,
  onSettings,
  onLogout,
  position = { top: 0, left: 0 },
}: ProfileMenuProps) {
  if (!isOpen) return null;

  return (
    <div className="profile-menu-overlay" onClick={onClose}>
      <div
        className="profile-menu"
        onClick={(e) => e.stopPropagation()}
        style={{
          position: 'fixed',
          top: `${position.top}px`,
          left: `${position.left}px`,
        }}
      >
        {/* User Info Header */}
        <div className="profile-menu-header">
          <div className="profile-menu-avatar">
            {profilePhoto ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={profilePhoto} alt={profileName} className="profile-menu-avatar-img" />
            ) : (
              profileName.charAt(0).toUpperCase()
            )}
          </div>
          <div className="profile-menu-info">
            <div className="profile-menu-name">{profileName}</div>
            <div className="profile-menu-email">{profileEmail}</div>
          </div>
        </div>

        {/* Menu Items */}
        <div className="profile-menu-items">
          <button
            className="profile-menu-item"
            onClick={() => {
              onSettings();
              onClose();
            }}
          >
            <Settings size={18} />
            <span>Settings</span>
          </button>

          <div className="profile-menu-divider" />

          <button
            className="profile-menu-item profile-menu-item-danger"
            onClick={() => {
              onLogout();
              onClose();
            }}
          >
            <LogOut size={18} />
            <span>Log Out</span>
          </button>
        </div>
      </div>
    </div>
  );
}
