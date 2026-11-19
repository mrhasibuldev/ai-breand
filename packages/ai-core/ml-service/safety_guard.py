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
# Calculator-style markup leaked from Core-01's pretraining format —
# never valid conversational output.
_MARKUP_RE = re.compile(r"<<|>>|####")
# Exemptions for the conservative language-mismatch check: legitimate
# Banglish, code, digits/math, and short technical answers must pass.
# Only unambiguous Banglish tokens — English collisions (to/ki/ke/na/age/
# problem/solution) are deliberately excluded or valid English would pass.
_BANGLISH_MARKERS_RE = re.compile(
    r'\b(tumi|tomar|apni|ami|kemon|kivabe|koto|hocche|hobe|bolo|bolun|'
    r'achhi|achho|kore|korbo|lagbe|chaio|chai|mone|bhalo|valob|dhonnobad|'
    r'shukria|kaaj|kotha|bujhlam|bujho|dao|ekhon|pore|sathe|jonno|vai|'
    r'bhai|dada|apa|khub|toh|keno)\b', re.I)
_CODEISH_RE = re.compile(r'(def |class |import |return |function |=>|\{|\}|==|!=|//|#\s|```|\bvar |\blet |\bconst )')

# English-side output validation: high-precision, low-recall heuristics.
# Only applied to substantive neural outputs (>40 chars) for English input.
_EN_STOP = frozenset(
    "the a an and or but if then else for to of in on at is are was were be been "
    "it its this that with as by from what when where which who whom whose why how "
    "can could should would do does did have has had you your i we they he she me "
    "him her us them my our their not no yes so such than too very just about into "
    "over after before between each other some any all both few more most".split())
_WORD_RE = re.compile(r"[A-Za-z]{3,}")

def _content_words(text: str) -> set:
    return {w.lower() for w in _WORD_RE.findall(text or "")} - _EN_STOP

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


def check_output(text: str, source: str = "neural",
                 expected_lang: str | None = None,
                 input_text: str | None = None) -> dict:
    """
    Output sanity: empty, degenerate repetition, no-linguistic-content,
    calculator-markup leak, and (conservatively) language mismatch.
    source: 'neural' | 'deterministic' | 'fallback' — only neural outputs
    get strict degenerate checks (handlers are trusted templates).
    expected_lang: detected input language; 'bengali' inputs should not
    receive all-Latin neural output (current models only produce English
    fragments for Bengali prompts — honest fallback is better).
    """
    t = (text or "").strip()
    if not t:
        return {"ok": False, "reason": "empty", "action": "fallback"}
    if source == "neural":
        if len(t) < 2:
            return {"ok": False, "reason": "too_short", "action": "fallback"}
        if _MARKUP_RE.search(t):
            return {"ok": False, "reason": "calc_markup_leak",
                    "action": "fallback"}
        if _ngram_repeat_ratio(t) > 0.6:
            return {"ok": False, "reason": "degenerate_repetition",
                    "action": "fallback"}
        # corrupted decode: mostly symbols/rare unicode, no letters at all
        if not (_LATIN_RE.search(t) or _BN_RE.search(t)):
            return {"ok": False, "reason": "no_linguistic_content",
                    "action": "fallback"}
        # Non-English inputs (bengali/banglish/mixed) should not receive
        # Latin-script prose output unless it carries Bengali script,
        # unambiguous Banglish markers, code, or is mostly non-linguistic
        # (pure math/numeric expressions). A bare digit no longer exempts
        # prose — "...210 miles per hour..." gibberish must not pass.
        # English input is exempt.
        if expected_lang in ("bengali", "banglish", "mixed") \
                and len(t) > 40 \
                and not _BN_RE.search(t) \
                and not _BANGLISH_MARKERS_RE.search(t) \
                and not _CODEISH_RE.search(t):
            letter_ratio = len(re.findall(r'[A-Za-z]', t)) / max(len(t), 1)
            if letter_ratio > 0.5:
                return {"ok": False, "reason": "language_mismatch",
                        "action": "fallback"}
        # English input: catch wrong-language and unrelated neural output.
        # (1) Bengali-dominant output for an English question is always wrong.
        # (2) Substantive answers sharing zero content words with the question
        #     are almost certainly unrelated — honest fallback beats gibberish.
        # Semantic correctness is NOT proven by this; it only filters obvious
        # mismatches. Remaining limitation documented in audit reports.
        if expected_lang == "english" and source == "neural":
            bn = len(_BN_RE.findall(t))
            lat = len(_LATIN_RE.findall(t))
            if bn > 5 and bn >= lat:
                return {"ok": False, "reason": "language_mismatch",
                        "action": "fallback"}
            if len(t) > 40 and input_text:
                shared = _content_words(input_text) & _content_words(t)
                if not shared:
                    return {"ok": False, "reason": "low_relevance",
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
    "calc_markup_leak": "দুঃখিত, এই প্রশ্নের জন্য আমি এখন সঠিক উত্তর দিতে পারছি না। অন্যভাবে চেষ্টা করুন।",
    "language_mismatch": "দুঃখিত, এই প্রশ্নের সঠিক উত্তর দিতে আমার এখন পর্যাপ্ত সক্ষমতা নেই।",
    "low_relevance": "দুঃখিত, এই প্রশ্নের সঠিক উত্তর দিতে আমার এখন পর্যাপ্ত সক্ষমতা নেই।",
    "generic": "দুঃখিত, এই বিষয়টি এখন সঠিকভাবে উত্তর দিতে পারছি না।",
}

def fallback_message(reason: str) -> str:
    return FALLBACKS.get(reason, FALLBACKS["generic"])
