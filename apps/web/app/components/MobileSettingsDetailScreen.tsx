'use client';

/**
 * Mobile Settings Detail Screen Component
 *
 * Full-screen detail page for individual Settings categories on mobile
 * Facebook-inspired design with back navigation
 */

import { ArrowLeft } from 'lucide-react';
import { SettingsSection } from './Settings';

interface MobileSettingsDetailScreenProps {
  /** Current active section */
  activeSection: SettingsSection;
  /** Callback when back is pressed */
  onBack: () => void;
  /** Children content for the detail page */
  children: React.ReactNode;
}

export default function MobileSettingsDetailScreen({
  activeSection,
  onBack,
  children,
}: MobileSettingsDetailScreenProps) {
  const sectionTitles: Record<SettingsSection, string> = {
    account: 'Account & Profile',
    appearance: 'Appearance',
    ai: 'AI & Chat Preferences',
    privacy: 'Privacy & Security',
    notifications: 'Notifications',
    about: 'About & Support',
  };

  return (
    <div className="mobile-settings-detail-screen">
      {/* Header */}
      <div className="mobile-settings-detail-header">
        <button className="mobile-settings-detail-back" onClick={onBack} aria-label="Back">
          <ArrowLeft size={24} />
        </button>
        <h1 className="mobile-settings-detail-title">{sectionTitles[activeSection]}</h1>
        <div className="mobile-settings-detail-header-spacer" />
      </div>

      {/* Content */}
      <div className="mobile-settings-detail-content">
        {children}
      </div>
    </div>
  );
}
