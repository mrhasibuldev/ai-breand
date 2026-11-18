# =============================================================================
# NEXUSAI MULTI-MODEL — CENTRAL BRAIN / ROUTER
# Language-aware, registry-driven model selection. Lazy loading, provenance.
# =============================================================================
import re, time, os
from model_registry import registry

# ------------------------- language detection -------------------------
BENGALI_SCRIPT = re.compile(r'[ঀ-৿]')
# Banglish markers: romanized Bengali function words common in BD chat
BANGLISH_MARKERS = re.compile(
    r'\b(tumi|tomar|apni|ami|kemon|kivabe|kivabe|koto|kotok|khub|hocche|hobe|'
    r'ki |na\b|bolun|bolo|achhi|achho|kore|korbo|lagbe|chaio|chai|mone|'
    r'bhalo|valob|dhonnobad|shukria|kaaj|kotha|kotha|problem|solution|'
    r'bujhlam|bujho|dao|dao\b|ekhon|age|pore|sathe|char|jonno)\b', re.I)
EN_ONLY = re.compile(r'^[a-zA-Z0-9\s\.,!?;:\'"()\-]+$')

def detect_language_v2(text: str) -> dict:
    """Returns {lang, confidence, reason}. lang in bengali|english|banglish|mixed|unknown."""
    if not text or not text.strip():
        return {"lang":"unknown","confidence":0.0,"reason":"empty"}
    t=text.strip()
    bn=len(BENGALI_SCRIPT.findall(t))
    lat=len(re.findall(r'[A-Za-z]',t))
    if bn>0 and lat>0:
        return {"lang":"mixed","confidence":0.9,"reason":"bengali+latin script"}
    if bn>0:
        return {"lang":"bengali","confidence":0.95,"reason":"bengali script"}
    if lat>0:
        if BANGLISH_MARKERS.search(t) and len(t.split())>=2:
            hits=len(BANGLISH_MARKERS.findall(t))
            conf=min(0.5+0.1*hits,0.9)
            return {"lang":"banglish","confidence":conf,"reason":f"{hits} banglish markers"}
        return {"lang":"english","confidence":0.8,"reason":"latin script"}
    return {"lang":"unknown","confidence":0.3,"reason":"no letters"}

# ------------------------- intent (lightweight) -------------------------
MATH_PATTERNS = [
    re.compile(r'(\d+)\s*(plus|minus|times|multiplied by|divided by|% of|percent of)\s*(\d+)',re.I),
    re.compile(r'what is\s+(\d+)\s*(\+|\-|x|×|\*)\s*(\d+)',re.I),
]
GREETING = re.compile(r'^(hi+|hello+|hey+|good (morning|afternoon|evening)|সুপ্রভাত|শুভ|হ্যালো|হাই|নমস্কার|আসসালামু|kemon acho|tumi kemon)',re.I)
THANKS  = re.compile(r'(thank|thanks|ধন্যবাদ|shukria)',re.I)
BYE     = re.compile(r'(bye|goodbye|farewell|viday|biday)',re.I)
IDENTITY= re.compile(r'(your name|who are you|who created|তোমার নাম|তোমাকে কে|ke create|ke banay|ke toiri)',re.I)
CAPABILITY=re.compile(r'(what can you do|your (capabilities|features)|capability|kemon help|sahaajjo)',re.I)
KNOWLEDGE = re.compile(r'(what is|what are|define|explain|describe|summarize|summary|classify|category|meaning of|বুঝাও|ব্যাখ্যা|বর্ণনা|সারাংশ)',re.I)
REASONING = re.compile(r'(if .+ then|suppose|assume|order|arrange|sequence|logic|logical|constraint|plan|steps to|which is (better|best|more|less)|compare|comparison|because|therefore|conclusion)',re.I)

