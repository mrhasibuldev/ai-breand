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

import { useState } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';

/**
 * Home Page Component
 *
 * Root component for the application.
 * Manages navigation state and renders the full app layout.
 */
export default function Home() {
  // State for currently active navigation item
  const [activeNav, setActiveNav] = useState('home');

  /**
   * Handle navigation change
   * @param nav - Navigation item ID to activate
   */
  const handleNavChange = (nav: string) => {
    setActiveNav(nav);
  };

  return (
    <div className="app-container">
      {/* Left Sidebar Navigation */}
      <Sidebar activeNav={activeNav} onNavChange={handleNavChange} />

      {/* Main Content Area */}
      <MainContent activeNav={activeNav} onNavChange={handleNavChange} />
    </div>
  );
}
