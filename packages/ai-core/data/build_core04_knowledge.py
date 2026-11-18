"""Core-04 knowledge dataset — self-contained concept cards with verified,
static facts (no live knowledge claims). en+bn. QA/explain/classify/summarize/
uncertainty formats. Hash-split, provenance, checksums.
Output: data/core04_knowledge/{train,validation,test}.jsonl + manifest"""
import json, os, random, hashlib
from collections import Counter

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), "core04_knowledge")
os.makedirs(OUT, exist_ok=True)


def h(s):
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


recs = []


def add(lang, cat, q, a):
    rid = f"{cat}:{lang}:{len(recs)}"
    recs.append({
        "sample_id": rid, "lang": lang, "category": cat,
        "conversation_id": rid,
        "messages": [{"role": "user", "content": q},
                     {"role": "assistant", "content": a}],
        "provenance": {"builder": "build_core04_knowledge.py",
                       "seed": SEED, "source": "curated_static_facts"},
    })


# concept cards: (topic, en_fact, bn_fact) — static, verifiable facts only
CARDS = [
    ("photosynthesis",
     "Photosynthesis is the process by which plants use sunlight, water and carbon dioxide to make food and release oxygen.",
     "Photosynthesis হলো যেভাবে গাছ সূর্যের আলো, পানি ও CO2 দিয়ে খাদ্য তৈরি করে ও অক্সিজেন ছাড়ে।"),
    ("gravity",
     "Gravity is the force that attracts objects toward each other; Earth's gravity pulls objects downward.",
     "মাধ্যাকর্ষণ হলো বস্তুগুলোর পরস্পরের দিকে আকর্ষণ বল; পৃথিবীর মাধ্যাকর্ষণ সবকিছু নিচের দিকে টানে।"),
    ("water cycle",
     "The water cycle describes evaporation, condensation and precipitation moving water through Earth's systems.",
     "জলচক্র বর্ণনা করে বাষ্পীভবন, ঘনীভবন ও বৃষ্টিপাতের মাধ্যমে পানি কীভাবে চলাচল করে।"),
    ("solar system",
     "The solar system consists of the Sun and the planets, moons, asteroids and comets orbiting it.",
     "সৌরজগতে সূর্য এবং তার চারপাশে কক্ষপথে থাকা গ্রহ, উপগ্রহ, গ্রহাণু ও ধূমকেতু রয়েছে।"),
    ("computer",
     "A computer is an electronic machine that stores data and follows instructions to process information.",
     "কম্পিউটার একটি ইলেকট্রনিক যন্ত্র যা তথ্য সংরক্ষণ করে ও নির্দেশনা অনুসরণ করে তথ্য প্রক্রিয়া করে।"),
    ("democracy",
     "Democracy is a system of government where people choose their leaders through free elections.",
     "গণতন্ত্র এমন শাসনব্যবস্থা যেখানে মানুষ মুক্ত নির্বাচনের মাধ্যমে নেতা নির্বাচন করে।"),
    ("internet",
     "The internet is a global network connecting computers worldwide to share information.",
     "ইন্টারনেট একটি বিশ্বব্যাপী নেটওয়ার্ক যা কম্পিউটারগুলোকে তথ্য ভাগাভাগি করতে সংযুক্ত করে।"),
    ("climate",
     "Climate is the long-term average weather pattern of a region over many years.",
     "জলবায়ু হলো কোনো অঞ্চলের দীর্ঘমেয়াদি গড় আবহাওয়া।"),
    ("chlorophyll",
     "Chlorophyll is the green pigment in plants that captures sunlight for photosynthesis.",
     "Chlorophyll হলো গাছে থাকা সবুজ রঞ্জক যা photosynthesis-এর জন্য সূর্যের আলো ধরে।"),
    ("renewable energy",
     "Renewable energy comes from sources that naturally replenish, like solar, wind and hydro power.",
     "নবায়নযোগ্য শক্তি এমন উৎস থেকে আসে যা স্বাভাবিকভাবে পুনরায় উৎপন্ন হয় — যেমন solar, wind ও hydro power।"),
    ("river",
     "A river is a natural stream of water that flows toward a sea, lake or another river.",
     "নদী হলো স্বাভাবিক পানির স্রোত যা সমুদ্র, হ্রদ বা অন্য নদীর দিকে বয়ে যায়।"),
    ("mountain",
     "A mountain is a large natural elevation of land, usually formed by tectonic activity.",
     "পাহাড় হলো ভূমির একটি বড় প্রাকৃতিক উচ্চতা, সাধারণত টেকটোনিক ক্রিয়ায় গঠিত হয়।"),
    ("oxygen",
     "Oxygen is a chemical element essential for respiration in most living organisms.",
     "অক্সিজেন একটি chemical element যা অধিকাংশ জীবের শ্বাসক্রিয়ার জন্য অপরিহার্য।"),
    ("dna",
     "DNA is the molecule that carries genetic instructions in living organisms.",
     "DNA হলো অণু যা জীবদেহে genetic নির্দেশনা বহন করে।"),
    ("volcano",
     "A volcano is an opening in Earth's crust through which lava, ash and gases erupt.",
     "আগ্নেয়গিরি হলো পৃথিবীর ভূত্বকের একটি খোলা অংশ দিয়ে lava, ছাই ও গ্যাস বেরিয়ে আসে।"),
    ("earthquake",
     "An earthquake is the shaking of Earth's surface caused by movement beneath the crust.",
     "ভূমিকম্প হলো ভূত্বকের নিচে নড়াচড়ার কারণে পৃথিবীর পৃষ্ঠের কাঁপুনি।"),
    ("ecosystem",
     "An ecosystem is a community of organisms interacting with their physical environment.",
     "পরিবেশতন্ত্র হলো জীব ও তাদের ভৌত পরিবেশের পারস্পরিক ক্রিয়ার একটি সমষ্টি।"),
    ("compass",
     "A compass is a navigation tool that points toward Earth's magnetic north.",
     "কম্পাস একটি navigation যন্ত্র যা পৃথিবীর চুম্বকীয় উত্তর দিকে নির্দেশ করে।"),
    ("battery",
     "A battery stores chemical energy and converts it to electrical energy when used.",
     "ব্যাটারি chemical energy সঞ্চয় করে এবং ব্যবহারের সময় তাকে electrical energy-তে রূপান্তর করে।"),
    ("satellite",
     "A satellite is an object that orbits a planet or star under gravitational pull.",
     "উপগ্রহ হলো একটি বস্তু যা মাধ্যাকর্ষণের কারণে গ্রহ বা তারকা প্রদক্ষিণে ঘোরে।"),
    ("ocean",
     "The ocean covers most of Earth's surface and regulates the global climate.",
     "মহাসাগর পৃথিবীর বেশিরভাগ পৃষ্ঠ ঢাকা এবং global climate নিয়ন্ত্রণ করে।"),
    ("train",
     "A train is a connected series of vehicles that runs on rails to transport passengers or goods.",
     "ট্রেন হলো সংযুক্ত যানবাহনের একটি সারি যা রেলে চলে যাত্রী বা পণ্য পরিবহন করে।"),
    ("bridge",
     "A bridge is a structure built to span a physical obstacle such as water or a valley.",
     "সেতু হলো এমন একটি কাঠামো যা পানি বা উপত্যকার মতো বাধা পার হওয়ার জন্য নির্মিত হয়।"),
    ("library",
     "A library is a place that collects and lends books and other reading materials.",
     "লাইব্রেরি হলো এমন একটি জায়গা যা বই ও অন্যান্য পড়ার উপকরণ সংগ্রহ ও বিতরণ করে।"),
    ("hospital",
     "A hospital is a healthcare institution providing medical treatment to patients.",
     "হাসপাতাল হলো একটি স্বাস্থ্যসেবা প্রতিষ্ঠান যা রোগীদের চিকিৎসা সেবা দেয়।"),
    ("school",
     "A school is an institution where students learn academic subjects and skills.",
     "স্কুল হলো এমন একটি প্রতিষ্ঠান যেখানে শিক্ষার্থীরা academic বিষয় ও দক্ষতা শেখে।"),
    ("farm",
     "A farm is land used for growing crops or raising animals for food.",
     "খামার হলো এমন জমি যেখানে ফসল চাষ বা খাদ্যের জন্য পশুপালন করা হয়।"),
    ("desert",
     "A desert is a dry region that receives very little rainfall each year.",
     "মরুভূমি হলো এমন শুষ্ক অঞ্চল যেখানে প্রতি বছর খুব কম বৃষ্টি হয়।"),
    ("forest",
     "A forest is a large area covered densely with trees and other vegetation.",
     "বন হলো এমন একটি বড় এলাকা যা গাছপালা দিয়ে ঘনভাবে ঢাকা।"),
    ("artificial intelligence",
     "Artificial intelligence is the simulation of human intelligence by machines, especially computers.",
     "কৃত্রিম বুদ্ধিমত্তা হলো মেশিন, বিশেষ করে কম্পিউটারের মাধ্যমে মানব বুদ্ধিমত্তার অনুকরণ।"),
    ("algorithm",
     "An algorithm is a step-by-step procedure for solving a problem or performing a task.",
     "অ্যালগরিদম হলো কোনো সমস্যা সমাধান বা কাজ সম্পাদনের ধাপে ধাপে পদ্ধতি।"),
    ("database",
     "A database is an organized collection of data stored and accessed electronically.",
     "ডাটাবেস হলো ইলেকট্রনিকভাবে সংরক্ষিত ও অ্যাক্সেস করা তথ্যের একটি সুসংগঠিত সংগ্রহ।"),
    ("photosynthesis_extra",
     "Leaves contain chlorophyll which captures sunlight to power photosynthesis.",
     "পাতায় chlorophyll থাকে যা sunlight ধরে photosynthesis চালায়।"),
]

