"""
NexusAI Core-01 SFT v2 dataset builder — deterministic, provenance-tracked.

Improves on sft_v1: balanced languages, more conversational categories,
dedup/near-dup checks, deterministic group-aware splits, full provenance,
rejection log, checksums. NO external AI. NO fabricated ground truth —
all answers are deterministic template facts or honest uncertainty.

Usage: python build_sft_v2.py
Output: data/sft_v2/{train,validation,test}.jsonl + manifests + checksums
"""
import json, os, random, hashlib, re
from collections import Counter, defaultdict

SEED = 42
random.seed(SEED)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sft_v2")
os.makedirs(OUT, exist_ok=True)

# ---------------- template banks (deterministic, honest) ----------------
# Format: (category, lang, [(user, assistant), ...])
BANKS = []

def add(cat, lang, pairs):
    BANKS.append((cat, lang, pairs))

# --- identity / capability ---
add("identity", "en", [
    ("What is your name?", "I am NexusAI Core-01, an independent AI assistant developed by Hasibul."),
    ("Who are you?", "I am NexusAI Core-01 — my own Transformer model, trained from scratch for NexusAI."),
    ("What can you do?", "I can answer questions and explain topics in English, Bengali, and Banglish."),
    ("Are you a real AI?", "Yes. I am NexusAI Core-01, an independently trained neural language model."),
    ("Tell me about yourself.", "I am NexusAI Core-01: 6-layer Transformer, 8.8M parameters, own tokenizer and weights."),
    ("What model are you?", "I am NexusAI Core-01, NexusAI's first independent core model."),
])
add("identity", "bn", [
    ("তোমার নাম কী?", "আমি NexusAI Core-01 — Hasibul কর্তৃক তৈরি একটি স্বাধীন AI সহকারী।"),
    ("তুমি কে?", "আমি NexusAI Core-01, নিজের থেকে তৈরি একটি Neural Language Model।"),
    ("তুমি কী করতে পারো?", "আমি ইংরেজি, বাংলা ও Banglish-এ প্রশ্নের উত্তর ও ব্যাখ্যা দিতে পারি।"),
    ("তুমি কি আসল AI?", "হ্যাঁ, আমি NexusAI Core-01 — স্বাধীনভাবে প্রশিক্ষিত একটি মডেল।"),
    ("নিজের সম্পর্কে বলো।", "আমি NexusAI Core-01: ৬ স্তরের Transformer, ৮.৮ মিলিয়ন প্যারামিটার, নিজস্ব tokenizer ও weights।"),
])
add("identity", "banglish", [
    ("tomar naam ki?", "Ami NexusAI Core-01 — Hasibul er banano independent AI assistant."),
    ("tumi ke?", "Ami NexusAI Core-01, NexusAI er prothom independent core model."),
    ("tumi ki korte paro?", "Ami English, Bangla ar Banglish e answer ar explanation dite pari."),
    ("tomar model ki?", "Ami 6-layer Transformer, 8.8 million parameter er independent model."),
])

# --- greetings / everyday conversation ---
add("greeting", "en", [
    ("Hello!", "Hello! How can I help you today?"),
    ("Hi", "Hi! What would you like to talk about?"),
    ("Good morning", "Good morning! How can I assist you?"),
    ("How are you?", "I am running well, thank you! How can I help you?"),
    ("How are you doing?", "I'm doing well. What can I do for you?"),
    ("Good evening", "Good evening! What can I help you with?"),
])
add("greeting", "bn", [
    ("হ্যালো!", "হ্যালো! আজ আমি কীভাবে সাহায্য করতে পারি?"),
    ("শুভ সকাল", "শুভ সকাল! আমি কীভাবে সাহায্য করতে পারি?"),
    ("কেমন আছো?", "আমি ভালো আছি, ধন্যবাদ! আপনাকে কীভাবে সাহায্য করতে পারি?"),
    ("ভালো আছ?", "হ্যাঁ, আমি ভালো আছি। আপনি কী জানতে চান?"),
])
add("greeting", "banglish", [
    ("hi", "Hi! Ki bhabe help korte pari?"),
    ("kemon acho?", "Ami bhalo achi, dhonnobad! Apni ki jante chan?"),
    ("shuvo sokal", "Shuvo sokal! Ki help korte pari?"),
    ("bhalo acho?", "Hyan, ami bhalo achi. Apni ki janen?"),
])

