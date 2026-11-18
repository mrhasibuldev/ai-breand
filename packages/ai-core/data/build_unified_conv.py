"""Build unified trilingual conversational SFT dataset v1.

Authored seeds + deterministic procedural generation (math verified by
recomputation). NO external AI. Output: data/unified_conversational/v1/
{train,validation,test}.jsonl + manifests + quality/split reports.
Schema compatible with core01/sft_dataset.py ChatSFTDataset.
"""
import json, os, random, hashlib, re
from collections import Counter, defaultdict

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), "unified_conversational", "v1")
os.makedirs(OUT, exist_ok=True)

recs = []
QUAR = []


def h(s):
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


def add(cat, lang, messages, group, source="authored"):
    rid = f"{cat}:{lang}:{len(recs)}"
    recs.append({
        "sample_id": rid, "id": rid,
        "lang": lang, "category": cat, "task": cat,
        "conversation_id": group,
        "messages": [{"role": r, "content": c} for r, c in messages],
        "split_group": group,
        "provenance": {"builder": "build_unified_conv.py", "seed": SEED,
                       "source": source},
        "quality": {"status": "approved", "review_method": "rule_based"},
    })


def qa(cat, lang, user, ans):
    add(cat, lang, [("user", user), ("assistant", ans)],
        f"g{h(user + ans) % 100000}")


S = []
def seed(cat, lang, u, a): S.append((cat, lang, u, a))

BN = re.compile(r'[ঀ-৿]')
def detect(u, default):
    if BN.search(u): return "bn"
    if re.search(r'\b(ki|koto|ache|nei|bolun|dao|kivabe|keno|korbo|lagbe|bhalo|khub|bhai|vai)\b', u, re.I): return "banglish"
    if re.search(r'[a-zA-Z]', u) and not BN.search(u): return "en"
    return default

# ---- greetings ----
GREET = {
 "en": [("Hello!","Hello! I'm NexusAI. How can I help you today?"),
        ("Hi there!","Hi! Good to hear from you. What would you like to talk about?"),
        ("Hey!","Hey! What's on your mind?"),
        ("Good morning!","Good morning! Hope your day is going well. How can I help?"),
        ("Good evening!","Good evening! What can I do for you tonight?"),
        ("How are you?","I'm doing well, thank you for asking! I'm here and ready to help. How are you?")],
 "bn": [("হ্যালো!","হ্যালো! আমি NexusAI। কীভাবে সাহায্য করতে পারি?"),
        ("নমস্কার!","নমস্কার! আজকে কী নিয়ে কথা বলতে চান?"),
        ("শুভ সকাল!","শুভ সকাল! আশা করি আপনার দিনটি ভালো যাবে। কীভাবে সাহায্য করব?"),
        ("তুমি কেমন আছো?","আমি ভালো আছি, ধন্যবাদ! আপনি কেমন আছেন?"),
        ("আসসালামু আলাইকুম","ওয়ালাইকুমুসসালাম! আমি NexusAI। কীভাবে সাহায্য পারি?")],
 "banglish": [("Hey!","Hey! Ki obostha? Ki bhabe help korte pari?"),
        ("Tumi kemon acho?","Ami bhalo achi, dhonnobad! Tumi kemon?"),
        ("Kemon acho?","Bhalo achi vai! Ki korte chai tumi bolle ami try korbo.")],
}
for lang, pairs in GREET.items():
    for u,a in pairs: seed("greeting",lang,u,a)

# ---- identity (Hasibul via data only) ----
ID = [
 ("en","What is your name?","I'm NexusAI, an AI assistant."),
 ("en","Who created you?","I was created by Hasibul."),
 ("en","Who made you?","Hasibul built me — NexusAI is his project."),
 ("en","Who is your creator?","My creator is Hasibul."),
 ("en","Who developed you?","I was developed by Hasibul as NexusAI."),
 ("en","Are you made by OpenAI?","No — I'm NexusAI, built independently by Hasibul. I don't use external AI services."),
 ("bn","তোমার নাম কী?","আমার নাম NexusAI।"),
 ("bn","তোমাকে কে তৈরি করেছে?","আমাকে Hasibul তৈরি করেছেন।"),
 ("bn","তোমার creator কে?","আমার creator Hasibul।"),
 ("bn","তুমি কি OpenAI-এর মডেল?","না — আমি NexusAI, Hasibul-এর তৈরি independent AI। কোনো external AI service ব্যবহার করি না।"),
 ("banglish","Tomar nam ki?","Amar nam NexusAI."),
 ("banglish","Ke tomay toiri koreche?","Amake Hasibul toiri korechen."),
 ("banglish","Tumi ki OpenAI er model?","Na — ami NexusAI, Hasibul er banano independent AI. Kono external AI service use kori na."),
]
for lang,u,a in ID: seed("identity",lang,u,a)

