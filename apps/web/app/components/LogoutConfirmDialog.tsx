'use client';

/**
 * Logout Confirmation Dialog
 *
 * Confirms logout action before executing
 */

import { LogOut } from 'lucide-react';

interface LogoutConfirmDialogProps {
  /** Whether dialog is open */
  isOpen: boolean;
  /** Whether logout is in progress */
  isLoggingOut: boolean;
  /** Callback when logout is confirmed */
  onConfirm: () => void;
  /** Callback when dialog is cancelled */
  onCancel: () => void;
}

export default function LogoutConfirmDialog({
  isOpen,
  isLoggingOut,
  onConfirm,
  onCancel,
}: LogoutConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="logout-confirm-overlay" onClick={onCancel}>
      <div className="logout-confirm-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="logout-confirm-header">
          <div className="logout-confirm-icon">
            <LogOut size={32} />
          </div>
          <h2>Log Out</h2>
        </div>

        {/* Content */}
        <div className="logout-confirm-content">
          <p>Are you sure you want to log out?</p>
          <p className="logout-confirm-subtext">You will need to sign in again to access your account.</p>
        </div>

        {/* Footer */}
        <div className="logout-confirm-footer">
          <button
            className="logout-confirm-cancel"
            onClick={onCancel}
            disabled={isLoggingOut}
            type="button"
          >
            Cancel
          </button>
          <button
            className="logout-confirm-confirm"
            onClick={onConfirm}
            disabled={isLoggingOut}
            type="button"
            style={{ opacity: isLoggingOut ? 0.5 : 1 }}
          >
            {isLoggingOut ? 'Logging out...' : 'Log Out'}
          </button>
        </div>
      </div>
    </div>
  );
}
