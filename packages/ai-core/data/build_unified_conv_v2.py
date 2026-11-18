"""Build unified trilingual conversational SFT dataset v2.

v2 = v1 records (preserved, re-grouped) + new authored seeds:
multi-turn scenarios, reasoning/decision/self-correction/clarification,
expanded uncertainty/social, procedural verified math & logic.
NO external AI. Output: data/unified_conversational/v2/
"""
import json, os, random, hashlib, re, itertools
from collections import Counter, defaultdict

SEED = 42
random.seed(SEED)
BASE = os.path.join(os.path.dirname(__file__), "unified_conversational")
V1 = os.path.join(BASE, "v1")
OUT = os.path.join(BASE, "v2")
os.makedirs(OUT, exist_ok=True)

recs, QUAR = [], []
BN = re.compile(r'[ঀ-৿]')

def h(s): return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)
def detect(u):
    if BN.search(u): return "bn"
    if re.search(r'\b(ki|koto|ache|nei|bolun|dao|kivabe|keno|korbo|lagbe|bhalo|khub|bhai|vai|hocche|gechi|chai)\b', u, re.I): return "banglish"
    if re.search(r'[a-zA-Z]', u): return "en"
    return "bn"

def add(cat, lang, messages, group, caps=None, source="authored"):
    rid = f"v2:{cat}:{lang}:{len(recs)}"
    recs.append({"sample_id": rid, "id": rid, "lang": lang,
        "category": cat, "task": cat, "capabilities": caps or [],
        "conversation_id": group,
        "messages": [{"role": r, "content": c} for r, c in messages],
        "split_group": group,
        "provenance": {"builder": "build_unified_conv_v2.py", "seed": SEED,
                       "source": source},
        "quality": {"status": "approved", "review_method": "rule_based"}})

def qa(cat, lang, u, a, caps=None):
    add(cat, lang, [("user",u),("assistant",a)], f"g{h(u+a)%200000}", caps)

# ============ 1. LOAD V1 RECORDS (preserved as base) ============
v1_count = 0
for split in ("train","validation","test"):
    p = os.path.join(V1, f"{split}.jsonl")
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        r["split_group"] = r.get("split_group") or f"v1{h(r['sample_id'])%50000}"
        r.setdefault("capabilities", [])
        r["provenance"] = {**r.get("provenance",{}), "source": "v1_carryover"}
        recs.append(r); v1_count += 1
print(f"v1 carryover: {v1_count}")

S = []
def seed(cat, lang, u, a, caps=None): S.append((cat, lang, u, a, caps))

# ============ 2. REASONING / DECISION / SELF-CORRECTION ============
REASON=[
("en","All bloops are razzies. All razzies are lazzies. Are all bloops lazzies?","Yes — since every bloop is a razzie and every razzie is a lazy, every bloop must be a lazy."),
("en","If it rains, the match is cancelled. It is raining. What happens?","The match is cancelled — the rule says rain leads to cancellation."),
("en","Some cats are black. Some black things are cars. Can we conclude some cats are cars?","No — 'some' doesn't guarantee overlap; a cat could be black without being a car."),
("en","Tom is taller than Sam. Sam is taller than Joe. Who is tallest?","Tom is tallest — the order is Tom > Sam > Joe."),
("en","A farmer has chickens and cows. 10 heads, 28 legs. How many of each?","Chickens have 2 legs, cows 4. If x chickens and y cows: x+y=10, 2x+4y=28 → y=4 cows, x=6 chickens."),
("en","If all A are B, and some B are C, are all A necessarily C?","No — A is inside B, but only some B are C, so A may not be C."),
("en","Which is heavier: a kg of feathers or a kg of iron?","They weigh the same — 1 kg each. Iron is denser, but weight is equal."),
("en","A bat and ball cost $1.10 total. Bat costs $1 more than ball. Ball cost?","The ball costs $0.05. ($1.05 bat + $0.05 ball = $1.10, and $1.05 - $0.05 = $1.00.)"),
("bn","সব bloop razzie এবং সব razzie lazy। সব bloop কি lazy?","হ্যাঁ — প্রতিটি bloop একটি razzie এবং প্রতিটি razzie lazy, তাই প্রতিটি bloop lazy।"),
("bn","বৃষ্টি হলে ম্যাচ বাতিল। বৃষ্টি হচ্ছে। কী হবে?","ম্যাচ বাতিল হবে — নিয়ম অনুযায়ী বৃষ্টিতে বাতিল হয়।"),
("bn","Tom, Sam-এর চেয়ে লম্বা। Sam, Joe-এর চেয়ে লম্বা। সবচেয়ে লম্বা কে?","Tom সবচেয়ে লম্বা — ক্রম: Tom > Sam > Joe।"),
("bn","এক কিসের ওজন আরেক কিসের চেয়ে বেশি —_feather নাকি iron?","দুটোই ১ কেজি হলে সমান ওজন। Iron বেশি dense, কিন্তু ওজন সমান।"),
("banglish","Ami 5 ta apple nilam, 3 ta khailam. Koto ta roilo?","5 - 3 = 2 ta apple roilo."),
("banglish","If X > Y and Y > Z, tahole X naki Z boro?","X boro — karon X > Y > Z chain."),
]
for lang,u,a in REASON: seed("reasoning",lang,u,a,["reasoning","deduction"])

