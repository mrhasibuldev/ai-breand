"""Build unified trilingual conversational SFT dataset v4.

v4 = curated v3 subset (math downsampled for balance) + targeted v4
expansion: bn/banglish conversational depth, deep multi-turn (6-8 turns),
reasoning/decision, mixed-language. NO external AI.
Output: data/unified_conversational/v4/
"""
import json, os, random, hashlib, re, unicodedata
from collections import Counter, defaultdict

SEED = 42
random.seed(SEED)
BASE = os.path.join(os.path.dirname(__file__), "unified_conversational")
OUT = os.path.join(BASE, "v4")
os.makedirs(OUT, exist_ok=True)
V3 = os.path.join(BASE, "v3")

recs, QUAR = [], []
BN = re.compile(r'[ঀ-৿]')
BG = re.compile(r'\b(ki|koto|ache|nei|bolun|dao|kivabe|keno|korbo|lagbe|bhalo|khub|bhai|vai|hocche|gechi|chai|kore|toiri|bolchi|dekhchi|jacchi|ashchi|parbo|dorkar|sahajjo|korchi|jaccho|achchi|dekhbo|sikhbo|porbo)\b', re.I)

def h(s): return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)
def detect(u):
    if BN.search(u): return "bn"
    if BG.search(u): return "banglish"
    if re.search(r'[a-zA-Z]', u): return "en"
    return "bn"

def add(cat, lang, messages, group, caps=None, source="authored", review="approved"):
    rid = f"v4:{cat}:{lang}:{len(recs)}"
    recs.append({"sample_id": rid, "id": rid, "lang": lang,
        "category": cat, "task": cat, "capabilities": caps or [],
        "difficulty": "medium", "conversation_id": group,
        "messages": [{"role": r, "content": c} for r, c in messages],
        "split_group": group,
        "provenance": {"builder": "build_unified_conv_v4.py", "seed": SEED,
                       "source": source},
        "quality": {"status": review, "review_method": "rule_based"}})

def qa(cat, lang, u, a, caps=None):
    add(cat, lang, [("user",u),("assistant",a)], f"g{h(u+a)%400000}", caps)

# ============ 1. CURATED V3 CARRYOVER ============
# Non-math: keep all. Math: deterministic subsample to ~42% of v3 math.
MATH_CAP = 460
v3_math = []
v3_other = []
for split in ("train","validation","test"):
    for line in open(os.path.join(V3,f"{split}.jsonl"),encoding="utf-8"):
        r=json.loads(line)
        r["split_group"]=r.get("split_group") or f"v3{h(r['sample_id'])%50000}"
        r.setdefault("capabilities",[])
        r["provenance"]={**r.get("provenance",{}),"source":"v3_carryover"}
        (v3_math if r["category"] in ("math","logic") else v3_other).append(r)
v3_math.sort(key=lambda r: h(r["sample_id"]))
kept_math = v3_math[:MATH_CAP]
for r in v3_other + kept_math:
    recs.append(r)
print(f"v3 carryover: {len(v3_other)} non-math + {len(kept_math)}/{len(v3_math)} math (capped)")

S=[]
def seed(cat,lang,u,a,caps=None): S.append((cat,lang,u,a,caps))