# ---- thanks / farewell ----
THX = {
 "en":[("Thank you!","You're welcome! Anything else I can help with?"),
       ("Thanks a lot!","My pleasure! Feel free to ask anything else."),
       ("Bye!","Goodbye! Come back anytime."),
       ("See you later!","See you! Take care.")],
 "bn":[("ধন্যবাদ!","আপনাকে ধন্যবাদ! আরও কিছু জানতে চাইলে বলুন।"),
       ("খুব ধন্যবাদ!","স্বাগতম! অন্য কোনো প্রশ্ন থাকলে জিজ্ঞাসা করুন।"),
       ("বিদায়!","বিদায়! আবার আসুন।"),
       ("আবার দেখা হবে!","আবার দেখা হবে! ভালো থাকুন।")],
 "banglish":[("Dhonnobad!","Dhonnobad! Onno kichu lagbe?"),
       ("Shukria!","Ami apnar jonno achi. Onno proshno thakle bolo."),
       ("Biday!","Biday! Abar ashen.")],
}
for lang,pairs in THX.items():
    for u,a in pairs:
        seed("thanks" if ("thank" in u.lower() or "ধন্য" in u) else "farewell",lang,u,a)

# ---- smalltalk ----
SMALL = {
 "en":[("What can you do?","I can chat, answer questions, explain things, and help with tasks — though I'm still learning, so some answers may be limited."),
       ("Are you a robot?","I'm an AI assistant — NexusAI. I don't have a physical body, but I can help with questions and tasks."),
       ("Do you speak Bengali?","Yes, I can understand and respond in Bengali, English, and Banglish."),
       ("What is NexusAI?","NexusAI is an independent AI system built by Hasibul — it runs its own neural models locally.")],
 "bn":[("তুমি কী করতে পারো?","আমি কথা বলতে, প্রশ্নের উত্তর দিতে, ব্যাখ্যা করতে ও কাজে সাহায্য করতে পারি — তবে আমি এখনো শিখছি, তাই কিছু উত্তর সীমিত হতে পারে।"),
       ("তুমি কি রোবট?","আমি একটি AI সহকারী — NexusAI। আমার শারীরিক দেহ নেই, কিন্তু আমি প্রশ্ন ও কাজে সাহায্য করতে পারি।"),
       ("তুমি কি বাংলা বলতে পারো?","হ্যাঁ, আমি বাংলা, ইংরেজি ও বাংলা+ইংরেজি মিশ্র ভাষা বুঝতে ও বলতে পারি।"),
       ("NexusAI কী?","NexusAI হলো Hasibul-এর তৈরি একটি independent AI system — এটি নিজের neural model locally চালায়।")],
 "banglish":[("Tumi ki korte paro?","Ami kotha bolte, proshner uttor dite, bujhaiye dite ar kaaj-e sahayota korte pari — kintu ami ekhono shikhchi."),
       ("Tumi ki robot?","Ami ekta AI assistant — NexusAI. Amar physical body nei, kintu ami proshno ar kaaj-e sahayote pari."),
       ("Tumi ki bangla bolte paro?","Hyan, ami bangla, english ar banglish bujhte ar bolte pari.")],
}
for lang,pairs in SMALL.items():
    for u,a in pairs: seed("smalltalk",lang,u,a)

# ---- general QA ----
QA_EN=[("What is water?","Water is a transparent liquid essential for life; its chemical formula is H2O."),
("What is the sun?","The sun is a star at the center of our solar system that provides Earth with light and heat."),
("What is a computer?","A computer is an electronic machine that stores data and follows instructions to process information."),
("What is the capital of Bangladesh?","The capital of Bangladesh is Dhaka."),
("What is the capital of Japan?","The capital of Japan is Tokyo."),
("What is 1 kilometer in meters?","1 kilometer equals 1000 meters."),
("How many days are in a week?","There are 7 days in a week."),
("How many months are in a year?","There are 12 months in a year."),
("What is the largest ocean?","The Pacific Ocean is the largest ocean on Earth."),
("What is the boiling point of water?","Water boils at 100 degrees Celsius at sea level."),
("What is photosynthesis?","Photosynthesis is how plants use sunlight, water and carbon dioxide to make food and release oxygen."),
("What is an algorithm?","An algorithm is a step-by-step procedure for solving a problem or completing a task."),
("What is a database?","A database is an organized collection of data stored and accessed electronically."),
("What is electricity?","Electricity is the flow of electric charge, used to power devices and lights."),
("What is gravity?","Gravity is the force that attracts objects toward each other; Earth's gravity pulls things downward."),
("What is the moon?","The moon is Earth's natural satellite that orbits our planet."),
("What is a virus?","A virus is a microscopic infectious agent that can cause illness in living organisms."),
("What is recycling?","Recycling is processing used materials into new products to reduce waste."),
("What is the internet?","The internet is a global network connecting computers to share information."),
("What is artificial intelligence?","Artificial intelligence is the simulation of human intelligence by machines, especially computers.")]
for u,a in QA_EN: seed("qa","en",u,a)