DECISION=[
("en","I have 500 taka and want to buy either a book for 300 or two pens for 150 each. Which is better if I want to save money?","Two pens cost 300 total, same as the book — but if saving money is the goal, pens leave 200 taka vs book leaves 200 too. Actually both leave 200; choose based on what you need."),
("en","Should I take the bus or walk? It's 2 km and I have 15 minutes.","Walking 2 km takes about 20-25 minutes, so you'd be late. Take the bus — it's the safer choice for your time."),
("en","I can study now or after dinner. I have an exam tomorrow. What should I do?","Study now — you have more energy earlier in the day, and reviewing before sleep helps memory. Finish by dinner, then rest."),
("en","Which phone should I buy: one with better camera or better battery?","It depends on your priority — if you take many photos, choose camera; if you need all-day battery, choose battery. What matters more to you?"),
("bn","আমার ৫০০ টাকা আছে — ৩০০ টাকার বই না ১৫০ টাকার দুইটি কলম? সাশ্রয়ের জন্য কোনটা?","দুটোই মোট ৩০০ টাকা — সাশ্রয় সমান। আপনি কী প্রয়োজন তা ঠিক করে বেছে নিন।"),
("bn","বাসে যাব নাকি হেঁটে? ২ কিলোমিটার আর ১৫ মিনিট সময়।","হেঁটে ২ কিলোমিটার ~২০-২৫ মিনিট লাগে, তাই দেরি হবে। বাস নিন — সময় বাঁচবে।"),
("bn","এখন পড়ব নাকি রাতের খাবারের পর? কাল পরীক্ষা।","এখনই পড়ুন — দিনে শক্তি বেশি, আর ঘুমানোর আগে পড়া মনে রাখে ভালো।"),
("banglish","Ami ekhon porbo naki rater por? Exam kal.","Ekhon-i porun — dine shakti beshi, ar shonar age porle mone rakha easy."),
("banglish","Kon ta nen — bhalo camera wala phone naki bhalo battery wala?","Apnar priority dekhe — onek photo tolen tahole camera, shorol din battery lagbe tahole battery. Apnar jonno konta important?"),
]
for lang,u,a in DECISION: seed("decision",lang,u,a,["decision","reasoning"])

SELFCORR=[
("en","You said the capital of Australia is Sydney, but it's actually Canberra. Can you correct that?","You're right — I made an error. The capital of Australia is Canberra, not Sydney. Sydney is the largest city, but not the capital. Thank you for correcting me."),
("en","I think you made a mistake earlier — 7 x 8 is 56, not 54.","You're correct — 7 x 8 = 56. I apologize for the error; thank you for pointing it out."),
("bn","আপনি আগের উত্তরে ভুল বলেছেন — বাংলাদেশের রাজধানী ঢাকা, চট্টগ্রাম নয়।","আপনি ঠিক বলেছেন, আমি ভুল করেছিলাম। বাংলাদেশের রাজধানী ঢাকা। দুঃখিত, সংশোধনের জন্য ধন্যবাদ।"),
("banglish","Tumi age vul bolecho — 7 x 8 = 56, 54 noy.","Thik bolecho, vai — 7 x 8 = 56. Amar vul, sorry. Thik kore dawyar jonno dhonnobad."),
]
for lang,u,a in SELFCORR: seed("self_correction",lang,u,a,["self_correction"])

CLARIFY=[
("en","Tell me about it.","Could you be more specific? 'It' could refer to many things — what would you like to know about?"),
("en","How much does it cost?","I'd need to know what 'it' refers to. What product or service are you asking about?"),
("en","Is it good?","Good for what purpose? Could you tell me what you're evaluating?"),
("bn","এটা কেমন?","'এটা' বলতে কী বোঝাচ্ছেন? আরও নির্দিষ্ট করে বললে ভালো হয়।"),
("banglish","Eta kemon?","'Eta' mane ki bujhaacchen? Aro specific bole dile valo hobe."),
]
for lang,u,a in CLARIFY: seed("clarification",lang,u,a,["clarification"])

UNC2=[
("en","What is the exact population of Tokyo in 2050?","I can't predict future populations precisely. I can explain trends or estimation methods if that helps."),
("en","What did the president say in yesterday's speech?","I don't have access to current events or speeches. My knowledge has a cutoff date."),
("en","Is it safe to eat this food? It smells a bit off.","If food smells off, it's safer not to eat it. When in doubt, throw it out — food poisoning isn't worth the risk."),
("en","Can you predict tomorrow's lottery numbers?","I can't predict random events like lottery numbers — each draw is independent. If you play, do it for fun, not as an investment."),
("bn","২০৫০ সালে টোকিওর সঠিক জনসংখ্যা কত হবে?","ভবিষ্যতের জনসংখ্যা আমি সঠিকভাবে বলতে পারি না। Trend বা estimation method বুঝিয়ে দিতে পারি।"),
("bn","গতকালের mónn Muktir-request تغیر?","আমি বর্তমান ঘটনা জানি না — আমার জ্ঞানের cutoff আছে।"),
("banglish","Kal je speech dilen seita ki bolsen?","Amar kache current event nei — amar knowledge er cutoff ache, tai janbo na."),
("banglish","Ekhon-i stock market e invest korbo?","Amar kache live market data nei. Financial decision er age research lagbe — ami explanation dite pari kintu prediction na."),
]
for lang,u,a in UNC2: seed("uncertainty",lang,u,a,["uncertainty","honesty"])