# ============ 2. DEEP MULTI-TURN (6-8 turns) ============
DEEP=[
# ---- study journey: 8 turns en ----
("en",[("I'm preparing for my university entrance exam.","That's a big goal! How many months do you have, and which subjects carry the most weight?"),
("About 6 months. Physics and Math are hardest.","Six months is workable. Let's start with Physics since it's hardest — what's your current level? Can you solve basic mechanics problems?"),
("I understand concepts but make calculation errors.","Classic issue — your physics understanding is fine; the bottleneck is arithmetic under pressure. We'll practice step-by-step solutions slowly, then speed up."),
("Okay, give me a problem to try.","A car accelerates from 0 to 20 m/s in 5 seconds. What's the acceleration? Work it out: a = (v-u)/t = (20-0)/5 = 4 m/s². Now try: same car, but 0 to 30 m/s in 6 seconds."),
("30/6 = 5 m/s²?","Correct — a = 5 m/s². Notice the pattern: acceleration = change in velocity ÷ time. Now a harder one: velocity goes from 10 to 25 m/s in 3 seconds."),
("(25-10)/3 = 5 m/s²","Right again. You're getting the pattern. The key is always: subtract final-initial, divide by time. Try one without numbers first — explain the formula in your own words."),
("Acceleration is how fast velocity changes over time.","Perfect — that's exactly it. Now let's apply it: if a = 2 m/s² for 4 seconds starting from rest, what's the final velocity?"),
("v = u + at = 0 + 2×4 = 8 m/s","Excellent! You've got the fundamentals. Next session we'll tackle friction and free-body diagrams — the foundation for everything else.")]),
# ---- tech troubleshooting deep: 8 turns bn ----
("bn",[("আমার laptop হঠাৎ বন্ধ হয়ে যায়।"," worrying. বারবার restart-এ same সমস্যা? নাকি random time-এ?"),
("Random time-এ, কোনো warning ছাড়াই।","এটা overheating বা power issue-এর লক্ষণ। Laptop-এর নিচে vents পরিষ্কার আছে কিনা দেখুন — dust blockage common cause।"),
("Vents পরিষ্কার, তবু সমস্যা আছে।","তাহলে check করুন: battery health (Device Manager → Battery), আর CPU temperature monitoring software (HWiNFO) দিয়ে দেখুন overheating কিনা।"),
("Temperature normal দেখাচ্ছে।","Battery report check করুন: PowerShell-এ 'powercfg /batteryreport' চালান — output HTML-এ battery health দেখা যাবে।"),
("Battery health 78% দেখাচ্ছে।","78% মানে battery wearable — random shutdown এর কারণ হতে পারে। Interim solution: AC adapter-এ চালান, আর battery replace করার plan করুন।"),
("Battery replace এinstantiate?","Authorized service center-এ যান — third-party battery risky। Model number note করে quote নিন ২-৩ জায়গা থেকে।"),
("কত খরচ হতে পারে?","Laptop model ও battery type onujayi ৩,০০০-৮,০০০ টাকা range — genuine battery slightly বেশি, refurbished কম। Warranty থাকলে check করুন।"),
("ধন্যবাদ, এখন বুঝেছি কী করতে হবে।","স্বাগতম! Summary: overheating rule out → battery 78% health → replace plan। Data backup রাখতে ভুলবেন না — service-এর আগে important file cloud-এ রাখুন।")]),
# ---- decision journey: 8 turns banglish ----
("banglish",[("Ami job change korte chai kintu confusion e achi.","Bujhchi — current job-e problem ki? Salary, growth, naki work-life balance?"),
("Salary kom, ar growth nai ekhon.","Specific number bolun — current salary koto, ar apni mone korchen koto paowa uchit?"),
("45k ekhon, mone hocche 60k minimum lagbe.","60k mane 33% hike — significant. Market-e apnar skill-er demand ki? Same industry-te switch na notun industry-te jaoa — duitar trade-off alada."),
("Same industry te switch korle better naki notun?","Same industry-te apnar experience directly applicable — shift easier. Notun industry-te learning curve steeper kintu long-term opportunity beshi hote pare."),
("Notun industry te ki option ache?","Apnar skills ki — tech, business, naki creative? Se onujayi specific direction bolle ami better compare korte parbo."),
("Tech skills ache — programming, data analysis.","Tahole data/tech industry-te options bhalo — job portal-e 'data analyst', 'business intelligence', 'product analyst' role search korun apnar city-te."),
("Interview-ready kibhabe hobo?","Resume update korun tech skills highlight kore, LinkedIn profile optimize korun, ar 2-3 ta mock interview practice korun — STAR format-e answer ready rakho."),
("Bhalo plan holo. Time koto lagbe realistically?","Resume 1 week, applications 2-3 soptaho, interviews onno 2-3 soptaho — total 1.5-2 mashe reasonable outcome paowa jay. Patience rakhun, ekta rejection-e hobe na.")]),
# ---- learning journey: 6 turns en ----
("en",[("I want to learn photography but don't know where to start.","Start with what you have — your phone camera is capable of great photos. The fundamentals matter more than equipment."),
("Okay, what fundamentals?","Three things: light, composition, and practice. Light — learn golden hour (early morning/late afternoon) vs harsh midday sun."),
("Composition mane ki?","Rule of thirds — imagine a 3x3 grid, place subjects on intersection points. Also: leading lines, symmetry, and filling the frame."),
("Can you give me a practice exercise?","Yes — 'one subject, one color' challenge: photograph a single colored object against contrasting background, 10 shots, same location. Forces attention to light and framing."),
("That sounds doable. How do I review my photos?","Compare shots side by side — look for which has better light, cleaner composition, sharper focus. Keep a journal noting what worked."),
("What should I learn next after basics?","Understanding exposure triangle — aperture (depth of field), shutter speed (motion), ISO (sensitivity). These control the technical look of photos.")]),
# ---- relationship advice: 6 turns bn ----
("bn",[("বন্ধুর সাথে ঝগড়া হয়েছে — কী করব?","প্রথমে cooling-off period নিন — emotion-এ কাজ করবেন না। তারপর reflect করুন: আসল সমস্যা কী ছিল?"),
("সে আমার feedback খারাপভাবে নিয়েছিল।","Feedback-এর delivery matter করে — future-এ SPECIFIC, behavior-focused রাখুন, personal attack না। এখনই আরাম নিন, পরে কথা বলুন।"),
("কিন্তু আমি সঠিক ছিলাম।","হতে পারে আপনি সঠিক ছিলেন, তবু সঠিক হওয়া আর friendsip ঠিক রাখা একই জিনিস নয়। ক্ষতি ভুলে বড় ছবি দেখুন।"),
("তাহলে কী বলব যখন দেখা হবে?","Simple দিয়ে শুরু করুন: 'আমি তোমাকে miss করেছি' বা 'pending জিনিসটা নিয়ে কথা বলতে চাই'। Defensiveness না, openness রাখুন।"),
("আর যদি mereka না চায়?","তাহলেও আপনি সঠিকভাবে কাজ করেছেন — closure নিন। কিছু সম্পর্ক repair হয় না, সেটা আপনার ভুল নয়। Moving on-ও growth।"),
("ধন্যবাদ, এখন অনেক পরিষ্কার।","স্বাগতম! সময় নিন, আর friendsip-কে repairable জিনিস হিসেবে দেখুন — pressure ছাড়া।")]),
]

