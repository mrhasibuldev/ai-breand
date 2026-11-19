import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

// NOTE: this contract previously targeted the Phase-13 onboarding wellness
// checkbox UI, which was removed in the chat-app redesign. It now verifies
// the accessibility contract of the CURRENT interface: labeled inputs,
// labeled action buttons, labeled navigation, and no display:none hiding of
// interactive controls.
describe('Current UI accessibility contract', () => {
  it('keeps primary inputs and actions labeled for assistive technology', () => {
    const css = readFileSync('apps/web/app/globals.css', 'utf8');
    const chat = readFileSync('apps/web/app/components/ChatInterface.tsx', 'utf8');
    const main = readFileSync('apps/web/app/components/MainContent.tsx', 'utf8');

    // Main prompt input and chat composer must be labeled
    expect(main).toContain('aria-label="AI input"');
    expect(chat).toContain('aria-label={isTyping ? "Cancel request" : "Send message"}');
    expect(main).toContain('aria-label="Send message"');

    // Navigation landmarks must be labeled
    expect(main).toContain('aria-label="Mobile navigation"');
    expect(main).toContain('aria-label="User profile"');

    // Interactive controls must not be hidden with display:none in CSS
    expect(css).not.toMatch(/\.main-input[^}]*display\s*:\s*none/);
    expect(css).not.toMatch(/\.chat-input[^}]*display\s*:\s*none/);
    expect(css).not.toMatch(/\.send-button[^}]*display\s*:\s*none/);
  });
});
