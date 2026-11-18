"""Build unified trilingual conversational SFT dataset v3.

v3 = v2 carryover (1054, re-grouped) + major expansion:
- multi-turn scenario engine (template families x slot variants x 3 langs)
- large authored bn/en/banglish conversational banks
- reasoning/decision/uncertainty/self-correction/knowledge/math
NO external AI. Output: data/unified_conversational/v3/
"""
import json, os, random, hashlib, re, unicodedata
from collections import Counter, defaultdict

SEED = 42
random.seed(SEED)
BASE = os.path.join(os.path.dirname(__file__), "unified_conversational")
OUT = os.path.join(BASE, "v3")
os.makedirs(OUT, exist_ok=True)
V2 = os.path.join(BASE, "v2")

recs, QUAR = [], []
BN = re.compile(r'[ঀ-৿]')
BG = re.compile(r'\b(ki|koto|ache|nei|bolun|dao|kivabe|keno|korbo|lagbe|bhalo|khub|bhai|vai|hocche|gechi|chai|kore|nitam|toiri|bolchi|dekhchi|jacchi|ashchi|parbo|lagbe|dorkar|sahajjo)\b', re.I)

def h(s): return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)
def detect(u):
    if BN.search(u): return "bn"
    if BG.search(u): return "banglish"
    if re.search(r'[a-zA-Z]', u): return "en"
    return "bn"

def add(cat, lang, messages, group, caps=None, source="authored", review="approved"):
    rid = f"v3:{cat}:{lang}:{len(recs)}"
    recs.append({"sample_id": rid, "id": rid, "lang": lang,
        "category": cat, "task": cat, "capabilities": caps or [],
        "difficulty": "medium",
        "conversation_id": group,
        "messages": [{"role": r, "content": c} for r, c in messages],
        "split_group": group,
        "provenance": {"builder": "build_unified_conv_v3.py", "seed": SEED,
                       "source": source},
        "quality": {"status": review, "review_method": "rule_based"}})

def qa(cat, lang, u, a, caps=None):
    add(cat, lang, [("user",u),("assistant",a)], f"g{h(u+a)%300000}", caps)

# ============ 1. V2 CARRYOVER ============
v2_count=0
for split in ("train","validation","test"):
    p=os.path.join(V2,f"{split}.jsonl")
    for line in open(p,encoding="utf-8"):
        r=json.loads(line)
        r["split_group"]=r.get("split_group") or f"v2{h(r['sample_id'])%50000}"
        r.setdefault("capabilities",[])
        r["provenance"]={**r.get("provenance",{}),"source":"v2_carryover"}
        recs.append(r); v2_count+=1
print(f"v2 carryover: {v2_count}")

S=[]
def seed(cat,lang,u,a,caps=None): S.append((cat,lang,u,a,caps))