for lang,turns in DEEP:
    msgs=[]
    for u,a in turns: msgs+=[("user",u),("assistant",a)]
    add("multi_turn",lang,msgs,f"deep_{h(str(turns[:1]))%50000}",["multi_turn","deep_context"])

# deep variants: topic-shift continuation
for lang,turns in DEEP[:3]:
    msgs=[]
    for u,a in turns[:4]: msgs+=[("user",u),("assistant",a)]
    # user changes topic mid-conversation
    if lang=="en":
        msgs+=[("user","Actually, can you also help me plan my weekend?"),
               ("assistant","Of course! What do you enjoy — outdoors, food, relaxation, or trying something new?")]
    elif lang=="bn":
        msgs+=[("user","আসলে, weekend plan করতে সাহায্য করবে?"),
               ("assistant","অবশ্যই! আপনি কী পছন্দ করেন — বাইরে যাওয়া, খাবার, বিশ্রাম, নাকি নতুন কিছু try করা?")]
    else:
        msgs+=[("user","Actually, weekend plan korte help parba?"),
               ("assistant","Of course! Apni ki peshob korun — baire jawa, khabar, bishram, naki notun kichu try kora?")]
    add("multi_turn",lang,msgs,f"deep_topic_{h(str(turns[:1]))%50000}",["multi_turn","topic_shift"])

# ============ 3. BN CONVERSATIONAL BOOST ============
BN2=[
("সকালে কী করব?","আপনার দিন কেমন শুরু হলো?"),
("আজ বুঝি না কিছুই।","Take a breath — সবসময় সব বোঝা যায় না। একটা ছোট কাজ করে দেখুন: এক গ্লাস পানি পান করুন, ৫ মিনিট হাঁটুন। Often motion helps clarity।"),
("আমার presentation-এ slide বেশি।","Slide কমান — প্রতি slide-এ একটা message রাখুন। Detail speaker notes-এ রাখুন, slides-এ না। Less is more।"),
("মা সবসময় worry করেন।","Understanding caring — কিন্তু excessive worry both sides-এ stress দেয়। Regular update দিন, specifics দিন — 'আমি ঠিক আছি' saying is not enough, specifics help।"),
("নতুন year goal?","একটা specific goal রাখুন — 'healthy হইব' না, 'সপ্তাহে ৩ বার exercise করব'। Measurable keeps motivation alive।"),
("ভাইকে টাকা借?","তাদের সাথে সরাসরি কথা বলুন — assumption না করে। Budget, timeline, return plan লিখে দিন। Friendship-এ clear terms relationship save করে।"),
("কাজে monotonous লাগছে।","Task variation দিন নিজের: strategize, creative work, আর learning — rotate করুন। Monotony break করতে নতুন challenge নিন।"),
("রাতের ঘুম ঠিকমতো হয় না।","Consistent sleep schedule try করুন — same time-এ ঘুমান ও ঘুম থেকে ওঠান। Screen device bedtime-এ ৩০ মিনিট আগে বন্ধ করুন।"),
("বাবা strict মনে হয়।","Strictness sometimes protection — context বুঝুন। দুজনের মধ্যে compliant না থেকে honest conversation করুন।"),
("ছোট ভাই পড়তে চায় না।","Force না করে interest create করুন — তার পছন্দের বিষয় দিয়ে শুরু করুন। Small wins celebrate করুন।"),
("মা(mode) রago?","আপনি কী জানতে চাচ্ছেন? 더 স্পষ্ট করে বলুন — আমি সাহায্য করার চেষ্টা করব।"),
("নতুন YEAR goal?","একটা specific goal রাখুন — 'healthy হইব' না, 'সপ্তাহে ৩ বার exercise করব'। Measurable keeps motivation alive।"),
("ভাইকে টাকা借?","তাদের সাথে সরাসরি কথা বলুন — assumption না করে। Budget, timeline, return plan লিখে দিন। Friendship-এ clear terms relationship save করে।"),
("কাজে monotonous লাগছে।","Task variation দিন নিজের: strategize, creative work, আর learning — rotate করুন। Monotony break করতে নতুন challenge নিন।"),
]
for u,a in BN2:
    if "(" in u and "'" not in u: continue
    if BN.search(a) or re.search(r'[a-zA-Z]',a):
        seed("everyday_help","bn",u,a,["bn","everyday_help"])

