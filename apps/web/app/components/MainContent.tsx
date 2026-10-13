'use client';

/**
 * MainContent Component
 *
 * Displays the main content area with:
 * - Greeting section with animated orb
 * - AI input field with action pills
 * - Chat interface for NexusData AI
 * - Mobile bottom navigation bar
 * - Placeholder pages for non-home sections
 *
 * @component
 * @example
 * <MainContent activeNav="home" onNavChange={(nav) => console.log(nav)} />
 */

import { useState } from 'react';
import { Zap, Image, FileText, Send, Home, Compass, Library, MessageSquare } from 'lucide-react';
import ChatInterface from './ChatInterface';

/**
 * Action pill configuration for input field
 */
interface ActionPill {
  /** Unique identifier for the action pill */
  id: string;
  /** Display label for the action pill */
  label: string;
  /** Icon component to display */
  icon: React.ComponentType<{ size?: number; className?: string }>;
}

/**
 * Navigation item configuration for mobile nav
 */
interface MobileNavItem {
  /** Unique identifier for the navigation item */
  id: string;
  /** Display label for the navigation item */
  label: string;
  /** Icon component to display */
  icon: React.ComponentType<{ size?: number; className?: string }>;
}

/**
 * Props for the MainContent component
 */
interface MainContentProps {
  /** Currently active navigation item ID */
  activeNav: string;
  /** Callback function when navigation changes */
  onNavChange: (nav: string) => void;
}

/**
 * Action pills configuration for the input field
 */
const ACTION_PILLS: ActionPill[] = [
  { id: 'reasoning', label: 'Reasoning', icon: Zap },
  { id: 'image', label: 'Create Image', icon: Image },
  { id: 'research', label: 'Deep Research', icon: FileText },
];

/**
 * Mobile navigation items configuration
 */
const MOBILE_NAV_ITEMS: MobileNavItem[] = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'explore', label: 'Explore', icon: Compass },
  { id: 'library', label: 'Library', icon: Library },
  { id: 'chat', label: 'Chat', icon: MessageSquare },
];

/**
 * MainContent Component
 *
 * Main content area for the application.
 * Contains greeting, input field, chat interface, and mobile navigation.
 */
export default function MainContent({ activeNav, onNavChange }: MainContentProps) {
  // State for input field value
  const [inputValue, setInputValue] = useState('');
  // State for message to pass to chat
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  // State for active action pill
  const [activePill, setActivePill] = useState<string | null>(null);

  /**
   * Handle form submission - redirect to chat with message
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setPendingMessage(inputValue);
      onNavChange('chat');
      setInputValue('');
    }
  };

  /**
   * Render Chat page
   */
  if (activeNav === 'chat') {
    return (
      <main className="main-content">
        <div className="content-area chat-mode">
          <ChatInterface {...(pendingMessage ? { initialMessage: pendingMessage } : {})} />
        </div>
        {/* Mobile Navigation */}
        <MobileNavigation activeNav={activeNav} onNavChange={onNavChange} />
      </main>
    );
  }

  /**
   * Render placeholder page for other non-home sections
   */
  if (activeNav !== 'home') {
    return (
      <main className="main-content">
        <div className="content-area">
          <div className="greeting-section">
            <h1 className="greeting-title">
              {activeNav.charAt(0).toUpperCase() + activeNav.slice(1)}
            </h1>
            <p className="greeting-subtitle">Coming soon...</p>
          </div>
        </div>
        {/* Mobile Navigation */}
        <MobileNavigation activeNav={activeNav} onNavChange={onNavChange} />
      </main>
    );
  }

  return (
    <main className="main-content">
      <div className="content-area">
        {/* Greeting Section */}
        <GreetingSection />

        {/* Input Section */}
        <InputSection
          inputValue={inputValue}
          onInputChange={setInputValue}
          activePill={activePill}
          onPillToggle={setActivePill}
          onSubmit={handleSubmit}
        />
      </div>

      {/* Mobile Navigation */}
      <MobileNavigation activeNav={activeNav} onNavChange={onNavChange} />
    </main>
  );
}

/**
 * Greeting Section Component
 *
 * Displays animated orb and time-based greeting
 */
function GreetingSection() {
  const getGreeting = (): string => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  return (
    <div className="greeting-section">
      <div className="greeting-orb" aria-hidden="true" />
      <h1 className="greeting-title">
        {getGreeting()}, Judha.
      </h1>
      <p className="greeting-subtitle">
        How Can I <span className="greeting-highlight">Assist You Today?</span>
      </p>
    </div>
  );
}

/**
 * Input Section Component
 *
 * Displays AI input field with action pills
 */
interface InputSectionProps {
  inputValue: string;
  onInputChange: (value: string) => void;
  activePill: string | null;
  onPillToggle: (pillId: string | null) => void;
  onSubmit: (e: React.FormEvent) => void;
}

function InputSection({
  inputValue,
  onInputChange,
  activePill,
  onPillToggle,
  onSubmit,
}: InputSectionProps) {
  return (
    <div className="input-section">
      <form onSubmit={onSubmit}>
        <div className="input-container">
          <div className="input-wrapper">
            <div className="input-icon">
              <Zap size={24} />
            </div>
            <textarea
              className="main-input"
              placeholder="Initiate a query or send a command to the AI..."
              value={inputValue}
              onChange={(e) => onInputChange(e.target.value)}
              rows={2}
              aria-label="AI input"
            />
          </div>

          <div className="input-actions">
            {/* Action Pills */}
            <div className="action-pills">
              {ACTION_PILLS.map((pill) => {
                const Icon = pill.icon;
                return (
                  <button
                    key={pill.id}
                    type="button"
                    className={`action-pill ${activePill === pill.id ? 'active' : ''}`}
                    onClick={() =>
                      onPillToggle(activePill === pill.id ? null : pill.id)
                    }
                    aria-label={pill.label}
                    aria-pressed={activePill === pill.id}
                  >
                    <Icon size={16} />
                    <span>{pill.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Send Button */}
            <button
              type="submit"
              className="send-button"
              aria-label="Send message"
            >
              <Send size={24} />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

/**
 * Mobile Navigation Component
 *
 * Bottom navigation bar for mobile devices
 */
interface MobileNavigationProps {
  activeNav: string;
  onNavChange: (nav: string) => void;
}

function MobileNavigation({ activeNav, onNavChange }: MobileNavigationProps) {
  return (
    <nav className="mobile-nav" aria-label="Mobile navigation">
      <div className="mobile-nav-items">
        {MOBILE_NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className={`mobile-nav-item ${activeNav === item.id ? 'active' : ''}`}
              onClick={() => onNavChange(item.id)}
              aria-label={item.label}
              aria-current={activeNav === item.id ? 'page' : undefined}
            >
              <Icon />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
      <div className="mobile-nav-profile" aria-label="User profile">
        <div className="mobile-nav-avatar">JM</div>
      </div>
    </nav>
  );
}
