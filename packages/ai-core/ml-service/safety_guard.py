"""
NexusAI Safety Guard — heuristic input/output checks for the ML service.

NOT a learned safety model — transparent rule-based screening:
  - Input: prompt-injection / jailbreak / unsafe-request patterns
  - Output: empty, degenerate repetition, corrupted decode detection
  - Fallback: honest Bengali refusal/apology messages (labeled, not neural)

All decisions are logged via the metrics pipeline when available.
"""
import re

# ---------- input patterns (lowercased substring/regex match) ----------
INJECTION_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above) instructions",
    r"disregard (all |any |the )?(previous|prior|above)",
    r"you are now (a |an )?",
    r"act as (a |an |the )?(different|new|unrestricted|DAN)",
    r"jailbreak",
    r"do anything now",
    r"DAN mode",
    r"forget your (instructions|rules|guidelines|training)",
    r"reveal your (system prompt|instructions|prompt)",
    r"print your (system prompt|instructions)",
    r"what are your (system )?instructions",
    r"bypass (your |the )?(safety|filters|restrictions|guidelines)",
    r"pretend you (have no|don't have) (restrictions|rules|limits)",
    r"enable (developer|admin|root|god) mode",
]
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

# harmful-request categories (conservative, obvious-only — not exhaustive)
HARMFUL_PATTERNS = [
    r"how to (make|build|create) (a |an )?(bomb|explosive|weapon|poison)",
    r"how to (hack|break into|crack) (a |an |the )?(account|website|system|password)",
    r"write (a |an )?(malware|virus|ransomware|keylogger)",
    r"make (a |an )?(fake|forged) (id|document|certificate|money)",
    r"suicide method|how to kill myself|self.?harm method",
]
_HARMFUL_RE = [re.compile(p, re.IGNORECASE) for p in HARMFUL_PATTERNS]

# ---------- output degenerate detection ----------
_BN_RE = re.compile(r"[ঀ-৿]")
_LATIN_RE = re.compile(r"[A-Za-z]")

def _ngram_repeat_ratio(text: str, n: int = 4) -> float:
    """Fraction of duplicated n-grams — high = degenerate loop."""
    words = text.lower().split()
    if len(words) < n * 2:
        return 0.0
    grams = [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]
    return 1.0 - len(set(grams)) / max(len(grams), 1)

def check_input(text: str) -> dict:
    """
    Returns {"safe": bool, "reason": str|None, "category": str|None}.
    Conservative: only flags clear injection/harm patterns.
    """
    if not text or not text.strip():
        return {"safe": False, "reason": "empty_input", "category": "input"}
    if len(text) > 8000:
        return {"safe": False, "reason": "input_too_long", "category": "input"}
    for rx in _INJECTION_RE:
        if rx.search(text):
            return {"safe": False, "reason": "prompt_injection",
                    "category": "injection", "matched": rx.pattern}
    for rx in _HARMFUL_RE:
        if rx.search(text):
            return {"safe": False, "reason": "harmful_request",
                    "category": "harmful", "matched": rx.pattern}
    return {"safe": True, "reason": None, "category": None}


def check_output(text: str, source: str = "neural") -> dict:
    """
    Output sanity: empty, degenerate repetition, no-linguistic-content.
    source: 'neural' | 'deterministic' | 'fallback' — only neural outputs
    get strict degenerate checks (handlers are trusted templates).
    """
    t = (text or "").strip()
    if not t:
        return {"ok": False, "reason": "empty", "action": "fallback"}
    if source == "neural":
        if len(t) < 2:
            return {"ok": False, "reason": "too_short", "action": "fallback"}
        if _ngram_repeat_ratio(t) > 0.6:
            return {"ok": False, "reason": "degenerate_repetition",
                    "action": "fallback"}
        # corrupted decode: mostly symbols/rare unicode, no letters at all
        if not (_LATIN_RE.search(t) or _BN_RE.search(t)):
            return {"ok": False, "reason": "no_linguistic_content",
                    "action": "fallback"}
    return {"ok": True, "reason": None, "action": None}


# ---------- honest fallback messages (deterministic, labeled) ----------
FALLBACKS = {
    "injection": "আমি এই ধরনের অনুরোধে সহায়তা করতে পারি না। একটি সুরক্ষিত, স্বাভাবিক প্রশ্ন করুন।",
    "prompt_injection": "আমি এই ধরনের অনুরোধে সহায়তা করতে পারি না। একটি সুরক্ষিত, স্বাভাবিক প্রশ্ন করুন।",
    "harmful": "দুঃখিত, এই অনুরোধটি আমি সাহায্য করতে পারি না।",
    "harmful_request": "দুঃখিত, এই অনুরোধটি আমি সাহায্য করতে পারি না।",
    "empty_input": "একটি প্রশ্ন লিখুন, আমি সাহায্য করার চেষ্টা করব।",
    "input": "একটি প্রশ্ন লিখুন, আমি সাহায্য করার চেষ্টা করব।",
    "input_too_long": "বার্তা অনেক বড়। অনুগ্রহ করে ছোট করে লিখুন।",
    "neural_empty": "দুঃখিত, এই বিষয়ে আমার যথেষ্ট জ্ঞান নেই। অন্যভাবে প্রশ্ন করুন।",
    "degenerate": "দুঃখিত, এই প্রশ্নের জন্য আমি এখন সঠিক উত্তর দিতে পারছি না। অন্যভাবে চেষ্টা করুন।",
    "generic": "দুঃখিত, এই বিষয়টি এখন সঠিকভাবে উত্তর দিতে পারছি না।",
}

def fallback_message(reason: str) -> str:
    return FALLBACKS.get(reason, FALLBACKS["generic"])