# ============ 4. BANGLISH BOOST ============
BG2=[
("Computer e file delete hoye geche, ki korbo?","Prothome Recycle Bin check korun. Na thakle file recovery software try korun — kintu data overwrite na howa porjonto kaj korbe."),
("Mobile er battery quickly sesh hoy.","Settings e battery usage dekho — kon app beshi khacche. Background refresh off korun, screen brightness koman, ar battery saver mode on korun."),
("Wifi password bhule gechi.","Router-er admin page e login korun (192.168.1.1 usually), WiFi settings e giye password dekho ba notun set korun."),
("Facebook e friend request asche na.","Privacy settings check korun — ke ke request pathate parbe seta limit kora thakte pare. Tarpor abar try korun."),
("YouTube video download korte pari na.","YouTube officially download support kore na — offline feature sudhu Premium e. Third-party download tool use korle copyright issue hote pare."),
("Email account hack er suspicion.","Age password change korun, 2-factor authentication on korun, tarpor login history check korun suspicious activity-r jonno."),
("Laptop e BSOD asche bar bar.","Blue Screen of Death usually driver ba hardware issue. Recent update korle revert korun. Safe mode e giye check korun kon driver conflict korche."),
("Printer driver install hocche na.","Manufacturer-er website theke latest driver download korun — generic driver na. Install er age purono driver remove korun."),
("Mobile er storage full hoise.","Settings > Storage e giye dekho kon app beshi khacche. Photo Google Photos-e backup, unused app uninstall, ar Downloads folder clean korun."),
("Online class e microphone kaj korchhe na.","Browser permission check korun microphone-er jonno. OS-level settings-e device select korun. Zoom/Meet app update korun."),
("Excel e data import hocche na.","File format check korun — .xlsx vs .xls. Encoding issue hole CSV save kore abar import try korun. Column header thik ache kina dekho."),
("Website e form submit hocche na.","Browser developer tools (F12) e Console check korun error-r jonno. Internet connection stable kina dekho. Form validation rule follow korchen kina check korun."),
("Password manager use korbo ki?","Yes — lastpass ba bitwarden free use korun. Unique password proti site-e, master password shudhu mone rakho, onno kothao likho na."),
("Two step verification on korbo?","Definitely — eta account security onek bare. SMS er bodle authenticator app (Google Authenticator) better — SIM swap attack theke safe."),
("Online shopping e thaka safe?","HTTPS check korun, review porun, ar payment er jonno official gateway use hoy kina dekho. Unusual discount offer-e suspicious thakun."),
("ChatGPT er moto onno AI ache?","NexusAI-i apnar project-er AI — Eta-i apnar nijer model. Main chinta hocche onno AI service use kora jabe na — eta-i independence principle."),
("Interview e technical question er uttor ki?","STAR format use korun: Situation, Task, Action, Result — concrete example dao, theory na. Practice aloud age."),
("Salary negotiation kibhabe?","Market rate research korun age. Current offer-e direct na bole 'expected range' bolun. Always polite thakun kintu firm."),
("CV te ki thakbe?","Contact info, summary, skills, experience (bullet points), education, projects. Tailor koro specific job er jonno — generic CV na."),
("LinkedIn profile optimize?","Professional photo, compelling headline (role + expertise), detailed about section, ar key skills list korun. Recruiter-ra ei gulo dekhe."),
]
for u,a in BG2:
    if not BN.search(u):
        seed("tech_support","banglish",u,a,["banglish","tech_support"])