SOC2=[
("en","I'm worried about my exam tomorrow.","It's normal to feel nervous before an exam. A quick review of key points and a good night's sleep will help more than last-minute cramming. You've prepared — trust yourself."),
("en","My friend is going through a hard time.","That's kind of you to notice. Listening without judgment helps more than advice. Ask what they need — sometimes people just want to be heard."),
("en","I don't know what to do with my life.","That's a big question and it's okay not to have the answer yet. What aspects of work or life feel most important to you right now?"),
("bn","আগামীকালের পরীক্ষার worrying?","পরীক্ষার আগে nervous হওয়া স্বাভাবিক। Spend-তে panic না করে ভালো করে ঘুমান — prepared effort-ই কাজ করবে।"),
("bn","আমার বন্ধু কষ্টে আছে।","আপনি খেয়াল করা সুন্দর। Judgment না করে শোনা rescues করে — তারা কী চায় জিজ্ঞেস করুন।"),
("banglish","Ami life niye confused.","Boro proshno — answer na thakleo thik ache. Apnar jonno ki important ekhon — kaj naki somoy?"),
]
for lang,u,a in SOC2: seed("social",lang,u,a,["social","emotional"])

# ============ 3. MULTI-TURN SCENARIOS (authored scripts + slot variants) ============
# Each scenario: per-language list of (user,assistant) turn pairs.
SCENARIOS = {
"trip_plan": {
 "en":[("I'm planning a trip to Cox's Bazar.","That sounds nice! When are you thinking of going?"),
       ("Next month, for 3 days.","Three days is good for Cox's Bazar. The beach, Himchari, and Inani are popular spots. Have you booked accommodation?"),
       ("Not yet. What should I pack?","Pack light cotton clothes, sunscreen, a hat, and comfortable sandals. Don't forget swimwear if you plan to swim."),
       ("Thanks! Anything else?","Check the weather forecast before leaving, and keep some cash handy — card machines aren't everywhere. Have a great trip!")],
 "bn":[("আমি কক্সবাজারে ঘুরতে যাব।","দারুণ! কখন যাবেন ভাবছেন?"),
       ("আগামী মাসে, ৩ দিনের জন্য।","৩ দিন কোxsবাজারে ভালো। সমুদ্র সৈকত, হিমছড়ি আর ইনানী জনপ্রিয়। থাকার ব্যবস্থা করেছেন?"),
       ("এখনো না। কী নেব?","হালকা সুতির পোশাক, সানস্ক্রিন, টুপি আর আরামদায়ক স্যান্ডেল। সাঁতার কাটলে swimwear ভুলবেন না।"),
       ("ধন্যবাদ! আর কিছু?","যাওয়ার আগে আবহাওয়ার পূর্বাভাস দেখুন, আর কিছু cash রাখুন — কার্ড machine সব জায়গায় নেই। উপভোগ করুন!"),],
 "banglish":[("Ami Cox's Bazar e ghurate jabo.","Darun! Kobe jaccho bhabchho?"),
       ("Next mashe, 3 din er jonno.","3 din Cox's Bazar e valo. Beach, Himchari, ar Inani popular. Thaka booked korecho?"),
       ("Ekhono na. Ki niye jabo?","Halka suti por suk, sunscreen, topi, ar comfortable sandal. Sootar jonne swimwearo nebena."),
       ("Dhonnobad! Ar kichu?","Jabar age weather forecast dekho, ar cash rekhe jao — card machine sob jaygay nei. Subha jatra!")],
},
"homework": {
 "en":[("I don't understand this math problem.","Sure — can you share the problem or a photo of it?"),
       ("Solve for x: 2x + 6 = 14","Subtract 6 from both sides: 2x = 8. Then divide by 2: x = 4."),
       ("Why do we subtract first?","Because we want to isolate x. The equation says 2x plus 6 equals 14, so removing the 6 from both sides keeps it balanced."),
       ("Got it! Can you give me another one?","Try: 3x - 5 = 16. Add 5 to both sides first, then divide by 3.")],
 "bn":[("আমি এই অঙ্কটা বুঝতে পারছি না।","অবশ্যই — অঙ্কটা বা ছবিটা পাঠাতে পারেন?"),
       ("x বের করো: 2x + 6 = 14","দুই পক্ষে ৬ বিয়োগ করুন: 2x = 8। তারপর ২ দিয়ে ভাগ করুন: x = 4।"),
       ("কেন আগে বিয়োগ করি?","কারণ x-কে একা রাখতে হবে। 2x যোগ 6 সমান 14, তাই দুই পক্ষে 6 বাদ দিলে balance থাকে।"),
       ("বুঝেছি! আরেকটা দিন।","এটা try করুন: 3x - 5 = 16। আগে দুই পক্ষে 5 যোগ করুন, তারপর 3 দিয়ে ভাগ করুন।")],
 "banglish":[("Ami ei math ta bujhte pari na.","Sure — proshnota ba picture pathao."),
       ("x ber koro: 2x + 6 = 14","Duita pashe 6 minus koro: 2x = 8. Tarpor 2 diye vag koro: x = 4."),
       ("Age minus keno kori?","X-ke ekla rakhte hole. 2x jog 6 soman 14, tai duita pashe 6 baad dile balance thake."),
       ("Bujhechi! Ar ekta dao.","Try koro: 3x - 5 = 16. Age duita pashe 5 jog koro, tarpor 3 diye vag koro.")],
},
"job_interview": {
 "en":[("I have a job interview tomorrow. I'm nervous.","That's completely normal! Preparation is the best cure for nerves. Have you researched the company?"),
       ("Yes, but I don't know what they'll ask.","Prepare answers for common questions: tell me about yourself, your strengths, weaknesses, and why you want this job. Practice out loud once."),
       ("What should I wear?","Dress slightly more formally than the office style — clean, ironed, comfortable shoes. First impressions matter."),
       ("Thanks, I feel better.","You're welcome! You've got this. Good luck tomorrow — believe in your preparation.")],
 "bn":[("কাল আমার job interview। nervous লাগছে।","এটা একদম স্বাভাবিক! প্রস্তুতিই nerves-এর ওষুধ। কোম্পানি সম্পর্কে জানেন?"),
       ("হ্যাঁ, কিন্তু কী জিজ্ঞেস করবে জানি না।","সাধারণ প্রশ্নের উত্তর প্রস্তুত করুন: নিজের পরিচয়, strengths, weaknesses, এই job কেন চান। একবার জোরে জোরে practice করুন।"),
       ("কী পরব?","অফিসের চেয়ে একটু formal — পরিষ্কার, ইস্ত্রি করা, আরামদায়ক জুতা। প্রথম প্রভাব গুরুত্বপূর্ণ।"),
       ("ধন্যবাদ, ভালো লাগছে।","স্বাগতম! আপনি পারবেন। কাল শুভকামনা — আপনার প্রস্তুতিতে বিশ্বাস রাখুন।")],
 "banglish":[("Kal amar job interview. Nervous lagche.","Ekdom normal! Preparation-i nerves er osudh. Company niye research korecho?"),
       ("Hyan, kintu ki jigges korbe janbo na.","Common proshner uttor ready koro: nije niye bolo, strengths, weaknesses, ei job keno chan. Jore jore practice koro ekbar."),
       ("Ki porbo?","Office er cheye slightly formal — porishkar, istiri kora, comfortable juta. First impression matter kore."),
       ("Dhonnobad, bhalo lagche.","Swagatom! Apni parben. Kal shubho kamona — preparation e bishash rakho.")],
},
"health": {
 "en":[("I've had a headache all day.","Sorry to hear that. How would you describe it — sharp, dull, or throbbing? And have you eaten or drunk enough water today?"),
       ("It's dull and I've only had tea.","Dehydration and low blood sugar can both cause dull headaches. Try drinking a glass of water and eating something light, then rest in a quiet room."),
       ("Okay, I'll try that. When should I see a doctor?","If the headache is severe, comes with fever, vision problems, or doesn't improve after a day of rest and fluids, see a doctor."),
       ("Thanks for the advice.","You're welcome! Take care and get plenty of rest.")],
 "bn":[("সারাদিন মাথা ধরেছে।","দুঃখিত। কেমন ব্যথা — তীক্ষ্ণ, মন্দ, নাকি ধামা? আর আজ পানি-কিছু খেয়েছেন?"),
       ("মন্দ ব্যথা, শুধু চা খেয়েছি।","পানির অভাব ও রক্তে শর্করার কমতি দুটোই মন্দ মাথাব্যথা করতে পারে। এক গ্লাস পানি ও হালকা কিছু খেয়ে শান্ত জায়গায় বিশ্রাম নিন।"),
       ("ঠিক আছে, করি। ডাক্তার দেখাব কবে?","ব্যথা তীব্র হলে, জ্বর-চোখের সমস্যা- satu- রে না কমলে বা একদিন বিশ্রাম-পানিতেও না সরলে ডাক্তার দেখান।"),
       ("ধন্যবাদ, উপায়র জন্য!","স্বাগতম! ভালো থাকুন আর প্রচুর বিশ্রাম নিন.")],
 "banglish":[("Sora din matha dhore.","Sorry vai. Kemon betha — sharp, dull, naki dhama? Ar aaj jol-kichu kheyecho?"),
       ("Dull, shudhu cha kheyechi.","Jol er komoti ar rakter shorkhara kom dutoi dull matha korte pare. Ek glass jol ar halka kichu khaiye shanti jaygay bishram nin."),
       ("Thik ache, kori. Doctor dekhab kobe?","Btheta tibro hole, jor, chokh er somossa, ba ekdin bishram-joleo na komle doctor dekhan."),
       ("Dhonnobad advice er jonno.","Swagatom! Vhalo thakben ar beshi bishram nin.")],
},
"shopping": {
 "en":[("I'm buying a birthday gift for my mom.","What does she enjoy — cooking, reading, gardening, or something else? Knowing her interests helps narrow it down."),
       ("She loves gardening.","A potted herb garden, gardening gloves with a tool set, or a nice planter would all be thoughtful. What's your budget?"),
       ("Around 1500 taka.","With that budget, a quality planter with herb seeds or a gardening tool kit would be excellent. Both are useful and personal."),
       ("The tool kit sounds good.","Great choice! Look for stainless steel tools — they last longer. Wrap it nicely and add a handwritten card.")],
 "bn":[("মায়ের জন্মদিনের উপহার কিনব।","মা কী পছন্দ করেন — রান্না, পড়া, বাগান, নাকি অন্য কিছু? আগ্রহ জানলে ভালো উপহার বেছে নেওয়া যায়।"),
       ("বাগান করতে ভালোবাসেন।","একটি ছোট গাছের টব, বাগানের দস্তানা-যন্ত্র, বা সুন্দর cachepot ভালো হবে। বাজেট কত?"),
       ("প্রায় ১৫০০ টাকা।","এই বাজেটে মানসম্মত planter বা বাগানের tool kit দারুণ হবে — দুটোই উপকারী ও ব্যক্তিগত।"),
       ("Tool kit ভালো লাগল।","দারুণ! Stainless steel যন্ত্র দেখতে চান — বেশি টেকে। সুন্দর করে wrap করে হাতে লেখা card যোগ করুন।")],
 "banglish":[("Mayer jonmider upohar kinchi.","Ma ki peshob korun — ranna, pora, bagan, naki onno kichu? Agroho janle valo upohar boche neoya jay."),
       ("Bagan korte bhalo basen.","Ekta chhoto gachher tub, baganer dostana-jantr, ba sundor planter bhalo hobe. Budget koto?"),
       ("Proy 1500 taka.","Ei budget e manosomt planter ba baganer tool kit darun hobe — dutoi upokari ar byakti-goto."),
       ("Tool kit bhalo laglo.","Darun! Stainless steel jantr dekho — beshi take. Sundor kore wrap kore hate lekha card jog koro.")],
},
}

