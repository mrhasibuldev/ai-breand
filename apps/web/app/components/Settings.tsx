'use client';

/**
 * Settings Component
 *
 * Complete Settings and Account Management experience with:
 * - Account & Profile (includes ProfileEdit)
 * - Appearance
 * - AI & Chat Preferences
 * - Privacy & Security
 * - Notifications
 * - About & Support
 */

import { useState } from 'react';
import {
  User,
  Palette,
  Bot,
  Shield,
  Bell,
  Info,
  ChevronRight,
  X,
  Camera,
} from 'lucide-react';
import MobileSettingsDetailScreen from './MobileSettingsDetailScreen';
import { useTheme } from './ThemeProvider';

interface SettingsProps {
  /** Profile name */
  profileName: string;
  /** Profile email */
  profileEmail: string;
  /** Profile photo URL */
  profilePhoto: string | null;
  /** Callback when close is requested */
  onClose: () => void;
  /** Callback when profile edit is requested */
  onProfileEditRequest: () => void;
  /** Whether on mobile */
  isMobile?: boolean;
}

type SettingsSection = 'account' | 'appearance' | 'ai' | 'privacy' | 'notifications' | 'about';

export type { SettingsSection };

export default function Settings({
  profileName,
  profileEmail,
  profilePhoto,
  onClose,
  onProfileEditRequest,
  isMobile = false,
}: SettingsProps) {
  const [activeSection, setActiveSection] = useState<SettingsSection>('account');
  const [isMobileDetailOpen, setIsMobileDetailOpen] = useState(false);

  // Handle mobile section click - open detail screen
  const handleMobileSectionClick = (section: SettingsSection) => {
    setActiveSection(section);
    setIsMobileDetailOpen(true);
  };

  // Handle mobile detail back
  const handleMobileDetailBack = () => {
    setIsMobileDetailOpen(false);
  };

  const sections = [
    { id: 'account' as SettingsSection, label: 'Account & Profile', icon: User },
    { id: 'appearance' as SettingsSection, label: 'Appearance', icon: Palette },
    { id: 'ai' as SettingsSection, label: 'AI & Chat Preferences', icon: Bot },
    { id: 'privacy' as SettingsSection, label: 'Privacy & Security', icon: Shield },
    { id: 'notifications' as SettingsSection, label: 'Notifications', icon: Bell },
    { id: 'about' as SettingsSection, label: 'About & Support', icon: Info },
  ];

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="settings-header">
          <div className="settings-header-content">
            <h2>Settings</h2>
            <p className="settings-header-description">Manage your account, preferences, and application settings</p>
          </div>
          <button
            className="settings-close"
            onClick={onClose}
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="settings-content">
          {/* Navigation Sidebar */}
          <div className="settings-nav">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  className={`settings-nav-item ${activeSection === section.id ? 'active' : ''}`}
                  onClick={() => {
                    if (isMobile) {
                      handleMobileSectionClick(section.id);
                    } else {
                      setActiveSection(section.id);
                    }
                  }}
                >
                  <Icon size={18} />
                  <span>{section.label}</span>
                  {activeSection === section.id && <ChevronRight size={16} />}
                </button>
              );
            })}
          </div>

          {/* Settings Panel - Desktop Only */}
          {!isMobile && (
            <div className="settings-panel">
              {activeSection === 'account' && (
                <SettingsAccount
                  profileName={profileName}
                  profileEmail={profileEmail}
                  profilePhoto={profilePhoto}
                  onEditProfile={onProfileEditRequest}
                />
              )}
              {activeSection === 'appearance' && (
                <SettingsAppearance />
              )}
              {activeSection === 'ai' && <SettingsAIPreferences />}
              {activeSection === 'privacy' && <SettingsPrivacySecurity />}
              {activeSection === 'notifications' && <SettingsNotifications />}
              {activeSection === 'about' && <SettingsAbout />}
            </div>
          )}
        </div>

        {/* Mobile Settings Detail Screen */}
        {isMobile && isMobileDetailOpen && (
          <MobileSettingsDetailScreen
            activeSection={activeSection}
            onBack={handleMobileDetailBack}
          >
            {activeSection === 'account' && (
              <SettingsAccount
                profileName={profileName}
                profileEmail={profileEmail}
                profilePhoto={profilePhoto}
                onEditProfile={onProfileEditRequest}
              />
            )}
            {activeSection === 'appearance' && (
              <SettingsAppearance />
            )}
            {activeSection === 'ai' && <SettingsAIPreferences />}
            {activeSection === 'privacy' && <SettingsPrivacySecurity />}
            {activeSection === 'notifications' && <SettingsNotifications />}
            {activeSection === 'about' && <SettingsAbout />}
          </MobileSettingsDetailScreen>
        )}
      </div>
    </div>
  );
}