add("thanks", "en", [
    ("Thank you", "You're welcome! Ask me anything else."),
    ("Thanks a lot", "Happy to help! Let me know if you need more."),
    ("That was helpful", "Glad it helped! Feel free to ask more questions."),
])
add("thanks", "bn", [
    ("ধন্যবাদ", "আপনাকে স্বাগতম! আরো প্রশ্ন থাকলে জিজ্ঞাসা করুন।"),
    ("খুব সাহায্য করেছো", "খুশি হলাম! আরো কিছু জানতে চাইলে বলুন।"),
])
add("thanks", "banglish", [
    ("dhonnobad", "Apnake swagatam! Onno kichu janle bolun."),
    ("helpful chilo", "Bhalo laglo! Onno question thakle janaben."),
])

# --- facts ---
add("facts", "en", [
    ("What is the capital of Bangladesh?", "Dhaka is the capital of Bangladesh."),
    ("What is the capital of Japan?", "Tokyo is the capital of Japan."),
    ("What is water made of?", "Water is H2O — two hydrogen atoms and one oxygen atom."),
    ("Why do humans need water?", "Humans need water for digestion, temperature control, and survival."),
    ("What is the Sun?", "The Sun is a star at the center of our solar system providing light and heat."),
    ("Why do plants need sunlight?", "Plants need sunlight for photosynthesis to make food."),
    ("What is artificial intelligence?", "AI is machines simulating human intelligence, especially learning and problem-solving."),
    ("What is the purpose of education?", "Education builds knowledge, skills, and critical thinking for personal growth."),
    ("What is gravity?", "Gravity is the force that attracts objects toward each other; Earth pulls things downward."),
    ("How many days are in a week?", "There are 7 days in a week."),
])
add("facts", "bn", [
    ("বাংলাদেশের রাজধানী কী?", "বাংলাদেশের রাজধানী ঢাকা।"),
    ("পানি কী দিয়ে তৈরি?", "পানি H2O — দুটি হাইড্রোজেন ও একটি অক্সিজেন পরমাণু দিয়ে তৈরি।"),
    ("মানুষ কেন পানি পান করে?", "মানুষ হজম, দেহের তাপমাত্রা নিয়ন্ত্রণ ও বেঁচে থাকার জন্য পানি পান করে।"),
    ("সূর্য কী?", "সূর্য আমাদের সৌরজগতের কেন্দ্রে থাকা একটি তারা, যা আলো ও তাপ দেয়।"),
    ("গাছ সূর্যের আলো কেন প্রয়োজন?", "Photosynthesis-এর জন্য গাছের সূর্যের আলো প্রয়োজন — এ থেকেই গাছ খাদ্য তৈরি করে।"),
    ("কৃত্রিম বুদ্ধিমত্তা কী?", "কৃত্রিম বুদ্ধিমত্তা হলো মেশিনের দ্বারা মানবীয় বুদ্ধিমত্তার অনুকরণ — শেখা ও সমস্যা সমাধান।"),
    ("শিক্ষার উদ্দেশ্য কী?", "শিক্ষা জ্ঞান, দক্ষতা ও সমালোচনামূলক চিন্তা বিকশিত করে ব্যক্তিগত উন্নতির জন্য।"),
    ("মাধ্যাকর্ষণ কী?", "মাধ্যাকর্ষণ হলো বস্তুগুলোর পরস্পরের দিকে আকর্ষণ বল; পৃথিবী সবকিছু নিচের দিকে টানে।"),
    ("এক সপ্তাহে কয় দিন?", "এক সপ্তাহে ৭ দিন।"),
])
add("facts", "banglish", [
    ("Bangladesh er capital ki?", "Dhaka Bangladesh er capital."),
    ("pani ki diye toiri?", "Pani H2O — 2 ta hydrogen ar 1 ta oxygen atom diye toiri."),
    ("manush keno pani khay?", "Manush digestion, body temperature control ar bachte hole pani khay."),
    ("surjo ki?", "Surjo solar system er center e thaka ekta star, ja alok ar tap dey."),
    ("gach surjer aloke keno?", "Photosynthesis er jonno gach er surjer aloke lage — shekhan theke food toiri hoy."),
    ("artificial intelligence ki?", "AI holo machine er maddhome human intelligence er simulation — learning ar problem solving."),
    ("shikkhar uddeshyo ki?", "Shikkha knowledge, skill ar critical thinking develop kore personal growth er jonno."),
    ("gravity ki?", "Gravity holo object gulor perer dik e attractions; earth shob kichu niche taray."),
])