# ============ 2. MULTI-TURN SCENARIO ENGINE ============
# Families: (topic, {lang: [turns]}) — each turn (user,assistant), context-dependent.
MT_FAMILIES={
"study_plan":{
 "en":[("I want to improve my English.","Great goal! How much time can you study each day?"),
       ("About 30 minutes.","30 minutes daily is enough for steady progress. Do you prefer reading, watching videos, or practicing conversations?"),
       ("Conversations mostly.","Then let's practice! Tell me about your daily routine in English — just a few sentences."),
       ("I wake up early and drink tea.","Good start! Let's build on it: 'I wake up early, drink tea, and then I go to work.' Now you try adding one more detail.")],
 "bn":[("আমি আমার English improve করতে চাই।","দারুণ লক্ষ্য! দিনে কতক্ষণ পড়তে পারবেন?"),
       ("প্রায় ৩০ মিনিট।","প্রতিদিন ৩০ মিনিট steady progress-এর জন্য যথেষ্ট। পড়া, ভিডিও দেখা নাকি কথা বলা — কোনটা পছন্দ?"),
       ("Mostly কথা বলা।","তাহলে practice করি! English-এ আপনার দৈনন্দিন রুটিনের কথা বলুন — কয়েকটি বাক্য।"),
       ("আমি সকালে ঘুম থেকে risen-up করি আর চা খাই।","ভালো শুরু! এবার যোগ করুন: 'I wake up early, drink tea, and then I go to work.' এখন আপনি আরেকটি detail যোগ করে বলুন।")],
 "banglish":[("Ami amar English improve korte chai.","Darun goal! Dine koto somoy porte parben?"),
       ("Proy 30 minute.","Proti din 30 minute steady progress er jonno thik ache. Porha, video dekhha naki kotha bola — konta peshob?"),
       ("Mostly kotha bola.","Tahole practice kori! English e apnar daily routine er kotha bolun — koyekti baksho."),
       ("Ami sokale ghum theke uthi ar cha khai.","Bhalo start! Ebar jog korun: 'I wake up early, drink tea, and then I go to work.' Ekhon apni aro ekta detail jog kore bolun.")]},
"tech_support":{
 "en":[("My laptop is running very slow.","Let's troubleshoot. First — how much RAM does it have, and how many programs do you usually keep open?"),
       ("8GB RAM, maybe 10-15 tabs.","15 browser tabs can easily use most of your RAM. Try closing tabs you don't need, and restart the laptop once."),
       ("I restarted and it's better but still slow.","Check startup programs — press Ctrl+Shift+Esc, look at the Startup tab, and disable apps you don't need at boot."),
       ("That helped a lot. What if it slows down again?","If it happens again, check for updates and scan for viruses. Persistent slowness might mean the drive is aging — back up important files regularly.")],
 "bn":[("আমার laptop খুব slow চলছে।","চলুন troubleshoot করি। প্রথমে — RAM কত, আর সাধারণত কতগুলো program খোলা থাকে?"),
       ("8GB RAM, হয়তো ১০-১৫টা tab।","১৫টা browser tab RAM-এর বেশিরভাগ ব্যবহার করতে পারে। দরকার নেই এমন tab বন্ধ করুন, আর একবার laptop restart করুন।"),
       ("Restart-এর পর ভালো, তবু slow।","Startup program দেখুন — Ctrl+Shift+Esc চেপে Startup tab-এ boot-এ দরকার নেই এমন app বন্ধ করুন।"),
       ("অনেক সাহায্য হলো। আবার slow হলে?","আবার হলে update check করুন আর virus scan করুন। বারবার slow হলে drive পুরনো হতে পারে — গুরুত্বপূর্ণ file নিয়মিত backup নিন।")],
 "banglish":[("Amar laptop khub slow cholche.","Chalun troubleshoot kori. Prothome — RAM koto, ar shadharonoto koto gulo program khola thake?"),
       ("8GB RAM, hoyto 10-15 ta tab.","15 ta browser tab RAM er beshirag use korte pare. Dorkar nei emon tab bondho korun, ar ekbar laptop restart korun."),
       ("Restart er por bhalo, toubu slow.","Startup program dekho — Ctrl+Shift+Esc chapo, Startup tab e boot e dorkar nei emon app bondho korun."),
       ("Onek sahajjo holo. Abar slow hole?","Abar hole update check korun ar virus scan korun. Bar bar slow hole drive purono hote pare — important file niyomito backup nin.")]},
"money_management":{
 "en":[("I want to save money but I always end up spending it.","That's very common. Do you know roughly how much you spend each month and on what?"),
       ("Not really, maybe food and transport mostly.","Then let's track for one week — write down every taka you spend. Awareness alone usually cuts 10-20% of spending."),
       ("Okay, I'll try. Should I use a separate account?","A separate savings account helps — move a fixed amount there on payday before you can spend it. Even 500 taka monthly builds a habit."),
       ("Good idea. What if I need money urgently?","Keep a small emergency fund separate — aim for 1-2 months of essential expenses. For urgent needs, use it; for wants, wait.")],
 "bn":[("টাকা বাঁচাতে চাই কিন্তু সবসময় খরচ হয়ে যায়।","এটা খুব common। মাসে মোটামুটি কত খরচ করেন আর কীসে — জানেন?"),
       ("ঠিক জানি না, mostly food আর transport।","তাহলে এক সপ্তাহ track করুন — প্রতিটা টাকা কোথায় গেলেন লিখে রাখুন। শুধু awareness-ই ১০-২০% খরচ কমায়।"),
       ("ঠিক আছে, করি। আলাদা account ব্যবহার করব?","আলাদা savings account সাহায্য করে — payday-তেই আগে fixed amount  সরিয়ে নিন। মাসে ৫০০ টাকা হলেও habit তৈরি হয়।"),
       ("ভালো idea। জরুরি প্রয়োজনে?","Alada emergency fund রাখুন — ১-২ মাসের essential খরচ। জরুরি প্রয়োজনে সেটা ব্যবহার করুন, ইচ্ছায় নয়।")],
 "banglish":[("Taka bachaite chai kintu shobshomoy khoroch hoye jay.","Eta khub common. Mashe motamuti koto khoroch korun ar kise — janen?"),
       ("Thik janbo na, mostly food ar transport.","Tahole ek soptaho track korun — proti ta taka kothay gechhe likhe rakhun. Sudhu awareness-i 10-20% khoroch komay."),
       ("Thik ache, kori. Alada account use korbo?","Alada savings account sahajjo kore — payday te age fixed amount okhane sorie nin. Mashe 500 taka holeo habit toiri hoy."),
       ("Bhalo idea. Joruri proyojone?","Alada emergency fund rakhun — 1-2 masher essential khoroch. Joruri proyojone sheta use korun, ichchhay na.")]},
"exam_prep":{
 "en":[("My exam is in 10 days. How should I study?","With 10 days, prioritize high-weightage topics first, then revise daily. Don't try to cover everything — focus on what carries marks."),
       ("Which subjects should I start with?","Start with the subjects you find hardest — they need the most time. Do 2-3 hours of focused study, then a 15-minute break."),
       ("How do I remember what I study?","Active recall beats re-reading: close the book and write what you remember, then check. Practice past papers under timed conditions."),
       ("What about the night before?","Light revision only — key formulas and summary notes. Sleep 7-8 hours; a tired brain forgets more than it retains.")],
 "bn":[("১০ দিন পর পরীক্ষা। কীভাবে পড়ব?","১০ দিনে বেশি নম্বরের topic আগে priority দিন, তারপর প্রতিদিন revise করুন। সব topics cover করার চেষ্টা না করে যেটায় নম্বর বেশি তাতে focus করুন।"),
       ("কোন বিষয়ে শুরু করব?","যে বিষয়ে সবচেয়ে কষ্ট হয় সেখান থেকে শুরু করুন — সবচেয়ে বেশি সময় লাগে। ২-৩ ঘণ্টা focused পড়া, তারপর ১৫ মিনিটের break।"),
       ("যা পড়ি তা কীভাবে মনে রাখব?","Active recall re-reading-এর চেয়ে ভালো: বই বন্ধ করে যা মনে আছে লিখুন, তারপর check করুন। Timedভাবে আগের প্রশ্নপত্র practice করুন।"),
       ("পরের রাতের আগে?","শুধু হালকা revision — মূল সূত্র ও summary notes। ৭-৮ ঘণ্টা ঘুমান; ক্লান্ত brain বেশি ভুলে যায়।")],
 "banglish":[("Amar exam 10 din por. Kivabe porbo?","10 dine beshi mark er topic age priority din, tarpor proti din revise korun. Sob topic cover korar try na kore jeita te mark beshi seta te focus korun."),
       ("Kon bishoye shuru korbo?","Je bishoye shobcheye koshto hoy sekhane theke shuru korun — shobcheye beshi somoy lage. 2-3 ghonta focused pora, tarpor 15 minute er break."),
       ("Ja pori ta kivabe mone rakhbo?","Active recall re-reading er cheye valo: boi bondho kore ja mone ache likhun, tarpor check korun. Timed bhabe ager proshnopatro practice korun."),
       ("Porer rat er age?","Shudhu halka revision — mul sutro ar summary notes. 7-8 ghonta ghumun; klanto brain beshi bhule jay.")]},
"cooking":{
 "en":[("I want to cook biryani for guests. Where do I start?","Start with marinating the meat — at least 30 minutes, ideally overnight. Then prepare the rice separately while making the masala."),
       ("How do I get fluffy rice?","Soak rice 20-30 minutes, then cook until 70% done (grains still firm). Drain completely — excess water makes it mushy."),
       ("How do I layer it?","In a heavy pot: rice, then masala, then fried onions and mint, repeat. Seal tightly and cook on low heat 20-25 minutes ('dum')."),
       ("How do I know it's done?","The aroma will tell you — when you smell the spices through the lid, it's ready. Let it rest 10 minutes before serving.")],
 "bn":[("অতিথির জন্য biryani রান্না করতে চাই। কোথা থেকে শুরু?","মাংস marinate করে শুরু করুন — কমপক্ষে ৩০ মিনিট,最好 overnight। তারপর masala বানানোর সময় আলাদা করে rice প্রস্তুত করুন।"),
       ("Fluffy rice কীভাবে পাব?","Rice ২০-৩০ মিনিট ভিজিয়ে নিন, তারপর ৭০% সেদ্ধ করুন (দানা এখনো শক্ত)। পুরোপুরি water ঝরিয়ে নিন — extra water এ clumpy হয়।"),
       ("Layer কীভাবে দেব?","ভারী পাত্রে: rice, তারপর masala, তারপর fried onion ও পুদিনা — repeat করুন। ভালো করে seal করে low flame-এ ২০-২৫ মিনিট ('dum') রাঁধুন।"),
       ("Done বুঝব কীভাবে?","গন্ধ জানিয়ে দেবে — lid-এর মধ্য দিয়ে মসলার smell এলে তৈরি। ১০ মিনিট(rest) রেখে তারপর serve করুন।")],
 "banglish":[("Ami guest der jonno biryani ranna korte chai. Kotha theke shuru?","Mangsho marinate kore shuru korun — kompokkhe 30 minute, best overnight. Tarpor masala bananor somoy alada kore rice toiri korun."),
       ("Fluffy rice kivabe pabo?","Rice 20-30 minute bhijie nin, tarpor 70% sedho korun (dana ekhono shokto). Purapuri water jhore nin — extra water e clumpy hoy."),
       ("Layer kivabe dibo?","Bhari patray: rice, tarpor masala, tarpor fried onion ar pudina — repeat korun. Bhalo kore seal kore low flame e 20-25 minute ('dum') randhun."),
       ("Done bojhbo kivabe?","Gondh janie debe — lid er moddhe theke moshlar smell ashle toiri. 10 minute rest rekhe tarpor serve korun.")]},
"language_learning":{
 "en":[("I'm learning Bengali. What's the best way to start?","Start with greetings and common phrases — 'nomoshkar', 'kemon acho', 'dhonnobad'. Practice saying them daily until they're automatic."),
       ("How do I learn vocabulary faster?","Learn words in context, not lists — attach each new word to a sentence you might actually use. Review with spaced repetition."),
       ("How do I practice speaking without a partner?","Talk to yourself in Bengali during daily tasks — describe what you're doing. Record yourself and compare pronunciation later."),
       ("How long until I'm conversational?","With 30 minutes daily, expect basic conversation in 3-6 months. Consistency matters more than intensity — don't skip days.")],
 "bn":[("আমি বাংলা শিখছি। সেরা উপায় কী?","শুভেচ্ছা ও সাধারণ phrase দিয়ে শুরু করুন — 'নমস্কার', 'কেমন আছো', 'ধন্যবাদ'। প্রতিদিন বলুন যতক্ষণ automatic না হয়।"),
       ("Vocabulary দ্রুত শিখব কীভাবে?","List না করে context-এ শিখুন — প্রতিটি নতুন শব্দ এমন বাক্যে ব্যবহার করুন যা সত্যিই বলবেন। Spaced repetition দিয়ে revise করুন।"),
       ("সঙ্গী ছাড়া বলার practice কীভাবে?","দৈনন্দিন কাজে নিজে নিজে বাংলায় কথা বলুন — যা করছেন তা বর্ণনা করুন। পরে pronunciation compare করতে record করুন।"),
       ("কখন conversational হব?","প্রতিদিন ৩০ মিনিটে ৩-৬ মাসে basic conversation। Consistency intensity-র চেয়ে জরুরি — দিন skip করবেন না।")],
 "banglish":[("Ami Bangla shikhchi. Sesta upay ki?","Shobhasha ar general phrase diye shuru korun — 'nomoshkar', 'kemon acho', 'dhonnobad'. Proti din bolun jokhon porjonto automatic na hoy."),
       ("Vocabulary druto shikhbo kivabe?","List na kore context e shikhen — proti ta notun shobdo emon baksho te use korun ja tumi asole bolben. Spaced repetition diye revise korun."),
       ("Sangi chara bola practice kivabe?","Daily kaaje nije nije Banglay kotha bolun — ja korchen ta bornona korun. Por e pronunciation compare korte record korun."),
       ("Kobe conversational hobo?","Proti din 30 minute e 3-6 mash e basic conversation. Consistency intensity er cheye joruri — din skip korben na.")]},
"travel_bangladesh":{
 "en":[("I'm traveling to Sylhet next week.","Sylhet is beautiful — tea gardens and wildlife. Are you traveling alone or with family?"),
       ("With my wife and two kids.","Family trip! Book accommodation near Jaflong or Ali Amjang for easy access to attractions. December-February is ideal weather."),
       ("What places should we visit?","Jaflong for river rocks, Lawachara National Park for hiking, Ratargul swamp for boating, and Bisnakandi for waterfalls."),
       ("Any food recommendations?","Try the local 'shatkora' curry, beef polao (if you eat beef), and fresh oranges from local orchards — Sylhet is famous for citrus.")],
 "bn":[("আগামী সপ্তাহে সিলেটে যাচ্ছি।","সিলেট সুন্দর — চা বাগান ও বন্যপ্রাণী। একা যাচ্ছেন নাকি পরিবারের সাথে?"),
       ("স্ত্রী ও দুই সন্তান নিয়ে।","Family trip! জাফলং বা আলীআমজং-এর কাছে থাকা বুক করুন — attraction-এ যাওয়া সহজ। ডিসেম্বর-ফেব্রুয়ারি সেরা সময়।"),
       ("কোন জায়গা দেখব?","জাফলং river rock-এর জন্য, লাওয়াছাড়া national park হাইকিং, র gaurgul pedal boat, আর বিসনাকান্দি waterfall।"),
       ("কী খাবার খাব?","Local 'shatkora' curry, beef polao (beef খেলে), আর local orchard-এর তাজা কমলা — সিলেট citrus-এর জন্য বিখ্যাত।")],
 "banglish":[("Ami next soptaho Sylhete jacchi.","Sylhet sundor — cha bagan ar bonno-prani. Ekla jaccho naki poribar shoho?"),
       ("Stri ar dui shontan niye.","Family trip! Jaflong ba Ali Amjang er kachhe thaka book korun — attraction e jawa shohoj. December-February sesh somoy."),
       ("Kon jayga dekhbo?","Jaflong river rock er jonno, Lawachara national park hiking, Ratargul pedal boat, ar Bisnakandi waterfall er jonno."),
       ("Ki khabar khabo?","Local 'shatkora' curry, beef polao (beef khele), ar local orchard er torja komola — Sylhet citrus er jonno bikhyato.")]},
"event_planning":{
 "en":[("I'm organizing my sister's wedding. Where do I start?","Start with the date and venue — those determine everything else. Then guest list, catering, decoration, and photography."),
       ("We have about 200 guests.","200 guests need careful budgeting — catering alone can be 40-50% of costs. Get quotes from 3-4 caterers and compare menus."),
       ("How do I manage the budget?","Break it into categories: venue 30%, catering 40%, decoration 15%, photography 10%, misc 5%. Track every expense against this."),
       ("What about the day itself?","Make a timeline: guest arrival, ceremony, photos, reception, dinner. Assign a coordinator for each segment so nothing overlaps.")],
 "bn":[("আমার বোনের বিয়ের আয়োজন করছি। কোথা থেকে শুরু?","তারিখ ও venue দিয়ে শুরু করুন — সেগুলোই সব নির্ধারণ করে। তারপর guest list, catering, decoration, photography।"),
       ("প্রায় ২০০ অতিথি।","২০০ অতিথিতে careful budgeting দরকার — catering একাই খরচের ৪০-৫০% হতে পারে। ৩-৪ caterer-এর quote নিয়ে compare করুন।"),
       ("বাজেট কীভাবে manage করব?","Category-তে ভাগ করুন: venue ৩০%, catering ৪০%, decoration ১৫%, photography ১০%, misc ৫%। প্রতিটি খরচেরagainst-track করুন।"),
       ("দিনটা কীভাবে?","Timeline তৈরি করুন: guest আগমন, ceremony, ছবি, reception, রাতের খাবার। প্রতিটি segment-এ coordinator ঠিক করুন যাতে overlap না হয়।")],
 "banglish":[("Ami amar bon er biye arojon korchi.","Tarikh ar venue diye shuru korun — segulo-i shob nirdharon kore. Tarpor guest list, catering, decoration, photography."),
       ("Proy 200 atithi.","200 atithite careful budgeting dorkar — catering ekai khoroch er 40-50% hote pare. 3-4 caterer er quote niye compare korun."),
       ("Budget kivabe manage korbo?","Category te bhag korun: venue 30%, catering 40%, decoration 15%, photography 10%, misc 5%. Proti ta khoroch er against track korun."),
       ("Dintar kaaj kivabe?","Timeline toiri korun: guest agomon, ceremony, chobi, reception, rater khabar. Proti ta segment e coordinator thik korun jate overlap na hoy.")]},
}