# slot variants: substitute names/items to expand honestly
def slot_variants():
    variants=[]
    # health scenario: vary symptom description
    for lang in ("en","bn","banglish"):
        base=SCENARIOS["health"][lang]
        # create 3 variants per language by changing opening symptom
        if lang=="en":
            subs=[("I've had a fever since morning.","I'm sorry — fever can be uncomfortable. Have you taken your temperature?"),
                  ("My throat is sore.","A sore throat is common — do you have a fever or cough too?"),
                  ("I feel dizzy.","Dizziness can have many causes — have you eaten recently, and do you feel weak or nauseous?")]
        elif lang=="bn":
            subs=[("সকাল থেকে জ্বর হয়েছে।","দুঃখিত — জ্বর অস্বস্তিকর। তাপমাত্রা মাপা আছে?"),
                  ("গলা ব্যথা করছে।","গলা ব্যথা সাধারণ — জ্বর বা কাশি আছে?"),
                  ("মাথা ঘোরে।","মাথা ঘোরা অনেক কারণে হতে পারে — খেয়েছেন, দুর্বল বা বমি লাগছে?")]
        else:
            subs=[("Sokal theke jor hoyeche.","Sorry vai — jor aswostikor. Temperature mapecho?"),
                  ("Gola betha korchhe.","Gola betha common — jor ba kashi ache?"),
                  ("Matha ghore.","Matha ghora onek karone hote pare — kheyecho, durbal ba vomi lagche?")]
        for i,(u,a) in enumerate(subs):
            turns=[(u,a)]+base[1:]
            variants.append(("multi_turn",lang,turns,f"mt_health_{lang}_{i}"))
    return variants

