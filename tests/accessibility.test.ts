import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

describe('Phase 13 Part 1 onboarding accessibility contract', () => {
  it('keeps every wellness option as a focusable native checkbox with visible focus', () => {
    const css = readFileSync('apps/web/app/globals.css', 'utf8');
    const page = readFileSync('apps/web/app/page.tsx', 'utf8');
    const choiceInputRule = css.match(/\.choice input\s*\{([^}]*)\}/)?.[1] ?? '';

    expect(choiceInputRule).not.toMatch(/display\s*:\s*none/);
    expect(choiceInputRule).toMatch(/opacity\s*:\s*0/);
    expect(css).toMatch(/\.choice:focus-within\s*\{[^}]*outline\s*:/s);
    expect(page).toContain('type="checkbox"');
    expect(page).toContain('old.includes(area) ? old.filter((x) => x !== area) : [...old, area]');
    expect(page).toContain('disabled={busy || selected.length === 0}');
    expect(page).toContain("aria-describedby={error ? 'app-form-error' : undefined}");
    expect(page).toContain('id="app-form-error" role="alert" tabIndex={-1}');
  });
});
