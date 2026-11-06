'use client';

/**
 * Mobile Profile Screen Component
 *
 * Full-screen profile interface for mobile devices
 * Facebook-inspired design with organized profile information and settings navigation
 */

import { ArrowLeft, Settings, LogOut, Edit, ChevronRight } from 'lucide-react';

interface MobileProfileScreenProps {
  /** Profile name */
  profileName: string;
  /** Profile email */
  profileEmail: string;
  /** Profile photo URL */
  profilePhoto: string | null;
  /** Callback when back is pressed */
  onBack: () => void;
  /** Callback when Settings is clicked */
  onSettings: () => void;
  /** Callback when Logout is clicked */
  onLogout: () => void;
  /** Callback when Edit Profile is clicked */
  onEditProfile: () => void;
}

export default function MobileProfileScreen({
  profileName,
  profileEmail,
  profilePhoto,
  onBack,
  onSettings,
  onLogout,
  onEditProfile,
}: MobileProfileScreenProps) {
  return (
    <div className="mobile-profile-screen">
      {/* Header */}
      <div className="mobile-profile-header">
        <button className="mobile-profile-back" onClick={onBack} aria-label="Back">
          <ArrowLeft size={24} />
        </button>
        <h1 className="mobile-profile-title">Profile</h1>
        <div className="mobile-profile-header-spacer" />
      </div>

      {/* Profile Card */}
      <div className="mobile-profile-card">
        <div className="mobile-profile-avatar-large">
          {profilePhoto ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={profilePhoto} alt={profileName} className="mobile-profile-avatar-img" />
          ) : (
            <div className="mobile-profile-avatar-placeholder">
              {profileName.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <h2 className="mobile-profile-name-large">{profileName}</h2>
        <p className="mobile-profile-email-large">{profileEmail}</p>
        <button className="mobile-profile-edit-btn" onClick={onEditProfile}>
          <Edit size={16} />
          <span>Edit Profile</span>
        </button>
      </div>

      {/* Actions Section */}
      <div className="mobile-profile-section">
        <h3 className="mobile-profile-section-title">Account</h3>
        
        <button className="mobile-profile-action-item" onClick={onSettings}>
          <div className="mobile-profile-action-icon">
            <Settings size={20} />
          </div>
          <div className="mobile-profile-action-content">
            <span className="mobile-profile-action-label">Settings</span>
            <span className="mobile-profile-action-subtitle">Manage your account and preferences</span>
          </div>
          <ChevronRight className="mobile-profile-action-chevron" size={20} />
        </button>

        <button className="mobile-profile-action-item" onClick={onLogout}>
          <div className="mobile-profile-action-icon mobile-profile-action-icon-danger">
            <LogOut size={20} />
          </div>
          <div className="mobile-profile-action-content">
            <span className="mobile-profile-action-label mobile-profile-action-label-danger">Log Out</span>
            <span className="mobile-profile-action-subtitle">Sign out of your account</span>
          </div>
          <ChevronRight className="mobile-profile-action-chevron" size={20} />
        </button>
      </div>
    </div>
  );
}