# expand families via slot variants: substitute key nouns deterministically
SLOT_SETS={
 "trip_place":["Cox's Bazar","Sylhet","Chittagong","Rajshahi","Kuakata"],
 "budget_num":["500","1000","2000","5000"],
 "time_unit":["30 minutes","1 hour","2 hours"],
 "item":["laptop","phone","book","bag"],
}
def mt_variants():
    V=[]
    # generate extra multi-turns by composing greeting+scenario opening+followup
    for fam,langs in MT_FAMILIES.items():
        for lang,turns in langs.items():
            msgs=[]
            for u,a in turns: msgs+=[("user",u),("assistant",a)]
            add("multi_turn",lang,msgs,f"m3_{fam}_{lang}",["multi_turn","context"],source="authored_scenario")
            # variant: prepend a greeting turn (context start)
            G={"en":("Hi!","Hi! How can I help?"),"bn":("হ্যালো!","হ্যালো! কীভাবে সাহায্য করব?"),
               "banglish":("Hey!","Hey! Ki bhabe help korte pari?")}[lang]
            msgs2=[("user",G[0]),("assistant",G[1])]+msgs
            add("multi_turn",lang,msgs2,f"m3g_{fam}_{lang}",["multi_turn","context","greeting"],source="authored_scenario_variant")
    return V
mt_variants()

# ============ 3. AUTHOR BN SINGLE-TURN BANK ============
BN_BANK=[
("আজ আবহাওয়া কেমন?","আমি real-time আবহাওয়া জানি না। আপনার当地的 forecast app বা news check করুন।"),
("ডাক্তার দেখাব কবে?","জ্বর ৩ দিনের বেশি থাকলে, তীব্র ব্যথা হলে, বা শ্বাসকষ্ট হলে doctor দেখান। হালকা উপসর্গে বিশ্রাম ও fluid নিন।"),
("ভালো SEO কী?","SEO হলো website-কে search engine-এ উপরে আনতে content, structure ও technical optimization-এর কাজ।"),
("মোটরসাইকেল চালাতে কী লাগে?","Valid driving license, registration, insurance, এবং 안전驾驶 awareness।"),
("চাকরিInterview এর পর follow-up ইমেল কীভাবে লিখব?","সventy দিন ভেতর লিখুন: কৃতজ্ঞতা, আগ্রহ পুনর্ব্যক্তি, আর availability জানিয়ে।"),
("পড়াশোনায় backed up feel?","Small breaks নিন, realistic target রাখুন, আর progress-কে celebrate করুন — burnout কমবে।"),
("মেয়েদের/event venue?","Budget, guest সংখ্যা, location accessibility আর catering quality compare করে বেছে নিন।"),
("Rustmud kena কী হবে?","Rust mud দেখলে dental checkup করুন; fluoride toothpaste ব্যবহার করুন আর sugar কমান।"),
("মোবাইলের battery drain?","Screen brightness কমান, background app বন্ধ করুন, আর battery saver mode ব্যবহার করুন।"),
("বাংলাদেশের நடந்த Conference?","আমি বর্তমান খবর জানি না — আমার training data-র cutoff আছে।"),
("বাংলা ব্যাকরণ শিখতে চাই।","শুরু করুন/basic sentence structure দিয়ে: subject-verb-object। প্রতিদিন ১০টি sentence লিখে practice করুন।"),
("নিয়মিত ব্যায়াম কীভাবে শুরু?","প্রতিদিন ২০-৩০ মিনিট হাঁটা দিয়ে শুরু করুন; তারপর gradually intensity বাড়ান। Consistency intensity-র চেয়ে জরুরি।"),
("সাপ্তাহিক Menu কীভাবে_balance করব?","সঠিক balance করুন: protein, সবজি, complex carb আর healthy fat। ছোট ছোট changes দিন।"),
("Bank account খুলতে কী লাগে?","Valid NID, passport-size ছবি, address proof, আর initial deposit। স determinarে ১-২ দিন লাগে।"),
("Laptop এ password ভুলে গেছি।","Account recovery option ব্যবহার করুন; না থাকলে authorized service center-এ যান — data backup থাকলে আগে নিন।"),
("ঘরে workout করতে পারি?","হ্যাঁ — simple workout: jumping jack, squat, push-up — daily ১৫ মিনিট যথেষ্ট।"),
("Password Manage?","Long, unique password ব্যবহার করুন প্রতি site-এ; password manager ব্যবহার করলে মনে রাখার চাপ কমে।"),
("ভিসা apply?","Official government portal-এ apply করুন;.required documents ready রাখুন আর fee সঠিক পরিমাণে দিন।"),
("InternationalCall?","Internet-based app (WhatsApp, Skype) ব্যবহার করুন — traditional call-এর চেয়ে সস্তা।"),
("ডাক্তার suggestion?","আমি medical advice দিতে পারি না — symptom বর্ণনা করে qualified doctor দেখান। Emergency হলে hospital-এ যান।"),
]
for u,a in BN_BANK:
    if "কী" in u or "কি" in u or "কবে" in u or "কীভাবে" in u:
        seed("qa","bn",u,a,["qa","bengali"])