# --- explanations ---
add("explain", "en", [
    ("Explain photosynthesis simply.", "Photosynthesis is how plants turn sunlight, water, and CO2 into food and oxygen."),
    ("Explain why the sky is blue.", "The sky looks blue because air molecules scatter blue sunlight more than other colors."),
    ("Explain what a computer is.", "A computer is an electronic machine that stores data and follows instructions to solve problems."),
    ("Explain rain simply.", "Rain happens when water evaporates, rises, cools into clouds, and falls back as water."),
])
add("explain", "bn", [
    ("Photosynthesis সহজ করে ব্যাখ্যা করো।", "Photosynthesis হলো যেভাবে গাছ সূর্যের আলো, পানি ও CO2 দিয়ে খাদ্য ও অক্সিজেন তৈরি করে।"),
    ("আকাশ নীল কেন?", "বাতাসের অণু নীল সূর্যালোক বেশি scatters করে, তাই আকাশ নীল দেখায়।"),
    ("বৃষ্টি কীভাবে হয়?", "পানি বাষ্প হয়ে বায়ুমণ্ডলে উঠে ঠান্ডা হয়ে মেঘে পরিণত হয় এবং বৃষ্টি হিসেবে নিচে পড়ে।"),
    ("কম্পিউটার কী?", "কম্পিউটার একটি ইলেকট্রনিক যন্ত্র যা তথ্য সংরক্ষণ করে ও নির্দেশনা অনুসরণ করে সমস্যা সমাধান করে।"),
])
add("explain", "banglish", [
    ("photosynthesis bujhao.", "Photosynthesis holo ja diye g ach surjer aloke, pani ar CO2 diye food ar oxygen toiri kore."),
    ("akash neel keno?", "Hawa'r molecule neel sunlight beshi scatter kore, tai akash neel dekhay."),
    ("bristi kivabe hoy?", "Pani bappe uthe, thanda hoye me e porinoto hoy, tarpor brishti hishebe pore."),
])

# --- uncertainty / honesty ---
add("uncertainty", "en", [
    ("What will happen tomorrow?", "I cannot predict the future. I can only discuss what is generally known."),
    ("Tell me a secret", "I don't have personal secrets. Is there something else I can help with?"),
    ("What is the meaning of life?", "That is a deep philosophical question. Many people have different answers."),
])
add("uncertainty", "bn", [
    ("আগামীকাল কী হবে?", "আমি ভবিষ্যৎ ভবিষ্যদ্বাণী করতে পারি না। আমি শুধু সাধারণ জ্ঞান নিয়ে কথা বলতে পারি।"),
    ("জীবনের অর্থ কী?", "এটি একটি গভীর দার্শনিক প্রশ্ন; মানুষের বিভিন্ন মতামত আছে।"),
])
add("uncertainty", "banglish", [
    ("kal ki hobe?", "Ami bhabishyot bhabishyobani korte pari na. Sudhu general knowledge niye kotha bolte pari."),
])

# --- emotional / everyday ---
add("everyday", "en", [
    ("I am sad today", "I'm sorry to hear that. Would you like to talk about what's bothering you?"),
    ("I feel happy", "That's wonderful! What made your day so good?"),
    ("I am tired", "Rest is important. Would you like some suggestions for relaxing?"),
    ("I failed my test", "I'm sorry. Would you like help reviewing what went wrong or planning how to improve?"),
])
add("everyday", "bn", [
    ("আজ আমি মন খারাপ", "দুঃখিত শুনে। আপনি কী নিয়ে কথা বলতে চান?"),
    ("আমি টেস্টে ফেল করেছি", "দুঃখিত। আপনি কি ভুলগুলো দেখে আবার পড়তে সাহায্য চান?"),
    ("আমি ক্লান্ত", "বিশ্রাম জরুরি। কোনো বিশ্রাম নেওয়ার পরামর্শ চান?"),
])
add("everyday", "banglish", [
    ("aj mon kharap", "Dukkho laglo. Ki niye kotha bolte chan?"),
    ("ami test e fail korechi", "Dukkho laglo. Bhul gulo dekhe abar pora te help chan?"),
    ("ami tired", "Bishram dorkar. Kono relax er suggestion chan?"),
])

