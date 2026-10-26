'use client';

/**
 * Sidebar Component
 *
 * Displays the left navigation sidebar with:
 * - Logo and branding
 * - Search bar
 * - Main navigation menu (Home, Explore, Library, History, Chat)
 * - Tomorrow section for scheduled items
 * - User profile card
 *
 * @component
 * @example
 * <Sidebar activeNav="home" onNavChange={(nav) => console.log(nav)} />
 */

import { useState } from 'react';
import {
  X,
  Home,
  Compass,
  Library,
  Clock,
  MessageSquare,
  ChevronDown,
} from 'lucide-react';

/**
 * Navigation item configuration
 */
interface NavItem {
  /** Unique identifier for the navigation item */
  id: string;
  /** Display label for the navigation item */
  label: string;
  /** Icon component to display */
  icon: React.ComponentType<{ size?: number; className?: string }>;
}

/**
 * Props for the Sidebar component
 */
interface SidebarProps {
  /** Currently active navigation item ID */
  activeNav: string;
  /** Callback function when navigation changes */
  onNavChange: (nav: string) => void;
  /** Profile name */
  profileName?: string;
  /** Profile email */
  profileEmail?: string;
  /** Profile photo URL */
  profilePhoto?: string | null;
  /** Whether user is authenticated */
  isAuthenticated?: boolean;
  /** Callback when profile card is clicked */
  onProfileClick?: () => void;
  /** Callback when logout is requested */
  onLogout?: () => void;
}

/**
 * Navigation items configuration
 */
const NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'explore', label: 'Explore', icon: Compass },
  { id: 'library', label: 'Library', icon: Library },
  { id: 'history', label: 'History', icon: Clock },
  { id: 'chat', label: 'Chat', icon: MessageSquare },
];

/**
 * Sidebar Component
 *
 * Main navigation sidebar for the application.
 * Contains logo, search, navigation menu, and user profile.
 */
export default function Sidebar({ 
  activeNav, 
  onNavChange,
  profileName = 'Guest',
  profileEmail = '',
  profilePhoto = null,
  isAuthenticated = false,
  onProfileClick,
  onLogout,
}: SidebarProps) {
  // State for search input
  const [searchQuery, setSearchQuery] = useState('');

  /**
   * Handle search input change
   */
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  /**
   * Clear search input
   */
  const clearSearch = () => {
    setSearchQuery('');
  };

  return (
    <aside className="sidebar">
      {/* Logo Section */}
      <div className="sidebar-header">
        <img src="/images/logo.png" alt="Nexus AI Logo" className="logo-image" />
        <span className="brand-name">Nexus AI</span>
      </div>

      {/* Search Bar */}
      <div className="search-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Q Search"
          value={searchQuery}
          onChange={handleSearchChange}
          aria-label="Search"
        />
        {searchQuery && (
          <button
            className="search-clear"
            onClick={clearSearch}
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Navigation Menu */}
      <nav className="nav-section">
        {/* Main Navigation */}
        <div className="nav-label">Menu</div>
        <ul className="nav-list">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.id}>
                <button
                  className={`nav-item ${activeNav === item.id ? 'active' : ''}`}
                  onClick={() => onNavChange(item.id)}
                  aria-label={item.label}
                  aria-current={activeNav === item.id ? 'page' : undefined}
                >
                  <Icon />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>

        {/* Tomorrow Section */}
        <div className="nav-label">Tomorrow</div>
        <ul className="nav-list">
          <li>
            <button className="nav-item" aria-label="Scheduled items">
              <Clock />
              <span>Scheduled</span>
            </button>
          </li>
        </ul>
      </nav>

      {/* User Profile Card */}
      <div 
        className="profile-card"
        onClick={isAuthenticated ? undefined : onProfileClick}
        style={isAuthenticated ? {} : { cursor: 'pointer' }}
        title={isAuthenticated ? 'Profile' : 'Click to sign in'}
      >
        <div className="profile-header">
          <div className="profile-avatar" aria-label="User avatar">
            {profilePhoto ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={profilePhoto} alt={profileName} className="profile-photo-image" />
            ) : (
              profileName.charAt(0).toUpperCase()
            )}
          </div>
          <div className="profile-info">
            <div className="profile-name">{profileName}</div>
            <div className="profile-email">{profileEmail || (isAuthenticated ? 'Logged in' : 'Click to sign in')}</div>
          </div>
          <div className="profile-action">
            {isAuthenticated ? (
              <button 
                onClick={(e) => { e.stopPropagation(); onLogout?.(); }}
                aria-label="Logout"
                title="Logout"
                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px' }}
              >
                <X size={16} />
              </button>
            ) : (
              <ChevronDown size={16} />
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