# ---- expanded multi-turn: slot variants for remaining scenarios ----
def more_variants():
    V=[]
    # homework: different problems
    hw={
     "en":[("I don't understand this fraction problem.","Tell me the fraction and what you need to find — adding, comparing, or simplifying?"),
           ("I need to add 1/4 and 1/2.","Find a common denominator: 1/2 = 2/4, so 1/4 + 2/4 = 3/4."),
           ("Why do we need the same denominator?","Because fractions can only be added directly when they measure the same-sized pieces — the denominator is the piece size."),
           ("That makes sense. What about 2/3 + 1/6?","Common denominator 6: 2/3 = 4/6, so 4/6 + 1/6 = 5/6.")],
     "bn":[("আমি এই fraction অঙ্কটা বুঝতে পারছি না।","কোন fraction আর কী করতে হবে বলুন — যোগ, তুলনা, নাকি simplify?"),
           ("১/৪ আর ১/২ যোগ করতে হবে।","Same denominator নিন: ১/২ = ২/৪, তাই ১/৪ + ২/৪ = ৩/৪।"),
           ("একই denominator কেন লাগে?","কারণ fraction তখনই সরাসরি যোগ হয় যখন piece size একই — denominator-ই piece size।"),
           ("বুঝেছি। ২/৩ + ১/৬?","Common denominator 6: ২/৩ = ৪/৬, তাই ৪/৬ + ১/৬ = ৫/৬।")],
     "banglish":[("Ami ei fraction ta bujhte pari na.","Kon fraction ar ki korte hobe bolun — jog, tulona, naki simplify?"),
           ("1/4 ar 1/2 jog korte hobe.","Same denominator nin: 1/2 = 2/4, tai 1/4 + 2/4 = 3/4."),
           ("Same denominator keno lagbe?","Karone fraction tokhon-i directly jog hoy jokhon piece size same — denominator-i piece size."),
           ("Bujhechi. 2/3 + 1/6?","Common denominator 6: 2/3 = 4/6, tai 4/6 + 1/6 = 5/6.")]}
    V.append(("multi_turn",hw))
    # job_interview variants
    ji={
     "en":[("I have an interview at a bank.","Banks value accuracy and customer service. Prepare an example of a time you handled a responsible task well."),
           ("What questions should I expect?","Why banking? Tell me about yourself. How do you handle pressure? A scenario question about a difficult customer."),
           ("How do I answer the customer scenario?","Use STAR: Situation, Task, Action, Result. Describe staying calm, listening, and resolving the issue politely."),
           ("This helps a lot.","You're welcome! Remember — confidence comes from preparation. Good luck!")],
     "bn":[("ব্যাংকে interview আছে।","ব্যাংক accuracy আর customer service prices করে। একটি দায়িত্বপূর্ণ কাজের উদাহরণ প্রস্তুত করুন।"),
           ("কী প্রশ্ন আসবে?","কেন banking? নিজের পরিচয়। Pressure handle করেন কীভাবে? কষ্টদায়ক customer-এর scenario।"),
           ("Customer scenario-র উত্তর কীভাবে?","STAR ব্যবহার করুন: Situation, Task, Action, Result। শান্ত থেকে.listener করে Issue resolve করার কথা বলুন।"),
           ("খুব সাহায্য হলো।","স্বাগতম! মনে রাখবেন — প্রস্তুতি থেকে confidence আসে। শুভকামনা!")],
     "banglish":[("Ami bank e interview achi.","Bank accuracy ar customer service values kore. Ekta responsible kaaj er example ready koro."),
           ("Ki proshno ashbe?","Keno banking? Nijer porichoy. Pressure handle kibhabe? Kostodaiok customer er scenario."),
           ("Customer scenario er uttor kivabe?","STAR use koro: Situation, Task, Action, Result. Shanto theke shono ar issue resolve er kotha bolo."),
           ("Khub sahajjo holo.","Swagatom! Mone rakho — preparation theke confidence ashe. Good luck!")]}
    V.append(("multi_turn",ji))
    # shopping variants
    sh={
     "en":[("I'm buying a laptop for study.","What's your budget, and will you mostly use it for documents or programming?"),
           ("Around 40000 taka, mostly documents and research.","For documents and research, prioritize battery life and a comfortable keyboard over raw speed. 8GB RAM and SSD are enough."),
           ("Any specific model suggestions?","Look for reliable brands with good service centers in your city. I can't name current models — check recent reviews for your budget."),
           ("Thanks, that's helpful.","You're welcome! Test the keyboard in person if possible — comfort matters for long study sessions.")],
     "bn":[("পড়াশোনার জন্য laptop কিনব।","বাজেট কত, আর মূলত documents নাকি programming-এ ব্যবহার?"),
           ("প্রায় ৪০,০০০ টাকা, mostly documents ও research।","Documents ও research-এ battery life আর আরামদায়ক keyboard priority — raw speed না। 8GB RAM ও SSD যথেষ্ট।"),
           ("কোন model দেখব?","আপনার শহরে ভালো service center আছে এমন নির্ভরযোগ্য brand দেখুন। বর্তমান model বলতে পারি না — budget-এ recent review দেখুন।"),
           ("ধন্যবাদ, সাহায্য হলো।","স্বাগতম! সম্ভব হলে keyboard হাতে দেখে নিন — লম্বা পড়াশোনায় আরাম গুরুত্বপূর্ণ।")],
     "banglish":[("Porashonar jonno laptop kinchi.","Budget koto, ar muloto documents naki programming e use?"),
           ("Proy 40000 taka, mostly documents ar research.","Documents ar research e battery life ar comfortable keyboard priority — raw speed na. 8GB RAM ar SSD enough."),
           ("Kon model dekhbo?","Apnar shohore bhalo service center ache emon reliable brand dekho. Current model bolte pari na — budget e recent review dekho."),
           ("Dhonnobad, help holo.","Swagatom! Possible hole keyboard hate dekhe nin — lomba porashonay comfort matter kore.")]}
    V.append(("multi_turn",sh))
    return V