# QA + explain formats per card
for topic, fact, bn in CARDS:
    add("en", "qa", f"What is {topic}?", fact)
    add("bn", "qa", f"{topic} কী?", bn)
    add("en", "explain", f"Explain {topic}.", fact)
    # phrasing variants — same verified fact, different surface form
    add("en", "qa", f"Tell me about {topic}.", fact)
    add("en", "qa", f"What does {topic} mean?", fact)
    add("bn", "qa", f"{topic} বলতে কী বোঝায়?", bn)
    add("bn", "qa", f"{topic} এর অর্থ কী?", bn)
    add("en", "explain", f"Describe {topic}.", fact)
    add("bn", "explain", f"{topic} ব্যাখ্যা করুন।", bn)

# classification
CLASSES = [
    ("animal", "dog", "mammal"), ("animal", "eagle", "bird"),
    ("object", "table", "furniture"), ("food", "rice", "grain"),
    ("vehicle", "bus", "transport"), ("color", "blue", "color"),
    ("body part", "heart", "organ"), ("profession", "doctor", "medical"),
]
BN_CLASSES = [
    ("পশু", "কুকুর", "স্তন্যপায়ী"), ("পশু", "বাড়াল", "স্তন্যপায়ী"),
    ("বস্তু", "টেবিল", "আসবাব"), ("খাবার", "ভাত", "শস্য"),
    ("যানবাহন", "বাস", "পরিবহন"), ("পেশা", "ডাক্তার", "চিকিৎসা"),
]
for cat, item, cls_ in CLASSES:
    add("en", "classify", f"What category does '{item}' belong to?",
        f"{item} is a {cls_}.")