/**
 * Account & Profile Section
 */
function SettingsAccount({
  profileName,
  profileEmail,
  profilePhoto,
  onEditProfile,
}: {
  profileName: string;
  profileEmail: string;
  profilePhoto: string | null;
  onEditProfile: () => void;
}) {
  return (
    <div className="settings-section">
      <h3>Account & Profile</h3>

      {/* Profile Card */}
      <div className="settings-profile-card">
        <div className="settings-profile-avatar">
          {profilePhoto ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={profilePhoto} alt={profileName} className="settings-profile-avatar-img" />
          ) : (
            profileName.charAt(0).toUpperCase()
          )}
        </div>
        <div className="settings-profile-info">
          <div className="settings-profile-name">{profileName}</div>
          <div className="settings-profile-email">{profileEmail}</div>
        </div>
        <button
          className="settings-profile-edit"
          onClick={onEditProfile}
        >
          <Camera size={16} />
          Edit Profile
        </button>
      </div>

      {/* Account Information */}
      <div className="settings-info-group">
        <h4>Account Information</h4>
        <div className="settings-info-item">
          <label>Email Address</label>
          <div className="settings-info-value">{profileEmail}</div>
        </div>
      </div>
    </div>
  );
}

/**
 * AI & Chat Preferences Section
 */
function SettingsAIPreferences() {
  return (
    <div className="settings-section">
      <h3>AI & Chat Preferences</h3>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Response Language</label>
          <p className="settings-option-description">Language for AI responses</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Response Style</label>
          <p className="settings-option-description">AI response tone and style</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Conversation Preferences</label>
          <p className="settings-option-description">Chat behavior and memory</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>
    </div>
  );
}

/**
 * Privacy & Security Section
 */
function SettingsPrivacySecurity() {
  return (
    <div className="settings-section">
      <h3>Privacy & Security</h3>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Change Password</label>
          <p className="settings-option-description">Update your account password</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Session Information</label>
          <p className="settings-option-description">View active sessions</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-info-group">
        <h4>Privacy Information</h4>
        <p className="settings-info-text">
          NexusAI values your privacy. Your personal information is stored securely and is not shared with third parties.
        </p>
      </div>
    </div>
  );
}

/**
 * Notifications Section
 */
function SettingsNotifications() {
  return (
    <div className="settings-section">
      <h3>Notifications</h3>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>General Notifications</label>
          <p className="settings-option-description">App-wide notification settings</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Wellness Reminders</label>
          <p className="settings-option-description">Health and wellness reminders</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Notification Sound</label>
          <p className="settings-option-description">Sound for notifications</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>
    </div>
  );
}

/**
 * About & Support Section
 */
function SettingsAbout() {
  return (
    <div className="settings-section">
      <h3>About & Support</h3>

      <div className="settings-info-group">
        <h4>About NexusAI</h4>
        <p className="settings-info-text">
          NexusAI is your Personal AI Health & Wellness Companion, designed to help you achieve your wellness goals through intelligent conversations and personalized insights.
        </p>
      </div>

      <div className="settings-info-group">
        <h4>Application Version</h4>
        <div className="settings-info-item">
          <label>Version</label>
          <div className="settings-info-value">0.1.0</div>
        </div>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Help & Support</label>
          <p className="settings-option-description">Get help and support</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Privacy Policy</label>
          <p className="settings-option-description">Read our privacy policy</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Terms of Service</label>
          <p className="settings-option-description">Read our terms of service</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>
    </div>
  );
}

/**
 * Appearance Section
 */
function SettingsAppearance() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="settings-section">
      <h3>Appearance</h3>

      <div className="settings-option">
        <div className="settings-option-info">
          <label>Theme</label>
          <p className="settings-option-description">Choose your preferred theme</p>
        </div>
        <select
          className="settings-select"
          value={theme}
          onChange={(e) => setTheme(e.target.value as 'system' | 'light' | 'dark')}
        >
          <option value="system">System Default</option>
          <option value="light">Light Mode</option>
          <option value="dark">Dark Mode</option>
        </select>
      </div>

      <div className="settings-option settings-option-disabled">
        <div className="settings-option-info">
          <label>Accent Color</label>
          <p className="settings-option-description">Customize your accent color</p>
        </div>
        <span className="settings-option-badge">Coming Soon</span>
      </div>
    </div>
  );
}