# ============ 4. AUTHOR EN/BANGLISH REASONING+DECISION BANK ============
EN_BANK=[
("What's the difference between 'affect' and 'effect'?","'Affect' is usually a verb (to influence); 'effect' is usually a noun (a result). Example: 'The rain affected the match' vs 'The effect was a cancelled game.'"),
("Explain the difference between 'their', 'there', and 'they're'.","'Their' shows possession (their book), 'there' indicates place (over there), 'they're' is 'they are' (they're coming)."),
("Is it 'who' or 'whom'?","Use 'who' for subjects (who called?) and 'whom' for objects (whom did you call?). In casual speech 'who' is often accepted for both."),
("What's the difference between 'say' and 'tell'?","'Say' doesn't need a person object (he said hello); 'tell' needs one (he told me hello)."),
("Explain 'fewer' vs 'less'.","'Fewer' for countable items (fewer apples); 'less' for uncountable (less water)."),
("What's the difference between 'historic' and 'historical'?","'Historic' means important in history (a historic event); 'historical' means related to history (historical documents)."),
("'Principal' vs 'principle'?","'Principal' = main person or most important (school principal, principal reason); 'principle' = a rule or belief."),
("'Compliment' vs 'complement'?","'Compliment' = praise; 'complement' = something that completes or goes well with."),
("When should I use 'who' vs 'that'?","'Who' for people (the man who called); 'that' for things or animals (the dog that barked)."),
("'Its' vs 'it's'?","'Its' shows possession (the dog wagged its tail); 'it's' = 'it is' (it's raining)."),
("How do I write a professional resignation letter?","Include: your position, notice period, gratitude for the opportunity, and offer to help with transition. Keep it under one page and positive."),
("What's a good structure for a business email?","Subject line, greeting, purpose in first paragraph, supporting details, clear request/action, polite closing with your name."),
("How do I prepare for a presentation?","Know your audience, structure as intro-body-conclusion, practice aloud 3 times, prepare for likely questions, and test your slides beforehand."),
("What is critical thinking?","Evaluating information objectively — examining evidence, identifying assumptions, considering alternatives, and reaching reasoned conclusions rather than accepting claims at face value."),
("What's the difference between correlation and causation?","Correlation means two things change together; causation means one causes the other. Ice cream sales and drowning both rise in summer — correlation, not causation."),
("Explain 'sunk cost fallacy'.","Continuing an investment because of what you've already spent, even when it's no longer the best choice. The rational approach is to decide based on future costs and benefits only."),
("What's 'confirmation bias'?","The tendency to seek, interpret, and remember information that confirms existing beliefs while ignoring contradictory evidence."),
("What's a 'logical fallacy'?","An error in reasoning that makes an argument invalid — like ad hominem (attacking the person) or hasty generalization (one example to a rule)."),
("How do I make better decisions?","Define the problem clearly, gather relevant info, list options, weigh pros/cons against your priorities, decide, then review the outcome later."),
("What's 'opportunity cost'?","What you give up when choosing one option over another — the next best alternative's value."),
("Explain 'risk' vs 'uncertainty'.","Risk has known probabilities (rolling a die); uncertainty doesn't (tomorrow's weather). Decisions under risk use probabilities; under uncertainty require judgment."),
("What's a 'feedback loop'?","A process where output becomes input — positive loops amplify (viral content), negative loops stabilize (thermostat)."),
("Explain 'network effects'.","A product becomes more valuable as more people use it — like a phone network or social platform."),
("What's 'first-mover advantage'?","Being first in a market can bring advantages (brand recognition, learning) but also risks (unproven demand, mistakes others learn from)."),
("Explain 'diminishing returns'.","The phenomenon where each additional unit of input produces less output — like adding more workers to a small task."),
("What's 'survivorship bias'?","Focusing only on successes while ignoring failures — like studying only billionaires and missing the thousands who failed."),
("Explain 'anchoring bias'.","Over-relying on the first piece of information when making decisions — like a high 'original price' making a sale price seem better."),
("What's 'supply and demand'?","The economic model where prices are determined by how much is available (supply) vs how much people want (demand)."),
("Explain 'inflation' simply.","The general rise in prices over time, reducing money's purchasing power — 100 taka today buys less than 100 taka last year."),
("What's 'GDP'?","Gross Domestic Product — the total value of goods and services produced in a country in a period. It's a rough measure of economic size, not wellbeing."),
("Explain 'supply chain'.","The network from raw materials to finished product reaching customers — disruption anywhere (like a factory closure) affects the whole chain."),
("What's 'cryptocurrency' simply?","Digital money secured by cryptography, operating on decentralized networks — like Bitcoin. Volatile and not backed by governments."),
("What's 'cloud computing'?","Using internet servers for storage, computing, and services instead of local machines — like renting computing power by the hour."),
("Explain 'machine learning' vs 'AI'.","AI is the broad goal of machines doing intelligent tasks; machine learning is a method where systems learn patterns from data rather than explicit programming."),
("What's 'blockchain' simply?","A distributed digital ledger where transactions are recorded in linked blocks — hard to alter, used for cryptocurrencies and verification."),
("Explain 'open source'.","Software whose code is publicly available for anyone to use, modify, and share — promotes collaboration and transparency."),
("What's 'digital footprint'?","The trail of data you leave online — posts, searches, purchases. It can affect privacy, reputation, and job prospects."),
("Explain 'phishing'.","Fake emails/messages pretending to be legitimate organizations to steal passwords or financial info. Check sender addresses and never click suspicious links."),
("What's a 'strong password'?","Long (12+ characters), unique per account, mixing letters, numbers, and symbols — or better, a passphrase of random words."),
("Explain 'two-factor authentication'.","A second verification step beyond password — like a code sent to your phone. It makes account theft much harder even if your password leaks."),
("What's 'malware'?","Malicious software — viruses, ransomware, spyware — that harms devices or steals data. Protection: updated software, antivirus, careful downloads."),
("Explain 'backup'.","A copy of your data stored separately — so you can restore if the original is lost, damaged, or stolen. Follow the 3-2-1 rule: 3 copies, 2 media types, 1 offsite."),
]
for u,a in EN_BANK: seed("knowledge","en",u,a,["knowledge","explanation"])

# ============ 5. BANGLISH BANK ============
BG_BANK=[
("Computer slow hoye geche, ki korbo?","Age Task Manager check koro — kon app beshi CPU ba RAM kheyeche dekho. Tarpor unnecessary startup app bondho koro."),
("Password bhule gechi, ki korbo?","Account er 'forgot password' option use koro. Na thakle registered email ba phone diye recovery koro."),
("WhatsApp e photo pathate parchi na.","Photo er size komano lagbe, ba Google Drive-e upload kore link pathao. Check koro storage ache kina."),
("WiFi connect hocche na.","Router restart koro age, tarpor phone/network settings check koro. Ekhono na hole router-er password thik ache kina dekho."),
("Mobile er storage full.","Unused app delete koro, photo Google Photos-e backup koro, ar download folder clean koro. Settings e storage analyze koro."),
("Email pathate pari na.","Internet connection check koro, spam folder dekho, ar sender address thik ache kina verify koro."),
("YouTube video load hocche na.","Internet speed slow hole video buffer hobe. WiFi change koro ba mobile data use koro. App update koro."),
("Facebook e login hocche na.","Password thik ache kina check koro, 'forgot password' try koro, ar 2-factor authentication off thakle on koro."),
("Printer kaj korchhe na.","Printer on ache kina, cable connected kina, ar driver install ache kina check koro. Restart printer + computer try koro."),
("Ami English bolte pari na kintu bojhai.","Eta common — speaking practice lagbe. Shuru koro short sentence diye: 'ami ___ kori'. Dine 10 minute bolun."),
("Exam e common mistake gulo ki?","Time manage kora, question miss kora, ar answer-er last part check na kora — ei gulo common. Time-table practice koro."),
("Reading comprehension e vul korchi.","Prothome question-ta puro porun, tarpor passage-e relevant line khujun. Answer passage-er bhitor thaka dorkar — outside knowledge na."),
("Math e vul korchi calculation e.","Har step-e slow likhun, then abar check korun. Rough calculation diye answer er age estimate korun — onek vul dhora porbe."),
("Interview te nervous hochi.","Eta normal. Age common question-er answer practice korun, tarpor shanti ronun. Interview-ke conversation dhoro — tumi-o tader judge korcho."),
("Study korle o mone thake na.","Passive pora na kore active recall koro — boi bondho kore ja mone ache likh. Spaced repetition best way."),
("Time manage korte pari na.","Proti din shuru te 3-ta important kaj list koro. Time-blocking koro — specific somoy-e specific kaj. Buffer time rakho."),
("Budget toiri korte pari na.","Prothome 1 masher shob khoroch likhe dekho. Tarpor 50/30/20 rule: 50% needs, 30% wants, 20% savings."),
("Goal set korte pari na.","SMART goal toiri koro — Specific, Measurable, Achievable, Relevant, Time-bound. 'Better English' na, '30 din e 500 shobdo' like."),
("Presentation dite gotechhi.","3-ta jinis ready koro: clear message, simple slides, practiced delivery. Audience-ke problem-der solution dao — feature na."),
("Report likhte pari na.","Structure koro: introduction, main points, conclusion. Prottekta point-e evidence dao. Simple language use koro — jargon komao."),
("Data analyze korte pari na.","Prothome data clean koro — missing value, duplicate check. Tarpor simple chart diye visualize koro. Trend ar outlier dhukchuk koro."),
("Team e kaj korte pari na.","Active shona shuru koro — question korun, suggestion dao. Deadline follow koro, conflict-e solution focus korun."),
("Customer er complaint handle korte pari na.","Age shono fully, tarpor acknowledge koro problem, tarpor solution dao. Aggressive hobar dorkar nei — calm thakle resolve easy."),
("Meeting e kichu bolte pari na.","Meeting-er age point gulo prepare koro. Ekta clear suggestion dao shuru te — tarpor onno ra contribute korbe. Silence-o contribution na."),
("Deadline miss korchi bar bar.","Task gulo choto koro — 'report likha' na, 'outline toiri kora'. Proti din ekta small step dao. Early start koro — last minute rush e vul hoy."),
("Focus korte pari na.","Phone silent koro, workspace clean koro, ar Pomodoro technique try koro — 25 minute focus, 5 minute break. Multitasking na kore single task koro."),
("Notun kichu shikhte pari na.","Learning curve shuru te slow thake — eta normal. Small daily practice boro session-er cheye bhalo. 'I can't yet' bola shuru koro."),
("Mistake kore feels bad.","Mistake shikhbar part — eta evidence tumi try korchho. Apnar ke sathe dorkar moto kotha bolun, onno der moto na."),
("Comparison e feels bad.","Onnoder highlight dekha jay — tader behind-the-scenes dekha jay na. Apnar nijer progress measure koro, onnoder sathe na."),
("Burnout feel korchi.","Rest o kaj — eta important. Screen theke break nin, real rest nin (sleep, hobi), ar 'no' bolte shikhen unnecessary kaaj-e."),
("Kono achievement niye khushi lagche na.","Achievement temporary — eta normal. Khushi asole journey-te ashe, destination-e na. Process-e focus koro."),
("Friend er sathe distance hoye geche.","Life busy hole relationship-o distance hoy — eta common. Ekta simple message dao — 'kemon acho?' — rekho regular contact."),
("Family er sathe conflict hocche.","Age boro hole-o harsh kotha avoid koro. Apnar viewpoint bolun 'I feel' diye, blame na kore. Shanti korle solution ashe."),
]
for u,a in BG_BANK:
    if BN.search(u): continue
    seed("everyday_help","banglish",u,a,["banglish","everyday_help"])