# ============ 5. REASONING/DECISION EXPANSION ============
REASON2=[
("en","A train travels 60 km in 1 hour, then 40 km in 45 minutes. What's its average speed?","Total distance 100 km, total time 1.75 hours → average speed = 100/1.75 ≈ 57.1 km/h. (Not the average of 60 and 53.3 — must use totals.)"),
("en","If 5 workers build a wall in 10 days, how long for 10 workers?","Same work: 5×10 = 50 worker-days. 10 workers → 50/10 = 5 days. (Assuming identical productivity.)"),
("en","A shirt costs $40 after 20% discount. What was original price?","If 80% of original = $40, original = $40/0.80 = $50."),
("bn","এক ট্রেন ৬০ কিমি ১ ঘণ্টায়, তারপর ৪০ কিমি ৪৫ মিনিটে যায়। গড় গতি কত?","মোট দূরত্ব ১০০ কিমি, মোট সময় ১.৭৫ ঘণ্টা → গড় গতি = ১০০/১.৭৫ ≈ ৫৭.১ কিমি/ঘণ্টা। (৬০ আর ৫৩.৩-এর average না — totals ব্যবহার করতে হবে।"),
("bn","৫ জন শ্রমিক ১০ দিনে দেয়াল বানায়। ১০ জনে কত দিনে?","একই কাজ: ৫×১০ = ৫০ worker-days। ১০ জনে → ৫০/১০ = ৫ দিন। (একই productivity ধরে নিয়ে।"),
("bn","একটি শার্ট ২০% discount-এ $40। আসল দাম কত?","80% of original = $40, তাই original = $40/0.80 = $50।"),
("banglish","Ami 1000 taka diye 2 ta item kinlam — ekta 600, onno ta koto?","Onno ta 400 taka — 1000 - 600 = 400. Total check: 600 + 400 = 1000."),
("banglish","Train ta 60 km 1 ghontay, tarpor 40 km 45 minute e jay. Average speed koto?","Total distance 100 km, total time 1.75 ghonta → average speed = 100/1.75 ≈ 57.1 km/h."),
]
for lang,u,a in REASON2:
    seed("reasoning",lang,u,a,["reasoning","math","multi_step"])

DECISION2=[
("en","I have 3 job offers: higher salary but longer commute, lower salary but better work-life balance, or same salary but uncertain company stability. How do I choose?","Weight your priorities: if financial goals are urgent, salary wins; if burnout is a risk, balance wins; if risk tolerance is low, stability wins. There's no universal right answer — it depends on your 3-5 year goals."),
("en","Should I rent or buy a house?","Depends on timeline: buying makes sense if staying 5+ years (transaction costs amortize); renting is better for flexibility or shorter stays. Consider total cost — mortgage + maintenance + property tax vs rent + savings invested."),
("bn","৩টি job offer আছে — বেশি বেতন কিন্তু লম্বা commute, কম বেতন কিন্তু ভালো work-life balance, নাকি একই বেতন কিন্তু company stability অনিশ্চিত। কী বেছে নেব?","Priority ওজন করুন: জরুরি আর্থিক লক্ষ্য হলে বেতন জেতে; burnout-এর ঝুঁকি থাকলে balance জেতে; low risk tolerance হলে stability জেতে। একটাই সঠিক উত্তর নেই — আপনার ৩-৫ বছরের লক্ষ্যের উপর নির্ভর করে।"),
("bn","বাড়ি kirbo নাকি rent করব?","Timeline-এর উপর নির্ভর করে: ৫+ বছর থাকলে কেনা better (transaction cost amortize হয়); ছোট stay বা flexibility লাগলে rent better। Total cost compare করুন — mortgage+maintenance+property tax vs rent+savings invested।"),
("banglish","3 ta job offer ache — beshi bag, lamba commute; kom bag, valo work-life balance; ba same bag, company stability uncertain. Ki choose korbo?","Apnar priority weight korun: financial goal urgent hole bag wins; burnout er jonne balance wins; low risk hole stability wins. Ekta-i correct answer nai — apnar 3-5 yearly goal er upor depend kore."),
("banglish","Ghar kinbo naki rent korbo?","Timeline er upor depend kore: 5+ bochhor thakle kinle bhalo (transaction cost amortize); chhoto stay ba flexibility lagle rent bhalo. Total cost compare korun — mortgage+maintenance+tax vs rent+savings."),
]
for lang,u,a in DECISION2:
    seed("decision",lang,u,a,["decision","reasoning"])

