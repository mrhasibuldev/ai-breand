'use client';

/**
 * Home Page Component
 *
 * Main application entry point.
 * Combines Sidebar and MainContent to create the full app layout.
 *
 * @component
 * @example
 * <Home />
 */

import { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import AuthModal from './components/AuthModal';
import ProfileEdit from './components/ProfileEdit';
import ProfileMenu from './components/ProfileMenu';
import Settings from './components/Settings';
import LogoutConfirmDialog from './components/LogoutConfirmDialog';
import MobileProfileScreen from './components/MobileProfileScreen';
import { AuthProvider, useAuth } from './components/AuthContext';
import { getProfile, createProfile, updateProfile } from '../lib/backend-profile';
import { loadAvatar } from '../lib/avatar-service';

/**
 * Home Page Component
 *
 * Root component for the application.
 * Manages navigation state and renders the full app layout.
 */
function HomeContent() {
  const [activeNav, setActiveNav] = useState('home');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isProfileEditOpen, setIsProfileEditOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isLogoutConfirmOpen, setIsLogoutConfirmOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [isMobileProfileOpen, setIsMobileProfileOpen] = useState(false);
  const [profileMenuPosition, setProfileMenuPosition] = useState({ top: 0, left: 0 });
  const profileCardRef = useRef<HTMLDivElement>(null);

  // Profile state
  const [profileName, setProfileName] = useState('Guest');
  const [profileEmail, setProfileEmail] = useState('');
  const [profilePhoto, setProfilePhoto] = useState<string | null>(null);
  const [localProfileName, setLocalProfileName] = useState('Guest');
  const [localProfileEmail, setLocalProfileEmail] = useState('');
  const [localProfilePhoto, setLocalProfilePhoto] = useState<string | null>(null);
  const { user, isAuthenticated, initialized, signOut } = useAuth();

  // Sync local profile state with props
  useEffect(() => {
    setLocalProfileName(profileName);
    setLocalProfileEmail(profileEmail);
    setLocalProfilePhoto(profilePhoto);
  }, [profileName, profileEmail, profilePhoto]);

  // Update profile when auth state changes
  useEffect(() => {
    if (isAuthenticated && user) {
      setProfileName(user.email?.split('@')[0] || 'User');
      setProfileEmail(user.email || '');

      // Load profile from backend
      getProfile().then((profile) => {
        if (profile) {
          setProfileName(profile.display_name || user.email?.split('@')[0] || 'User');
          // Load avatar from backend (localStorage fallback removed)
          loadAvatar(user.id).then((avatarUrl) => {
            if (avatarUrl) {
              setProfilePhoto(avatarUrl);
            }
          }).catch((error) => {
            console.warn('[Profile] Failed to load avatar:', error);
          });
        }
      }).catch((error) => {
        console.error('[Profile] Failed to load profile:', error);
      });
    } else if (initialized) {
      // Only reset to Guest if initialization is complete and not authenticated
      setProfileName('Guest');
      setProfileEmail('');
      setProfilePhoto(null);
    }
  }, [isAuthenticated, user, initialized]);

  /**
   * Handle navigation change
   * @param nav - Navigation item ID to activate
   */
  const handleNavChange = (nav: string) => {
    setActiveNav(nav);
  };

  /**
   * Handle profile save
   */
  const handleProfileSave = async (name: string, email: string, photoUrl: string | null) => {
    if (!isAuthenticated || !user) {
      console.error('[Profile] Cannot save: user not authenticated');
      return;
    }

    try {
      const existingProfile = await getProfile();

      if (existingProfile) {
        await updateProfile({ displayName: name });
      } else {
        await createProfile({ displayName: name });
      }

      setProfileName(name);
      setProfileEmail(email);
      setProfilePhoto(photoUrl);
      setLocalProfileName(name);
      setLocalProfileEmail(email);
      setLocalProfilePhoto(photoUrl);

      console.log('[Profile] Saved successfully');
    } catch (error) {
      console.error('[Profile] Failed to save:', error);
      throw error;
    }
  };

  /**
   * Handle profile edit close
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleProfileEditClose = () => {
    setIsProfileEditOpen(false);
  };

  /**
   * Handle profile card click (open profile menu)
   */
  const handleProfileClick = () => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
    } else {
      // Check if on mobile (viewport width <= 768px)
      const isMobile = window.innerWidth <= 768;

      if (isMobile) {
        // Mobile: Open full-screen profile screen
        setIsMobileProfileOpen(true);
      } else {
        // Desktop: Calculate position to appear above the profile card within sidebar
        if (profileCardRef.current) {
          const rect = profileCardRef.current.getBoundingClientRect();
          const menuHeight = 200;
          const gap = 8;

          // Position menu above the profile card, aligned to sidebar left edge
          const top = rect.top - menuHeight - gap;
          const left = 24; // Sidebar padding (24px from viewport left)

          setProfileMenuPosition({ top, left });
        } else {
          // Fallback: Position near bottom of sidebar
          const viewportHeight = window.innerHeight;
          const menuHeight = 200;

          const top = viewportHeight - menuHeight - 100;
          const left = 24; // Sidebar padding

          setProfileMenuPosition({ top, left });
        }
        setIsProfileMenuOpen(true);
      }
    }
  };

  /**
   * Handle profile edit click
   */
  const handleProfileEditClick = () => {
    if (isAuthenticated) {
      setIsSettingsOpen(false); // Close Settings when opening ProfileEdit
      setIsProfileEditOpen(true);
    }
  };

  /**
   * Handle settings click
   */
  const handleSettingsClick = () => {
    setIsMobileProfileOpen(false); // Close mobile profile when opening settings
    setIsSettingsOpen(true);
  };

  /**
   * Handle logout click (show confirmation)
   */
  const handleLogoutClick = () => {
    setIsMobileProfileOpen(false); // Close mobile profile when logout is clicked
    setIsLogoutConfirmOpen(true);
  };

  /**
   * Handle logout confirmation
   */
  const handleLogoutConfirm = async () => {
    setIsLoggingOut(true);
    try {
      await signOut();
      setIsProfileMenuOpen(false);
      setIsSettingsOpen(false);
      setIsLogoutConfirmOpen(false);
      setProfileName('Guest');
      setProfileEmail('');
      setProfilePhoto(null);
      setLocalProfileName('Guest');
      setLocalProfileEmail('');
      setLocalProfilePhoto(null);
    } catch (error) {
      console.error('[Logout] Failed to logout:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  /**
   * Handle logout cancel
   */
  const handleLogoutCancel = () => {
    setIsLogoutConfirmOpen(false);
  };

  /**
   * Handle mobile profile open
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleMobileProfileOpen = () => {
    setIsMobileProfileOpen(true);
  };

  /**
   * Handle mobile profile back
   */
  const handleMobileProfileBack = () => {
    setIsMobileProfileOpen(false);
  };

  return (
    <div className="app-container">
      {/* Loading Overlay - only for authenticated users during session restoration */}
      {!initialized && isAuthenticated && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading...</p>
          </div>
        </div>
      )}

      {/* Left Sidebar Navigation */}
      <Sidebar
        activeNav={activeNav}
        onNavChange={handleNavChange}
        profileName={profileName}
        profileEmail={profileEmail}
        profilePhoto={profilePhoto}
        isAuthenticated={isAuthenticated}
        onProfileClick={handleProfileClick}
        profileCardRef={profileCardRef}
      />

      {/* Main Content Area */}
      <MainContent
        activeNav={activeNav}
        onNavChange={handleNavChange}
        profileName={profileName}
        profileEmail={profileEmail}
        profilePhoto={profilePhoto}
        onProfileSave={handleProfileSave}
        isAuthenticated={isAuthenticated}
        onAuthRequired={() => setShowAuthModal(true)}
        isProfileEditOpen={isProfileEditOpen}
        onProfileEditClose={() => setIsProfileEditOpen(false)}
        onProfileMenuRequest={handleProfileClick}
      />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      {/* Profile Edit Dialog */}
      {isProfileEditOpen && (
        <ProfileEdit
          initialName={localProfileName}
          initialEmail={localProfileEmail}
          initialPhotoUrl={localProfilePhoto}
          onSave={handleProfileSave}
          onClose={() => setIsProfileEditOpen(false)}
        />
      )}

      {/* Profile Menu */}
      {isProfileMenuOpen && (
        <ProfileMenu
          profileName={profileName}
          profileEmail={profileEmail}
          profilePhoto={profilePhoto}
          isOpen={isProfileMenuOpen}
          onClose={() => setIsProfileMenuOpen(false)}
          onSettings={handleSettingsClick}
          onLogout={handleLogoutClick}
          position={profileMenuPosition}
        />
      )}

      {/* Settings Dialog */}
      {isSettingsOpen && (
        <Settings
          profileName={profileName}
          profileEmail={profileEmail}
          profilePhoto={profilePhoto}
          onClose={() => setIsSettingsOpen(false)}
          onProfileEditRequest={handleProfileEditClick}
          isMobile={window.innerWidth <= 768}
        />
      )}

      {/* Mobile Profile Screen */}
      {isMobileProfileOpen && (
        <MobileProfileScreen
          profileName={profileName}
          profileEmail={profileEmail}
          profilePhoto={profilePhoto}
          onBack={handleMobileProfileBack}
          onSettings={handleSettingsClick}
          onLogout={handleLogoutClick}
          onEditProfile={handleProfileEditClick}
        />
      )}

      {/* Profile Edit Dialog - Available from both Settings and Mobile Profile */}
      {isProfileEditOpen && (
        <ProfileEdit
          initialName={profileName}
          initialEmail={profileEmail}
          initialPhotoUrl={profilePhoto}
          onSave={handleProfileSave}
          onClose={() => setIsProfileEditOpen(false)}
        />
      )}

      {/* Logout Confirmation Dialog */}
      <LogoutConfirmDialog
        isOpen={isLogoutConfirmOpen}
        isLoggingOut={isLoggingOut}
        onConfirm={handleLogoutConfirm}
        onCancel={handleLogoutCancel}
      />
    </div>
  );
}

export default function Home() {
  return (
    <AuthProvider>
      <HomeContent />
    </AuthProvider>
  );
}