for catname,langmap in more_variants():
    for lang,turns in langmap.items():
        msgs=[]
        for u,a in turns: msgs += [("user",u),("assistant",a)]
        add("multi_turn",lang,msgs,f"scv_{catname}_{lang}",["multi_turn","context"])

# materialize scenarios (authored, full conversations)
MT_COUNT=0
for name,langs in SCENARIOS.items():
    for lang,turns in langs.items():
        msgs=[]
        for u,a in turns: msgs += [("user",u),("assistant",a)]
        add("multi_turn",lang,msgs,f"sc_{name}_{lang}",["multi_turn","context"])
        MT_COUNT+=1
# slot variants add more multi-turn
for cat,lang,turns,g in slot_variants():
    msgs=[]
    for u,a in turns: msgs += [("user",u),("assistant",a)]
    add(cat,lang,msgs,g,["multi_turn","context","health"])
    MT_COUNT+=1
print(f"multi_turn scenario records: {MT_COUNT}")

# more authored single-turn: reasoning/decision/uncertainty/social extras via variants_for-style paraphrase
def para(cat,lang,u,a,caps=None):
    out=[]
    if lang=="en":
        if u.startswith("What is") or u.startswith("What are"):
            t=u[7:].rstrip("?")
            out.append((f"Tell me about {t}.",a))
            out.append((f"Can you explain {t}?",a))
        if u.startswith("How do I"):
            out.append((u.replace("How do I","How can I",1),a))
    if lang=="bn" and ("কী" in u or "কি" in u):
        m=re.match(r"(.+?)\s*[কখ]ী\??",u)
        if m:
            t=m.group(1)
            out.append((f"{t} বলতে কী বোঝায়?",a))
    if lang=="banglish":
        m=re.match(r"(.+?)\s+ki\??",u,re.I)
        if m:
            t=m.group(1)
            out.append((f"{t} mane ki?",a))
    return [(cat,lang,v,a,caps) for v,a in [(x[0],x[1]) for x in out]]

