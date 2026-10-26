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

import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './components/AuthContext';
import { getProfile, createProfile, updateProfile } from '../lib/backend-profile';
import { loadAvatarFromLocalStorage } from '../lib/avatar-service';

/**
 * Home Page Component
 *
 * Root component for the application.
 * Manages navigation state and renders the full app layout.
 */
function HomeContent() {
  const [activeNav, setActiveNav] = useState('home');
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Profile state
  const [profileName, setProfileName] = useState('Guest');
  const [profileEmail, setProfileEmail] = useState('');
  const [profilePhoto, setProfilePhoto] = useState<string | null>(null);
  const { user, isAuthenticated, initialized } = useAuth();

  // Update profile when auth state changes
  useEffect(() => {
    if (isAuthenticated && user) {
      setProfileName(user.email?.split('@')[0] || 'User');
      setProfileEmail(user.email || '');

      // Load profile from backend
      getProfile().then((profile) => {
        if (profile) {
          setProfileName(profile.display_name || user.email?.split('@')[0] || 'User');
          const localAvatar = loadAvatarFromLocalStorage(user.id);
          if (localAvatar) {
            setProfilePhoto(localAvatar);
          }
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

      console.log('[Profile] Saved successfully');
    } catch (error) {
      console.error('[Profile] Failed to save:', error);
      throw error;
    }
  };

  /**
   * Handle profile card click
   */
  const handleProfileClick = () => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
    }
    // Profile edit will be handled by MainContent
  };

  /**
   * Handle logout
   */
  const handleLogout = async () => {
    const { signOut } = useAuth();
    await signOut();
    setShowAuthModal(false);
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
        onLogout={handleLogout}
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
      />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
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