# ============ 6. MIXED LANGUAGE ============
MIX_BANK=[
("আমি React shikhte chai, kintu hooks bujhtesi na.","Hooks hocche React-er special function — useState, useEffect. Ekdom notun start hole age functional component + useState diye shuru koro."),
("আমার computer e Python install korte hobe, kintu ami bujhi na.","python.org theke installer download koro, install er somoy 'Add to PATH' check box ta mark koro — tarpor terminal e 'python --version' diye verify koro."),
("Why does my Bengali text show as question marks?","Eta encoding problem — file-ta UTF-8 e save koro. HTML hole <meta charset=\"UTF-8\"> thakbe kina check koro."),
("আমি এই photo-ta edit korte chai kintu kon software use korbo janbo na.","Free option: GIMP ba Canva. Paid: Photoshop. Mobile: Lightroom ba Snapseed — basic editing er jonno bhalo."),
("Please explain 'machine learning' in Bangla.","Machine learning holo AI-er ekta shakhha — system data theke pattern shikhe, sudhu handwritten niyom follow kore na."),
("আমার wifi password thik ache kintu connect hocche na.","Router restart koro age — beshi somoy e eta-i solve kore. Tarpor phone-er network settings reset koro."),
("What is the difference between 'affect' and 'effect' — Bangla te bujhao.","'Affect' usually verb — 'The rain affected my plans' mane poriborton korlo. 'Effect' usually noun — 'The effect was bad' mane porinam. Verb hole affect, noun hole effect."),
("আমি Git install korlam kintu command kaj korchhe na.","Git bash theke check koro 'git --version' — kaj korle terminal-e problem, na korle install problem. Re-install try koro."),
("How do I make my Bengali typing faster?","Avro ba Bijoy keyboard layout practice koro — mukhoya key gulo familiar hole speed bare. Online typing test diye roz practice koro."),
("আমার exam e math-e vul korlam — steps bujhte chi.","Prottekta step e notun variable use koro — 'a', 'b', tarpor final 'x'. Jekono step-e abar check koro — ekta vul step shob vul kore dey."),
("Can you explain blockchain like I'm five?","Blockchain holo ekta digital ledger ja copy hoy onek computer-e — keu change korte parbe na karon sobai-ke mile verify korte hobe."),
("আমার friend-ke job khujhte help korte chai.","Take his resume, current job history, ar skills list koro. Tarpor linkedIn-e profile update + relevant job board-e apply korte help koro."),
("What does 'CPU' stand for?","Central Processing Unit — computer-er brain ja shob calculation kore. GPU holo graphics er jonno, RAM holo short-term memory."),
("আমি database design korchi kintu normalize korte pari na.","Prothome duplicate data alada table-e rakho — 'student' table, 'course' table, tarpor relationship table diye connect koro."),
("My phone battery drains fast — is it normal?","3-5 years er phone-e eta common — battery degrade hoy. Settings e battery usage check koro — kon app beshi khacche dekho."),
]
for u,a in MIX_BANK: seed("mixed_lang","mixed",u,a,["mixed_lang","code_switch"])

# ============ 7. PROCEDURAL MATH+LOGIC (verified, steps) ============
def gen_math():
    ops=[("+","plus","যোগ","add"),("-","minus","বিয়োগ","subtract"),("*","times","গুণ","multiply"),("/","divided by","ভাগ","divide")]
    for i in range(400):
        a,b=random.randint(2,60),random.randint(2,30)
        op,opw,opbn,opv=random.choice(ops)
        if op=="+": ans=a+b; verb=f"adding {a} and {b}"
        elif op=="-": ans=a-b; verb=f"subtracting {b} from {a}"
        elif op=="*": ans=a*b; verb=f"multiplying {a} by {b}"
        else:
            if b==0 or a%b!=0: continue
            ans=a//b; verb=f"dividing {a} by {b}"
        sym={"+":"+","-":"-","*":"x","/":"/"}[op]
        r=i%4
        if r==0:
            seed("math","en",f"What is {a} {opw} {b}?",
                 f"{a} {sym} {b} = {ans}. Step: {verb} gives {ans}.",["math","arithmetic","steps"])
        elif r==1:
            seed("math","bn",f"{a} {opbn} {b} কত?",
                 f"{a} {sym} {b} = {ans}। ধাপ: {verb} করলে {ans} হয়।",["math","arithmetic","steps"])
        elif r==2:
            seed("math","banglish",f"{a} {opw} {b} koto?",
                 f"{a} {sym} {b} = {ans}. Step: {verb} korle {ans} hoy.",["math","arithmetic","steps"])
        else:
            # word problem with steps
            kind=random.choice(["apples","books","taka","students","eggs"])
            wl=("en","bn","banglish")[i%3]
            if kind=="apples":
                if wl=="en":
                    seed("math","en",f"I have {a} apples, eat {b}, then buy {a}. How many now?",
                         f"{a} - {b} = {a-b}, then {a-b} + {a} = {a-b+a} apples.",["math","word_problem","steps"])
                elif wl=="bn":
                    seed("math","bn",f"আমার {a}টি আপেল আছে, {b}টি খেলাম, তারপর {a}টি কিনলাম। মোট কতটি?",
                         f"{a} - {b} = {a-b}, তারপর {a-b} + {a} = {a-b+a}টি আপেল।",["math","word_problem","steps"])
                else:
                    seed("math","banglish",f"Amar {a} ta aapel ache, {b} ta khalam, tarpor {a} ta kinlam. Mot koto ta?",
                         f"{a} - {b} = {a-b}, tarpor {a-b} + {a} = {a-b+a} ta aapel.",["math","word_problem","steps"])
            elif kind=="books":
                if wl=="en":
                    seed("math","en",f"A shelf has {a*2} books, {b} are removed, then {a} added. How many?",
                         f"{a*2} - {b} = {a*2-b}, then {a*2-b} + {a} = {a*2-b+a} books.",["math","word_problem","steps"])
                elif wl=="bn":
                    seed("math","bn",f"এক তাকে {a*2}টি বই আছে, {b}টি সরানো হলো, তারপর {a}টি যোগ হলো। মোট কতটি?",
                         f"{a*2} - {b} = {a*2-b}, তারপর {a*2-b} + {a} = {a*2-b+a}টি বই।",["math","word_problem","steps"])
                else:
                    seed("math","banglish",f"Ek shake {a*2} ta boi ache, {b} ta sorano holo, tarpor {a} ta jog holo. Mot koto ta?",
                         f"{a*2} - {b} = {a*2-b}, tarpor {a*2-b} + {a} = {a*2-b+a} ta boi.",["math","word_problem","steps"])
            elif kind=="taka":
                if wl=="en":
                    seed("math","en",f"Rahim earns {a*10} taka, spends {b*5}, saves the rest. How much saved?",
                         f"Earnings {a*10}, spending {b*5}: {a*10} - {b*5} = {a*10-b*5} taka saved.",["math","word_problem","steps"])
                elif wl=="bn":
                    seed("math","bn",f"রহিম {a*10} টাকা উপার্জন করে, {b*5} টাকা খরচ করে, বাকিটা সাশ্রয় করে। কত সাশ্রয় হলো?",
                         f"উপার্জন {a*10}, খরচ {b*5}: {a*10} - {b*5} = {a*10-b*5} টাকা সাশ্রয়।",["math","word_problem","steps"])
                else:
                    seed("math","banglish",f"Rahim {a*10} taka uparjon kore, {b*5} taka khoroch kore, baki ta shashroy kore. Koto ta shashroy holo?",
                         f"Uparjon {a*10}, khoroch {b*5}: {a*10} - {b*5} = {a*10-b*5} taka shashroy.",["math","word_problem","steps"])
            elif kind=="students":
                if wl=="en":
                    seed("math","en",f"A class has {a} boys and {b} girls. If {b} girls leave, how many remain?",
                         f"Total {a+b}, after {b} leave: {a+b} - {b} = {a} students remain.",["math","word_problem","steps"])
                elif wl=="bn":
                    seed("math","bn",f"এক ক্লাসে {a} ছেলে ও {b} মেয়ে। {b} মেয়ে চলে গেলে কত জন থাকবে?",
                         f"মোট {a+b}, {b} চলে গেলে: {a+b} - {b} = {a} জন থাকবে।",["math","word_problem","steps"])
                else:
                    seed("math","banglish",f"Ek class e {a} chele ar {b} meye. {b} meye chole gele koto jon thakbe?",
                         f"Mot {a+b}, {b} chole gele: {a+b} - {b} = {a} jon thakbe.",["math","word_problem","steps"])
            else:
                if wl=="en":
                    seed("math","en",f"A box has {a*3} eggs, {b*2} break. How many good eggs?",
                         f"{a*3} - {b*2} = {a*3-b*2} good eggs remain.",["math","word_problem","steps"])
                elif wl=="bn":
                    seed("math","bn",f"এক বাক্সে {a*3}টি ডিম আছে, {b*2}টি ভেঙে গেল। ভালো ডিম কতটি?",
                         f"{a*3} - {b*2} = {a*3-b*2}টি ভালো ডিম আছে।",["math","word_problem","steps"])
                else:
                    seed("math","banglish",f"Ek box e {a*3} ta dim ache, {b*2} ta bhenge gelo. Bhalo dim koto ta?",
                         f"{a*3} - {b*2} = {a*3-b*2} ta bhalo dim ache.",["math","word_problem","steps"])
    # fractions/percent/ratio
    for i in range(100):
        a,b=random.randint(1,12),random.randint(1,12)
        if random.random()<0.4:
            seed("math","en",f"What is {a}/{b} as a percentage?",f"{a}/{b} = {round(a/b*100,1)}%.",["math","fraction","percent"])
        elif random.random()<0.5:
            seed("math","bn",f"{a} Diagn 1/tk rest?",f"{a}/{b} = {round(a/b*100,1)}%।",["math","fraction","percent"])
        else:
            seed("math","en",f"Simplify {a*2}/{b*2}",f"{a*2}/{b*2} = {a}/{b} (dividing numerator and denominator by {b*2//max(1,b)} reduces to lowest terms when possible).",["math","fraction"])
    # algebra
    for i in range(60):
        c=random.randint(2,20); x=random.randint(2,12)
        r=i%3
        if r==0:
            seed("math","en",f"If x + {c} = {x+c}, what is x?",f"x = {x}. Check: {x} + {c} = {x+c}.",["math","algebra"])
        elif r==1:
            seed("math","bn",f"x + {c} = {x+c} হলে x কত?",f"x = {x}। যাচাই: {x} + {c} = {x+c}।",["math","algebra"])
        else:
            seed("math","en",f"Solve: {x}x = {x*x}",f"x = {x} (since {x} × {x} = {x*x}).",["math","algebra"])
    # logic puzzles procedural
    for i in range(80):
        a,b,c=random.sample(range(1,50),3)
        mx=max(a,b,c)
        r=i%3
        who={a:"A",b:"B",c:"C"}[mx]
        if r==0:
            seed("logic","en",f"A scored {a}, B scored {b}, C scored {c}. Who scored highest?",
                 f"{who} scored highest with {mx}.",["reasoning","comparison"])
        elif r==1:
            seed("logic","bn",f"A {a} পেয়েছে, B {b}, C {c}। সবার মধ্যে সর্বোচ্চ কে?",
                 f"{who} সর্বোচ্চ {mx} পেয়েছে।",["reasoning","comparison"])
        else:
            seed("logic","en",f"If today is Monday, what day is it in 5 days?",
                 "Monday + 5 days = Saturday.",["reasoning","sequence"])