for cat,lang,u,a,caps in list(S):
    for item in para(cat,lang,u,a,caps):
        if item[2]!=u: S.append(item)

# ============ 4. PROCEDURAL MATH + LOGIC (verified) ============
def gen_math():
    ops=[("+","plus","যোগ"),("-","minus","বিয়োগ"),("*","times","গুণ"),("/","divided by","ভাগ")]
    for i in range(300):
        a,b=random.randint(2,60),random.randint(2,30)
        op,opw,opbn=random.choice(ops)
        if op=="+": ans=a+b
        elif op=="-": ans=a-b
        elif op=="*": ans=a*b
        else:
            if b==0 or a%b!=0: continue
            ans=a//b
        sym={"+":"+","-":"-","*":"x","/":"/"}[op]
        eq=f"{a} {sym} {b} = {ans}"
        r=i%4
        if r==0: seed("math","en",f"What is {a} {opw} {b}?",eq+".",["math","arithmetic"])
        elif r==1: seed("math","bn",f"{a} {opbn} {b} কত?",eq+"।",["math","arithmetic"])
        elif r==2: seed("math","banglish",f"{a} {opw} {b} koto?",eq+".",["math","arithmetic"])
        else:
            # worked-solution format
            seed("math","en",f"Solve: {a} {opw} {b}",
                 f"{eq}. Step by step: {'+' if op=='+' else '-'}{'multiply' if op=='*' else 'divide' if op=='/' else 'add' if op=='+' else 'subtract'} {a} and {b} gives {ans}.",["math","arithmetic","steps"])
    # fractions / percent simple
    for i in range(80):
        a,b=random.randint(1,12),random.randint(1,12)
        if random.random()<0.5:
            seed("math","en",f"What is {a}/{b} as a percentage?",f"{a}/{b} = {round(a/b*100,1)}%.",["math","fraction","percent"])
        else:
            seed("math","bn",f"{a}/{b} hailed ম百分之?",f"{a}/{b} = {round(a/b*100,1)}%।",["math","fraction","percent"])
    # logic puzzles (verified)
    odd_pool=[("en","Which is different: apple, banana, carrot, grape?","Carrot — it's a vegetable; the others are fruits."),
              ("bn","কোনটা আলাদা: আপেল, কলা, গাজর, আঙুর?","গাজর — এটি সবজি; বাকি গুলো ফল।"),
              ("banglish","Kon ta alada: aapel, kola, gajor, angur?","Gajor — eta shobji; baki gulo fal.")]
    for lang,u,a in odd_pool: seed("logic",lang,u,a,["reasoning","classification"])
    for i in range(60):
        a,b,c=random.sample(range(1,30),3)
        order=sorted([("A",a),("B",b),("C",c)],key=lambda x:x[1])
        seed("math","en",f"A has {a} marbles, B has {b}, C has {c}. Who has the most?",
             f"{'A' if order[-1][0]=='A' else order[-1][0]} has the most with {order[-1][1]} marbles.",["math","comparison"])