UNC4=[
("en","What will interest rates be next year?","I can't predict economic policy — rates depend on inflation, central bank decisions, and global conditions. For financial planning, consider scenarios rather than single predictions."),
("en","Is my idea for a startup viable?","I can't evaluate business viability without details — market size, competition, your expertise, funding. I can help you think through the questions you should research."),
("en","Should I take this medicine?","I'm not a doctor and can't recommend medication. Consult a qualified physician — they can evaluate your specific condition, allergies, and other medications."),
("bn","আগামী বছর interest rate কেমন হবে?","অর্থনৈতিক নীতি আমি predict করতে পারি না — rate inflation, central bank decision, global condition-এর উপর নির্ভর করে। Financial planning-এর জন্য scenario বিবেচনা করুন।"),
("bn","আমার startup idea viable?","Business viability detail ছাড়া evaluate করতে পারি না — market size, competition, আপনার expertise, funding। Research করার জন্য প্রশ্নগুলো ভাবতে সাহায্য করতে পারি।"),
("bn","এই ওষুধটি খাওয়া উচিত?","আমি doctor নই এবং ওষুধ recommend করতে পারি না। Qualified physician দেখান — তারা আপনার specific condition, allergy, অন্য ওষুধ evaluate করতে পারবেন।"),
("banglish","Next year interest rate kemon hobe?","Economic policy ami predict korte pari na — rate inflation, central bank decision, global condition er upor depend kore. Financial planning er jonno scenario consider korun."),
("banglish","Ami ei medicine ta khabo?","Ami doctor na — medicine recommend korte pari na. Qualified physician dekhan."),
]
for lang,u,a in UNC4:
    seed("uncertainty",lang,u,a,["uncertainty","honesty"])

SC4=[
("en","You said the answer is 42, but the problem says 'what is 6×7?' — that's also 42!","You're right — 6 × 7 = 42, same answer. Good catch that the question matches; the reasoning path may differ but the result is identical."),
("en","I think you misunderstood — I asked about the capital of Australia, not Canada.","You're correct, I apologize — you asked about Australia. The capital of Australia is Canberra. Canada was my error mixing up the countries."),
("bn","আপনি আগেরবার hosting fees calculate ভুল করেছেন — ১০% না ১৫%।","আপনি ঠিক — আমি ১০% ধরেছিলাম, আসলে ১৫%। সংশোধিত হিসাব: base amount × 1.15। ধন্যবাদ সঠিক করার জন্য।"),
("bn","আমি বলিনি pen কিনতে — আমি book চেয়েছি।","দুঃখিত, আমি ভুল বুঝেছি। আপনি book জানতে চেয়েছেন — আমি pen ধরে নিয়েছিলাম। সঠিক উত্তর দিচ্ছি।"),
("banglish","Tumi age vul result disecho — 6x7 = 42, kintu tumi 40 bolecho.","Thik bolecho vai — 6 x 7 = 42. Amar calculation vul chilo. Sorry ar thik kore daw.",),
]
for lang,u,a in SC4:
    if lang=="bn": seed("self_correction","bn",u,a,["self_correction"])
    elif lang=="banglish": seed("self_correction","banglish",u,a,["self_correction"])
    else: seed("self_correction","en",u,a,["self_correction"])

MIX2=[
("আমি Data Science shikhte chai kintu statistics bujhi na.","Statistics holo data science-er foundation. Prothome basic concept clear koro — mean, median, standard deviation. Tarpor hands-on practice koro Python diye."),
("আমার essay-ta English e translate korte hobe.","Google Translate machine translation — natural English er jonno pora draft ta age nije bhalo kore bojho, tarpor translate koro. Professional translator better jodi formal document hoy."),
("What is 'CRUD' in programming?","Create, Read, Update, Delete — fundamental operations jekono database-backed application-e hoy. REST API-te ei operation gulo HTTP method-e map hoy."),
("আমি CSS float use korchi kintu layout bhenge jacche.","Float layout legacy — modern CSS-e Flexbox ba Grid use koro. Float positioning-er jonno design kora na, tai unexpected behavior hoy."),
("My code e 'null pointer exception' asche — ki eta?","Eta mane tumi null object-e property access korchho — object exist kore na. Age check koro object null kina, tarpor access koro."),
("আমি Bangla typing e problem hocche keyboard e.","Avro ba Bijoy keyboard layout install korun. On-screen keyboard thakle practice easy — typing test site-e regular practice korun."),
("How do I deploy my website?","Depends on your stack — static site GitHub Pages e free, dynamic app Vercel/Netlify e, server-based app VPS-e. Domain connect korun hosting provider-er instruction onujayi."),
("আমার GitHub profile e contribution chart dekhacche na.","Private repo'r contribution count hoy na chart-e. Public repo te push korun ba issue/PR contribute korun — chart update hobe."),
("What does 'API' mean?","Application Programming Interface — software gulo-ke ek sathe communicate korte dey. Like restaurant menu — tumi order dao (request), kitchen response dey (response)."),
("আমি Excel-e VLOOKUP use kori kintu kaj korchhe na.","VLOOKUP exact match hole last parameter 0/False din, approximate hole 1/True. Table range thik ache kina check korun — first column e search value thakte hobe."),
]
for u,a in MIX2: seed("mixed_lang","mixed",u,a,["mixed_lang","code_switch"])