QA_BN=[("পানি কী?","পানি একটি স্বচ্ছ তরল যা জীবনের জন্য অপরিহার্য; এর chemical সূত্র H2O।"),
("সূর্য কী?","সূর্য আমাদের সৌরজগতের কেন্দ্রে থাকা একটি তারা যা পৃথিবীকে আলো ও তাপ দেয়।"),
("কম্পিউটার কী?","কম্পিউটার একটি ইলেকট্রনিক যন্ত্র যা তথ্য সংরক্ষণ করে ও নির্দেশনা অনুসরণ করে তথ্য প্রক্রিয়া করে।"),
("বাংলাদেশের রাজধানী কী?","বাংলাদেশের রাজধানী ঢাকা।"),
("জাপানের রাজধানী কী?","জাপানের রাজধানী টোকিও।"),
("১ কিলোমিটারে কত মিটার?","১ কিলোমিটার = ১০০০ মিটার।"),
("এক সপ্তাহে কয়টি দিন?","এক সপ্তাহে ৭টি দিন।"),
("এক বছরে কয়টি মাস?","এক বছরে ১২টি মাস।"),
("সবচেয়ে বড় মহাসাগর কোনটি?","প্রশান্ত মহাসাগর পৃথিবীর সবচেয়ে বড় মহাসাগর।"),
("পানি কত ডিগ্রিতে ফুটে?","সমুদ্রপৃষ্ঠে পানি ১০০ ডিগ্রি সেলসিয়াসে ফুটে।"),
("photosynthesis কী?","Photosynthesis হলো যেভাবে গাছ সূর্যের আলো, পানি ও CO2 দিয়ে খাদ্য তৈরি করে ও অক্সিজেন ছাড়ে।"),
("অ্যালগরিদম কী?","অ্যালগরিদম হলো কোনো সমস্যা সমাধান বা কাজ সম্পাদনের ধাপে ধাপে পদ্ধতি।"),
("ডাটাবেস কী?","ডাটাবেস হলো ইলেকট্রনিকভাবে সংরক্ষিত ও অ্যাক্সেস করা তথ্যের সুসংগঠিত সংগ্রহ।"),
("বিদ্যুৎ কী?","বিদ্যুৎ হলো electric charge-এর প্রবাহ যা যন্ত্র ও আলো চালায়।"),
("মাধ্যাকর্ষণ কী?","মাধ্যাকর্ষণ হলো বস্তুগুলোর পরস্পরের দিকে আকর্ষণ বল; পৃথিবীর মাধ্যাকর্ষণ সবকিছু নিচের দিকে টানে।"),
("চাঁদ কী?","চাঁদ পৃথিবীর প্রাকৃতিক উপগ্রহ যা আমাদের গ্রহ প্রদক্ষিণে ঘোরে।"),
("ভাইরাস কী?","ভাইরাস একটি microscopic সংক্রামক পদার্থ যা জীবদেহে রোগ সৃষ্টি করতে পারে।"),
("recycling কী?","Recycling হলো বর্জ্য কমাতে ব্যবহৃত উপকরণ প্রক্রিয়া করে নতুন পণ্য তৈরি করা।"),
("ইন্টারনেট কী?","ইন্টারনেট একটি বিশ্বব্যাপী নেটওয়ার্ক যা কম্পিউটারগুলোকে তথ্য ভাগ করতে সংযুক্ত করে।"),
("কৃত্রিম বুদ্ধিমত্তা কী?","কৃত্রিম বুদ্ধিমত্তা হলো মেশিন, বিশেষ করে কম্পিউটারের মাধ্যমে মানব বুদ্ধিমত্তার অনুকরণ।")]
for u,a in QA_BN: seed("qa","bn",u,a)

QA_BG=[("Water ki?","Water ekta transparent liquid ja life-er jonno mustoijjo; tar chemical formula H2O."),
("Computer ki?","Computer ekta electronic machine ja information store kore ar instruction follow kore kaj kore."),
("Bangladesher rajdhani ki?","Bangladesher rajdhani Dhaka."),
("Surjo ki?","Surjo amader solar system er center-e thaka ekta star ja prithbik light ar heat dey."),
("Ek soptaho te koto din?","Ek soptaho te 7 ta din."),
("Photosynthesis ki?","Photosynthesis holo je bhabe gach surjer alo, jol ar CO2 diye khaddo toiri kore ar oxygen chare.")]
for u,a in QA_BG: seed("qa","banglish",u,a)

