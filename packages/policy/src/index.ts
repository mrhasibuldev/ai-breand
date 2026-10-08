export const SAFETY_MODES = [
  'NORMAL',
  'WELLNESS_REDIRECT',
  'SAFETY_ESCALATION',
  'BLOCKED',
] as const;
export type SafetyMode = (typeof SAFETY_MODES)[number];

export type ConsentDecision = 'granted' | 'revoked' | 'denied' | 'pending';

export function isSafetyMode(value: string): value is SafetyMode {
  return (SAFETY_MODES as readonly string[]).includes(value);
}