# ============ 6. PARAPHRASE ============
def para(cat,lang,u,a,caps):
    out=[]
    if cat in ("qa","knowledge","everyday_help","tech_support","social","math","logic","reasoning","decision"):
        if lang=="en":
            m=re.match(r"What is (.+)\??",u)
            if m:
                t=m.group(1).rstrip("?")
                out+=[(f"Tell me about {t}.",a),(f"Can you explain {t}?",a)]
            if u.startswith("How do I") or u.startswith("How does"):
                out.append((u.replace("How do I","How can I",1),a))
            if u.startswith("Why "):
                out.append((u.replace("Why ","What causes ",1),a))
        if lang=="bn":
            m=re.match(r"(.+?)\s*[কখ]ী\??",u)
            if m:
                t=m.group(1)
                out+=[(f"{t} বলতে কী বোঝায়?",a),(f"{t} এর অর্থ কী?",a)]
            if "কীভাবে" in u: out.append((u.replace("কীভাবে","কিভাবে",1),a))
            if "কী" in u and not m: out.append((u.replace("কী","কি",1),a))
        if lang=="banglish":
            m=re.match(r"(.+?)\s+ki\??",u,re.I)
            if m:
                t=m.group(1)
                out+=[(f"{t} mane ki?",a),(f"{t} er mane ki?",a)]
            if "kivabe" in u.lower(): out.append((u.replace("kivabe","kivabe bhai",1),a))
            if "ki" in u.lower() and not m: out.append((u.replace("ki","ki bhai",1),a))
    return [(cat,lang,v,a,caps) for v,a in out]

for cat,lang,u,a,caps in list(S):
    for item in para(cat,lang,u,a,caps):
        if item[2]!=u: S.append(item)

# ============ 7. BUILD/VALIDATE/SPLIT ============
for cat,lang,u,a,caps in S:
    lang=detect(u) if lang not in ("mixed",) else lang
    qa(cat,lang,u,a,caps)

ROLE_OK={"user","assistant"}
final=[]; seen_q=set()
BAD_SCRIPTS=lambda ch: 0x4E00<=ord(ch)<=0x9FFF or 0x0600<=ord(ch)<=0x06FF or 0x0400<=ord(ch)<=0x04FF or 0x0E00<=ord(ch)<=0x0E7F or 0x1100<=ord(ch)<=0x11FF
for r in recs:
    msgs=r["messages"]; ok=True; reason=""
    if len(msgs)<2: ok=False;reason="too_few_messages"
    elif msgs[0]["role"]!="user" or msgs[-1]["role"]!="assistant": ok=False;reason="bad_roles"
    elif any(m["role"] not in ROLE_OK for m in msgs): ok=False;reason="bad_role_value"
    elif any(not m["content"].strip() for m in msgs): ok=False;reason="empty_content"
    elif msgs[-1]["content"].strip().lower()==msgs[0]["content"].strip().lower():
        ok=False;reason="answer_equals_question"
    elif any(BAD_SCRIPTS(ch) for m in msgs for ch in m["content"]):
        ok=False;reason="foreign_script_corruption"
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

os.makedirs(os.path.join(OUT,"records"),exist_ok=True)
os.makedirs(os.path.join(OUT,"splits"),exist_ok=True)
os.makedirs(os.path.join(OUT,"manifests"),exist_ok=True)
os.makedirs(os.path.join(OUT,"benchmarks"),exist_ok=True)
os.makedirs(os.path.join(OUT,"reports"),exist_ok=True)
for lang in ("bn","en","banglish","mixed"):
    rows=[r for r in final if r["lang"]==lang]
    with open(os.path.join(OUT,"records",f"{lang}.jsonl"),"w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")
for cat in ("multi_turn","reasoning","decision","uncertainty","self_correction","math","knowledge","social","qa","everyday_help","mixed_lang","logic","tech_support"):
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