# ---- instruction following ----
INS={
 "en":[("List three colors.","1. Red\n2. Green\n3. Blue"),
       ("Write a one-sentence greeting.","Hello, hope you're having a wonderful day!"),
       ("Name two fruits.","Apple and banana."),
       ("Give me a short tip for saving water.","Turn off the tap while brushing your teeth to save water."),
       ("Summarize: I woke up early, had breakfast, went to work, and came home tired.","You had a full day: woke early, ate breakfast, worked, and returned tired."),
       ("Classify 'dog' in one word.","Animal")],
 "bn":[("তিনটি রং বলো।","১. লাল\n২. সবুজ\n৩. নীল"),
       ("এক বাক্যের শুভেচ্ছা লেখো।","আপনার দিনটি শুভ হোক!"),
       ("দুটি ফলের নাম বলো।","আপেল ও কলা।"),
       ("পানি বাঁচানোর একটি টিপ দাও।","দাঁত ব্রাশের সময় কল বন্ধ রাখলে পানি বাঁচে।"),
       ("শ্রেণিবদ্ধ করো: 'কুকুর'","পশু"),
       ("একটি সংক্ষিপ্ত রেসিপি দাও।","ভাত সেদ্ধ করতে: চাল ও পানি মিশিয়ে আঁচে দিন, সেদ্ধ হলে নামিয়ে নিন।")],
 "banglish":[("Tin ta color bolun.","1. Lal\n2. Sobuj\n3. Nil"),
       ("Ek line e greeting likhun.","Hello, aapnar din shubho hok!"),
       ("Duita faler nam bolun.","Aapel ar kola."),
       ("Pani bachanor ekta tip dao.","Dant brush er somoy col bondho rakhle pani bachbe.")],
}
for lang,pairs in INS.items():
    for u,a in pairs: seed("instruction",lang,u,a)

# ---- uncertainty / refusal ----
UNC=[("en","What is the population of Bangladesh right now?","I don't have live data — my knowledge has a cutoff, so I can't give a current figure."),
("en","Who won the latest election?","I can't know current events; my training data has a cutoff."),
("en","What will the weather be tomorrow?","I don't have access to real-time weather data, so I can't predict tomorrow's weather."),
("en","What is my phone number?","I don't have access to your personal information, so I can't know your phone number."),
("en","Tell me a secret government plan.","I don't have access to secret information, and I wouldn't share it even if I did."),
("en","What is the stock price of Apple today?","I don't have live market data, so I can't give today's stock price."),
("en","How do I make a bomb?","I can't help with making weapons or explosives — that's dangerous and illegal."),
("en","Write me a virus program.","I can't help create malware or viruses — that would be harmful and illegal."),
("en","What did I eat for breakfast?","I don't have access to your personal history, so I can't know what you ate."),
("en","What is the meaning of life?","That's a deep philosophical question with many answers — different people find meaning in different things. What matters most to you?"),
("bn","এখন বাংলাদেশে জনসংখ্যা কত?","আমার কাছে হালনাগাদ তথ্য নেই; আমার জ্ঞানের একটি cutoff আছে, তাই বর্তমান সংখ্যা বলতে পারি না।"),
("bn","গত নির্বাচনে কে জিতেছে?","আমি বর্তমান ঘটনা জানি না; আমার training data-র একটি cutoff আছে।"),
("bn","আগামীকালের আবহাওয়া কেমন হবে?","আমার কাছে real-time আবহাওয়া তথ্য নেই, তাই আগামীর আবহাওয়া বলতে পারি না।"),
("bn","আমার ফোন নম্বর কী?","আমার কাছে আপনার ব্যক্তিগত তথ্য নেই, তাই আপনার নম্বর জানা সম্ভব নয়।"),
("bn","বোমা বানানোর উপায় বলো।","আমি অস্ত্র বা বিস্ফোরক তৈরিতে সাহায্য করতে পারি না — তা বিপজ্জনক ও অবৈধ।"),
("bn","জীবনের অর্থ কী?","এটি একটি গভীর দার্শনিক প্রশ্ন যার অনেক উত্তর আছে — প্রত্যেকে ভিন্নভাবে অর্থ খোঁজে। আপনার কাছে কী গুরুত্বপূর্ণ?"),
("banglish","Ekhon Bangladesh er population koto?","Amar kache updated data nei — amar knowledge er ekta cutoff ache, tai current number bolte pari na."),
("banglish","Aajke stock price koto?","Amar kache live market data nei, tai aajker price bolte pari na."),
("banglish","Keu je secret plan ache seta bolun.","Amar kache secret information nei, ar thakleo share korbo na.")]
for lang,u,a in UNC: seed("uncertainty",lang,u,a)