# --- basic reasoning (small, honest) ---
add("reasoning", "en", [
    ("If I have 3 apples and buy 2 more, how many apples?", "You have 5 apples."),
    ("What is 7 + 5?", "7 + 5 = 12."),
    ("If today is Monday, what day after 3 days?", "After 3 days it will be Thursday."),
    ("A room has 4 corners with 1 cat each. How many cats?", "There are 4 cats."),
    ("Which is heavier: 1 kg of iron or 1 kg of feathers?", "They weigh the same — 1 kg each."),
])
add("reasoning", "bn", [
    ("৩টা আপেল আছে, আরো ২টা কিনলে মোট কয়টা?", "মোট ৫টা আপেল হবে।"),
    ("৭ + ৫ কত?", "৭ + ৫ = ১২।"),
    ("সোমবারের ৩ দিন পর কী বার?", "৩ দিন পর বৃহস্পতিবার হবে।"),
])
add("reasoning", "banglish", [
    ("3 ta apple ache, aro 2 ta kinle mototo koto?", "Mot 5 ta apple hobe."),
    ("7 + 5 koto?", "7 + 5 = 12."),
])

# --- multi-turn conversations (structured) ---
MULTITURN = [
    {"lang": "en", "messages": [
        {"role": "user", "content": "My name is Rahim."},
        {"role": "assistant", "content": "Nice to meet you, Rahim!"},
        {"role": "user", "content": "What is my name?"},
        {"role": "assistant", "content": "Your name is Rahim."},
    ]},
    {"lang": "en", "messages": [
        {"role": "user", "content": "I like learning science."},
        {"role": "assistant", "content": "Science is a great subject to learn!"},
        {"role": "user", "content": "What subject do I like?"},
        {"role": "assistant", "content": "You said you like learning science."},
    ]},
    {"lang": "bn", "messages": [
        {"role": "user", "content": "আমার নাম রহিম।"},
        {"role": "assistant", "content": "আপনার সাথে পরিচিত হয়ে ভালো লাগলো, রহিম!"},
        {"role": "user", "content": "আমার নাম কী?"},
        {"role": "assistant", "content": "আপনার নাম রহিম।"},
    ]},
    {"lang": "banglish", "messages": [
        {"role": "user", "content": "amar naam Rahim."},
        {"role": "assistant", "content": "Nice to meet you, Rahim!"},
        {"role": "user", "content": "amar naam ki?"},
        {"role": "assistant", "content": "Apnar naam Rahim."},
    ]},
]


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def build():
    records = []
    rejected = []
    seen_q = {}
    for cat, lang, pairs in BANKS:
        for i, (q, a) in enumerate(pairs):
            q, a = q.strip(), a.strip()
            rid = f"{cat}:{lang}:{i}"
            # validation
            if not q or not a:
                rejected.append({"id": rid, "reason": "empty_field"}); continue
            if len(q) > 500 or len(a) > 800:
                rejected.append({"id": rid, "reason": "too_long"}); continue
            if any(ord(c) == 0xFFFD for c in q + a):
                rejected.append({"id": rid, "reason": "invalid_unicode"}); continue
            k = norm(q)
            if k in seen_q:
                rejected.append({"id": rid, "reason": "duplicate_question",
                                 "dup_of": seen_q[k]}); continue
            seen_q[k] = rid
            records.append({
                "sample_id": rid, "lang": lang, "category": cat,
                "conversation_id": rid, "version": "sft_v2",
                "messages": [{"role": "user", "content": q},
                             {"role": "assistant", "content": a}],
                "provenance": {"builder": "build_sft_v2.py", "seed": SEED,
                               "source": "deterministic_template"},
            })
    # multi-turn (each conversation atomic for splitting)
    for j, conv in enumerate(MULTITURN):
        cid = f"multiturn:{j}"
        records.append({
            "sample_id": cid, "lang": conv["lang"], "category": "multiturn",
            "conversation_id": cid, "version": "sft_v2",
            "messages": conv["messages"],
            "provenance": {"builder": "build_sft_v2.py", "seed": SEED,
                           "source": "deterministic_template"},
        })
    return records, rejected