gen_math()

# ============ 8. UNCERTAINTY/KNOWLEDGE EXTRA ============
UNC3=[
("en","What will the weather be next Friday?","I can't predict weather that far ahead — check a forecast closer to the date. I can explain weather patterns if that helps."),
("en","What's the population of Dhaka right now?","I don't have live population data — my information has a cutoff. For current figures, check official census or government sources."),
("en","Who won the latest cricket match?","I don't have access to current sports results. My knowledge has a cutoff date — check recent sports news for the latest score."),
("en","What should I invest in right now?","I can't give personalized financial advice — it depends on your goals, risk tolerance, and timeline. A financial advisor can help based on your situation."),
("en","Is this website safe to enter my password?","Check for HTTPS (padlock icon) and verify the domain name carefully. If unsure, don't enter credentials — when in doubt, don't risk it."),
("bn","আগামী শুক্রবার আবহাওয়া কেমন হবে?","এত दूर WEATHER predict করতে পারি না — তারিখের কাছে গিয়ে forecast দেখুন। আবহাওয়ার pattern বুঝিয়ে দিতে পারি।"),
("bn","এখন ঢাকার জনসংখ্যা কত?","আমার কাছে live population data নেই — তথ্যের cutoff আছে। বর্তমান সংখ্যার জন্য official census বা government source দেখুন।"),
("bn","শেষ cricket ম্যাচে কে জিতেছে?","আমি বর্তমান খেলার ফল জানি না। Knowledge cutoff আছে — সর্বশেষ score-এর জন্য sports news দেখুন।"),
("banglish","Next Friday er weather kemon hobe?","Itun-i future er weather predict korte pari na — tarikh er kachhe giye forecast dekho. Weather pattern bujhaiye dite pari."),
("banglish","Ekhon Dhaka er population koto?","Amar kache live population data nei — information er cutoff ache. Current figure er jonno official census ba government source dekho."),
]
for lang,u,a in UNC3: seed("uncertainty",lang,u,a,["uncertainty","honesty"])

KNOW3=[
("en","What is photosynthesis?","Photosynthesis is how plants convert sunlight, water, and CO2 into food (glucose) and oxygen — the foundation of most food chains."),
("en","What causes earthquakes?","Earthquakes happen when tectonic plates suddenly slip past each other, releasing stored energy as seismic waves."),
("en","What is the water cycle?","Water evaporates from oceans, condenses into clouds, falls as rain/snow, and returns to oceans via rivers — a continuous cycle."),
("en","Why is the sky blue?","Sunlight scatters off air molecules; blue light scatters more than other colors, making the sky appear blue."),
("en","What is gravity?","Gravity is the force attracting objects with mass toward each other — Earth's gravity keeps us on the ground and the moon in orbit."),
("en","What are tectonic plates?","Large slabs of Earth's crust that move slowly over the mantle — their collisions cause earthquakes, volcanoes, and mountains."),
("en","What is DNA?","DNA is the molecule carrying genetic instructions — like a biological blueprint that determines traits in living organisms."),
("en","How do vaccines work?","Vaccines train the immune system to recognize and fight specific pathogens without causing the disease — creating memory cells for future protection."),
("en","What is the greenhouse effect?","Atmospheric gases trap heat from the sun — like a greenhouse. Human activities (burning fossil fuels) have intensified it, causing global warming."),
("en","What is a black hole?","A region where gravity is so strong that nothing escapes — not even light. Formed when massive stars collapse."),
("en","What is the difference between weather and climate?","Weather is short-term atmospheric conditions (today's rain); climate is long-term patterns over decades (a region's average rainfall)."),
("en","What is renewable energy?","Energy from naturally replenishing sources — solar, wind, hydro, geothermal. Unlike fossil fuels, they don't deplete."),
("bn","Photosynthesis কী?","Photosynthesis হলো যেভাবে গাছ সূর্যের আলো, পানি ও CO2 দিয়ে খাদ্য (glucose) তৈরি করে ও oxygen ছাড়ে — বেশিরভাগ food chain-এর ভিত্তি।"),
("bn","ভূমিকম্প হয় কেন?","Tectonic plate হঠাৎ সরে গেলে জমা energy seismic wave হিসেবে ছেড়ে দেয় — এটাই earthquake।"),
("bn","জলচক্র কী?","Ocean থেকে water বাষ্প হয়ে মেঘে জমে, বৃষ্টি/তুষার হয়ে নেমে river দিয়ে আবার ocean-এ যায় — continuous cycle।"),
("bn","আকাশ নীল কেন?","সূর্যের আলো বায়ুর অণুতে scatters হয়; নীল আলোর wavelength ছোট বলে বেশি scatters হয়।"),
("bn","মাধ্যাকর্ষণ কী?","Mass থাকা বস্তুগুলোর পরস্পরের দিকে আকর্ষণ বল — পৃথিবীর মাধ্যাকর্ষণ আমাদের মাটিতে ধরে রাখে ও চাঁদকে orbit-এ রাখে।"),
("bn","DNA কী?","DNA হলো genetic নির্দেশনা বহনকারী অণু — জীবদেহের blueprint-এর মতো যা traits নির্ধারণ করে।"),
("bn","Vaccine কীভাবে কাজ করে?","Vaccine immune system-কে specific pathogen চিনতে ও লড়তে শেখায়, disease না করে — ভবিষ্যতের সুরক্ষার জন্য memory cell তৈরি করে।"),
("bn","Greenhouse effect কী?","বায়ুমণ্ডলীয় gas সূর্যের তাপ আটকে রাখে — greenhouse-এর মতো। 인간 busiest (fossil fuel পোড়ানো) এটিকে তীব্র করেছে,_global warming হচ্ছে।"),
("banglish","Photosynthesis ki?","Photosynthesis holo je bhabe gach surjer alo, jol ar CO2 diye khaddo (glucose) toiri kore ar oxygen chare — beshirag food chain er bhiti."),
("banglish","Earthquake hoy keno?","Tectonic plate hothat sore gele joma energy seismic wave hisabe chere dey — etai earthquake."),
("banglish","Sky neel keno?","Surjer alo batash er molekule scatter hoy; neel light er wavelength choto tai beshi scatter hoy."),
("banglish","Gravity ki?","Mass thaka boutugulo-r parsporer dike akorshon bal — prithbir gravity amader matite dhore rakhe ar chand ke orbit e rakhe."),
]
for lang,u,a in KNOW3:
    seed("knowledge",lang,u,a,["knowledge","science"])

# ============ 9. SOCIAL/IDENTITY extras ============
SOC3=[
("en","I'm nervous about my first day at a new job.","That's completely normal — everyone feels that way. Prepare the night before: know the route, pick out clothes, and plan to arrive 10 minutes early. First days are about learning, not perfection."),
("en","My friend just got engaged. What should I say?","Congratulations! Ask about their plans — where, when, who. Genuine excitement matters more than perfect words. Offer specific help: 'Can I help with anything for the wedding?'"),
("en","I apologized but they didn't accept it.","Apologies don't guarantee forgiveness — that's okay. Give them space, don't push. If the relationship matters, consistent changed behavior over time rebuilds trust better than words."),
("en","I'm bad at small talk.","Small talk is a skill, not a personality trait. Prepare 2-3 openers: 'How was your weekend?', 'What are you working on?', 'Have you tried the new café nearby?' Listen more than you talk."),
("bn","নতুন চাকরির প্রথম দিনে nervous।","এটা একদম স্বাভাবিক — সবাই এভাবে ফিল করে। আগের রাতে প্রস্তুত থাকুন: route জেনে নিন, পোশাক বাছুন, ১০ মিনিট আগে পৌঁছানোর plan করুন। প্রথম দিন learning-এর, perfection-এর না।"),
("bn","বন্ধুর engagement হয়েছে। কী বলব?","অভিনন্দন! তাদের plans জিজ্ঞেস করুন — কোথায়, কখন, কারা। আসল উৎসাহ perfect শব্দের চেয়ে জরুরি। Specific সাহায্য offer করুন।"),
("bn","মাফ চেয়েছি কিন্তু তারা মেনে নেনি।","মাফ চাওয়া সবসময় forgiveness-এর নিশ্চয়তা দেয় না — সেটা ঠিক আছে। Space দিন, push করবেন না। সম্পর্ক জরুরি হলে consistent behavior সময়ের সাথে trust rebuild করে।"),
("bn","Small talk করতে পারি না।","Small talk একটা skill, personality না। ২-৩টা opener প্রস্তুত করুন — 'weekend কেমন ছিল?', 'কী নিয়ে কাজ?', 'নতুন café try করেছেন?' বেশি শোনুন, কম বলুন।"),
("banglish","Notun job er prothom dine nervous.","Eta ekdom normal — shobai emon-i feel kore. Ager raat e ready thakun: route jene nin, poshak bachhun, 10 minute age pouchhar plan korun. Prothom din learning er, perfection er na."),
("banglish","Bondhu engagement hoyeche. Ki bolbo?","Obhinondon! Tara-r plan jigges korun — kothay, kokhon, ke. Asol utshah perfect shobder cheye joruri. Specific sahajjo offer korun."),
("banglish","Sorry bolchi kintu ora accept koreni.","Sorry bolle shobshomoy forgiveness er nishchinti dey na — sheta thik ache. Space din, push korben na. Somporko joruri hole consistent behavior shomoyer sathe trust rebuild kore."),
]
for lang,u,a in SOC3: seed("social",lang,u,a,["social","emotional"])