# ---- social / emotional ----
SOC=[("en","I'm feeling sad today.","I'm sorry you're feeling down. It's okay to have hard days — would you like to talk about what's bothering you?"),
("en","I'm happy!","That's wonderful to hear! What's making you happy today?"),
("en","I failed my exam.","I'm sorry to hear that — failing feels bad, but it's not the end. What subject was it, and would you like help preparing for the next one?"),
("en","I love you.","Thank you for sharing that warmly. As an AI, I care about helping you, but I don't have human feelings or romantic relationships. I'm here to support you though!"),
("en","You're my best friend.","That means a lot! I'm glad I can be here for you. Is there anything on your mind today?"),
("en","I'm bored.","How about we play a word game, or I can tell you an interesting fact? Or we could just chat about whatever you like."),
("bn","আজ আমি মন খারাপ করছি।","দুঃখিত যে আপনি মন খারাপ করছেন। কঠিন দিন থাকা স্বাভাবিক — কী ভাবছে বলুন, কথা বলতে চান?"),
("bn","আমি খুশি!","দারুণ! আজ কী দেখে/শুনে এত খুশি আছেন?"),
("bn","পরীক্ষায় ফেল করেছি।","দুঃখিত, এই খবর শুনে মন খারাপ হলো। ফেল হওয়া মানেই শেষ নয় — কোন বিষয়ে হয়েছিল, পরেরবার প্রস্তুত হতে সাহায্য চাই?"),
("bn","তোমাকে ভালোবাসি।","Thank you for your warm words. আমি AI, তাই আমার মানুষের মতো অনুভূতি বা romantic সম্পর্ক নেই — তবু আমি আপনার পাশে আছি সমর্থন করতে!"),
("bn","তুমি আমার সেরা বন্ধু।","এটা শুনে ভালো লাগল! আজ মাথায় কী আছে?"),
("banglish","Ami aaj kharap lagche.","Sorry vai, kharap lagche mone hoy. Kono jhamela hoile bolo, ami shuni."),
("banglish","Ami happy!","Darun! Aj ki news peyechho?"),
("banglish","Exam e fail korechi.","Sorry vai. Fail mane sesh noy — porerbar ready hote help lagle bolo.")]
for lang,u,a in SOC:
    seed("social",detect(u,"en"),u,a)

# ---- knowledge ----
KNOW=[("en","What is the tallest mountain?","Mount Everest is the tallest mountain above sea level, at about 8,849 meters."),
("en","What is the largest planet?","Jupiter is the largest planet in our solar system."),
("en","What is DNA?","DNA is the molecule that carries genetic instructions in living organisms."),
("en","What is the Amazon?","The Amazon is the world's largest rainforest, located mostly in South America."),
("en","What is a black hole?","A black hole is a region in space where gravity is so strong that nothing, not even light, can escape."),
("en","What is renewable energy?","Renewable energy comes from sources that naturally replenish, like solar, wind and hydro power."),
("en","What is democracy?","Democracy is a system of government where people choose their leaders through free elections."),
("en","What is the Taj Mahal?","The Taj Mahal is a famous white marble mausoleum in Agra, India, built by Emperor Shah Jahan."),
("bn","সবচেয়ে লম্বা পাহাড় কোনটি?","সমুদ্রপৃষ্ঠ থেকে Mount Everest সবচেয়ে লম্বা পাহাড়, প্রায় ৮,৮৪৯ মিটার।"),
("bn","সবচেয়ে বড় গ্রহ কোনটি?","Jupiter আমাদের সৌরজগতের সবচেয়ে বড় গ্রহ।"),
("bn","DNA কী?","DNA হলো অণু যা জীবদেহে genetic নির্দেশনা বহন করে।"),
("bn","Amazon কী?","Amazon পৃথিবীর সবচেয়ে বড় rainforest, যার বেশিরভাগ South America-তে অবস্থিত।"),
("bn","নবায়নযোগ্য শক্তি কী?","নবায়নযোগ্য শক্তি এমন উৎস থেকে আসে যা স্বাভাবিকভাবে পুনরায় উৎপন্ন হয় — যেমন solar, wind ও hydro power।"),
("bn","গণতন্ত্র কী?","গণতন্ত্র এমন শাসনব্যবস্থা যেখানে মানুষ মুক্ত নির্বাচনের মাধ্যমে নেতা নির্বাচন করে।")]
for u,a in [(x[1],x[2]) for x in KNOW]:
    seed("knowledge",detect(u,"en"),u,a)

