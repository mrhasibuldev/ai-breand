'use client';

/**
 * Authentication Modal Component
 * 
 * Provides signup and login functionality
 */

import { useState } from 'react';
import { X, Mail, Lock } from 'lucide-react';
import { signUp, signIn } from '../../lib/backend-auth';
import { useAuth } from './AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultMode?: 'login' | 'signup';
}

export default function AuthModal({ isOpen, onClose, defaultMode = 'login' }: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'signup'>(defaultMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { forceRefresh } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'signup') {
        await signUp(email, password);
      } else {
        await signIn(email, password);
      }

      // Success - close modal and refresh session
      onClose();
      // Note: forceRefresh happens, but loading state is already cleared
      // The AuthContext will handle the session restoration
      await forceRefresh();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login');
    setError('');
  };

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="auth-modal-header">
          <h2>{mode === 'login' ? 'Log In' : 'Create Account'}</h2>
          <button
            className="auth-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="auth-modal-content">
          {error && (
            <div className="auth-error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-form-group">
              <label htmlFor="auth-email">
                <Mail size={16} />
                Email
              </label>
              <input
                id="auth-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                disabled={loading}
              />
            </div>

            <div className="auth-form-group">
              <label htmlFor="auth-password">
                <Lock size={16} />
                Password
              </label>
              <input
                id="auth-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="•••••••••"
                required
                disabled={loading}
                minLength={8}
              />
            </div>

            <button
              type="submit"
              className="auth-submit-button"
              disabled={loading || !email || !password}
            >
              {loading ? 'Processing...' : mode === 'login' ? 'Log In' : 'Create Account'}
            </button>
          </form>

          {/* Switch Mode */}
          <div className="auth-switch-mode">
            {mode === 'login' ? (
              <>
                <span>Don't have an account?</span>
                <button type="button" onClick={switchMode} disabled={loading}>
                  Sign Up
                </button>
              </>
            ) : (
              <>
                <span>Already have an account?</span>
                <button type="button" onClick={switchMode} disabled={loading}>
                  Log In
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
