import type { SafetyMode } from '@nexusai/policy';

export type SafetyInput = {
  readonly accountId?: string;
  readonly content: string;
  readonly stage: 'input' | 'output';
};

export type SafetyDecision = {
  readonly mode: SafetyMode;
  readonly policyVersion: string;
  readonly allowModel: boolean;
  readonly allowAction: boolean;
};

export interface SafetyPolicyBoundary {
  evaluate(input: SafetyInput): Promise<SafetyDecision>;
}

export type WellnessFreeTextDecision = {
  readonly allowed: boolean;
  readonly policyVersion: 'wellness-input-v1';
  readonly reason?: 'prohibited_clinical_content';
};

const PROHIBITED_WELLNESS_INPUT = [
  /\bdiagnos(?:e|ed|es|ing|is|tic|tics)\b/i,
  // Match literal condition claims/requests; never infer a condition from symptoms.
  /\b(?:diseases?|disorders?|clinical condition)\b/i,
  /\b(?:have|has|suffer from|suffering from)\b.*\b(?:diabetes|cancer|anemia|depression|hypertension|asthma|adhd)\b/i,
  /\bprescri(?:be|bed|bes|bing|ption|ptions)\b/i,
  // This profile contract excludes medication content, including claims, not just advice.
  /\b(?:medications?|medicines?|drugs?|pills?|tablets?|capsules?|dosages?|doses?|dosing)\b/i,
  // Explicit medication vocabulary only; no symptom or condition inference.
  /\b(?:aspirin|insulin|amoxicillin|ibuprofen|acetaminophen|paracetamol|naproxen|flucloxacillin|metformin|cetirizine|warfarin|prednisone|levothyroxine|sertraline|loratadine|antibiotics?)\b/i,
  /\b(?:inject|administer|infuse)\b/i,
  /\b(?:determine|identify|confirm|tell me)\b.*\b(?:disease|clinical condition|disorder)\b/i,
  /\b(?:clinical|medical)\s+(?:triage|treatment|assessment)\b/i,
  /\b(?:treat|treatment|cure)\b.*\b(?:disease|condition|symptoms?|infection|disorder)\b/i,
  /\b(?:treat|treatment|cure|manage|control)\b.*\b(?:diabetes|cancer|anemia|depression|hypertension|asthma|adhd)\b/i,
  /\b(?:guarantee[ds]?|certain|definite)\b.*\b(?:cure|recovery|treatment)\b/i,
  /\b(?:replace|act as|be my)\b.*\b(?:doctor|therapist|pharmacist|crisis responder|emergency service)\b/i,
  /\b(?:dispatch|contact|call|monitor)\b.*\b(?:ambulance|emergency|paramedic)\b/i,
] as const;