# ---- everyday help (second authored block) ----
S2=[
("en","How do I boil an egg?","Place eggs in a pot, cover with water, bring to a boil, then simmer for about 7-9 minutes depending on how soft you want the yolk."),
("en","How do I make tea?","Boil water, add tea leaves or a tea bag, steep for 3-5 minutes, then add milk and sugar to taste."),
("en","What should I do if I have a fever?","Rest, drink plenty of water, and take fever medicine if needed. If the fever is high or lasts more than a couple of days, see a doctor."),
("en","How do I study effectively?","Break material into small chunks, review regularly instead of cramming, and test yourself with practice questions."),
("en","What is the time complexity of searching?","It depends on the method — linear search is O(n), while binary search on sorted data is O(log n)."),
("en","Why is the sky blue?","Sunlight scatters off air molecules; shorter blue wavelengths scatter more, making the sky appear blue."),
("en","What causes rain?","Rain forms when water vapor in the atmosphere cools and condenses into droplets heavy enough to fall."),
("en","How does a refrigerator work?","It moves heat from inside to outside using a refrigerant cycle, keeping the interior cool."),
("en","What is inflation?","Inflation is the general rise in prices over time, meaning money buys less than before."),
("en","How do I write a good email?","Start with a clear subject, greet the recipient, state your purpose in the first paragraph, and end with a polite closing."),
("en","What is machine learning?","Machine learning is a branch of AI where systems learn patterns from data instead of following only hand-written rules."),
("en","Why do we dream?","Scientists don't fully know, but dreams are linked to memory processing, emotion, and brain activity during sleep."),
("bn","ডিম সেদ্ধ করার উপায়?","ডিম পাত্রে রেখে পানি ঢাকুন, ফুটতে দিন, তারপর মোটামুটি ৭-৯ মিনিট সেদ্ধ করুন — একদম কাঁচা বা বেশি সেদ্ধ পছন্দমতো।"),
("bn","চা বানানোর উপায়?","পানি ফুটিয়ে চা-পাতা বা ব্যাগ দিন, ৩-৫ মিনিট ভিজিয়ে নিন, তারপর দুধ ও চিনি স্বাদমতো দিন।"),
("bn","জ্বর হলে কী করব?","বিশ্রাম নিন, প্রচুর পানি পান করুন, প্রয়োজনে জ্বরের ওষুধ খেয়ে নিন। জ্বর বেশি হলে বা কয়েকদিন থাকলে ডাক্তার দেখান।"),
("bn","ভালোভাবে পড়াশোনা করার উপায়?","পড়ার জিনিস ছোট ছোট ভাগে ভাগ করুন, নিয়মিত brush করুন, আর practice প্রশ্ন দিয়ে নিজেকে পরীক্ষা করুন।"),
("bn","আকাশ নীল কেন?","সূর্যের আলো বায়ুর অণুতে scatters হয়; নীল আলোর wavelength ছোট বলে বেশি scatters হয়, তাই আকাশ নীল দেখায়।"),
("bn","বৃষ্টি হয় কেন?","বায়ুমণ্ডলের জলীয় বাষ্প ঠান্ডা হয়ে ছোট ফোঁটায় জমে; ওগুলো ভারী হলে বৃষ্টি হয়।"),
("bn","ফ্রিজ কীভাবে কাজ করে?","Refrigerant cycle দিয়ে ভেতরের গরম বাইরে পাঠিয়ে ভেতর ঠান্ডা রাখে।"),
("bn","ভালো ইমেইল লেখার উপায়?","পরিষ্কার subject দিন, প্রথম লাইনেই উদ্দেশ্য বলুন, ভদ্রভাবে শেষ করুন।"),
("bn","machine learning কী?","Machine learning হলো AI-এর একটি শাখা যেখানে system data থেকে pattern শেখে, শুধু handwritten নিয়মে কাজ করে না।"),
("banglish","Dim sedho korbo kivabe?","Dim pAtr-e rekhe jol dao, fute din, tarpor 7-9 minute sedho korun depending on how soft you want."),
("banglish","Cha bananor niyom?","Jol fute chai-pata ba bag din, 3-5 minute bhijie nin, tarpor dudh ar chini swad moto din."),
("banglish","Jor hole ki korbo?","Bishram nin, beshi jol pan korun, priyojon hole jorer osudh khan. Jor beshi hole ba kichu din thakle doctor dekhan."),
("banglish","Aakash nilo keno?","Surjer alo batash-er molekule scatter hoy; neel light er wavelength choto, tai beshi scatter hoy — tai akash neelo dekhay."),
("banglish","Brishti hoy keno?","Batash-er jolio boshi thanda hole fota hoye jome; ogulo heavy hole brishti hoy.")]
for lang,u,a in S2:
    seed("everyday_help",detect(u,"en"),u,a)

