'use client';

/**
 * Authentication Context
 * 
 * Provides authentication state and methods to the application
 * Uses backend API for authentication
 */

import { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { signOut, getSession, isBackendConfigured, type User } from '../../lib/backend-auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  initialized: boolean;
  isAuthenticated: boolean;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const refreshUser = async () => {
    if (!isBackendConfigured()) {
      setUser(null);
      setLoading(false);
      setInitialized(true);
      return;
    }

    // Cancel previous request if exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    try {
      const session = await getSession();
      if (session.authenticated && session.account_id && session.email) {
        setUser({
          id: session.account_id,
          email: session.email,
        });
      } else {
        // Only set to null if backend definitively says not authenticated
        setUser(null);
      }
    } catch (error) {
      // On timeout or network error, preserve existing user state during initialization
      // After initialization, errors may indicate actual logout
      if (!initialized) {
        console.log('[Auth] Initial session check failed, retrying...', error);
        // Don't change user state on initial load failure
        // Will retry with polling
      } else {
        // After initialization, treat errors as unauthenticated
        // Unless it's a timeout (preserve state for network issues)
        if (error instanceof Error && error.message === 'Request timeout') {
          // Keep existing user state silently
          console.log('[Auth] Session check timeout, preserving existing state');
          return;
        }
        console.log('[Auth] Session check failed after initialization, treating as unauthenticated', error);
        setUser(null);
      }
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  };

  useEffect(() => {
    if (!isBackendConfigured()) {
      setLoading(false);
      setInitialized(true);
      return;
    }

    // Get initial session
    refreshUser();

    // Poll for session changes periodically (for demo purposes)
    // In production, this could use server-sent events or websockets
    const interval = setInterval(refreshUser, 30000); // Check every 30 seconds

    return () => {
      clearInterval(interval);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleSignOut = async () => {
    try {
      await signOut();
      setUser(null);
    } catch (error) {
      console.error('[Auth] Failed to sign out:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        initialized,
        isAuthenticated: !!user,
        signOut: handleSignOut,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