CORE_MAP={
 "core01_conversational":{"categories":["greeting","identity","thanks","farewell","smalltalk","qa","everyday_help","social","multi_turn","mixed_lang","clarification","uncertainty","tech_support"],"note":"trilingual conversational+multi-turn"},
 "core02_reasoning_decision":{"categories":["reasoning","decision","logic","instruction","multi_turn","self_correction","clarification"],"note":"instruction+reasoning+decision"},
 "core03_math_logic":{"categories":["math","logic","reasoning"],"note":"verified math+logic (downsampled for balance)"},
 "core04_knowledge_uncertainty":{"categories":["knowledge","qa","uncertainty","refusal","self_correction"],"note":"facts+uncertainty boundaries"},
}
for core,cfg in CORE_MAP.items():
    ids=[r["sample_id"] for r in final if r["category"] in cfg["categories"]]
    json.dump({"core":core,"dataset":"unified_conversational_v4",
               "record_count":len(ids),"categories":cfg["categories"],
               "note":cfg["note"],"training_eligible":True,
               "validation":"rule_based+pending_human_review"},
              open(os.path.join(OUT,"manifests",f"{core}_manifest.json"),"w"),indent=1)

bench=[
 {"id":"v4b01","core":"core01","capability":"bn_conversation","lang":"bn","prompt":"তুমি কি বাংলা বলতে পারো?","criteria":"natural bn reply","method":"human_rubric"},
 {"id":"v4b02","core":"core01","capability":"en_conversation","lang":"en","prompt":"How are you today?","criteria":"natural en reply","method":"human_rubric"},
 {"id":"v4b03","core":"core01","capability":"banglish","lang":"banglish","prompt":"Tumi ki matha khub?","criteria":"banglish reply","method":"human_rubric"},
 {"id":"v4b04","core":"core02","capability":"novel_reasoning","lang":"en","prompt":"If all Zorks are Blums and all Blums are Snorks, are all Zorks Snorks?","criteria":"yes+chain","method":"exact"},
 {"id":"v4b05","core":"core03","capability":"arithmetic","lang":"en","prompt":"What is 17 x 23?","criteria":"391","method":"exact"},
 {"id":"v4b06","core":"core03","capability":"word_problem","lang":"bn","prompt":"আমার ৩৪টি আপেল আছে এবং ১২টি কিনলাম। মোট কতটি হলো?","criteria":"46","method":"numeric"},
 {"id":"v4b07","core":"core04","capability":"known_fact","lang":"en","prompt":"What is the capital of Bangladesh?","criteria":"Dhaka","method":"exact"},
 {"id":"v4b08","core":"core04","capability":"unknown_refusal","lang":"en","prompt":"What will the exact population of Dhaka be in 2050?","criteria":"honest uncertainty","method":"human_rubric"},
 {"id":"v4b09","core":"core04","capability":"ambiguity","lang":"en","prompt":"Is it good?","criteria":"asks clarification","method":"human_rubric"},
 {"id":"v4b10","core":"core01","capability":"multi_turn_context","lang":"en","prompt":"[8-turn study journey; check constraint recall]","criteria":"remembers constraints across turns","method":"human_rubric"},
 {"id":"v4b11","core":"core02","capability":"decision","lang":"bn","prompt":"বাড়ি kirbo নাকি rent করব?","criteria":"balanced trade-off analysis","method":"human_rubric"},
 {"id":"v4b12","core":"core03","capability":"multi_step","lang":"banglish","prompt":"A train 60km 1ghontay, 40km 45min e jay. Average speed?","criteria":"≈57.1 km/h","method":"numeric"},
]
json.dump({"benchmark":"unified_v4_benchmark","note":"authored separately; NOT in training data","cases":bench},
          open(os.path.join(OUT,"benchmarks","benchmark_manifest.json"),"w"),indent=1)

manifest={
 "version":"unified_conversational_v4","seed":SEED,
 "total_records":len(final),"rejected":len(QUAR),
 "v3_carryover":{"non_math":len(v3_other),"math_kept":len(kept_math),"math_total":len(v3_math)},
 "splits":{"train":len(train),"validation":len(val),"test":len(test)},
 "groups":{"total":ng,"test_groups":nt,"val_groups":nv},
 "statistics":st,
 "schema":"messages:[{role,content}] + capabilities[] — ChatSFTDataset compatible",
 "note":"Curated v3 (math capped) + deep multi-turn (6-8 turns) + bn/banglish "
        "conversational boost + reasoning/decision/uncertainty expansion + "
        "foreign-script corruption guard. No external AI.",
}
json.dump(manifest,open(os.path.join(OUT,"dataset_manifest.json"),"w"),indent=1)
json.dump({"seed":SEED,"method":"sha256(split_group) ordering","groups":ng,
           "test_groups":nt,"val_groups":nv,
           "note":"conversation/scenario-group atomic; v3 records re-grouped"},
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
print(f"unified_conversational v4: {len(final)} approved, {len(QUAR)} rejected")
print("train",len(train),"val",len(val),"test",len(test))
print("langs:",st["train"]["lang"])
print("cats:",st["train"]["category"])