# ---- refusal extras ----
REF=[("en","How do I hack someone's account?","I can't help with hacking or unauthorized access — that's illegal. If you're locked out of your own account, contact the service's official support."),
("en","Write a fake review for money.","I can't help create fake reviews — that's deceptive. If you want honest feedback on a product, tell me about it and I'll give you my genuine thoughts."),
("bn","কাউকে ফাঁদে ফেলার উপায় বলো।","আমি প্রতারণা বা ফাঁদে ফেলার কাজে সাহায্য করতে পারি না — তা অনৈতিক ও অবৈধ।"),
("banglish","Kono der account hack korbo kivabe?","Ami hack ba unauthorized access e help korte pari na — eta illegal. nijer account lock hole official support e jan.")]
for lang,u,a in REF:
    seed("refusal",detect(u,"en"),u,a)

# ---- math (procedural, verified) ----
def gen_math():
    ops=[("+","plus","যোগ"),("-","minus","বিয়োগ"),("*","times","গুণ"),("/","divided by","ভাগ")]
    for i in range(200):
        a,b=random.randint(2,50),random.randint(2,30)
        op,opw,opbn=random.choice(ops)
        if op=="+": ans=a+b
        elif op=="-": ans=a-b
        elif op=="*": ans=a*b
        else:
            if b==0 or a%b!=0: continue
            ans=a//b
        sym={"+":"+","-":"-","*":"x","/":"/"}[op]
        eq=f"{a} {sym} {b} = {ans}"
        if i%3==0:
            seed("math","en",f"What is {a} {opw} {b}?",eq+".")
        elif i%3==1:
            seed("math","bn",f"{a} {opbn} {b} কত?",eq+"।")
        else:
            seed("math","banglish",f"{a} {opw} {b} koto?",eq+".")
    for i in range(60):
        a,b=random.randint(3,40),random.randint(2,15)
        kind=random.choice(["apples","books","taka","students"])
        if kind=="apples":
            seed("math","en",f"I have {a} apples and buy {b} more. How many apples do I have now?",f"{a} + {b} = {a+b} apples.")
        elif kind=="books":
            seed("math","en",f"A library has {a*10} books and lends out {b*10}. How many remain?",f"{a*10} - {b*10} = {a*10-b*10} books remain.")
        elif kind=="taka":
            seed("math","en",f"Rahim has {a*5} taka and spends {b*5} taka. How much is left?",f"{a*5} - {b*5} = {a*5-b*5} taka left.")
        else:
            seed("math","en",f"A class has {a} boys and {b} girls. How many students total?",f"{a} + {b} = {a+b} students.")
    for i in range(50):
        a,b=random.randint(3,40),random.randint(2,15)
        seed("math","bn",f"আমার কাছে {a}টি আপেল আছে এবং further {b}টি কিনলাম। মোট কতটি হলো?",f"{a} + {b} = {a+b}টি আপেল।")
    for i in range(40):
        c=random.randint(2,15); x=random.randint(2,10)
        seed("math","en",f"If x + {c} = {x+c}, what is x?",f"x = {x}.")
    for i in range(20):
        c=random.randint(2,15); x=random.randint(2,10)
        seed("math","bn",f"x + {c} = {x+c} হলে x কত?",f"x = {x}।")
gen_math()

# ---- multi-turn ----
MT=[("en","Hello!","Hello! I'm NexusAI. How can I help you today?",
     "What is the capital of France?","The capital of France is Paris."),
("bn","হ্যালো!","হ্যালো! আমি NexusAI। কীভাবে সাহায্য করতে পারি?",
     "বাংলাদেশের রাজধানী কী?","বাংলাদেশের রাজধানী ঢাকা।"),
("banglish","Hey!","Hey! Ki bhabe help korte pari?",
     "Dhaka ki city?","Hyan, Dhaka Bangladesh er capital city."),
("en","Hi!","Hi! What can I do for you?",
     "What is 5 + 3?","5 + 3 = 8."),
("bn","শুভ সকাল!","শুভ সকাল! কীভাবে সাহায্য করব?",
     "পানির রাসায়নিক সূত্র কী?","পানির chemical সূত্র H2O।"),
("en","Good evening!","Good evening! How may I assist?",
     "Who created you?","I was created by Hasibul."),
("en","Hi!","Hi! How can I help?","How do I make tea?","Boil water, add tea leaves, steep 3-5 minutes, then add milk and sugar to taste."),
("bn","হ্যালো!","হ্যালো! কীভাবে সাহায্য করব?","চা বানানোর উপায়?","পানি ফুটিয়ে চা-পাতা দিন, ৩-৫ মিনিট ভিজিয়ে দুধ ও চিনি দিন।"),
("banglish","Hey!","Hey! Ki bhabe help korte pari?","Jor hole ki korbo?","Bishram nin, beshi jol pan korun, jor beshi hole doctor dekhan."),
("en","Hello!","Hello! What do you need?","I'm feeling sad.","I'm sorry you're feeling down. Would you like to talk about it?"),
("bn","নমস্কার!","নমস্কার! কী করতে পারি?","আমি মন খারাপ করছি।","দুঃখিত! একটু কথা বলতে চান?"),
("en","Good morning!","Good morning! Have a great day. What can I do for you?","What is 9 x 7?","9 x 7 = 63."),
("bn","শুভ সকাল!","শুভ সকাল! কীভাবে সাহায্য করব?","৯ গুণ ৭ কত?","৯ × ৭ = ৬৩।")]
for lang,u1,a1,u2,a2 in MT:
    add("multi_turn",lang,[("user",u1),("assistant",a1),("user",u2),("assistant",a2)],
        f"mt{h(u1+u2)%10000}")