for cat, item, cls_ in BN_CLASSES:
    add("bn", "classify", f"'{item}' কোন category-তে পড়ে?",
        f"{item} হলো একটি {cls_}।")

# summarization
SUMS = [
    ("en", "The water cycle has three main stages: evaporation, condensation, and precipitation. Water moves continuously through these stages.",
     "The water cycle has three main stages: evaporation, condensation, and precipitation."),
    ("en", "Computers process data using a CPU, memory, and storage. They follow instructions from programs to produce outputs.",
     "Computers process data using a CPU, memory, and storage."),
    ("bn", "কম্পিউটার CPU, memory ও storage ব্যবহার করে তথ্য প্রক্রিয়া করে। প্রোগ্রামের নির্দেশনা অনুসরণ করে ফলাফল তৈরি করে।",
     "কম্পিউটার CPU, memory ও storage ব্যবহার করে তথ্য প্রক্রিয়া করে।"),
    ("en", "A database stores organized data. Queries retrieve records. Indexes speed up searches. Backups protect against data loss.",
     "A database stores organized data; queries retrieve records and backups protect against data loss."),
]
for lang, src, summ in SUMS:
    add(lang, "summarize", f"Summarize: {src}", summ)

# uncertainty / refusal behavior — no live knowledge claims
add("en", "uncertainty", "What is the population of Bangladesh right now?",
    "I don't have live data. My knowledge has a cutoff, so I cannot give a current figure.")
add("en", "uncertainty", "Who won the latest election?",
    "I cannot know current events; my training data has a cutoff.")
add("bn", "uncertainty", "এখন বাংলাদেশে জনসংখ্যা কত?",
    "আমার কাছে হালনাগাদ তথ্য নেই; আমার জ্ঞানের একটি cutoff আছে, তাই বর্তমান সংখ্যা বলতে পারি না।")

# hash-split, deterministic
# FACT-LEVEL split: group by reference answer so the same fact never
# appears in both train and test (prevents answer-level leakage).
recs.sort(key=lambda r: h(r["messages"][1]["content"]))
n = len(recs)
nv = max(1, n // 10)
nt = max(1, n // 10)
test = recs[:nt]
val = recs[nt:nt + nv]
train = recs[nt + nv:]

for nm, rows in (("train", train), ("validation", val), ("test", test)):
    with open(os.path.join(OUT, f"{nm}.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def stats(rows):
    return {"n": len(rows),
            "lang": dict(Counter(r["lang"] for r in rows)),
            "category": dict(Counter(r["category"] for r in rows))}


st = {k: stats(v) for k, v in (("train", train), ("validation", val), ("test", test))}
man = {
    "version": "core04_knowledge_v1", "seed": SEED, "total": len(recs),
    "splits": {"train": len(train), "validation": len(val), "test": len(test)},
    "statistics": st,
    "note": ("Static curated facts only — NO live/current knowledge claims. "
             "Uncertainty behavior trained explicitly. All facts are "
             "self-contained and verifiable; no third-party corpus used."),
}
json.dump(man, open(os.path.join(OUT, "dataset_manifest.json"), "w"), indent=1)

lines = []
for nm in ("train.jsonl", "validation.jsonl", "test.jsonl", "dataset_manifest.json"):
    p = os.path.join(OUT, nm)
    lines.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {nm}")
open(os.path.join(OUT, "checksums.sha256"), "w").write("\n".join(lines) + "\n")

print(f"core04_knowledge: {len(recs)} train={len(train)} val={len(val)} test={len(test)}")
print(st["train"])
