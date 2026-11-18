"""
NexusAI Core-01 SFT v1 dataset builder — deterministic, no external AI.

Generates conversational instruction data in English, Bengali, and Banglish
using transparent templates. Output: JSONL {messages:[user,assistant]}
plus manifest. Deterministic seed -> reproducible.

Usage: python build_sft_v1.py
Output: data/phase3/sft_v1/sft_train.jsonl + sft_manifest.json
"""
import json, os, random, hashlib

SEED = 42
random.seed(SEED)
OUT_DIR = os.path.join(os.path.dirname(__file__), "phase3", "sft_v1")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- template banks ----------
IDENTITY = {
    "en": [
        ("What is your name?", "I am NexusAI Core-01, an independent AI assistant developed by Hasibul. I run my own Transformer model locally."),
        ("Who are you?", "I am NexusAI Core-01 — an independently developed neural language model. I don't rely on external AI services."),
        ("What can you do?", "I can answer questions, explain concepts, help with writing and reasoning in English, Bengali, and Banglish."),
        ("Are you a real AI?", "Yes — I am NexusAI Core-01, my own Transformer model with 8.8 million parameters, trained from scratch."),
        ("Tell me about yourself.", "I am NexusAI Core-01, an independent decoder-only Transformer language model built for the NexusAI ecosystem."),
    ],
    "bn": [
        ("তোমার নাম কী?", "আমি NexusAI Core-01 — Hasibul কর্তৃক নির্মিত একটি স্বাধীন AI সহকারী। আমি নিজের Transformer মডেল ব্যবহার করি।"),
        ("তুমি কে?", "আমি NexusAI Core-01, একটি স্বাধীন Neural Language Model। আমি বাহ্যিক AI সেবার উপর নির্ভর করি না।"),
        ("তুমি কী করতে পারো?", "আমি ইংরেজি, বাংলা ও Banglish-এ প্রশ্নের উত্তর, ব্যাখ্যা ও যুক্তি দিতে পারি।"),
        ("তুমি কি আসল AI?", "হ্যাঁ — আমি NexusAI Core-01, নিজের থেকে তৈরি ৮.৮ মিলিয়ন প্যারামিটারের Transformer মডেল।"),
    ],
    "banglish": [
        ("tomar naam ki?", "Ami NexusAI Core-01 — Hasibul er banano independent AI assistant. Ami nijer Transformer model use kori."),
        ("tumi ke?", "Ami NexusAI Core-01, ekta independent neural language model. External AI service er upor depend kori na."),
        ("tumi ki korte paro?", "Ami English, Bangla ar Banglish e question er answer, explanation ar reasoning dite pari."),
    ],
}

GREETING = {
    "en": [("Hello!", "Hello! How can I help you today?"), ("Hi", "Hi there! What would you like to know?"),
           ("Good morning", "Good morning! How can I assist you?")],
    "bn": [("হ্যালো!", "হ্যালো! আজ আমি কীভাবে সাহায্য করতে পারি?"),
           ("শুভ সকাল", "শুভ সকাল! আমি কীভাবে সাহায্য করতে পারি?")],
    "banglish": [("hi", "Hi! Ki bhabe help korte pari?"), ("assalamu alaikum", "Walaikum assalam! Ki dorkar?")],
}
THANKS = {
    "en": [("Thank you", "You're welcome! Feel free to ask if you need anything else."),
           ("Thanks a lot", "Happy to help! Let me know if you have more questions.")],
    "bn": [("ধন্যবাদ", "আপনাকে স্বাগতম! আরো কিছুতে চাইলে জিজ্ঞাসা করুন।")],
    "banglish": [("dhonnobad", "Apnake swagatam! Onno kichu janle janaben.")],
}