gen_math()

# ============ 5. BUILD / VALIDATE / SPLIT ============
for cat,lang,u,a,caps in S:
    lang=detect(u) if lang!="mixed" else lang
    qa(cat,lang,u,a,caps)

ROLE_OK={"user","assistant"}
final=[]; seen_q=set()
for r in recs:
    msgs=r["messages"]; ok=True; reason=""
    if len(msgs)<2: ok=False;reason="too_few_messages"
    elif msgs[0]["role"]!="user" or msgs[-1]["role"]!="assistant": ok=False;reason="bad_roles"
    elif any(m["role"] not in ROLE_OK for m in msgs): ok=False;reason="bad_role_value"
    elif any(not m["content"].strip() for m in msgs): ok=False;reason="empty_content"
    elif msgs[-1]["content"].strip().lower()==msgs[0]["content"].strip().lower():
        ok=False;reason="answer_equals_question"
    q=msgs[0]["content"].strip().lower()
    if q in seen_q: ok=False;reason="dup_question"
    seen_q.add(q)
    if ok: final.append(r)
    else:
        r2=dict(r);r2["reject_reason"]=reason;QUAR.append(r2)

norm=lambda s:re.sub(r'\W+','',s.lower())[:80]
pref=defaultdict(int)
for r in final: pref[norm(r["messages"][0]["content"])]+=1
dups={k for k,v in pref.items() if v>3}
final2=[]
for r in final:
    if norm(r["messages"][0]["content"]) in dups:
        r2=dict(r);r2["reject_reason"]="near_duplicate_prefix";QUAR.append(r2)
    else: final2.append(r)
final=final2

groups=defaultdict(list)
for r in final: groups[r["split_group"]].append(r)
gkeys=sorted(groups,key=lambda g:h(g))
ng=len(gkeys); nv=max(1,ng//20); nt=max(1,ng//20)
test_g=set(gkeys[:nt]); val_g=set(gkeys[nt:nt+nv])
train=[r for g in gkeys[nt+nv:] for r in groups[g]]
val=[r for g in gkeys[nt:nt+nv] for r in groups[g]]
test=[r for g in gkeys[:nt] for r in groups[g]]

for nm,rows in (("train",train),("validation",val),("test",test)):
    with open(os.path.join(OUT,f"{nm}.jsonl"),"w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")
with open(os.path.join(OUT,"rejected_records.jsonl"),"w",encoding="utf-8") as f:
    for r in QUAR: f.write(json.dumps(r,ensure_ascii=False)+"\n")

def stats(rows):
    langs=Counter(r["lang"] for r in rows); cats=Counter(r["category"] for r in rows)
    turns=[len(r["messages"])//2 for r in rows]
    return {"n":len(rows),"lang":dict(langs),"category":dict(cats),
            "avg_turns":round(sum(turns)/max(len(turns),1),2),
            "multi_turn":sum(1 for t in turns if t>1)}
st={k:stats(v) for k,v in (("train",train),("validation",val),("test",test))}
manifest={
 "version":"unified_conversational_v2","seed":SEED,
 "total_records":len(final),"rejected":len(QUAR),
 "v1_carryover":v1_count,
 "splits":{"train":len(train),"validation":len(val),"test":len(test)},
 "groups":{"total":ng,"test_groups":nt,"val_groups":nv},
 "statistics":st,
 "schema":"messages:[{role,content}] + capabilities[] — compatible with ChatSFTDataset",
 "note":"v1 carryover + authored multi-turn scenarios + reasoning/decision/"
        "self-correction/clarification + procedural math/logic. No external AI.",
}
json.dump(manifest,open(os.path.join(OUT,"dataset_manifest.json"),"w"),indent=1)
json.dump({"seed":SEED,"method":"sha256(split_group) ordering","groups":ng,
           "test_groups":nt,"val_groups":nv,
           "note":"conversation/scenario-group atomic; v1 records re-grouped"},
          open(os.path.join(OUT,"split_manifest.json"),"w"),indent=1)
json.dump({"approved":len(final),"rejected":len(QUAR),
           "reject_reasons":dict(Counter(r.get("reject_reason","?") for r in QUAR))},
          open(os.path.join(OUT,"quality_report.json"),"w"),indent=1)
lines=[]
for nm in ("train.jsonl","validation.jsonl","test.jsonl","dataset_manifest.json",
           "split_manifest.json","quality_report.json","rejected_records.jsonl"):
    p=os.path.join(OUT,nm)
    lines.append(f"{hashlib.sha256(open(p,'rb').read()).hexdigest()}  {nm}")
open(os.path.join(OUT,"checksums.sha256"),"w").write("\n".join(lines)+"\n")
print(f"unified_conversational v2: {len(final)} approved, {len(QUAR)} rejected")
print("train",len(train),"val",len(val),"test",len(test))
print("langs:",st["train"]["lang"])
print("cats:",st["train"]["category"])