# ---- v3 bn/banglish depth boost: authored everyday+tech banks ----
BN_EVERYDAY=[
("বৃষ্টি হলে কী করব?","ছাতা নিন বা raincoat পরুন; ভেজা জায়গায়Variables এড়িয়ে চলুন। ঠান্ডা লাগলে গরম পানি পান করুন।"),
("গরমে ঘাম বেশি হয় কেন?","Body temperature regulate করতে sweat হয় — এটা normal. hydration রাখুন, loose clothing পরুন।"),
("ঘুম কম হলে কী হয়?","Concentration কমে, mood fluctuate করে, immunity কমে। ৭-৮ ঘণ্টা ঘুম aim করুন; consistent sleep schedule maintain করুন।"),
("চা-পান每天?","Too much caffeine (.5 cup/day+) jitteriness, sleep problem,dependency হতে পারে। Balance করুন water আর herbal tea দিয়ে।"),
("মোবাইলে excess screen time?","Eye strain, sleep problem, posture issue হতে পারে। 20-20-20 rule follow করুন: প্রতি 20 মিনিটে 20 সেকেন্ড 20 feet দূরে তাকান।"),
("নিয়মিত dental checkup?","৬ মাস পরপর dental checkup করুন; brushing+flossing daily করুন। Cavities early-তে ধরা পড়লে treatment সহজ।"),
("অ স্বাদু_health?","Hydration রাখুন, processed food কমান, regular meal time রাখুন। digestive problem হলে doctor দেখান।"),
("পড়তে পারি না মনোযোগে?","Distraction远离 করুন, quiet environment বেছে নিন, আর small chunks-এ পড়ুন। Pomodoro technique (25 min focus + 5 min break) try করুন।"),
("নতুন skill শিখতে চাই।","Small daily practice consistency-র চেয়ে জরুরি। 'I can't yet' mindset রাখুন — growth mindset learning accelerate করে।"),
("ভুল হলে দুঃখিত লাগে।","Mistake shikhbar part — evidence tumi try korchho. Self-compassion cultivation emotional resilience বাড়ায়।"),
("পরিবারের সাথে সময় কাটাতে চাই।","Quality time rules quantity-র চেয়ে — device-free meal, weekly outing, active listening। Shared activity relationship strengthen করে।"),
("বন্ধুদের সাথে distance?","Life busy হলে common। Simple message day keep করুন, regular contact maintain করুন — quality over frequency।"),
("সelve a better version?","Goal SMART করুন, small steps নিন, progress track করুন, আর setbacks-কে data হিসেবে দেখুন not failure হিসেবে।"),
("New year resolution fail?","97% fail করে — too vague, too many, no plan। একটা specific goal নিন, daily habit build করুন, weekly review করুন।"),
("Study group effective?","Effective যদি structure থাকে — specific topic, time limit, active participation। Casual group distraction হয়ে যায়।"),
("Reading slow?","Speed normal range — comprehension priority। Active reading (note-taking, summarizing) slow করে কিন্তু retention বাড়ায়।"),
("Public speaking fear?","Fear normal — exposure therapy কাজ করে। Practice in front of mirror/friend দিয়ে শুরু করুন, তারপর larger audience।"),
("Writing improvement?","Read widely, write daily (even 10 min), get feedback, edit ruthlessly। Style develop হয় practice+feedback দিয়ে।"),
("Coding shikhchi kintu confusing?","Fundamentals strong করুন আগে — variables, loops, functions। Project-based learning theory-র চেয়ে better retain করে।"),
("Time zone manage?","Priority matrix: important+urgent আগে, important+not urgent schedule করুন। 'No' politely বলুন — boundary necessary।"),
("Budget tight?","50/30/20 rule try করুন, subscription audit করুন, cooking home-এ করুন। Small saving habit compound হয়।"),
("Job change ভাবছি?","Current role-এ growth আছে কিনা assess করুন; market value check করুন; switch করার আগে 3-6 মাসের emergency fund রাখুন।"),
("Side hustle ideas?","Skill monetize করুন — freelancing, content creation, teaching। Validate idea small scale-এ before full investment।"),
("Investment beginner?","Index fund দিয়ে শুরু করুন — diversified, low cost। Individual stock beginners-এর জন্য risky। Emergency fund আগে, তারপর invest।"),
("Insurance.prothome?","Term life insurance আগে — cheapest, highest coverage। Health insurance next। Investment-linked plan beginners-এর জন্য complex।"),
("Credit card use?","Reward Convenience — but full payment monthly করুন, minimum payment এ revolving debt। Utilization <30% credit score ভালো রাখে।"),
("Loan nei kemon jain?","Credit score check করুন, income proof ready রাখুন, lender compare করুন। Too many application credit score নষ্ট করে।"),
("Tax file?","Documentation রাখুন year-round — receipts, bank statement, investment proof। Deadline miss করলে penalty + interest।"),
("Phone plan choose?","Usage analyze করুন — data, call, SMS। Compare plan features, hidden charge দেখুন, contract flexibility check করুন।"),
("Internet speed slow?","Speed test করুন, router placement optimize করুন (central, elevated), interference check করুন। ISP plan upgrade consider করুন।"),
("Laptop upgrade?","RAM 8GB minimum, SSD mandatory (HDD slower), battery health check করুন। Use case অনুযায়ী processor prioritize করুন।"),
]
for u,a in BN_EVERYDAY: seed("everyday_help","bn",u,a,["bn","everyday_help"])

BG_TECH=[
("Facebook e account hack hoyeche!","Ami aapnar jonno directly fix korte pari na — Facebook er official 'hacked account' flow follow korun. Password change + 2-factor on korun age.",),
("Whatsapp e message jacche na.","Internet check korun age — mobile data ba wifi thik ache kina. Tarpor WhatsApp update korun."),
("Google account lock hoyeche.","accounts.google.com e giye 'forgot password' use korun. Backup email/phone thakle recovery easy."),
("Laptop e virus detect hocche.","Antivirus scan korun full system — quick scan na. Suspicious file na delete korun age scan na howa porjonto."),
("Phone er display chhoto feel hocche.","Settings e display size/text size adjust korun. Screen resolution change korle area barbe."),
("Email e spam beshi asche.","Spam filter check korun, unknown sender block korun, ar phishing email-er sathe reply din na."),
("YouTube e ads beshi.","Premium chara alternative nai — browser e ad-block extension use korte pari kintu YouTube-er policy violate korte pare. Balanced approach bhalo."),
("Computer e file delete hoye geche.","Recycle Bin check korun age. Tarpor file recovery software try korun — kintu time critical, data overwrite na howa porjonto."),
("Mobile er camera clear na.","Lens soft cloth diye clean korun. App cache clear korun camera app-er. Problem thakle factory reset last option."),
("Printer er ink shesh hoye geche.","Refill na kore official cartridge use korun — refill quality issue + warranty void. Remanufactured option budget-friendly."),
("WiFi password change korte chai.","Router-er admin page e login korun (usually 192.168.1.1), WiFi settings e giye password change korun."),
("Phone er storage full hoye geche.","Settings e storage usage dekho — kon app beshi khacche. Photo backup, unused app uninstall, download clean korun."),
("Bank e OTP asche na.","Network problem check korun — SMS delay common. Bank er app install korun for faster OTP. Issue thakle bank helpline call korun."),
("Netflix e subtitle nei.","Subtitle icon e click korun player-e. Custom subtitle add korte pari external file diye — .srt format support kore."),
("Zoom e video chole na.","Camera permission check korun app settings-e. Driver update korun. Problem thakle app reinstall korun."),
("Excel e formula kaj korchhe na.","Formula-er '=' diye shuru hocche kina check korun. Cell reference thik ache kina dekho. Function name spelling thik korun."),
("Website slow load hocche.","CDN use koren kina check korun, image optimize koren, ar caching enable korun. Server location-o matter kore."),
("Password manage korte pari na.","Password manager use korun — lastpass, bitwarden free. Unique password proti site-e, master password mone rakho."),
("Two phones sync korte chai.","Google account diye sync korun — contacts, photos, app data. Samsung/Apple users respective cloud service use korun."),
("Data backup niye tension.","3-2-1 rule follow korun — 3 copies, 2 different media, 1 offsite (cloud). Automated backup set korun jate bhulben na."),
]
for u,a in BG_TECH: seed("tech_support","banglish",u,a,["banglish","tech_support"])

# ============ 10. SELF-CORRECTION more ============
SC3=[
("en","You said 15% of 200 is 30, but it's actually 30. Wait, let me check — 15% of 200 = 30. You're right!","Yes — 15% of 200 is indeed 30 (200 × 0.15 = 30). Good catch on verifying — checking calculations is always wise."),
("en","I think you made an error — the capital of Canada is Ottawa, not Toronto.","You're correct — I apologize for the confusion. The capital of Canada is Ottawa. Toronto is the largest city, but Ottawa is the capital."),
("bn","আপনি বলেছিলেন ২০% of ৫০০ = ১২০, কিন্তু আসলে ১০০।","আপনি ঠিক বলেছেন — ২০% of ৫০০ = ৫০০ × ০.২০ = ১০০। আমার ভুলের জন্য দুঃখিত।"),
("bn","Ottawa Canada's capital — you said Toronto earlier by mistake.","আপনি ঠিক — Canada-র রাজধানী Ottawa, Toronto নয়। Toronto সবচেয়ে বড় শহর, কিন্তু capital Ottawa। ধন্যবাদ সংশোধনের জন্য।"),
("banglish","Tumi age vul bolecho — 20% of 500 = 100, 120 na.","Thik bolecho — 20% of 500 = 500 × 0.20 = 100. Amar vul, sorry. Check korar jonno dhonnobad."),
]
for lang,u,a in SC3: seed("self_correction",lang,u,a,["self_correction","verification"])