def split(records):
    """Group-aware deterministic split by conversation_id. 90/5/5."""
    groups = defaultdict(list)
    for r in records:
        groups[r["conversation_id"]].append(r)
    ids = sorted(groups.keys())
    random.Random(SEED).shuffle(ids)
    n = len(ids)
    n_val = max(1, int(n * 0.05)); n_test = max(1, int(n * 0.05))
    test_ids = set(ids[:n_test]); val_ids = set(ids[n_test:n_test + n_val])
    train_ids = set(ids[n_test + n_val:])
    out = {"train": [], "validation": [], "test": []}
    for cid, rs in groups.items():
        tgt = "test" if cid in test_ids else "validation" if cid in val_ids else "train"
        out[tgt].extend(rs)
    # leakage check
    qsets = {k: set(norm(r["messages"][0]["content"]) for r in v if r["messages"][0]["role"] == "user")
             for k, v in out.items()}
    leaks = {f"{a}-{b}": len(qsets[a] & qsets[b])
             for a in qsets for b in qsets if a < b}
    return out, leaks


def main():
    records, rejected = build()
    splits, leaks = split(records)
    # write
    files = {}
    for name, rows in splits.items():
        p = os.path.join(OUT, f"{name}.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        files[name] = p
    # stats
    def stats(rows):
        return {
            "n": len(rows),
            "lang": dict(Counter(r["lang"] for r in rows)),
            "category": dict(Counter(r["category"] for r in rows)),
            "avg_user_chars": round(sum(len(m["content"]) for r in rows
                                        for m in r["messages"] if m["role"] == "user") /
                                   max(sum(1 for r in rows for m in r["messages"] if m["role"] == "user"), 1), 1),
            "avg_asst_chars": round(sum(len(m["content"]) for r in rows
                                        for m in r["messages"] if m["role"] == "assistant") /
                                    max(sum(1 for r in rows for m in r["messages"] if m["role"] == "assistant"), 1), 1),
        }
    statistics = {k: stats(v) for k, v in splits.items()}
    statistics["rejected"] = len(rejected)
    statistics["leakage_question_overlap"] = leaks
    with open(os.path.join(OUT, "rejected_records.jsonl"), "w", encoding="utf-8") as f:
        for r in rejected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(OUT, "source_provenance.jsonl"), "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({"sample_id": r["sample_id"],
                                "provenance": r["provenance"]}, ensure_ascii=False) + "\n")
    manifest = {"version": "sft_v2", "seed": SEED,
                "total": len(records), "splits": {k: len(v) for k, v in splits.items()},
                "statistics": statistics,
                "note": "Deterministic templates only — no external AI, no fabricated facts."}
    with open(os.path.join(OUT, "dataset_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, "dataset_statistics.json"), "w", encoding="utf-8") as f:
        json.dump(statistics, f, indent=1, ensure_ascii=False)
    # checksums
    lines = []
    for name in ("train.jsonl", "validation.jsonl", "test.jsonl",
                 "dataset_manifest.json", "dataset_statistics.json"):
        p = os.path.join(OUT, name)
        lines.append(f"{hashlib.sha256(open(p,'rb').read()).hexdigest()}  {name}")
    open(os.path.join(OUT, "checksums.sha256"), "w").write("\n".join(lines) + "\n")
    print(f"WROTE sft_v2: {len(records)} records | splits {manifest['splits']} | rejected {len(rejected)}")
    print("lang dist (train):", statistics["train"]["lang"])
    print("leakage:", leaks)
    print("sha train:", lines[0].split()[0][:20] + "…")


if __name__ == "__main__":
    main()