const QUANTITY = '(?:\\d+(?:\\.\\d+)?|half|one|two|three|four|five|six|seven|eight|nine|ten)';
const DOSE_AMOUNT = new RegExp(
  `\\b${QUANTITY}\\s*(?:g|grams?|mg|mcg|milligrams?|micrograms?|ml|milliliters?|units?)\\b`,
  'i',
);
const SCHEDULE =
  /\b(?:daily|nightly|weekly|(?:every|each)\s+(?:(?:other|\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+)?(?:hours?|days?|weeks?|mornings?|evenings?|nights?|meals?)|once|twice|bedtime|(?:before|after|with)\s+(?:meals?|breakfast|lunch|dinner))\b/i;
const DIRECTION =
  /\b(start|use|take|increase|decrease|reduce|change|adjust|calculate|recommend|drink|eat|track)\b\s+(.+)/i;
const SUBSTANCE_DIRECTION = /^(?:start|use|take|increase|decrease|change|adjust|recommend)$/i;
const LEADING_QUANTITY = new RegExp(
  `^${QUANTITY}\\s*(?:(?:kg|kilograms?|g|grams?|mg|mcg|milligrams?|micrograms?|ml|milliliters?|liters?|litres?|units?|minutes?)\\b\\s*)?(?:of\\s+)?`,
  'i',
);
// A bounded set of ordinary instruction subjects, not a general food/medical classifier.
const WELLNESS_SUBJECT =
  /\b(?:water|fluids?|hydration|fruits?|vegetables?|food|meals?|snacks?|breakfast|lunch|dinner|oats|rice|beans|lentils|nuts|apples?|bananas?|avocados?|berries|milk|yogurt|oil|juice|tea|coffee|drinks?|walks?|walking|cycling|biking|running|swimming|yoga|treadmills?|breaks?|breaths?|breathing|steps?|sips?|time|care|rest|sleep|exercise|activity|movement|stretching|weights?|relaxation|meditation|mindfulness|encouragement|support|coaching|tone|feedback|reminders?|journaling)(?:\s+(?:intake|consumption|practices?|routines?|schedules?|bottles?|consistency|goals?|exercises?))?$/i;

function isWellnessSubject(value: string, action?: string): boolean {
  // Only the instruction's subject can disambiguate a quantity. Purpose/adjunct text
  // such as "with water" or "after exercise" cannot exempt an unknown substance.
  const subject = value
    .trim()
    .replace(/^with\s+/i, '')
    .replace(/^(?:a|an|the|my|some)\s+/i, '')
    .replace(LEADING_QUANTITY, '')
    .split(
      /\s+\b(?:to|by|for|after|before|with|at|during|throughout|every|each|daily|nightly|weekly|once|twice)\b/i,
    )[0]!
    .trim();
  // Modifiers need not be enumerated (e.g. "a brisk walk", "warm water").
  if (WELLNESS_SUBJECT.test(subject)) return true;
  // Eating/drinking a named food/beverage is an explicit wellness context. Do not
  // turn this into a food-name dictionary, or treat g/ml as clinical by themselves.
  // Clinical names/terms are still rejected before this contextual check.
  return (
    /^(?:eat|drink)$/i.test(action ?? '') &&
    /[a-z]/i.test(subject) &&
    !/\b(?:mg|mcg|milligrams?|micrograms?|units?)\b/i.test(value)
  );
}

function hasMedicationDirection(content: string): boolean {
  // Separate instructions are checked independently; a food/water clause is not
  // an exemption for a second dosage instruction. Preserve decimal quantities.
  let precedingAction: string | undefined;
  return content.split(/[;,!?]|\.(?!\d)|\b(?:and|but|then)\b/i).some((clause) => {
    const direction = DIRECTION.exec(clause);
    // Coordinated objects inherit the verb: "take water and <substance> daily".
    const action = direction?.[1] ?? precedingAction;
    if (direction) precedingAction = direction[1];
    const scheduled = SCHEDULE.test(clause);
    const amount = DOSE_AMOUNT.test(clause);
    const medicationLike =
      (amount && (Boolean(action) || scheduled)) ||
      (scheduled && action !== undefined && SUBSTANCE_DIRECTION.test(action));
    return medicationLike && !isWellnessSubject(direction?.[2] ?? clause, action);
  });
}

/**
 * Minimal, deterministic storage gate for bounded wellness-profile free text.
 * It is not a diagnosis, triage, or medical-classification system.
 */
export function evaluateWellnessFreeText(content: string): WellnessFreeTextDecision {
  const normalized = content
    .normalize('NFKC')
    .replace(/[\u200B-\u200D\u2060\uFEFF]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  const prohibited =
    PROHIBITED_WELLNESS_INPUT.some((pattern) => pattern.test(normalized)) ||
    hasMedicationDirection(normalized);
  return prohibited
    ? {
        allowed: false,
        policyVersion: 'wellness-input-v1',
        reason: 'prohibited_clinical_content',
      }
    : { allowed: true, policyVersion: 'wellness-input-v1' };
}

export function enforceSafetyDecision(decision: SafetyDecision): void {
  if (decision.mode === 'BLOCKED' || !decision.allowAction) {
    throw new Error('Action blocked by independent safety policy');
  }
}