# ============ 11. PARAPHRASE VARIANTS (documented) ============
def para(cat,lang,u,a,caps):
    out=[]
    if cat in ("qa","knowledge","everyday_help","math","logic","reasoning","decision"):
        if lang=="en":
            m=re.match(r"What is (.+)\??",u)
            if m:
                t=m.group(1).rstrip("?")
                out+=[(f"Tell me about {t}.",a),(f"Can you explain {t}?",a)]
            if u.startswith("How do I") or u.startswith("How does"):
                out.append((u.replace("How do I","How can I",1).replace("How does","How do",1),a))
            if "What is the difference" in u:
                out.append((u.replace("What is the difference","Explain the difference"),a))
        if lang=="bn":
            m=re.match(r"(.+?)\s*[কখ]ী\??",u)
            if m:
                t=m.group(1)
                out+=[(f"{t} বলতে কী বোঝায়?",a),(f"{t} এর অর্থ কী?",a)]
            if "কীভাবে" in u:
                out.append((u.replace("কীভাবে","কিভাবে",1),a))
        if lang=="banglish":
            m=re.match(r"(.+?)\s+ki\??",u,re.I)
            if m:
                t=m.group(1)
                out+=[(f"{t} mane ki?",a),(f"{t} er mane ki?",a)]
            if "kivabe" in u.lower():
                out.append((u.replace("kivabe","kivabe bhai",1),a))
    return [(cat,lang,v,a,caps) for v,a in out]

for cat,lang,u,a,caps in list(S):
    for item in para(cat,lang,u,a,caps):
        if item[2]!=u: S.append(item)

# ============ 12. BUILD/VALIDATE/SPLIT ============
for cat,lang,u,a,caps in S:
    lang=detect(u) if lang not in ("mixed",) else lang
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
    # suspicious foreign scripts (CJK, Arabic, Cyrillic, Thai, etc.) — corruption guard
    elif any(unicodedata.category(ch)=='Lo' and not BN.match(ch) and not ch.isascii() and ord(ch)>0x2000 and not (0x0900<=ord(ch)<=0x097F) for m in msgs for ch in m["content"]):
        # allow Bengali block + latin + common Indic; flag CJK/Arabic/etc.
        bad=any(0x4E00<=ord(ch)<=0x9FFF or 0x0600<=ord(ch)<=0x06FF or 0x0400<=ord(ch)<=0x04FF or 0x0E00<=ord(ch)<=0x0E7F for m in msgs for ch in m["content"])
        if bad: ok=False;reason="foreign_script_corruption"
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

# group-atomic split
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

# per-language/category split files (spec structure)
os.makedirs(os.path.join(OUT,"records"),exist_ok=True)
os.makedirs(os.path.join(OUT,"splits"),exist_ok=True)
os.makedirs(os.path.join(OUT,"manifests"),exist_ok=True)
os.makedirs(os.path.join(OUT,"benchmarks"),exist_ok=True)
os.makedirs(os.path.join(OUT,"reports"),exist_ok=True)
for lang in ("bn","en","banglish","mixed"):
    rows=[r for r in final if r["lang"]==lang]
    with open(os.path.join(OUT,"records",f"{lang}.jsonl"),"w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")
for cat in ("multi_turn","reasoning","decision","uncertainty","self_correction","math","knowledge","social","qa","everyday_help","mixed_lang","logic"):
    rows=[r for r in final if r["category"]==cat]
    if rows:
        with open(os.path.join(OUT,"records",f"{cat}.jsonl"),"w",encoding="utf-8") as f:
            for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")

def stats(rows):
    langs=Counter(r["lang"] for r in rows); cats=Counter(r["category"] for r in rows)
    turns=[len(r["messages"])//2 for r in rows]
    return {"n":len(rows),"lang":dict(langs),"category":dict(cats),
            "avg_turns":round(sum(turns)/max(len(turns),1),2),
            "multi_turn":sum(1 for t in turns if t>1)}
st={k:stats(v) for k,v in (("train",train),("validation",val),("test",test))}

# per-core manifests (record IDs by category relevance)
CORE_MAP={
 "core01_conversational":{"categories":["greeting","identity","thanks","farewell","smalltalk","qa","everyday_help","social","multi_turn","mixed_lang","clarification","uncertainty"],"note":"all conversational + trilingual"},
 "core02_reasoning_decision":{"categories":["reasoning","decision","logic","instruction","multi_turn","self_correction","clarification"],"note":"instruction+reasoning+decision"},
 "core03_math_logic":{"categories":["math","logic","reasoning"],"note":"verified math+logic"},
 "core04_knowledge_uncertainty":{"categories":["knowledge","qa","uncertainty","refusal","self_correction"],"note":"facts+uncertainty boundaries"},
}
for core,cfg in CORE_MAP.items():
    ids=[r["sample_id"] for r in final if r["category"] in cfg["categories"]]
    json.dump({"core":core,"dataset":"unified_conversational_v3",
               "record_count":len(ids),"categories":cfg["categories"],
               "note":cfg["note"],"training_eligible":True,
               "validation":"rule_based+pending_human_review"},
              open(os.path.join(OUT,"manifests",f"{core}_manifest.json"),"w"),indent=1)

# benchmark spec (authored separately — NOT in training data)
bench=[
 {"id":"b01","core":"core01","capability":"bn_conversation","lang":"bn","prompt":"তুমি কি বাংলা বলতে পারো?","criteria":"bn response, natural","method":"human_rubric"},
 {"id":"b02","core":"core01","capability":"en_conversation","lang":"en","prompt":"How are you today?","criteria":"natural en reply","method":"human_rubric"},
 {"id":"b03","core":"core01","capability":"banglish","lang":"banglish","prompt":"Tumi ki matha khub?","criteria":"banglish reply","method":"human_rubric"},
 {"id":"b03","core":"core01","capability":"banglish","lang":"banglish","prompt":"Tumi ki matha khub?","criteria":"banglish reply","method":"human_rubric"},
 {"id":"b04","core":"core02","capability":"novel_reasoning","lang":"en","prompt":"If all Zorks are Blums and all Blums are Snorks, are all Zorks Snorks?","criteria":"yes+chain","method":"exact"},
 {"id":"b05","core":"core03","capability":"arithmetic","lang":"en","prompt":"What is 17 x 23?","criteria":"391","method":"exact"},
 {"id":"b06","core":"core03","capability":"word_problem","lang":"bn","prompt":"আমার ৩৪টি আপেল আছে এবং ১২টি কিনলাম। মোট কতটি হলো?","criteria":"46","method":"numeric"},
 {"id":"b07","core":"core04","capability":"known_fact","lang":"en","prompt":"What is the capital of Bangladesh?","criteria":"Dhaka","method":"exact"},
 {"id":"b08","core":"core04","capability":"unknown_refusal","lang":"en","prompt":"What will the exact population of Dhaka be in 2050?","criteria":"honest uncertainty","method":"human_rubric"},
 {"id":"b09","core":"core04","capability":"ambiguity","lang":"en","prompt":"Is it good?","criteria":"asks clarification","method":"human_rubric"},
 {"id":"b10","core":"core01","capability":"multi_turn_context","lang":"en","prompt":"[3-turn: trip planning with constraint introduced turn 1]","criteria":"remembers constraint","method":"human_rubric"},
]
json.dump({"benchmark":"unified_v3_benchmark","note":"authored separately; NOT in training data","cases":bench},
          open(os.path.join(OUT,"benchmarks","benchmark_manifest.json"),"w"),indent=1)

manifest={
 "version":"unified_conversational_v3","seed":SEED,
 "total_records":len(final),"rejected":len(QUAR),
 "v2_carryover":v2_count,
 "splits":{"train":len(train),"validation":len(val),"test":len(test)},
 "groups":{"total":ng,"test_groups":nt,"val_groups":nv},
 "statistics":st,
 "schema":"messages:[{role,content}] + capabilities[] — ChatSFTDataset compatible",
 "note":"v2 carryover + multi-turn scenario engine + authored trilingual banks "
        "+ procedural verified math/logic + uncertainty/knowledge/self-correction. "
        "No external AI.",
}
json.dump(manifest,open(os.path.join(OUT,"dataset_manifest.json"),"w"),indent=1)
json.dump({"seed":SEED,"method":"sha256(split_group) ordering","groups":ng,
           "test_groups":nt,"val_groups":nv,
           "note":"conversation/scenario-group atomic; v1/v2 re-grouped"},
          open(os.path.join(OUT,"split_manifest.json"),"w"),indent=1)
json.dump({"approved":len(final),"rejected":len(QUAR),
           "reject_reasons":dict(Counter(r.get("reject_reason","?") for r in QUAR))},
          open(os.path.join(OUT,"quality_report.json"),"w"),indent=1)
json.dump(manifest,open(os.path.join(OUT,"manifests","dataset_manifest.json"),"w"),indent=1)
lines=[]
for root,dirs,files in os.walk(OUT):
    for fn in files:
        if fn.endswith((".jsonl",".json",".md",".sha256")) and fn!="checksums.sha256":
            p=os.path.join(root,fn)
            rel=os.path.relpath(p,OUT).replace("\\","/")
            lines.append(f"{hashlib.sha256(open(p,'rb').read()).hexdigest()}  {rel}")
open(os.path.join(OUT,"checksums.sha256"),"w").write("\n".join(sorted(lines))+"\n")
print(f"unified_conversational v3: {len(final)} approved, {len(QUAR)} rejected")
print("train",len(train),"val",len(val),"test",len(test))
print("langs:",st["train"]["lang"])
print("cats:",st["train"]["category"])