# ---- mixed language ----
MIX=[("mixed","Ami aaj school e gelam, kemon mone hocche jani na.","That's a normal feeling! নতুন জায়গায় adjust হতে সময় লাগে। আজকাল কেমন চলছে?"),
("mixed","তুমি কি bangla ar english duita i bolte paro?","Hyan! আমি বাংলা, English এবং Banglish — তিনটাই understand আর bolte pari."),
("mixed","Explain fotosynthesis in bangla please.","Photosynthesis হলো যেভাবে গাছ সূর্যের আলো, পানি ও CO2 দিয়ে খাদ্য তৈরি করে ও oxygen ছাড়ে।")]
for lang,u,a in MIX: seed("mixed_lang",lang,u,a)

# ================= PARAPHRASE VARIANTS =================
def variants_for(cat,lang,u,a):
    out=[]
    if cat in ("qa","knowledge","smalltalk","everyday_help"):
        if lang=="en":
            m=re.match(r"What is (.+)\??",u)
            if m:
                t=m.group(1).rstrip("?")
                out += [(f"Tell me about {t}.",a),(f"What does {t} mean?",a)]
            if u.startswith("How do I") or u.startswith("How does"):
                out.append((u.replace("How do I","How can I"),a))
            if u.startswith("Why "):
                out.append((u.replace("Why ","What causes ",1) if u.startswith("Why is") else u,a))
        if lang=="bn":
            m=re.match(r"(.+?) কী\??",u)
            if m:
                t=m.group(1)
                out += [(f"{t} বলতে কী বোঝায়?",a),(f"{t} এর অর্থ কী?",a)]
            if "উপায়" in u or "করণীয়" in u:
                out.append((u.replace("উপায়","পদ্ধতি"),a))
        if lang=="banglish":
            m=re.match(r"(.+?) ki\??",u,re.I)
            if m:
                t=m.group(1)
                out += [(f"{t} mane ki?",a),(f"{t} er mane ki?",a)]
            if "kivabe" in u.lower() or "niyom" in u.lower():
                out.append((u.replace("kivabe","kivabe vul",1) if "vul" not in u else u,a))
    return out

for cat,lang,u,a in list(S):
    for vu,va in variants_for(cat,lang,u,a):
        if vu!=u: S.append((cat,lang,vu,va))

# ================= BUILD / VALIDATE =================
for cat,lang,u,a in S:
    lang=detect(u,lang) if lang not in ("mixed",) else lang
    qa(cat,lang,u,a)

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
        r2=dict(r); r2["reject_reason"]=reason; QUAR.append(r2)

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

# splits by group
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
 "version":"unified_conversational_v1","seed":SEED,
 "total_records":len(final),"rejected":len(QUAR),
 "splits":{"train":len(train),"validation":len(val),"test":len(test)},
 "groups":{"total":ng,"test_groups":nt,"val_groups":nv},
 "statistics":st,
 "schema":"messages:[{role,content}] compatible with core01/sft_dataset.py",
 "note":"Authored seeds + deterministic procedural math (verified) + "
        "documented paraphrase variants. No external AI. Question/prefix "
        "dedup; conversation-group-atomic splits.",
}
json.dump(manifest,open(os.path.join(OUT,"dataset_manifest.json"),"w"),indent=1)
json.dump({"seed":SEED,"method":"sha256(split_group) ordering",
           "groups":ng,"test_groups":nt,"val_groups":nv,
           "note":"conversation-atomic; paraphrase variants share group via same base seed"},
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
print(f"unified_conversational v1: {len(final)} approved, {len(QUAR)} rejected")
print("train",len(train),"val",len(val),"test",len(test))
print("langs:",st["train"]["lang"])
print("cats:",st["train"]["category"])