def classify_intent_v2(text: str, lang: str) -> str:
    t=text.strip()
    if GREETING.match(t): return "GREETING"
    if BYE.search(t): return "FAREWELL"
    if THANKS.search(t): return "THANKS"
    if IDENTITY.search(t): return "IDENTITY"
    if CAPABILITY.search(t): return "CAPABILITY"
    if any(p.search(t) for p in MATH_PATTERNS): return "MATH"
    if REASONING.search(t): return "REASONING"
    if KNOWLEDGE.search(t): return "KNOWLEDGE"
    if re.match(r'^(what|how|why|when|where|who|which|is|are|can|does|do)\b',t,re.I): return "GENERAL_QUESTION"
    if re.match(r'^(কী|কি|কেন|কিভাবে|কীভাবে|কত|কোথায়|কে|কখন)\b',t): return "GENERAL_QUESTION"
    if lang in ("banglish","mixed") and re.search(r'\?',t): return "GENERAL_QUESTION"
    return "CHAT"

# ------------------------- math tool (labeled, deterministic) -----------
def try_math_tool(text: str):
    """Deterministic arithmetic ONLY. Returns (answer,used) — never neural."""
    m=re.search(r'(\d+)\s*(?:\+|plus)\s*(\d+)',text,re.I)
    if m: return str(int(m.group(1))+int(m.group(2))),True
    m=re.search(r'(\d+)\s*(?:\-|minus)\s*(\d+)',text,re.I)
    if m: return str(int(m.group(1))-int(m.group(2))),True
    m=re.search(r'(\d+)\s*(?:x|×|\*|times|multiplied by)\s*(\d+)',text,re.I)
    if m: return str(int(m.group(1))*int(m.group(2))),True
    m=re.search(r'(\d+)\s*(?:÷|/|divided by)\s*(\d+)',text,re.I)
    if m:
        d=int(m.group(2))
        if d: return str(int(m.group(1))//d),True
    m=re.search(r'(\d+)%\s*(?:off\s*)?(?:of\s*)?(\d+)',text,re.I) or re.search(r'(\d+)\s*টাকার\s*(\d+)%\s*ছাড়',text)
    if m:
        pct,base=int(m.group(1)),int(m.group(2))
        return f"{base} - {pct}% = {base - base*pct//100} (মোট {base*pct//100} ছাড়)",True
    return None,False

# ------------------------- fallback (language-aware) ---------------------
FALLBACKS = {
    "bengali": "দুঃখিত, এই প্রশ্নের সঠিক উত্তর দিতে আমার presently পর্যাপ্ত সক্ষমতা নেই। আমি শিখছি — অনুগ্রহ করে অন্যভাবে জিজ্ঞাসা করুন।",
    "english": "Sorry, I don't have enough reliable capability to answer that correctly yet. I'm still learning — please try rephrasing.",
    "banglish": "Sorry vai, ei proshner thik uttor dite ami ekhon paryapto noy — ami ekhono shikhchi. Onno bhabe jiggesh koro.",
    "mixed":  "দুঃখিত, এই প্রশ্নের সঠিক উত্তর দিতে আমি এখনো সক্ষম নই — I'm still learning.",
    "unknown":"দুঃখিত, আমি এই প্রশ্নের সঠিক উত্তর দিতে পারছি না।",
}
IDENTITY_ANSWER = {
    "en": "I'm NexusAI — an independent AI assistant built by Hasibul. I run my own Transformer model locally; I don't call external AI services.",
    "bn": "আমি NexusAI — Hasibul তৈরি করা একটি স্বাধীন AI সহকারী। আমি নিজের Transformer মডেল ব্যবহার করি; কোনো বাইরের AI সার্ভিসে নির্ভর করি না।",
    "banglish": "Ami NexusAI — Hasibul er banano independent AI assistant. Ami nijer Transformer model use kori; kono baire AI service e depend kori na.",
    "mixed": "আমি NexusAI — Hasibul-এর তৈরি independent AI assistant; আমি নিজের model ব্যবহার করি।",
}
CAPABILITY_ANSWER = {
    "en": "I can chat, answer questions, and help with tasks — but I'm still early in training, so some answers may be limited or imperfect.",
    "bn": "আমি কথোপকথন, প্রশ্নের উত্তর ও কাজের সাহায্য করতে পারি — তবে আমি এখনো শেখার পর্যায়ে, তাই কিছু উত্তর সীমিত হতে পারে।",
    "banglish": "Ami kotha-bola, proshner uttor ar kaaj-e sahayota korte pari — kintu ami ekhono shikhechi, tai kichu uttor limited hote pare.",
    "mixed": "আমি কথা বলতে, প্রশ্নের উত্তর দিতে ও সাহায্য করতে পারি — তবে এখনো শেখার পর্যায়ে আছি।",
}
GREETING_ANSWER = {
    "bengali": "হ্যালো! আমি NexusAI। কীভাবে সাহায্য করতে পারি?",
    "english": "Hello! I'm NexusAI. How can I help you today?",
    "banglish": "Hey! Ami NexusAI. Ki bhabe help korte pari?",
    "mixed": "হ্যালো! I'm NexusAI — how can I help?",
}

_LANG_NORM={"english":"en","bengali":"bn","banglish":"banglish","mixed":"mixed","unknown":"en"}
def pick(d, lang):
    lang=_LANG_NORM.get(lang,"en")
    # try normalized key, then raw alternatives
    for k in (lang, {"en":"english","bn":"bengali"}.get(lang,lang)):
        if k in d: return d[k]
    return d.get("mixed") or d.get("english") or d.get("en") or next(iter(d.values()))

# ------------------------- central brain -------------------------------
class NexusBrain:
    """Central router: language → intent → model/tool → validated response."""
    PRIMARY = "nexus-core-01"
    FALLBACK_MODEL = "nexus-medium"
    # intent -> specialist model (only used when registry validates+loads it)
    SPECIALISTS = {"MATH":"nexus-core-03","REASONING":"nexus-core-02","KNOWLEDGE":"nexus-core-04"}

    def __init__(self, registry=registry):
        self.reg=registry
        self._provenance=None

    def _generate_neural(self, prompt, lang):
        """Try primary, then fallback model. Returns (text, prov, used_model)."""
        for mid in (self.PRIMARY, self.FALLBACK_MODEL):
            try:
                txt,prov=self.reg.generate(mid,prompt,max_new_tokens=64,
                                           temperature=0.8,do_sample=True)
                if txt and len(txt.strip())>=3 and not self._is_degenerate(txt):
                    return txt,prov,mid
            except Exception as e:
                print(f"[Brain] model {mid} failed: {e}")
                continue
        return None,None,None

    def _try_specialist(self, intent, message):
        """Route to task specialist if registered+loadable. Returns
        (text,prov,mid) or (None,None,None). Never substitutes silently."""
        mid=self.SPECIALISTS.get(intent)
        if not mid: return None,None,None
        if not self.reg.get(mid): return None,None,None
        try:
            ok,_=self.reg.validate(mid)
        except Exception:
            return None,None,None
        if not ok: return None,None,None
        try:
            txt,prov=self.reg.generate(mid,message,max_new_tokens=64,
                                       temperature=0.3,do_sample=False)
            if txt and len(txt.strip())>=3 and not self._is_degenerate(txt):
                return txt,prov,mid
        except Exception as e:
            print(f"[Brain] specialist {mid} failed: {e}")
        return None,None,None

    @staticmethod
    def _is_degenerate(txt):
        """Reject empty/repetitive/special-token garbage."""
        t=txt.strip()
        if not t or len(t)<3: return True
        if set(t)<=set(" \n<|>"): return True
        words=t.split()
        if len(words)>=8 and len(set(words))/len(words)<0.3: return True  # heavy repetition
        if "<unk>" in t or "<0x" in t: return True
        return False

    def respond(self, message: str, conversation_history=None, neural_only=False):
        """Full pipeline. Returns dict with response + full provenance.
        neural_only=True bypasses ALL deterministic handlers (test mode only)."""
        t0=time.time()
        dl=detect_language_v2(message); lang=dl["lang"]
        intent=classify_intent_v2(message, lang)
        trace={"language":lang,"lang_conf":dl["confidence"],"lang_reason":dl["reason"],
               "intent":intent,"model_used":None,"route":None,"tool":None,
               "neural_ran":False,"fallback":False,"neural_only":bool(neural_only)}

        if neural_only:
            # Isolated test mode: straight to neural, no canned/tool/fallback substitution.
            prompt=message
            if conversation_history:
                ctx=" ".join(h.get("content","") for h in conversation_history[-3:] if isinstance(h,dict))
                if ctx: prompt=ctx+" "+message
            txt,prov,mid=self._generate_neural(prompt,lang)
            trace["neural_ran"]=True
            if txt:
                trace["model_used"]=mid; trace["route"]=f"neural:{mid}"
                trace["provenance"]=prov
                return {"response":txt,"trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}
            trace["route"]="neural_failed"
            return {"response":"","trace":trace,"latency_ms":round((time.time()-t0)*1000,1),
                    "error":"neural generation failed"}

        # --- deterministic, honest handlers (labeled, not neural) ---
        if intent=="GREETING":
            trace["route"]="deterministic:greeting"
            return {"response":pick(GREETING_ANSWER,lang if lang!='unknown' else 'english'),
                    "trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}
        if intent=="THANKS":
            trace["route"]="deterministic:thanks"
            resp={"bengali":"আপনাকে ধন্যবাদ! আরও সাহায্য দরকার হলে বলুন।",
                  "english":"You're welcome! Anything else I can help with?",
                  "banglish":"Dhonnobad! Ar kichu lagle bolo.","mixed":"আপনাকে ধন্যবাদ!"}
            return {"response":pick(resp,lang),"trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}
        if intent=="FAREWELL":
            trace["route"]="deterministic:farewell"
            resp={"bengali":"বিদায়! আবার আসুন।","english":"Goodbye! Come back anytime.",
                  "banglish":"Biday! abar asho.","mixed":"Goodbye! আবার আসুন।"}
            return {"response":pick(resp,lang),"trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}
        if intent=="IDENTITY":
            trace["route"]="registry:identity_metadata"
            return {"response":pick(IDENTITY_ANSWER,lang if lang!='unknown' else 'english'),
                    "trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}
        if intent=="CAPABILITY":
            trace["route"]="registry:capability_metadata"
            return {"response":pick(CAPABILITY_ANSWER,lang if lang!='unknown' else 'english'),
                    "trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}
        if intent=="MATH":
            stxt,sprov,smid=self._try_specialist("MATH",message)
            if stxt:
                trace["neural_ran"]=True; trace["model_used"]=smid
                trace["route"]=f"neural:{smid}"; trace["provenance"]=sprov
                return {"response":stxt,"trace":trace,
                        "latency_ms":round((time.time()-t0)*1000,1)}
            ans,used=try_math_tool(message)
            if used:
                trace["route"]="tool:deterministic_math"
                trace["tool"]="math"
                trace["model_used"]="none(tool)"
                suffix={"bengali":" (নির্ণায়ক ক্যালকুলেটর)","english":" (deterministic calculator)",
                        "banglish":" (deterministic calculator)","mixed":" (calculator)"}
                return {"response":f"{ans}{pick(suffix,lang)}","trace":trace,
                        "latency_ms":round((time.time()-t0)*1000,1)}

        # --- specialist neural path (reasoning/knowledge) ---
        stxt,sprov,smid=self._try_specialist(intent,message)
        if stxt:
            trace["neural_ran"]=True; trace["model_used"]=smid
            trace["route"]=f"neural:{smid}"; trace["provenance"]=sprov
            return {"response":stxt,"trace":trace,
                    "latency_ms":round((time.time()-t0)*1000,1)}

        # --- neural path ---
        prompt=message
        if conversation_history:
            ctx=" ".join(h.get("content","") for h in conversation_history[-3:] if isinstance(h,dict))
            if ctx: prompt=ctx+" "+message
        txt,prov,mid=self._generate_neural(prompt,lang)
        trace["neural_ran"]=True
        if txt:
            trace["model_used"]=mid; trace["route"]=f"neural:{mid}"
            trace["provenance"]=prov
            return {"response":txt,"trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}
        # neural failed/degenerate → honest language-aware fallback
        trace["fallback"]=True; trace["route"]="fallback"
        return {"response":pick(FALLBACKS,lang if lang!='unknown' else 'english'),
                "trace":trace,"latency_ms":round((time.time()-t0)*1000,1)}

brain = NexusBrain()