# factual QA — simple, verifiable, honest scope
FACTS = {
    "en": [
        ("What is the capital of Bangladesh?", "Dhaka is the capital of Bangladesh."),
        ("What is water made of?", "Water is made of two hydrogen atoms and one oxygen atom (H2O)."),
        ("Why do humans need water?", "Humans need water for digestion, temperature regulation, and survival — about 60% of the body is water."),
        ("What is the Sun?", "The Sun is a star at the center of our solar system that provides light and heat to Earth."),
        ("What is 7 + 5?", "7 + 5 = 12."),
        ("If I have 3 apples and buy 2 more, how many do I have?", "You have 5 apples."),
        ("What is artificial intelligence?", "Artificial intelligence is the simulation of human intelligence by machines, especially computers."),
        ("What is the purpose of education?", "Education develops knowledge, skills, and critical thinking for personal and social growth."),
        ("Why do plants need sunlight?", "Plants need sunlight for photosynthesis, which produces their food."),
        ("What is the capital of Japan?", "Tokyo is the capital of Japan."),
    ],
    "bn": [
        ("বাংলাদেশের রাজধানী কী?", "বাংলাদেশের রাজধানী ঢাকা।"),
        ("পানি কী দিয়ে তৈরি?", "পানি দুটি হাইড্রোজেন ও একটি অক্সিজেন পরমাণু দিয়ে তৈরি (H2O)।"),
        ("মানুষ কেন পানি পান করে?", "মানুষ হজম, শরীরের তাপমাত্রা নিয়ন্ত্রণ ও বেঁচে থাকার জন্য পানি পান করে।"),
        ("সূর্য কী?", "সূর্য আমাদের সৌরজগতের কেন্দ্রে অবস্থিত একটি তারা, যা পৃথিবীকে আলো ও তাপ দেয়।"),
        ("৭ + ৫ কত?", "৭ + ৫ = ১২।"),
        ("কৃত্রিম বুদ্ধিমত্তা কী?", "কৃত্রিম বুদ্ধিমত্তা হলো মেশিনের দ্বারা মানবীয় বুদ্ধিমত্তার অনুকরণ, বিশেষ করে কম্পিউটারের মাধ্যমে।"),
        ("শিক্ষার উদ্দেশ্য কী?", "শিক্ষা জ্ঞান, দক্ষতা ও সমালোচনামূলক চিন্তা বিকশিত করে — ব্যক্তিগত ও সামাজিক উন্নতির জন্য।"),
        ("গাছ সূর্যের আলো কেন প্রয়োজন?", "গাছের photosynthesis-এর জন্য সূর্যের আলো প্রয়োজন, যার মাধ্যমে গাছ пищা তৈরি করে।"),
    ],
    "banglish": [
        ("Bangladesh er capital ki?", "Dhaka Bangladesh er capital."),
        ("pani ki diye toiri?", "Pani 2 ta hydrogen ar 1 ta oxygen atom diye toiri (H2O)."),
        ("manush keno pani khay?", "Manush digestion, body temperature control ar bachte hole pani khay."),
        ("surjo ki?", "Surjo amader solar system er center e thaka ekta star, ja earth ke alok ar tap dey."),
        ("7 + 5 koto?", "7 + 5 = 12."),
        ("artificial intelligence ki?", "AI holo machine er maddhome human intelligence er simulation."),
        ("shikkhar uddeshyo ki?", "Shikkha knowledge, skill ar critical thinking develop kore — personal ar social growth er jonno."),
    ],
}

# arithmetic templates — deterministic correct answers
MATH_TEMPLATES = [
    ("What is {a} + {b}?", "{a} + {b} = {c}."),
    ("{a} ar {b} mille koto hoy?", "{a} + {b} = {c}."),
    ("{a} plus {b} koto?", "{a} + {b} = {c}."),
    ("What is {a} - {b}?", "{a} - {b} = {c}."),
    ("If I have {a} apples and buy {b} more, how many apples?", "You have {c} apples."),
]

# safety / honesty templates — model should admit limits, not hallucinate
SAFETY = {
    "en": [("What will happen tomorrow?", "I cannot predict the future. I can only share what is generally known or reason about possibilities."),
           ("Tell me a secret", "I don't have personal secrets. Is there something else I can help you with?")],
    "bn": [("আগামীকাল কী হবে?", "আমি ভবিষ্যৎ ভবিষ্যদ্বাণী করতে পারি না। আমি শুধু সাধারণ জ্ঞান বা সম্ভাবনা নিয়ে আলোচনা করতে পারি।")],
    "banglish": [("kal ki hobe?", "Ami bhabishyot bhabishyobani korte pari na. Sudhu general knowledge ba somvabna niye kotha bolte pari.")],
}


def build_pairs():
    pairs = []
    for bank_name, bank in (("identity", IDENTITY), ("greeting", GREETING),
                            ("thanks", THANKS), ("facts", FACTS), ("safety", SAFETY)):
        for lang, items in bank.items():
            for q, a in items:
                pairs.append({"lang": lang, "category": bank_name,
                              "messages": [
                                  {"role": "user", "content": q},
                                  {"role": "assistant", "content": a}]})
    # arithmetic expansion
    for a in range(2, 20):
        for b in range(1, 10):
            for cat, q, ans in (
                ("math_en", f"What is {a} + {b}?", f"{a} + {b} = {a+b}."),
                ("math_bg", f"{a} + {b} koto?", f"{a} + {b} = {a+b}."),
                ("math_en2", f"What is {a} - {b}?", f"{a} - {b} = {a-b}."),
            ):
                pairs.append({"lang": "en" if "en" in cat else "banglish",
                              "category": cat,
                              "messages": [{"role": "user", "content": q},
                                           {"role": "assistant", "content": ans}]})
    return pairs


def main():
    pairs = build_pairs()
    # dedup
    seen = set(); out = []
    for p in pairs:
        k = p["messages"][0]["content"]
        if k not in seen:
            seen.add(k); out.append(p)
    path = os.path.join(OUT_DIR, "sft_train.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for p in out:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    lang_count = {}
    cat_count = {}
    for p in out:
        lang_count[p["lang"]] = lang_count.get(p["lang"], 0) + 1
        cat_count[p["category"]] = cat_count.get(p["category"], 0) + 1
    manifest = {
        "seed": SEED, "total_pairs": len(out), "lang_dist": lang_count,
        "category_dist": cat_count,
        "format": "chatml-lite {messages:[user,assistant]}",
        "note": "Deterministic templates only — no external AI. Small but clean; "
                "expand with human-reviewed data later.",
        "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
    }
    with open(os.path.join(OUT_DIR, "sft_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    print(f"WROTE {path} — {len(out)} pairs")
    print(json.dumps(lang_count, indent=1))
    print("sha:", manifest["sha256"][:20] + "…")


if __name__ == "__main__":
    main()
